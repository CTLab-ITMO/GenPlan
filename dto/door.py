from config import DOOR_WIDTH
from dto.door_position_type import PositionType
from dto.point import Point
import drawsvg as draw

from dto.rect import Rect


class Door(Rect):
    position_type: PositionType

    def __init__(self, start_point: Point, end_point: Point, color: [int], position_type: PositionType):
        super().__init__(start_point, end_point, color)
        self.position_type = position_type

    def to_svg(self, drawing: draw.Drawing):
        r = self.end_point.x - self.start_point.x
        if self.position_type == PositionType.LEFT:
            drawing.append(
                draw.Rectangle(self.start_point.x, self.start_point.y, r, DOOR_WIDTH, fill=self.hex_color)
            )
            drawing.append(
                draw.Arc(self.start_point.x, self.start_point.y, r, 0, 90,
                         cw=True, stroke=self.hex_color, fill='none', stroke_width=DOOR_WIDTH)
            )
        elif self.position_type == PositionType.UP:
            drawing.append(draw.Rectangle(self.start_point.x, self.start_point.y, DOOR_WIDTH, r))
            drawing.append(
                draw.Arc(self.start_point.x, self.start_point.y, r, 0, 90,
                         cw=True, stroke=self.hex_color, fill='none', stroke_width=DOOR_WIDTH)
            )
        elif self.position_type == PositionType.RIGHT:
            drawing.append(
                draw.Rectangle(self.start_point.x, self.start_point.y, r, DOOR_WIDTH, fill=self.hex_color)
            )
            drawing.append(
                draw.Arc(self.end_point.x, self.start_point.y, r, 90, 180,
                         cw=True, stroke=self.hex_color, fill='none', stroke_width=DOOR_WIDTH)
            )
        elif self.position_type == PositionType.BOTTOM:
            drawing.append(
                draw.Rectangle(self.start_point.x, self.start_point.y, DOOR_WIDTH, r, fill=self.hex_color))
            drawing.append(
                draw.Arc(self.start_point.x, self.end_point.y, r, 0, 270,
                         cw=False, stroke=self.hex_color, fill='none', stroke_width=DOOR_WIDTH)
            )

    def __str__(self):
        return f'Door(start = {self.start_point}, end = {self.end_point}, position_type = {self.position_type})'
