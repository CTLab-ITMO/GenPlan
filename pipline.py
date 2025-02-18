import argparse
import generator.generator as generator
import vectorization.vectorization as vectorization
import preprocessor.preprocessor as preprocessor


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
                        default="gen_plan.svg"
                        )
    args = parser.parse_args()

    print("Generating plan")
    generator.main(args.__dict__["text"])

    print("Preprocessing image")
    preprocessor.main()

    print("Plan vectorization")
    vectorization.main(args.__dict__["output_svg"])
    pass


if __name__ == "__main__":
    main()
