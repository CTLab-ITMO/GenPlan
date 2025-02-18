import cv2
import numpy as np

from dto.rect import Rect
import drawsvg as draw
from tqdm import tqdm

from config import MIN_THICKNESS, MAX_PERCENTILE, MAX_VALUE, MAX_DEVIATION, CLEAN_PNG_PATH
from utils import get_full_path
from vectorization.dto.point import Point


def reorder_points(point1: Point, point2: Point) -> (Point, Point):
    x_min = min(point1.x, point2.x)
    x_max = max(point1.x, point2.x)
    y_min = min(point1.y, point2.y)
    y_max = max(point1.y, point2.y)
    return Point(x_min, y_min), Point(x_max, y_max)


def prepare_image(image) -> np.array:
    prepared_image = np.zeros((len(image), len(image[0])))
    for i in tqdm(range(len(image))):
        for j in range(len(image[0])):
            if image[i][j][0] > 0 or image[i][j][1] > 0 or image[i][j][2] > 0:
                value = 1
            else:
                value = 0
            if i == 0 and j == 0:
                prepared_image[i][j] = value
            elif i == 0:
                prepared_image[i][j] = value + prepared_image[i][j - 1]
            elif j == 0:
                prepared_image[i][j] = value + prepared_image[i - 1][j]
            else:
                prepared_image[i][j] = value + prepared_image[i - 1][j] + prepared_image[i][j - 1] - \
                                       prepared_image[i - 1][j - 1]
    return prepared_image


def calculate_fitness(start_point: Point, end_point: Point, prepared_image: np.array) -> int:
    if start_point.x == 0 and start_point.y == 0:
        return prepared_image[end_point.y][end_point.x]
    elif start_point.y == 0:
        return prepared_image[end_point.y][end_point.x] - prepared_image[end_point.y][start_point.x - 1]
    elif start_point.x == 0:
        return prepared_image[end_point.y][end_point.x] - prepared_image[start_point.y - 1][end_point.x]
    else:
        return prepared_image[end_point.y][end_point.x] - prepared_image[start_point.y - 1][end_point.x] - \
            prepared_image[end_point.y][start_point.x - 1] + prepared_image[start_point.y - 1][start_point.x - 1]


def is_available_rect(point1, point2, prepared_image) -> bool:
    start_point, end_point = reorder_points(point1, point2)
    width = end_point.x - start_point.x + 1
    height = end_point.y - start_point.y + 1

    max_percentile_value = MAX_PERCENTILE * width * height

    if width < MIN_THICKNESS or height < MIN_THICKNESS:
        return False

    fitness = calculate_fitness(start_point, end_point, prepared_image)

    return fitness <= max_percentile_value and fitness <= MAX_VALUE


def find_similar_points(initial_point: Point, points: [Point]) -> [Point]:
    x = initial_point.x
    y = initial_point.y
    similar_points = set()
    points_has_eq_x = []
    points_has_eq_y = []
    for point in points:
        if point.x == x and point.y == y:
            continue
        elif point.x == x:
            points_has_eq_x.append(point)
        elif point.y == y:
            points_has_eq_y.append(point)

    for point1 in points_has_eq_x:
        for point2 in points:
            if point1.y == point2.y and point1.x != point2.x:
                similar_points.add(point2)

    for point1 in points_has_eq_y:
        for point2 in points:
            if point1.x == point2.x and point1.y != point2.y:
                similar_points.add(point2)

    return list(similar_points)


def average_similar_points_coordinates(points: [Point]):
    xs = np.ones(len(points)) * -1
    ys = np.ones(len(points)) * -1

    for i, point1 in enumerate(points):
        if xs[i] == -1:
            similar_xs = []
            similar_x_indexes = []
            for j, point2 in enumerate(points):
                if xs[j] == -1 and abs(point1.x - point2.x) <= MAX_DEVIATION:
                    similar_xs.append(point2.x)
                    similar_x_indexes.append(j)
            avg_x = np.average(similar_xs)
            for index in similar_x_indexes:
                xs[index] = avg_x

    for i, point1 in enumerate(points):
        if ys[i] == -1:
            similar_ys = []
            similar_y_indexes = []
            for j, point2 in enumerate(points):
                if ys[j] == -1 and abs(point1.y - point2.y) <= MAX_DEVIATION:
                    similar_ys.append(point2.y)
                    similar_y_indexes.append(j)
            avg_y = np.average(similar_ys)
            for index in similar_y_indexes:
                ys[index] = avg_y

    new_points = []
    for xy in zip(xs, ys):
        new_points.append(Point(xy[0], xy[1]))
    return new_points


def find_rects(points: [Point], prepared_image):
    new_points = set()
    rects = []
    for point1 in tqdm(points):
        for point2 in find_similar_points(point1, points):
            new_points.add(point1)
            new_points.add(point2)
            if is_available_rect(point1, point2, prepared_image):
                start_point, end_point = reorder_points(point1, point2)
                rect = Rect(start_point, end_point, [0, 0, 0])
                if not rects.__contains__(rect):
                    rects.append(rect)
                    new_points.add(Point(rect.start_point.x, rect.start_point.y))
                    new_points.add(Point(rect.end_point.x, rect.start_point.y))
                    new_points.add(Point(rect.start_point.x, rect.end_point.y))
                    new_points.add(Point(rect.end_point.x, rect.end_point.y))
    return rects, new_points


def main(final_svg_path: str):
    image = cv2.imread(get_full_path(CLEAN_PNG_PATH))
    corners = cv2.goodFeaturesToTrack(image, maxCorners=1000, qualityLevel=0.1, minDistance=3)

    points = []
    for corner in corners:
        x, y = corner.ravel()
        p = Point(x, y)
        points.append(p)
    points = average_similar_points_coordinates(points)

    prepared_image = prepare_image(image)
    _, new_points = find_rects(points, prepared_image)
    _, new_points = find_rects(new_points, prepared_image)
    rects, new_points = find_rects(new_points, prepared_image)

    pic = draw.Drawing(len(image[0]), len(image))
    for rect in rects:
        pic.append(rect.to_rect())
    pic.save_svg(final_svg_path)


if __name__ == "__main__":
    main(final_svg_path="test.svg")
