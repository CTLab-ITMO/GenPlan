import argparse
import os

import generator.generator as generator
import vectorization.vectorization as vectorization
import preprocessor.preprocessor as preprocessor
from config import RESULTS_FOLDER
from dto.input_params.gen_model_type import Type as GenType
from dto.input_params.resultl_type import Type as ResultType
from utils import parse_formats, parse_coordinates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text",
                        help="Text promt of vector plan.",
                        type=str,
                        default="plan"
                        )
    parser.add_argument("--generation_model",
                        help="Name of generation model. SDXL with white loss by default.",
                        type=str,
                        default=GenType.FALLBACK.value
                        )
    parser.add_argument("--result_type",
                        help="Expected result type. 2D plan by default.",
                        type=str,
                        default=ResultType.TWO_DIMENSIONAL.value
                        )
    parser.add_argument("--formats",
                        help="Expected formats of 3D results. None by default",
                        type=str,
                        default=None
                        )
    parser.add_argument("--control_image_coordinates",
                        help="Coordinates of the foundation for generation. Example: (1,2),(2,3),(3,4),(4,5),(1,2). None by default",
                        type=str,
                        default=None
                        )
    args = parser.parse_args()

    if not os.path.exists(RESULTS_FOLDER):
        os.mkdir(RESULTS_FOLDER)

    print("Generating plan...")
    generator.main(
        prompt=args.__dict__["text"],
        model_type=GenType.parse(args.__dict__["generation_model"]),
        control_image_path=parse_coordinates(args.__dict__["control_image_coordinates"]),
    )

    print("Preprocessing image...")
    preprocessor.main()

    print("Plan vectorization...")
    vectorization.main(
        description=args.__dict__["text"],
        result_type=ResultType.parse(args.__dict__["result_type"]),
        formats=parse_formats(formats=args.__dict__["formats"]),
    )
    pass


if __name__ == "__main__":
    main()
