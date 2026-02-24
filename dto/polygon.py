from typing import List

from dto.rect import Rect
from utils import to_hex
from dto.point import Point


class Polygon:
    points: List[Point]
    color: [int]
    hex_color: str

    def __init__(self, points: List[Point], color: [int]):
        self.points = points
        self.color = color
        self.hex_color = f'#{to_hex(color[0])}{to_hex(color[1])}{to_hex(color[2])}'

    def recolor(self, color: [int]):
        self.color = color
        self.hex_color = f'#{to_hex(color[0])}{to_hex(color[1])}{to_hex(color[2])}'

    def to_rect(self) -> Rect:
        assert len(self.points) == 4, \
            f'Polygon should have 4 points for converting to rect, but have {len(self.points)}'
        min_x = min(p.x for p in self.points)
        min_y = min(p.y for p in self.points)
        max_x = max(p.x for p in self.points)
        max_y = max(p.y for p in self.points)
        start_point = Point(min_x, min_y)
        end_point = Point(max_x, max_y)
        return Rect(start_point, end_point, self.color)

    def __str__(self):
        return f'Polygon(points = {self.points})'

    def __eq__(self, other) -> bool:
        if isinstance(other, Polygon):
            return self.points == other.points
        return False

    def __hash__(self):
        return sum([p.__hash__() for p in self.points])
