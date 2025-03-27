from vectorization.dto.point import Point
from vectorization.dto.rect import Rect


def create_windows(rects: [Rect]) -> [Rect]:
    windows = set()
    rect1: Rect
    rect2: Rect
    window_color = [153, 204, 255]
    for rect1 in rects:
        for rect2 in rects:
            if rect1 == rect2: continue
            rect = None
            if rect1.start_point.x == rect2.start_point.x and rect1.end_point.x == rect2.end_point.x:
                if rect1.start_point.y < rect2.start_point.y:
                    y1 = rect1.end_point.y
                    y2 = rect2.start_point.y
                else:
                    y1 = rect2.end_point.y
                    y2 = rect1.start_point.y
                rect = Rect(
                    start_point=Point(x=rect1.start_point.x, y=y1),
                    end_point=Point(x=rect1.end_point.x, y=y2),
                    color=window_color,
                )
            if rect1.start_point.y == rect2.start_point.y and rect1.end_point.y == rect2.end_point.y:
                if rect1.start_point.x < rect2.start_point.x:
                    x1 = rect1.end_point.x
                    x2 = rect2.start_point.x
                else:
                    x1 = rect2.end_point.x
                    x2 = rect1.start_point.x
                rect = Rect(
                    start_point=Point(x=x1, y=rect1.start_point.y),
                    end_point=Point(x=x2, y=rect1.end_point.y),
                    color=window_color,
                )
            if rect is not None:
                can_add = True
                for r in rects:
                    can_add = can_add and not rect.takeover_rect(r)
                if can_add:
                    windows.add(rect)
    return windows
