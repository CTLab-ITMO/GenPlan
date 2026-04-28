import os

import torch
from PIL import Image
from diffusers import FluxPipeline, AuraFlowPipeline, DiffusionPipeline, LMSDiscreteScheduler, AutoencoderKL, \
    ControlNetModel
from torch.utils.hipify.hipify_python import InputError

from config import PNG_PATH
from dto.input_params.gen_model_type import Type
from .sdxl import SDXL
from utils import get_full_path

IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
# Need to test algorithm without generation
FALLBACK_IMAGE = "fallback.png"


def main(prompt: str, model_type: Type, control_image_path: str = None):
    if model_type == Type.FALLBACK:
        image = Image.open(os.path.join(FALLBACK_IMAGE))
        image.save(get_full_path(PNG_PATH))
        return
    if control_image_path is None:
        generate_without_control_net(prompt, model_type)
    else:
        generate_with_control_net(prompt, model_type, control_image_path)


def generate_without_control_net(prompt: str, model_type: Type):
    if model_type == Type.FLUX:
        pipeline = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.bfloat16,
        )

        image = pipeline(
            prompt,
            height=IMAGE_HEIGHT,
            width=IMAGE_WIDTH,
            guidance_scale=0.0,
            num_inference_steps=4,
            max_sequence_length=256,
            generator=torch.Generator("cpu").manual_seed(0),
            controlnet_conditioning_scale=1.0
        ).images[0]
    elif model_type == Type.AURA_FLOW:
        pipeline = AuraFlowPipeline.from_pretrained(
            "fal/AuraFlow",
            torch_dtype=torch.float16,
        ).to("cuda")

        image = pipeline(
            prompt=prompt,
            height=IMAGE_HEIGHT,
            width=IMAGE_WIDTH,
            num_inference_steps=50,
            generator=torch.Generator().manual_seed(0),
            guidance_scale=3.5,
            controlnet_conditioning_scale=1.0,
        ).images[0]
    elif model_type == Type.SDXL:
        pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            use_safetensors=True,
            torch_dtype=torch.float16,
            variant="fp16",
            scheduler=LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear",
                                           num_train_timesteps=1000),
            vae=AutoencoderKL.from_pretrained('madebyollin/sdxl-vae-fp16-fix').to(torch.float16)
        ).to("cuda")

        sdxl = SDXL(
            pipe,
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT
        )
        image = sdxl.inference(prompt, generator=torch.Generator("cpu").manual_seed(33))[0]
    else:
        raise InputError('Unknown type of model.')

    image.save(get_full_path(PNG_PATH))


def generate_with_control_net(prompt: str, model_type: Type, control_image_path: str):
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-canny",
        torch_dtype=torch.float16
    )
    control_image = Image.open(control_image_path).resize((IMAGE_WIDTH, IMAGE_HEIGHT))
    if model_type == Type.FLUX:
        pipeline = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            controlnet=controlnet,
            torch_dtype=torch.bfloat16,
        )

        image = pipeline(
            prompt,
            image=control_image,
            height=IMAGE_HEIGHT,
            width=IMAGE_WIDTH,
            guidance_scale=0.0,
            num_inference_steps=4,
            max_sequence_length=256,
            generator=torch.Generator("cpu").manual_seed(0),
            controlnet_conditioning_scale=1.0
        ).images[0]
    elif model_type == Type.AURA_FLOW:
        pipeline = AuraFlowPipeline.from_pretrained(
            "fal/AuraFlow",
            torch_dtype=torch.float16,
            controlnet=controlnet,
        ).to("cuda")

        image = pipeline(
            prompt=prompt,
            image=control_image,
            height=IMAGE_HEIGHT,
            width=IMAGE_WIDTH,
            num_inference_steps=50,
            generator=torch.Generator().manual_seed(0),
            guidance_scale=3.5,
            controlnet_conditioning_scale=1.0,
        ).images[0]
    elif model_type == Type.SDXL:
        pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            use_safetensors=True,
            torch_dtype=torch.float16,
            variant="fp16",
            controlnet=controlnet,
            scheduler=LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear",
                                           num_train_timesteps=1000),
            vae=AutoencoderKL.from_pretrained('madebyollin/sdxl-vae-fp16-fix').to(torch.float16)
        ).to("cuda")

        sdxl = SDXL(
            pipe,
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT
        )
        image = sdxl.inference(prompt, generator=torch.Generator("cpu").manual_seed(33))[0]
    else:
        raise InputError('Unknown type of model.')

    image.save(get_full_path(PNG_PATH))


if __name__ == "__main__":
    main("plan", Type.AURA_FLOW.value)
