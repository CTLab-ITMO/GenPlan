import cv2
import numpy as np

from config import PNG_PATH, CLEAN_PNG_PATH, BLACK_COLOR_BORDER
from utils import get_full_path


def main(min_black_value=BLACK_COLOR_BORDER, initial_png_path=PNG_PATH, final_png_path=CLEAN_PNG_PATH):
    image = cv2.imread(get_full_path(initial_png_path))

    if image is None:
        raise ValueError(f'Not image by path {get_full_path(initial_png_path)}')

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    (w, h) = len(gray_image), len(gray_image[0])

    new_image = np.zeros((w, h))

    for i in range(w):
        for j in range(h):
            if gray_image[i][j] >= min_black_value:
                new_image[i][j] = 255

    cv2.imwrite(get_full_path(final_png_path), new_image)


if __name__ == "__main__":
    main()
