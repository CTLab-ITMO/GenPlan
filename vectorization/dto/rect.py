from vectorization.dto.point import Point
import drawsvg as draw


class Rect:
    start_point: Point
    end_point: Point
    color: [int]

    def __init__(self, start_point: Point, end_point: Point, color: [int]):
        self.start_point = start_point
        self.end_point = end_point
        self.color = color

    def get_color(self, x: int, y: int) -> [int]:
        if self.start_point.x <= x < self.end_point.x and self.start_point.y <= y < self.end_point.y:
            return self.color
        return None

    def __str__(self):
        return f'Rect(start = {self.start_point}, end = {self.end_point})'

    def to_rect(self) -> draw.Rectangle:
        return draw.Rectangle(self.start_point.x, self.start_point.y, self.end_point.x - self.start_point.x,
                              self.end_point.y - self.start_point.y, fill='#000000')

    def __eq__(self, other) -> bool:
        if isinstance(other, Rect):
            return self.start_point == other.start_point and self.end_point == other.end_point and self.color == other.color
        return False
