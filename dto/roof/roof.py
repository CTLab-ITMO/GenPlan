import math
from typing import List, Tuple

from dto.enum.position_type import PositionType
from dto.rect import Rect


class Roof:
    rect: Rect
    roof_thickness: int
    wall_thickness: int
    angle: int
    slopes_count: int
    indent: int
    height: int
    door_position_type: PositionType
    roof_color: List[int]
    wall_color: List[int]

    def __init__(self,
                 rect: Rect,
                 roof_thickness: int,
                 wall_thickness: int,
                 angle: int,
                 slopes_count: int,
                 indent: int,
                 height: int,
                 position_type: PositionType):
        self.rect = rect
        self.roof_thickness = roof_thickness
        self.wall_thickness = wall_thickness
        assert 0 < angle < 90, f'Angle should be from 0 to 90 degrees. Current param = {angle}'
        self.angle = angle
        assert slopes_count == 1 or slopes_count == 2, 'Support only one and two slopes'
        self.slopes_count = slopes_count
        self.indent = indent
        self.height = height
        self.door_position_type = position_type

        radians = math.radians(angle)
        outer_width = rect.end_point.x - rect.start_point.x
        outer_depth = rect.end_point.y - rect.start_point.y
        if slopes_count == 2:
            inner_width = outer_width - 2 * wall_thickness
            inner_depth = outer_depth - 2 * wall_thickness
            self.indent_height = self.indent * math.tan(radians)
            if position_type in [PositionType.UP, PositionType.BOTTOM]:
                self.inner_ridge_height = (inner_width / 2) * math.tan(radians)
                self.outer_ridge_height = (outer_width / 2) * math.tan(radians)
            elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
                self.inner_ridge_height = (inner_depth / 2) * math.tan(radians)
                self.outer_ridge_height = (outer_depth / 2) * math.tan(radians)
        elif slopes_count == 1:
            self.indent_height = self.indent * math.tan(radians)
            inner_width = outer_width - wall_thickness
            inner_depth = outer_depth - wall_thickness
            if position_type in [PositionType.UP, PositionType.BOTTOM]:
                self.inner_ridge_height = inner_depth * math.tan(radians)
                self.outer_ridge_height = outer_depth * math.tan(radians)
            elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
                self.inner_ridge_height = inner_width * math.tan(radians)
                self.outer_ridge_height = outer_width * math.tan(radians)

    def get_coordinates_of_walls(self) -> List[List[Tuple[int, int, int]]]:
        if self.slopes_count == 1:
            return self._get_one_slope_walls()
        elif self.slopes_count == 2:
            return self._get_two_slope_walls()
        else:
            raise ValueError('Unsupported count of slopes.')

    def get_coordinates_of_slopes(self) -> List[List[Tuple[int, int, int]]]:
        if self.slopes_count == 1:
            return self._get_one_slope_roof()
        elif self.slopes_count == 2:
            return self._get_two_slope_roof()
        else:
            raise ValueError('Unsupported count of slopes.')

    def get_all_coordinates(self) -> List[List[Tuple[int, int, int]]]:
        return self.get_coordinates_of_walls() + self.get_coordinates_of_slopes()

    def _get_one_slope_walls(self) -> List[List[Tuple[int, int, int]]]:
        walls = []

        x1, y1 = self.rect.start_point.x, self.rect.start_point.y
        x2, y2 = self.rect.end_point.x, self.rect.end_point.y
        wt = self.wall_thickness

        front_wall: List[Tuple[int, int, int]] = []
        triangular_wall_left: List[Tuple[int, int, int]] = []
        triangular_wall_right: List[Tuple[int, int, int]] = []

        if self.door_position_type == PositionType.UP:
            front_wall = self._create_front_wall_for_one_slope(
                (x1, y1),
                (x2, y1 + wt)
            )
            triangular_wall_left = self._create_triangular_wall_for_one_slope(
                (x1, y1),
                (x1 + wt, y2)
            )
            triangular_wall_right = self._create_triangular_wall_for_one_slope(
                (x2 - wt, y1),
                (x2, y2)
            )
        elif self.door_position_type == PositionType.BOTTOM:
            front_wall = self._create_front_wall_for_one_slope(
                (x1, y2 - wt),
                (x2, y2)
            )
            triangular_wall_left = self._create_triangular_wall_for_one_slope(
                (x1, y1),
                (x1 + wt, y2)
            )
            triangular_wall_right = self._create_triangular_wall_for_one_slope(
                (x2 - wt, y1),
                (x2, y2)
            )
        elif self.door_position_type == PositionType.LEFT:
            front_wall = self._create_front_wall_for_one_slope(
                (x1, y1),
                (x1 + wt, y2)
            )
            triangular_wall_left = self._create_triangular_wall_for_one_slope(
                (x1, y1),
                (x2, y1 + wt)
            )
            triangular_wall_right = self._create_triangular_wall_for_one_slope(
                (x1, y2 - wt),
                (x2, y2)
            )
        elif self.door_position_type == PositionType.RIGHT:
            front_wall = self._create_front_wall_for_one_slope(
                (x2 - wt, y1),
                (x2, y2)
            )
            triangular_wall_left = self._create_triangular_wall_for_one_slope(
                (x1, y1),
                (x2, y1 + wt)
            )
            triangular_wall_right = self._create_triangular_wall_for_one_slope(
                (x1, y2 - wt),
                (x2, y2)
            )

        walls.append(front_wall)
        walls.append(triangular_wall_left)
        walls.append(triangular_wall_right)
        return walls

    def _get_two_slope_walls(self) -> List[List[Tuple[int, int, int]]]:
        walls = []

        x1, y1 = self.rect.start_point.x, self.rect.start_point.y
        x2, y2 = self.rect.end_point.x, self.rect.end_point.y
        wt = self.wall_thickness

        front_wall: List[Tuple[int, int, int]] = []
        back_wall: List[Tuple[int, int, int]] = []

        if self.door_position_type in [PositionType.UP, PositionType.BOTTOM]:
            front_wall = self._create_front_wall_for_two_slopes(
                (x1, y1),
                (x2, y1 + wt)
            )
            back_wall = self._create_front_wall_for_two_slopes(
                (x1, y2 - wt),
                (x2, y2)
            )
        elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
            front_wall = self._create_front_wall_for_two_slopes(
                (x1, y1),
                (x1 + wt, y2)
            )
            back_wall = self._create_front_wall_for_two_slopes(
                (x2 - wt, y1),
                (x2, y2)
            )

        walls.append(front_wall)
        walls.append(back_wall)
        return walls

    def _create_front_wall_for_one_slope(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> List[Tuple[int, int, int]]:
        points = []
        x1, y1 = p1
        x2, y2 = p2

        if self.door_position_type == PositionType.UP:
            points.append((x1, y1, self.height + self.outer_ridge_height))
            points.append((x2, y1, self.height + self.outer_ridge_height))
            points.append((x2, y2, self.height + self.inner_ridge_height))
            points.append((x1, y2, self.height + self.inner_ridge_height))
        elif self.door_position_type == PositionType.RIGHT:
            points.append((x1, y1, self.height + self.inner_ridge_height))
            points.append((x2, y1, self.height + self.outer_ridge_height))
            points.append((x2, y2, self.height + self.outer_ridge_height))
            points.append((x1, y2, self.height + self.inner_ridge_height))
        elif self.door_position_type == PositionType.BOTTOM:
            points.append((x1, y1, self.height + self.inner_ridge_height))
            points.append((x2, y1, self.height + self.inner_ridge_height))
            points.append((x2, y2, self.height + self.outer_ridge_height))
            points.append((x1, y2, self.height + self.outer_ridge_height))
        elif self.door_position_type == PositionType.LEFT:
            points.append((x1, y1, self.height + self.outer_ridge_height))
            points.append((x2, y1, self.height + self.inner_ridge_height))
            points.append((x2, y2, self.height + self.inner_ridge_height))
            points.append((x1, y2, self.height + self.outer_ridge_height))

        points.append((x1, y1, self.height))
        points.append((x2, y1, self.height))
        points.append((x2, y2, self.height))
        points.append((x1, y2, self.height))

        return points

    def _create_triangular_wall_for_one_slope(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> List[
        Tuple[int, int, int]]:
        points = []
        x1, y1 = p1
        x2, y2 = p2

        if self.door_position_type == PositionType.UP:
            points.append((x2, y1, self.height))
            points.append((x2, y2, self.height))
            points.append((x2, y1, self.height + self.outer_ridge_height))

            points.append((x1, y1, self.height))
            points.append((x1, y2, self.height))
            points.append((x1, y1, self.height + self.outer_ridge_height))

        elif self.door_position_type == PositionType.RIGHT:
            points.append((x1, y1, self.height))
            points.append((x2, y1, self.height))
            points.append((x2, y1, self.height + self.outer_ridge_height))

            points.append((x1, y2, self.height))
            points.append((x2, y2, self.height))
            points.append((x2, y2, self.height + self.outer_ridge_height))

        elif self.door_position_type == PositionType.BOTTOM:
            points.append((x2, y1, self.height))
            points.append((x2, y2, self.height))
            points.append((x2, y2, self.height + self.outer_ridge_height))

            points.append((x1, y1, self.height))
            points.append((x1, y2, self.height))
            points.append((x1, y2, self.height + self.outer_ridge_height))

        elif self.door_position_type == PositionType.LEFT:
            points.append((x1, y1, self.height))
            points.append((x2, y1, self.height))
            points.append((x1, y1, self.height + self.outer_ridge_height))

            points.append((x1, y2, self.height))
            points.append((x2, y2, self.height))
            points.append((x1, y2, self.height + self.outer_ridge_height))

        return points

    def _create_front_wall_for_two_slopes(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> List[Tuple[int, int, int]]:
        points = []
        x1, y1 = p1
        x2, y2 = p2

        if self.door_position_type in [PositionType.UP, PositionType.BOTTOM]:
            x_ridge = x1 + abs(x2 - x1) / 2

            points.append((x1, y1, self.height))
            points.append((x2, y1, self.height))
            points.append((x_ridge, y1, self.height + self.outer_ridge_height))

            points.append((x1, y2, self.height))
            points.append((x2, y2, self.height))
            points.append((x_ridge, y2, self.height + self.outer_ridge_height))

        elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
            y_ridge = y1 + abs(y2 - y1) / 2

            points.append((x2, y1, self.height))
            points.append((x2, y2, self.height))
            points.append((x2, y_ridge, self.height + self.outer_ridge_height))

            points.append((x1, y1, self.height))
            points.append((x1, y2, self.height))
            points.append((x1, y_ridge, self.height + self.outer_ridge_height))

        return points

    def _get_one_slope_roof(self) -> List[List[Tuple[int, int, int]]]:
        roof = []

        x1, y1 = self.rect.start_point.x, self.rect.start_point.y
        x2, y2 = self.rect.end_point.x, self.rect.end_point.y
        rt = self.roof_thickness
        ind = self.indent
        shift_ind = int(rt * math.sin(math.radians(self.angle)))
        shift_height = int(rt * math.cos(math.radians(self.angle)))

        if self.door_position_type == PositionType.UP:
            roof = self._create_roof_for_one_slope(
                (x1 - ind, y1 - ind + shift_ind),
                (x2 + ind, y2 + ind + shift_ind),
                shift_height
            ) + self._create_roof_for_one_slope(
                (x1 - ind, y1 - ind),
                (x2 + ind, y2 + ind),
                0
            )
        elif self.door_position_type == PositionType.BOTTOM:
            roof = self._create_roof_for_one_slope(
                (x1 - ind, y1 - ind - shift_ind),
                (x2 + ind, y2 + ind - shift_ind),
                shift_height
            ) + self._create_roof_for_one_slope(
                (x1 - ind, y1 - ind),
                (x2 + ind, y2 + ind),
                0
            )
        elif self.door_position_type == PositionType.LEFT:
            roof = self._create_roof_for_one_slope(
                (x1 - ind + shift_ind, y1 - ind),
                (x2 + ind + shift_ind, y2 + ind),
                shift_height
            ) + self._create_roof_for_one_slope(
                (x1 - ind, y1 - ind),
                (x2 + ind, y2 + ind),
                0
            )
        elif self.door_position_type == PositionType.RIGHT:
            roof = self._create_roof_for_one_slope(
                (x1 - ind - shift_ind, y1 - ind),
                (x2 + ind - shift_ind, y2 + ind),
                shift_height
            ) + self._create_roof_for_one_slope(
                (x1 - ind, y1 - ind),
                (x2 + ind, y2 + ind),
                0
            )
        return [roof]

    def _get_two_slope_roof(self) -> List[List[Tuple[int, int, int]]]:
        roof = []

        x1, y1 = self.rect.start_point.x, self.rect.start_point.y
        x2, y2 = self.rect.end_point.x, self.rect.end_point.y
        rt = self.roof_thickness
        ind = self.indent
        shift_ind = int(rt * math.sin(math.radians(self.angle)))
        shift_height_low = int(rt * math.cos(math.radians(self.angle)))
        shift_height_tall = int(rt / math.cos(math.radians(self.angle)))

        if self.door_position_type in [PositionType.UP, PositionType.BOTTOM]:
            left_part_1, right_part_1 = self._create_roof_for_two_slopes(
                (x1 - ind - shift_ind, y1 - ind),
                (x2 + ind + shift_ind, y2 + ind),
                shift_height_low, shift_height_tall
            )
            left_part_2, right_part_2 = self._create_roof_for_two_slopes(
                (x1 - ind, y1 - ind),
                (x2 + ind, y2 + ind),
                0, 0
            )
            roof = [left_part_1 + left_part_2] + [right_part_1 + right_part_2]
        elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
            left_part_1, right_part_1 = self._create_roof_for_two_slopes(
                (x1 - ind, y1 - ind - shift_ind),
                (x2 + ind, y2 + ind + shift_ind),
                shift_height_low, shift_height_tall
            )
            left_part_2, right_part_2 = self._create_roof_for_two_slopes(
                (x1 - ind, y1 - ind),
                (x2 + ind, y2 + ind),
                0, 0
            )
            roof = [left_part_1 + left_part_2] + [right_part_1 + right_part_2]

        return roof

    def _create_roof_for_one_slope(
            self,
            p1: Tuple[int, int],
            p2: Tuple[int, int],
            shift_height: int
    ) -> List[Tuple[int, int, int]]:
        points = []
        x1, y1 = p1
        x2, y2 = p2

        tall = int(self.height + self.outer_ridge_height + self.indent_height + shift_height)
        low = int(self.height - self.indent_height + shift_height)

        if self.door_position_type == PositionType.UP:
            points.append((x1, y1, tall))
            points.append((x2, y1, tall))
            points.append((x2, y2, low))
            points.append((x1, y2, low))
        elif self.door_position_type == PositionType.RIGHT:
            points.append((x1, y1, low))
            points.append((x2, y1, tall))
            points.append((x2, y2, tall))
            points.append((x1, y2, low))
        elif self.door_position_type == PositionType.BOTTOM:
            points.append((x1, y1, low))
            points.append((x2, y1, low))
            points.append((x2, y2, tall))
            points.append((x1, y2, tall))
        elif self.door_position_type == PositionType.LEFT:
            points.append((x1, y1, tall))
            points.append((x2, y1, low))
            points.append((x2, y2, low))
            points.append((x1, y2, tall))

        return points

    def _create_roof_for_two_slopes(
            self,
            p1: Tuple[int, int],
            p2: Tuple[int, int],
            shift_height_low: int,
            shift_height_tall: int
    ) -> Tuple[List[Tuple[int, int, int]], List[Tuple[int, int, int]]]:
        x1, y1 = p1
        x2, y2 = p2

        left_part = []
        right_part = []

        tall = int(self.height + self.outer_ridge_height + shift_height_tall)
        low = int(self.height - self.indent_height + shift_height_low)

        if self.door_position_type in [PositionType.UP, PositionType.BOTTOM]:
            x_ridge = x1 + abs(x2 - x1) / 2

            left_part.append((x1, y1, low))
            left_part.append((x_ridge, y1, tall))
            left_part.append((x_ridge, y2, tall))
            left_part.append((x1, y2, low))

            right_part.append((x_ridge, y1, tall))
            right_part.append((x2, y1, low))
            right_part.append((x2, y2, low))
            right_part.append((x_ridge, y2, tall))

        elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
            y_ridge = y1 + abs(y2 - y1) / 2

            left_part.append((x1, y1, low))
            left_part.append((x2, y1, low))
            left_part.append((x2, y_ridge, tall))
            left_part.append((x1, y_ridge, tall))

            right_part.append((x1, y_ridge, tall))
            right_part.append((x2, y_ridge, tall))
            right_part.append((x2, y2, low))
            right_part.append((x1, y2, low))

        return left_part, right_part
