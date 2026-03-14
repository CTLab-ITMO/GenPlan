import math
from typing import List, Tuple

from dto.enum.position_type import PositionType
from dto.rect import Rect


class Roof:
    rect: Rect
    roof_thickness: int
    wall_thickness: int
    beam_thickness: int
    beam_width: int
    beam_space: int
    beam_angle_space: int
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
                 beam_thickness: int,
                 beam_width: int,
                 beam_space: int,
                 beam_angle_space: int,
                 angle: int,
                 slopes_count: int,
                 indent: int,
                 height: int,
                 position_type: PositionType):
        self.rect = rect
        self.roof_thickness = roof_thickness
        self.wall_thickness = wall_thickness
        self.beam_thickness = beam_thickness
        self.beam_width = beam_width
        self.beam_space = beam_space
        self.beam_angle_space = beam_angle_space
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

    def get_coordinates_of_beams(self) -> List[List[Tuple[int, int, int]]]:
        if self.slopes_count == 1:
            return self._get_one_slope_beam()
        elif self.slopes_count == 2:
            return self._get_two_slope_beam()
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
        sin = math.sin(math.radians(self.angle))
        cos = math.cos(math.radians(self.angle))
        shift_ind = int(rt * sin)
        low = self.beam_width
        top = int(self.beam_width + rt * cos)
        roof_shift = ind

        if self.door_position_type == PositionType.UP:
            roof = self._create_roof_for_one_slope(
                (x1 - roof_shift, y1 - roof_shift + shift_ind),
                (x2 + roof_shift, y2 + roof_shift + shift_ind),
                top
            ) + self._create_roof_for_one_slope(
                (x1 - roof_shift, y1 - roof_shift),
                (x2 + roof_shift, y2 + roof_shift),
                low
            )
        elif self.door_position_type == PositionType.BOTTOM:
            roof = self._create_roof_for_one_slope(
                (x1 - roof_shift, y1 - roof_shift - shift_ind),
                (x2 + roof_shift, y2 + roof_shift - shift_ind),
                top
            ) + self._create_roof_for_one_slope(
                (x1 - roof_shift, y1 - roof_shift),
                (x2 + roof_shift, y2 + roof_shift),
                low
            )
        elif self.door_position_type == PositionType.LEFT:
            roof = self._create_roof_for_one_slope(
                (x1 - roof_shift + shift_ind, y1 - roof_shift),
                (x2 + roof_shift + shift_ind, y2 + roof_shift),
                top
            ) + self._create_roof_for_one_slope(
                (x1 - roof_shift, y1 - roof_shift),
                (x2 + roof_shift, y2 + roof_shift),
                low
            )
        elif self.door_position_type == PositionType.RIGHT:
            roof = self._create_roof_for_one_slope(
                (x1 - roof_shift - shift_ind, y1 - roof_shift),
                (x2 + roof_shift - shift_ind, y2 + roof_shift),
                top
            ) + self._create_roof_for_one_slope(
                (x1 - roof_shift, y1 - roof_shift),
                (x2 + roof_shift, y2 + roof_shift),
                low
            )
        return [roof]

    def _get_two_slope_roof(self) -> List[List[Tuple[int, int, int]]]:
        x1, y1 = self.rect.start_point.x, self.rect.start_point.y
        x2, y2 = self.rect.end_point.x, self.rect.end_point.y
        rt = self.roof_thickness
        ind = self.indent
        cos = int(math.cos(math.radians(self.angle)) * self.beam_width)
        return self._create_angle_block_for_two_slopes(
            (x1 - ind - cos, y1 - ind - cos),
            (x2 + ind + cos, y2 + ind + cos),
            rt, self.beam_width
        )

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

    def _get_one_slope_beam(self) -> List[List[Tuple[int, int, int]]]:
        beams = []

        x1, y1 = self.rect.start_point.x, self.rect.start_point.y
        x2, y2 = self.rect.end_point.x, self.rect.end_point.y
        bt = self.beam_thickness
        bs = self.beam_space
        bw = self.beam_width
        ind = self.indent
        tan = math.tan(math.radians(self.angle))
        sin = math.sin(math.radians(self.angle))
        cos = math.cos(math.radians(self.angle))
        bw_cos = int(bw * cos)
        bw_sin = int(bw * sin)

        y_beams = []
        begin_y = y1 - ind
        while begin_y + bt <= y2 + ind:
            y_beams.append((begin_y, begin_y + bt))
            begin_y += bt + bs
        y_beams.pop()
        y_beams.append((y2 + ind - bt, y2 + ind))

        y_beams_cos = []
        begin_y = y1 - ind
        while begin_y + bt <= y2 + ind:
            y_beams_cos.append((begin_y, begin_y + bt * cos))
            begin_y += bt * cos + bs
        y_beams_cos.pop()
        y_beams_cos.append((y2 + ind - bt * cos, y2 + ind))

        x_beams_cos = []
        begin_x = x1 - ind
        while begin_x + bt <= x2 + ind:
            x_beams_cos.append((begin_x, begin_x + bt * cos))
            begin_x += bt * cos + bs
        x_beams_cos.pop()
        x_beams_cos.append((x2 + ind - bt * cos, x2 + ind))

        x_beams = []
        begin_x = x1 - ind
        while begin_x + bt <= x2 + ind:
            x_beams.append((begin_x, begin_x + bt))
            begin_x += bt + bs
        x_beams.pop()
        x_beams.append((x2 + ind - bt, x2 + ind))

        if self.door_position_type == PositionType.LEFT:
            for (y1_beam, y2_beam) in y_beams:
                angle_beam = self._create_roof_for_one_slope(
                    (x1 - ind + bw_sin, y1_beam),
                    (x2 + ind + bw_sin, y2_beam),
                    bw_cos
                ) + self._create_roof_for_one_slope(
                    (x1 - ind, y1_beam),
                    (x2 + ind, y2_beam),
                    0
                )
                beams.append(angle_beam)

            for (x1_beam, x2_beam) in x_beams_cos:
                h = self.height + tan * (x2 - x1_beam) - 1
                angle_beam = self._create_angle_block_for_one_slopes(
                    (x1_beam, y1 - ind),
                    (x2_beam, y2 + ind),
                    bw,
                    h
                )
                beams.append(angle_beam)
        elif self.door_position_type == PositionType.RIGHT:
            for (y1_beam, y2_beam) in y_beams:
                angle_beam = self._create_roof_for_one_slope(
                    (x1 - ind, y1_beam),
                    (x2 + ind, y2_beam),
                    bw_cos
                ) + self._create_roof_for_one_slope(
                    (x1 - ind + bw_sin, y1_beam),
                    (x2 + ind + bw_sin, y2_beam),
                    0
                )
                beams.append(angle_beam)

            for (x1_beam, x2_beam) in x_beams_cos:
                h = self.height + tan * (x1_beam - x1) - 1
                angle_beam = self._create_angle_block_for_one_slopes(
                    (x1_beam, y1 - ind),
                    (x2_beam, y2 + ind),
                    bw,
                    h
                )
                beams.append(angle_beam)
        elif self.door_position_type == PositionType.UP:
            for (x1_beam, x2_beam) in x_beams:
                angle_beam = self._create_roof_for_one_slope(
                    (x1_beam, y1 - ind + bw_sin),
                    (x2_beam, y2 + ind + bw_sin),
                    bw_cos
                ) + self._create_roof_for_one_slope(
                    (x1_beam, y1 - ind),
                    (x2_beam, y2 + ind),
                    0
                )
                beams.append(angle_beam)

            for (y1_beam, y2_beam) in y_beams_cos:
                h = self.height + tan * (y2 - y1_beam)
                angle_beam = self._create_angle_block_for_one_slopes(
                    (x1 - ind, y1_beam),
                    (x2 + ind, y2_beam),
                    bw,
                    h
                )
                beams.append(angle_beam)
        elif self.door_position_type == PositionType.BOTTOM:
            for (x1_beam, x2_beam) in x_beams:
                angle_beam = self._create_roof_for_one_slope(
                    (x1_beam, y1 - ind),
                    (x2_beam, y2 + ind),
                    bw_cos
                ) + self._create_roof_for_one_slope(
                    (x1_beam, y1 - ind + bw_sin),
                    (x2_beam, y2 + ind + bw_sin),
                    0
                )
                beams.append(angle_beam)

            for (y1_beam, y2_beam) in y_beams_cos:
                h = self.height + tan * (y2_beam - y1)
                angle_beam = self._create_angle_block_for_one_slopes(
                    (x1 - ind, y1_beam),
                    (x2 + ind, y2_beam),
                    bw,
                    h
                )
                beams.append(angle_beam)

        return beams

    def _get_two_slope_beam(self) -> List[List[Tuple[int, int, int]]]:
        beams = []

        x1, y1 = self.rect.start_point.x, self.rect.start_point.y
        x2, y2 = self.rect.end_point.x, self.rect.end_point.y
        bt = self.beam_thickness
        bs = self.beam_space
        bw = self.beam_width
        ind = self.indent
        tan = math.tan(math.radians(self.angle))
        sin = math.sin(math.radians(self.angle))

        if self.door_position_type in [PositionType.UP, PositionType.BOTTOM]:
            width_half = (x2 - x1) / 2
            y_last = None
            y_beams = []
            begin_y = y1 - ind
            while begin_y + bt <= y2 + ind:
                y_beams.append((begin_y, begin_y + bt))
                begin_y += bt + bs
            y_beams.pop()
            y_beams.append((y2 + ind - bt, y2 + ind))

            for (y1_beam, y2_beam) in y_beams:
                angle_beam = self._create_angle_block_for_two_slopes(
                    (x1 - ind, y1_beam),
                    (x2 + ind, y2_beam),
                    bw
                )
                beams += angle_beam

                if y_last is not None:
                    x_start = x1 - ind
                    while x_start < x1 + width_half - bt:
                        beam_height = self.outer_ridge_height - tan * (x1 + width_half - x_start) + self.height
                        left_angle_beam = self._create_angle_beam_for_two_slopes(
                            (x_start, y_last),
                            (x_start - sin * bw, y1_beam),
                            beam_height,
                            PositionType.LEFT
                        )
                        beams.append(left_angle_beam)

                        right_angle_beam = self._create_angle_beam_for_two_slopes(
                            (x2 + x1 - x_start, y_last),
                            (x2 + x1 - x_start + sin * bw, y1_beam),
                            beam_height,
                            PositionType.RIGHT
                        )
                        beams.append(right_angle_beam)

                        x_start += self.beam_angle_space

                y_last = y2_beam

                if y1 <= y1_beam < y2_beam <= y2:
                    bottom_beam = self._create_bottom_horizontal_beam_for_two_slopes(
                        (x1, y1_beam),
                        (x2, y2_beam),
                        self.height
                    )
                    beams.append(bottom_beam)

                    z = int(min(self.outer_ridge_height * 5 / 6, self.outer_ridge_height - 2 * bw))
                    shift_top_beam = int(width_half * (1 - ((self.outer_ridge_height - z) / self.outer_ridge_height)))
                    top_beam = self._create_bottom_horizontal_beam_for_two_slopes(
                        (x1 + shift_top_beam, y1_beam),
                        (x2 - shift_top_beam, y2_beam),
                        z + self.height
                    )
                    beams.append(top_beam)

                    x1_left = max(x1 + bw, x1 + int(width_half / 4))
                    x2_left = x1_left + bw
                    x1_right = min(x2 - 2 * bw, x2 - int(width_half / 4) - bw)
                    x2_right = x1_right + bw
                    z2_small = self.height + int(tan * (x1_left - self.rect.start_point.x))
                    z2_big = self.height + int(tan * (x2_left - self.rect.start_point.x))
                    vertical_beam_left = self._create_bottom_vertical_beam_for_two_slopes(
                        (x1_left, y1_beam),
                        (x2_left, y2_beam),
                        z2_small, z2_big
                    )
                    vertical_beam_right = self._create_bottom_vertical_beam_for_two_slopes(
                        (x1_right, y1_beam),
                        (x2_right, y2_beam),
                        z2_big, z2_small
                    )
                    beams.append(vertical_beam_left)
                    beams.append(vertical_beam_right)

        elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
            width_half = (y2 - y1) / 2
            x_last = None
            x_beams = []
            begin_x = x1 - ind
            while begin_x + bt <= x2 + ind:
                x_beams.append((begin_x, begin_x + bt))
                begin_x += bt + bs
            x_beams.pop()
            x_beams.append((x2 + ind - bt, x2 + ind))

            for (x1_beam, x2_beam) in x_beams:
                angle_beam = self._create_angle_block_for_two_slopes(
                    (x1_beam, y1 - ind),
                    (x2_beam, y2 + ind),
                    bw
                )
                beams += angle_beam

                if x_last is not None:
                    y_start = y1 - ind
                    while y_start < y1 + width_half - bt:
                        beam_height = self.outer_ridge_height - tan * (y1 + width_half - y_start) + self.height
                        up_angle_beam = self._create_angle_beam_for_two_slopes(
                            (x_last, y_start),
                            (x1_beam, y_start + sin * bw),
                            beam_height,
                            PositionType.UP
                        )
                        beams.append(up_angle_beam)

                        bottom_angle_beam = self._create_angle_beam_for_two_slopes(
                            (x_last, y2 + y1 - y_start),
                            (x1_beam, y2 + y1 - y_start - sin * bw),
                            beam_height,
                            PositionType.BOTTOM
                        )
                        beams.append(bottom_angle_beam)

                        y_start += self.beam_angle_space

                x_last = x2_beam

                if x1 <= x1_beam < x2_beam <= x2:
                    bottom_beam = self._create_bottom_horizontal_beam_for_two_slopes(
                        (x1_beam, y1),
                        (x2_beam, y2),
                        self.height
                    )
                    beams.append(bottom_beam)

                    z = int(min(self.outer_ridge_height * 5 / 6, self.outer_ridge_height - 2 * bw))
                    shift_top_beam = int(width_half * (1 - ((self.outer_ridge_height - z) / self.outer_ridge_height)))
                    top_beam = self._create_bottom_horizontal_beam_for_two_slopes(
                        (x1_beam, y1 + shift_top_beam),
                        (x2_beam, y2 - shift_top_beam),
                        z + self.height
                    )
                    beams.append(top_beam)

                    y1_left = max(y1 + bw, y1 + int(width_half / 4))
                    y2_left = y1_left + bw
                    y1_right = min(y2 - 2 * bw, y2 - int(width_half / 4) - bw)
                    y2_right = y1_right + bw
                    z2_small = self.height + int(tan * (y1_left - self.rect.start_point.y))
                    z2_big = self.height + int(tan * (y2_left - self.rect.start_point.y))
                    vertical_beam_left = self._create_bottom_vertical_beam_for_two_slopes(
                        (x1_beam, y1_left),
                        (x2_beam, y2_left),
                        z2_small, z2_big
                    )
                    vertical_beam_right = self._create_bottom_vertical_beam_for_two_slopes(
                        (x1_beam, y1_right),
                        (x2_beam, y2_right),
                        z2_big, z2_small
                    )
                    beams.append(vertical_beam_left)
                    beams.append(vertical_beam_right)
        return beams

    def _create_angle_block_for_two_slopes(
            self,
            p1: Tuple[int, int],
            p2: Tuple[int, int],
            thickness: int,
            shift_height: int = 0
    ) -> List[List[Tuple[int, int, int]]]:
        block = []

        x1, y1 = p1
        x2, y2 = p2

        shift_ind = int(thickness * math.sin(math.radians(self.angle)))
        shift_height_low = int(thickness * math.cos(math.radians(self.angle))) + shift_height
        shift_height_tall = int(thickness / math.cos(math.radians(self.angle))) + shift_height

        if self.door_position_type in [PositionType.UP, PositionType.BOTTOM]:
            left_part_1, right_part_1 = self._create_roof_for_two_slopes(
                (x1 - shift_ind, y1),
                (x2 + shift_ind, y2),
                shift_height_low, shift_height_tall
            )
            left_part_2, right_part_2 = self._create_roof_for_two_slopes(
                (x1, y1),
                (x2, y2),
                0, 0
            )
            block = [left_part_1 + left_part_2] + [right_part_1 + right_part_2]
        elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
            left_part_1, right_part_1 = self._create_roof_for_two_slopes(
                (x1, y1 - shift_ind),
                (x2, y2 + shift_ind),
                shift_height_low, shift_height_tall
            )
            left_part_2, right_part_2 = self._create_roof_for_two_slopes(
                (x1, y1),
                (x2, y2),
                0, 0
            )
            block = [left_part_1 + left_part_2] + [right_part_1 + right_part_2]
        return block

    def _create_bottom_horizontal_beam_for_two_slopes(
            self,
            p1: Tuple[int, int],
            p2: Tuple[int, int],
            height: int
    ) -> List[Tuple[int, int, int]]:
        beam = []

        x1, y1 = p1
        x2, y2 = p2

        shift = int(self.beam_width / math.tan(math.radians(self.angle)))
        z1 = height
        z2 = height + self.beam_width

        beam.append((x1, y1, z1))
        beam.append((x1, y2, z1))
        beam.append((x2, y2, z1))
        beam.append((x2, y1, z1))

        if self.door_position_type in [PositionType.UP, PositionType.BOTTOM]:
            beam.append((x1 + shift, y1, z2))
            beam.append((x1 + shift, y2, z2))
            beam.append((x2 - shift, y2, z2))
            beam.append((x2 - shift, y1, z2))
        elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
            beam.append((x1, y1 + shift, z2))
            beam.append((x1, y2 - shift, z2))
            beam.append((x2, y2 - shift, z2))
            beam.append((x2, y1 + shift, z2))
        return beam

    def _create_bottom_vertical_beam_for_two_slopes(
            self,
            p1: Tuple[int, int],
            p2: Tuple[int, int],
            z2_start: int,
            z2_end: int,
    ) -> List[Tuple[int, int, int]]:
        beam = []

        x1, y1 = p1
        x2, y2 = p2

        z1 = self.height

        beam.append((x1, y1, z1))
        beam.append((x1, y2, z1))
        beam.append((x2, y2, z1))
        beam.append((x2, y1, z1))

        if self.door_position_type in [PositionType.UP, PositionType.BOTTOM]:
            beam.append((x1, y1, z2_start))
            beam.append((x1, y2, z2_start))
            beam.append((x2, y2, z2_end))
            beam.append((x2, y1, z2_end))
        elif self.door_position_type in [PositionType.LEFT, PositionType.RIGHT]:
            beam.append((x1, y1, z2_start))
            beam.append((x1, y2, z2_end))
            beam.append((x2, y2, z2_end))
            beam.append((x2, y1, z2_start))
        return beam

    def _create_angle_beam_for_two_slopes(
            self,
            p1: Tuple[int, int],
            p2: Tuple[int, int],
            z: int,
            position_type: PositionType
    ) -> List[Tuple[int, int, int]]:
        beam = []

        x1, y1 = p1
        x2, y2 = p2

        cos_width = math.cos(math.radians(self.angle)) * self.beam_width
        cos_bt = math.cos(math.radians(self.angle)) * self.beam_thickness
        sin_bt = math.sin(math.radians(self.angle)) * self.beam_thickness

        if position_type == PositionType.LEFT:
            beam.append((x1 + cos_bt, y1, z + sin_bt))
            beam.append((x1 + cos_bt, y2, z + sin_bt))
            beam.append((x2 + cos_bt, y2, z + cos_width + sin_bt))
            beam.append((x2 + cos_bt, y1, z + cos_width + sin_bt))

            beam.append((x1, y1, z))
            beam.append((x1, y2, z))
            beam.append((x2, y2, z + cos_width))
            beam.append((x2, y1, z + cos_width))
        elif position_type == PositionType.RIGHT:
            beam.append((x1, y1, z))
            beam.append((x1, y2, z))
            beam.append((x2, y2, z + cos_width))
            beam.append((x2, y1, z + cos_width))

            beam.append((x1 - cos_bt, y1, z + sin_bt))
            beam.append((x1 - cos_bt, y2, z + sin_bt))
            beam.append((x2 - cos_bt, y2, z + cos_width + sin_bt))
            beam.append((x2 - cos_bt, y1, z + cos_width + sin_bt))
        elif position_type == PositionType.UP:
            beam.append((x1, y1 - cos_bt, z + cos_width))
            beam.append((x1, y2 - cos_bt, z))
            beam.append((x2, y2 - cos_bt, z))
            beam.append((x2, y1 - cos_bt, z + cos_width))

            beam.append((x1, y1, z + sin_bt + cos_width))
            beam.append((x1, y2, z + sin_bt))
            beam.append((x2, y2, z + sin_bt))
            beam.append((x2, y1, z + sin_bt + cos_width))
        elif position_type == PositionType.BOTTOM:
            beam.append((x1, y1, z + sin_bt + cos_width))
            beam.append((x1, y2, z + sin_bt))
            beam.append((x2, y2, z + sin_bt))
            beam.append((x2, y1, z + sin_bt + cos_width))

            beam.append((x1, y1 + cos_bt, z + cos_width))
            beam.append((x1, y2 + cos_bt, z))
            beam.append((x2, y2 + cos_bt, z))
            beam.append((x2, y1 + cos_bt, z + cos_width))
        return beam

    def _create_angle_block_for_one_slopes(
            self,
            p1: Tuple[int, int],
            p2: Tuple[int, int],
            thickness: int,
            height: int
    ) -> List[Tuple[int, int, int]]:
        block = []

        x1, y1 = p1
        x2, y2 = p2

        sin = math.sin(math.radians(self.angle))
        cos = math.cos(math.radians(self.angle))

        delta_z = self.beam_thickness * sin
        cos_t = thickness * cos
        sin_t = thickness * sin

        if self.door_position_type == PositionType.LEFT:
            block.append((x1 + sin_t, y1, height + cos_t))
            block.append((x2 + sin_t, y1, height - delta_z + cos_t))
            block.append((x2 + sin_t, y2, height - delta_z + cos_t))
            block.append((x1 + sin_t, y2, height + cos_t))

            block.append((x1, y1, height))
            block.append((x2, y1, height - delta_z))
            block.append((x2, y2, height - delta_z))
            block.append((x1, y2, height))
        elif self.door_position_type == PositionType.RIGHT:
            block.append((x1, y1, height + cos_t))
            block.append((x2, y1, height + delta_z + cos_t))
            block.append((x2, y2, height + delta_z + cos_t))
            block.append((x1, y2, height + cos_t))

            block.append((x1 + sin_t, y1, height))
            block.append((x2 + sin_t, y1, height + delta_z))
            block.append((x2 + sin_t, y2, height + delta_z))
            block.append((x1 + sin_t, y2, height))
        elif self.door_position_type == PositionType.UP:
            block.append((x1, y1 + sin_t, height + delta_z + cos_t))
            block.append((x2, y1 + sin_t, height + delta_z + cos_t))
            block.append((x2, y2 + sin_t, height + cos_t))
            block.append((x1, y2 + sin_t, height + cos_t))

            block.append((x1, y1, height + delta_z))
            block.append((x2, y1, height + delta_z))
            block.append((x2, y2, height))
            block.append((x1, y2, height))
        elif self.door_position_type == PositionType.BOTTOM:
            block.append((x1, y1, height - delta_z + cos_t))
            block.append((x2, y1, height - delta_z + cos_t))
            block.append((x2, y2, height + cos_t))
            block.append((x1, y2, height + cos_t))

            block.append((x1, y1 + sin_t, height - delta_z))
            block.append((x2, y1 + sin_t, height - delta_z))
            block.append((x2, y2 + sin_t, height))
            block.append((x1, y2 + sin_t, height))
        return block
