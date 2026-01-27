import argparse
import generator.generator as generator
import vectorization.vectorization as vectorization
import preprocessor.preprocessor as preprocessor
from config import SVG_PATH
from dto.input_params.gen_model_type import Type as GenType
from dto.input_params.resultl_type import Type as ResultType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text",
                        help="Text promt of vector plan.",
                        type=str,
                        default="plan"
                        )
    parser.add_argument("--output_svg",
                        help="Svg path to vector plan. If it doesn't exits, it will create.",
                        type=str,
                        default=SVG_PATH
                        )
    parser.add_argument("--generation_model",
                        help="Name of generation model. SDXL with white loss by default.",
                        type=str,
                        default=GenType.SDXL.value
                        )
    parser.add_argument("--result_type",
                        help="Expected result type. 2D plan by default.",
                        type=str,
                        default=ResultType.TWO_DIMENSIONAL.value
                        )
    args = parser.parse_args()

    print("Generating plan")
    generator.main(prompt = args.__dict__["text"], model_type = args.__dict__["generation_model"])

    print("Preprocessing image")
    preprocessor.main()

    print("Plan vectorization")
    vectorization.main(
        description=args.__dict__["text"],
        final_svg_path=args.__dict__["output_svg"],
        result_type=args.__dict__["result_type"]
    )
    pass

if __name__ == "__main__":
    main()