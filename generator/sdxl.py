import config
from generator.loss.white_loss import WhiteLoss

import torch
from torch import autocast


class SDXL:

    def __init__(self, pipe, height=512, width=512, guidance_scale=7.5,
                 num_inference_steps=50, num_images_per_prompt=1,
                 torch_device="cuda"):

        self.pipe = pipe
        self.height = height
        self.width = width
        self.guidance_scale = guidance_scale
        self.num_inference_steps = num_inference_steps
        self.num_images_per_prompt = num_images_per_prompt
        self.torch_device = torch_device
        self.white_loss = WhiteLoss()

        # make sure the VAE is in float32 mode, as it overflows in float16
        self.needs_upcasting = self.pipe.vae.dtype == torch.float16 and self.pipe.vae.config.force_upcast

    def inference(self, prompt, generator, batch_size=1,
                  negative_prompt='blurry, artifacts, bad quality, worst color, text',
                  use_white_loss=config.USE_WHITE_LOSS,
                  stop_consider_additional_loss=7,
                  output_type='pil', use_watermark=None):

        # 1 and 2 steps - Check_inputs, batch_size and device respectively
        original_size = (self.height, self.width)
        target_size = (self.height, self.width)

        height = self.height or self.pipe.default_sample_size * self.pipe.vae_scale_factor
        width = self.width or self.pipe.default_sample_size * self.pipe.vae_scale_factor

        original_size = original_size or (height, width)
        target_size = target_size or (height, width)

        (prompt_2, callback_steps, negative_prompt_2, prompt_embeds,
         negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds,
         callback_on_step_end_tensor_inputs) = None, None, None, None, None, None, None, None

        self.pipe.check_inputs(
            prompt,
            prompt_2,
            height,
            width,
            callback_steps,
            negative_prompt,
            negative_prompt_2,
            prompt_embeds,
            negative_prompt_embeds,
            pooled_prompt_embeds,
            negative_pooled_prompt_embeds,
            callback_on_step_end_tensor_inputs,
        )

        # 3. Encode input prompt
        lora_scale = None
        with torch.no_grad():
            (
                prompt_embeds, negative_prompt_embeds,
                pooled_prompt_embeds, negative_pooled_prompt_embeds) = self.pipe.encode_prompt(
                prompt, negative_prompt=negative_prompt,
                num_images_per_prompt=self.num_images_per_prompt,
                do_classifier_free_guidance=True,
                lora_scale=lora_scale
            )
        # 4. Prepare timesteps
        self.pipe.scheduler.set_timesteps(self.num_inference_steps)
        self.pipe.scheduler.timesteps = self.pipe.scheduler.timesteps.to(dtype=torch.float16)

        # 5. Prepare latent variables
        latents = torch.randn(
            (batch_size * self.num_images_per_prompt, self.pipe.unet.in_channels, height // 8, width // 8),
            generator=generator,
        )

        num_channels_latents = self.pipe.unet.in_channels
        latents = self.pipe.prepare_latents(
            batch_size * self.num_images_per_prompt,
            num_channels_latents,
            height,
            width,
            prompt_embeds.dtype,
            self.torch_device,
            generator,
            latents,
        )
        # 6. Prepare extra step kwargs.
        extra_step_kwargs = self.pipe.prepare_extra_step_kwargs(generator, eta=0)

        # 7. Prepare added time ids & embeddings
        original_size = (height, width)
        target_size = (height, width)
        crops_coords_top_left = (0, 0)

        add_text_embeds = pooled_prompt_embeds

        if self.pipe.text_encoder_2 is None:
            text_encoder_projection_dim = int(pooled_prompt_embeds.shape[-1])
        else:
            text_encoder_projection_dim = self.pipe.text_encoder_2.config.projection_dim

        add_time_ids = self.pipe._get_add_time_ids(
            original_size,
            crops_coords_top_left,
            target_size,
            dtype=prompt_embeds.dtype,
            text_encoder_projection_dim=text_encoder_projection_dim,
        ).to(self.torch_device)

        negative_add_time_ids = add_time_ids

        prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
        add_text_embeds = torch.cat([negative_pooled_prompt_embeds, add_text_embeds], dim=0)
        add_time_ids = torch.cat([negative_add_time_ids, add_time_ids], dim=0).repeat(
            batch_size * self.num_images_per_prompt, 1)
        # 8. Denoising loop
        num_warmup_steps = 0
        # 9. Optionally get Guidance Scale Embedding
        timestep_cond = None
        if self.pipe.unet.config.time_cond_proj_dim is not None:
            guidance_scale_tensor = torch.tensor(self.pipe.guidance_scale - 1).repeat(
                batch_size * self.num_images_per_prompt)
            timestep_cond = self.pipe.get_guidance_scale_embedding(
                guidance_scale_tensor, embedding_dim=self.pipe.unet.config.time_cond_proj_dim
            ).to(device=self.torch_device, dtype=latents.dtype)

        with autocast("cuda"):
            with self.pipe.progress_bar(total=self.num_inference_steps) as progress_bar:
                for i, t in enumerate(self.pipe.scheduler.timesteps):
                    # Get sigma
                    sigma = self.pipe.scheduler.sigmas[i]
                    # expand the latents if we are doing classifier free guidance
                    latent_model_input = torch.cat([latents] * 2) if self.guidance_scale > 0 else latents

                    latent_model_input = self.pipe.scheduler.scale_model_input(latent_model_input, t).to(torch.float16)

                    # predict the noise residual
                    added_cond_kwargs = {"text_embeds": add_text_embeds, "time_ids": add_time_ids}
                    with torch.no_grad():
                        noise_pred = self.pipe.unet(
                            latent_model_input,
                            t,
                            encoder_hidden_states=prompt_embeds,
                            timestep_cond=timestep_cond,
                            # cross_attention_kwargs=pipe.cross_attention_kwargs,
                            added_cond_kwargs=added_cond_kwargs,
                            return_dict=False,
                        )[0]
                    # perform guidance
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)
                    # Apply white loss if needed
                    if use_white_loss and i < stop_consider_additional_loss:
                        latents = self.white_loss.add_loss(
                            self.pipe, latents, noise_pred,
                            sigma, self.needs_upcasting, step=i
                        )
                    # whether or not to save every denoised images during the diffusion process
                    latents = self.pipe.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]

                    if i == len(self.pipe.scheduler.timesteps) - 1 or (
                            (i + 1) > num_warmup_steps and (i + 1) % self.pipe.scheduler.order == 0):
                        progress_bar.update()
        # Get the final raster image
        if not output_type == "latent":

            if self.needs_upcasting:
                self.pipe.upcast_vae()
                latents = latents.to(next(iter(self.pipe.vae.post_quant_conv.parameters())).dtype)
            with torch.no_grad():
                latents = latents.to(dtype=torch.float16)
                image = self.pipe.vae.decode(latents / self.pipe.vae.config.scaling_factor, return_dict=False)[0]

            # cast back to fp16 if needed
            if self.needs_upcasting:
                self.pipe.vae.to(dtype=torch.float16)
        else:
            image = latents
        # Apply watermark if needed
        if not output_type == "latent":
            # apply watermark if available
            if use_watermark is not None:
                image = self.pipe.watermark.apply_watermark(image.detach())

            image = self.pipe.image_processor.postprocess(image, output_type=output_type)
        # Offload all models
        self.pipe.maybe_free_model_hooks()

        return image

    def latents_to_pil(self, latents, use_watermark=True):
        # bath of latents -> list of images
        latents = (1 / self.pipe.vae.config.scaling_factor) * latents
        with torch.no_grad():
            image = self.pipe.vae.decode(latents, return_dict=False)[0]

        if use_watermark:
            image = self.pipe.watermark.apply_watermark(image)

        pil_images = self.pipe.image_processor.postprocess(image, output_type='pil')

        return pil_images