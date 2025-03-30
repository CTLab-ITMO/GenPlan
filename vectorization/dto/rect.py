from utils import to_hex
from vectorization.dto.point import Point
import drawsvg as draw


class Rect:
    start_point: Point
    end_point: Point
    color: [int]
    hex_color: str

    def __init__(self, start_point: Point, end_point: Point, color: [int]):
        assert start_point.x <= end_point.x and start_point.y <= end_point.y, \
            f'Start point coordinates must be less then end point. Found start_point = {start_point}, end_point = {end_point}'
        self.start_point = start_point
        self.end_point = end_point
        self.color = color
        self.hex_color = f'#{to_hex(color[0])}{to_hex(color[1])}{to_hex(color[2])}'

    def get_color(self, x: int, y: int) -> [int]:
        if self.start_point.x <= x < self.end_point.x and self.start_point.y <= y < self.end_point.y:
            return self.color
        return None

    def recolor(self, color: [int]):
        self.color = color
        self.hex_color = f'#{to_hex(color[0])}{to_hex(color[1])}{to_hex(color[2])}'

    def to_svg(self, drawing: draw.Drawing):
        drawing.append(draw.Rectangle(self.start_point.x, self.start_point.y, self.end_point.x - self.start_point.x,
                                      self.end_point.y - self.start_point.y, fill=self.hex_color))

    def takeover_rect(self, rect) -> bool:
        return self.start_point.x <= rect.start_point.x and self.start_point.y <= rect.start_point.y and \
            self.end_point.x >= rect.end_point.x and self.end_point.y >= rect.end_point.y

    def has_common_part(self, rect) -> bool:
        return (self.end_point.x > rect.start_point.x and rect.end_point.x > self.start_point.x and
                self.end_point.y > rect.start_point.y and rect.end_point.y > self.start_point.y)

    def __str__(self):
        return f'Rect(start = {self.start_point}, end = {self.end_point})'

    def __eq__(self, other) -> bool:
        if isinstance(other, Rect):
            return self.start_point == other.start_point and self.end_point == other.end_point and self.color == other.color
        return False

    def __hash__(self):
        return self.start_point.__hash__() + self.end_point.__hash__() + hash(self.hex_color)
