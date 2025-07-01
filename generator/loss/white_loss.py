import torch
from generator.loss.masks import rectangle_edging_mask, random_mask, circle_edging_mask
import config

class WhiteLoss:

    def __init__(
            self, torch_device="cuda",
            edging_type=config.EDGING_TYPE,
            loss_scale=config.LOSS_SCALE,
            which_step_scale=2,
            loss_multiply=1.1,
            add_to_edge_mask=2.0,
            print_loss_update=False
    ):

        self.torch_device = torch_device
        self.edging_type = edging_type
        self.add_to_edge_mask = add_to_edge_mask
        self.loss_scale = loss_scale
        self.which_step_scale = which_step_scale
        self.loss_multiply = loss_multiply
        self.print_loss_update = print_loss_update

    def add_loss(self, pipe, latents, noise_pred, sigma, needs_upcasting, step):

        # Requires grad on the latents)
        latents = latents.detach().requires_grad_()
        # Get the predicted x0:
        latents_x0 = latents - sigma * noise_pred
        # Decode to image space
        if needs_upcasting:
            pipe.upcast_vae()
        latents_x0 = latents_x0.to(next(iter(pipe.vae.post_quant_conv.parameters())).dtype)
        # Use SDXL decoder
        denoised_images = pipe.vae.decode(latents_x0 / pipe.vae.config.scaling_factor, return_dict=False)[0]
        # Data standartization
        denoised_images = (denoised_images - torch.mean(denoised_images)) / torch.std(denoised_images)
        # Make distribution inside (0, 1) bound
        denoised_images = (denoised_images * 0.5 + 0.5).clamp(0, 1)
        # cast back to fp16 if needed
        if needs_upcasting:
            pipe.vae.to(dtype=torch.float16)
        # Calculate loss
        loss, latent_mask = self.apply_loss(denoised_images)
        # Add scaling
        loss *= self.loss_scale
        # Change loss for the next steps if needed
        if step % self.which_step_scale == 0:
            if self.print_loss_update:
                print('\n', 'step - ', step, 'loss:', loss.item(), 'loss_scale:', self.loss_scale)
            self.loss_scale = self.loss_scale * self.loss_multiply
        # Get gradient
        cond_grad = -torch.autograd.grad(loss, latents)[0]
        # Modify the latents based on this gradient
        latents = self.modify_latents_according_to_loss(latents, cond_grad, sigma, latent_mask)

        return latents

    def apply_loss(self, images):
        latent_ratio = 8
        # Extract parameters
        b, height, width = images.shape[0], images.shape[-2], images.shape[-1]
        # Initialize mask
        mask = torch.zeros((height, width))
        # Choose the edging type
        if self.edging_type == 'rectangle':
            mask, latent_mask = rectangle_edging_mask(
                mask,
                add=self.add_to_edge_mask,
                latent_ratio=latent_ratio
            )

        elif self.edging_type == 'random_mask':
            error, latent_mask = random_mask(
                images, height, width,
                self.torch_device,
                add=self.add_to_edge_mask,
                latent_ratio=latent_ratio)

            return error, latent_mask

        else:
            mask, latent_mask = circle_edging_mask(
                height,
                width,
                add=self.add_to_edge_mask,
                latent_ratio=latent_ratio
            )
        # Modify type for masks
        latent_mask = latent_mask.to(self.torch_device)
        mask = mask.to(self.torch_device)
        # Condition for which elements mask is applied
        fill_ones = torch.ones(3).to(self.torch_device).view(3, 1, 1)

        # Apply masks to images
        edging_images = torch.where(mask[None, :, :] > 1, fill_ones, images)
        # Calculate error
        error = torch.abs(images - edging_images).mean()

        return error, latent_mask

    def modify_latents_according_to_loss(self, latents, cond_grad, sigma, latent_mask):

        # Modify the latents based on this gradient
        latents = latents.detach()
        latents = latents + cond_grad * sigma ** 2 * latent_mask

        return latents