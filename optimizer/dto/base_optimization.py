from dto.rect import Rect


class BaseOptimization:

    def __init__(self):
        pass

    def can_optimize(self, rect1: Rect, rect2: Rect) -> bool:
        return False

    def optimize(self, rect1: Rect, rect2: Rect) -> Rect:
        return rect1
