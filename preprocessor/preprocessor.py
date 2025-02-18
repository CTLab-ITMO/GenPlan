import cv2
import numpy as np

from config import PNG_PATH, CLEAN_PNG_PATH, BLACK_COLOR_BORDER
from utils import get_full_path


def main():
    image = cv2.imread(get_full_path(PNG_PATH))

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    (w, h) = len(gray_image[0]), len(gray_image)

    new_image = np.zeros((w, h))

    for i in range(w):
        for j in range(h):
            if gray_image[i][j] > BLACK_COLOR_BORDER:
                new_image[i][j] = 255

    cv2.imwrite(get_full_path(CLEAN_PNG_PATH), new_image)


if __name__ == "__main__":
    main()
