from optimizer.dto.base_optimization import BaseOptimization
from vectorization.dto.rect import Rect


class TakeoverOptimization(BaseOptimization):

    def __init__(self):
        super().__init__()

    def can_optimize(self, rect1: Rect, rect2: Rect) -> bool:
        is_rect1_bigger = self.__is_rect1_bigger(rect1, rect2)
        is_rect2_bigger = self.__is_rect2_bigger(rect1, rect2)
        return is_rect1_bigger or is_rect2_bigger

    def optimize(self, rect1: Rect, rect2: Rect) -> Rect:
        is_rect1_bigger = self.__is_rect1_bigger(rect1, rect2)
        is_rect2_bigger = self.__is_rect2_bigger(rect1, rect2)
        if is_rect1_bigger:
            return rect1
        elif is_rect2_bigger:
            return rect2
        else:
            raise ValueError('Can\'t takeover any rect.')

    def __is_rect1_bigger(self, rect1: Rect, rect2: Rect) -> bool:
        return rect1.start_point.x <= rect2.start_point.x and rect1.start_point.y <= rect2.start_point.y and \
            rect1.end_point.x >= rect2.end_point.x and rect1.end_point.y >= rect2.end_point.y

    def __is_rect2_bigger(self, rect1: Rect, rect2: Rect) -> bool:
        return rect2.start_point.x <= rect1.start_point.x and rect2.start_point.y <= rect1.start_point.y and \
            rect2.end_point.x >= rect1.end_point.x and rect2.end_point.y >= rect1.end_point.y
