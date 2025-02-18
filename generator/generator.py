from clarifai.client.model import Model

from config import PNG_PATH
from utils import get_full_path


def main(prompt: str):
    inference_params = dict(quality="standard", size='512x512')

    model_prediction = Model("https://clarifai.com/openai/dall-e/models/dall-e-3").predict_by_bytes(
        input_bytes=prompt.encode(),
        input_type="text",
        inference_params=inference_params,
    )

    output_base64 = model_prediction.outputs[0].data.image.base64

    with open(get_full_path(PNG_PATH), 'wb') as f:
        f.write(output_base64)


if __name__ == "__main__":
    main("plan")
