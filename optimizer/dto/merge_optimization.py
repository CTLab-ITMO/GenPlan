from optimizer.dto.base_optimization import BaseOptimization
from vectorization.dto.point import Point
from vectorization.dto.rect import Rect


class MergeOptimization(BaseOptimization):

    def __init__(self):
        super().__init__()

    def can_optimize(self, rect1: Rect, rect2: Rect) -> bool:
        is_rects_has_similar_xs = self.__is_rects_has_similar_xs(rect1, rect2)
        is_rects_has_similar_ys = self.__is_rects_has_similar_ys(rect1, rect2)
        return is_rects_has_similar_xs or is_rects_has_similar_ys

    def optimize(self, rect1: Rect, rect2: Rect) -> Rect:
        is_rects_has_similar_xs = self.__is_rects_has_similar_xs(rect1, rect2)
        is_rects_has_similar_ys = self.__is_rects_has_similar_ys(rect1, rect2)
        if is_rects_has_similar_xs:
            min_y = min(rect1.start_point.y, rect2.start_point.y)
            max_y = max(rect1.end_point.y, rect2.end_point.y)
            return Rect(
                start_point=Point(x=rect1.start_point.x, y=min_y),
                end_point=Point(x=rect1.end_point.x, y=max_y),
                color=[0, 0, 0]
            )
        elif is_rects_has_similar_ys:
            min_x = min(rect1.start_point.x, rect2.start_point.x)
            max_x = max(rect1.end_point.x, rect2.end_point.x)
            return Rect(
                start_point=Point(x=min_x, y=rect1.start_point.y),
                end_point=Point(x=max_x, y=rect1.end_point.y),
                color=[0, 0, 0]
            )
        else:
            raise ValueError('Can\'t merge any rect.')

    def __is_rects_has_similar_xs(self, rect1: Rect, rect2: Rect) -> bool:
        return rect1.start_point.x == rect2.start_point.x and rect1.end_point.x == rect2.end_point.x and \
            (rect2.end_point.y >= rect1.end_point.y >= rect2.start_point.y or
             rect1.end_point.y >= rect2.end_point.y >= rect1.start_point.y)

    def __is_rects_has_similar_ys(self, rect1: Rect, rect2: Rect) -> bool:
        return rect1.start_point.y == rect2.start_point.y and rect1.end_point.y == rect2.end_point.y and \
            (rect2.end_point.x >= rect1.end_point.x >= rect2.start_point.x or
             rect1.end_point.x >= rect2.end_point.x >= rect1.start_point.x)
