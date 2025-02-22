import torch
from diffusers import FluxPipeline, AuraFlowPipeline
from torch.utils.hipify.hipify_python import InputError

from config import PNG_PATH
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
    else:
        raise InputError('Unknown type of model.')

    image.save(get_full_path(PNG_PATH))


if __name__ == "__main__":
    main("plan", Type.FLUX.value)
