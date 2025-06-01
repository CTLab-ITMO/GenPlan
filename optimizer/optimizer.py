import numpy as np

from optimizer.dto.merge_optimization import MergeOptimization
from optimizer.dto.takeover_optimization import TakeoverOptimization
from dto.rect import Rect


def merge_similar_rects(rects: [Rect]) -> [Rect]:
    new_rects = []
    optimizations = [TakeoverOptimization(),
                     MergeOptimization()]
    was_optimized = np.zeros(len(rects))
    for i, rect1 in enumerate(rects):
        if was_optimized[i] == 1:
            continue
        was_optimized[i] = 1
        new_rect = rect1
        for j, rect2 in enumerate(rects):
            if was_optimized[j] == 1:
                continue
            for optimization in optimizations:
                if optimization.can_optimize(new_rect, rect2):
                    was_optimized[j] = 1
                    new_rect = optimization.optimize(new_rect, rect2)
                    break
        new_rects.append(new_rect)
    return new_rects
