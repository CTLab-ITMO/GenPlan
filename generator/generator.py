import torch
from diffusers import FluxPipeline, AuraFlowPipeline, DiffusionPipeline, LMSDiscreteScheduler, AutoencoderKL
from torch.utils.hipify.hipify_python import InputError

from config import PNG_PATH
from generator.sdxl import SDXL
from generator.type import Type
from utils import get_full_path


def main(prompt: str, model_type: str):
    if model_type == Type.FLUX.value:
        pipeline = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.bfloat16
        )
        pipeline.enable_model_cpu_offload()  # save some VRAM by offloading the model to CPU. Remove this if you have enough GPU power

        image = pipeline(
            prompt,
            height=512,
            width=512,
            guidance_scale=0.0,
            num_inference_steps=4,
            max_sequence_length=256,
            generator=torch.Generator("cpu").manual_seed(0)
        ).images[0]
    elif model_type == Type.AURA_FLOW.value:
        pipeline = AuraFlowPipeline.from_pretrained(
            "fal/AuraFlow",
            torch_dtype=torch.float16
        ).to("cuda")

        image = pipeline(
            prompt=prompt,
            height=512,
            width=512,
            num_inference_steps=50,
            generator=torch.Generator().manual_seed(666),
            guidance_scale=3.5,
        ).images[0]
    elif model_type == Type.SDXL.value:
        pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            use_safetensors=True, torch_dtype=torch.float16,
            variant="fp16",
            scheduler=LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear", num_train_timesteps=1000),
            vae=AutoencoderKL.from_pretrained('madebyollin/sdxl-vae-fp16-fix').to(torch.float16)
        ).to("cuda")

        sdxl = SDXL(pipe)
        image = sdxl.inference(prompt,
                               generator=torch.Generator("cpu").manual_seed(33))[0]
    else:
        raise InputError('Unknown type of model.')

    image.save(get_full_path(PNG_PATH))


if __name__ == "__main__":
    main("plan", Type.FLUX.value)
