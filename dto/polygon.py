from typing import List
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

    def __str__(self):
        return f'Polygon(points = {self.points})'

    def __eq__(self, other) -> bool:
        if isinstance(other, Polygon):
            return self.points == other.points
        return False

    def __hash__(self):
        return sum([p.__hash__() for p in self.points])
