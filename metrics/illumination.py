from typing import List

from dto.point import Point
from dto.polygon import Polygon
from dto.rect import Rect


# Calculation of the NLC (natural light coefficient)
# Living rooms, kitchens: 0.5% — 1.0%
# Offices, offices : 1.0%
# Workrooms : 3.0%
def calculate_illumination(floor: Polygon, windows: List[Rect]) -> float:
    windows_square = 0.0
    for w in windows:
        windows_square += w.max_size * w.min_size
    floor_square = polygon_area(floor.points)
    t = 0.55  # light transmission of windows (светопропускание окон)
    q = 0.7  # average reflection (среднее отражение)
    n = 1.4  # reflection coefficient(коэффициент отражения)
    return (t * q * n * windows_square / floor_square) * 100


def polygon_area(points: List[Point]) -> float:
    x = [p.x for p in points]
    y = [p.y for p in points]
    x.append(x[0])
    y.append(y[0])
    area = 0.0
    for i in range(len(points)):
        area += (x[i] * y[i + 1] - x[i + 1] * y[i])
    return abs(area) / 2.0
