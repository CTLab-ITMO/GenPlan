import os
import re

from PIL import Image, ImageDraw

from config import IMAGE_SHIFT, IMAGE_WIDTH, IMAGE_HEIGHT, CONTROL_PNG_PATH
from dto.enum.format_type import FormatType


def get_full_path(path: str) -> str:
    parent_directory = os.getcwd()
    return os.path.join(parent_directory, path)


def to_hex(number: int) -> str:
    s = hex(number).split('x')[-1]
    if len(s) == 1:
        s = '0' + s
    return s


def parse_formats(formats):
    if formats is not None:
        parts = [p.strip() for p in formats.split(",")]
        parts = [p for p in parts if p]
        return [FormatType.parse(p) for p in parts]
    return None


def normalize_coordinates(coordinates):
    xs = []
    ys = []
    normalized_coordinates = []
    for x, y in coordinates:
        xs.append(x)
        ys.append(y)
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    for x, y in coordinates:
        new_x = ((x - min_x) / (max_x - min_x)) * (IMAGE_WIDTH - IMAGE_SHIFT) + IMAGE_SHIFT / 2
        new_y = ((y - min_y) / (max_y - min_y)) * (IMAGE_HEIGHT - IMAGE_SHIFT) + IMAGE_SHIFT / 2
        normalized_coordinates.append((new_x, new_y))
    return normalized_coordinates


def parse_coordinates(coordinates):
    if coordinates is not None:
        coordinates = [(float(x), float(y)) for x, y in re.findall(r'\(\s*(\d+)\s*,\s*(\d+)\s*\)', coordinates)]
        coordinates = normalize_coordinates(coordinates)
        img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), "white")
        draw = ImageDraw.Draw(img)
        for i in range(len(coordinates) - 1):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[i + 1]
            draw.line((x1, y1, x2, y2), fill="black", width=5)
        img.save(CONTROL_PNG_PATH)
        return CONTROL_PNG_PATH
    return None
