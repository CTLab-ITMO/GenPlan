from dto.door import Door
from dto.door_position_type import PositionType
from dto.point import Point
from dto.rect import Rect


def find_openings(walls: [Rect]) -> [Rect]:
    openings = set()
    default_color = [0, 0, 0]
    wall1: Rect
    wall2: Rect
    for wall1 in walls:
        for wall2 in walls:
            if wall1 == wall2: continue
            opening = None
            if wall1.start_point.x == wall2.start_point.x and wall1.end_point.x == wall2.end_point.x:
                if wall1.start_point.y < wall2.start_point.y:
                    y1 = wall1.end_point.y
                    y2 = wall2.start_point.y
                else:
                    y1 = wall2.end_point.y
                    y2 = wall1.start_point.y
                opening = Rect(
                    start_point=Point(x=wall1.start_point.x, y=y1),
                    end_point=Point(x=wall1.end_point.x, y=y2),
                    color=default_color
                )
            if wall1.start_point.y == wall2.start_point.y and wall1.end_point.y == wall2.end_point.y:
                if wall1.start_point.x < wall2.start_point.x:
                    x1 = wall1.end_point.x
                    x2 = wall2.start_point.x
                else:
                    x1 = wall2.end_point.x
                    x2 = wall1.start_point.x
                opening = Rect(
                    start_point=Point(x=x1, y=wall1.start_point.y),
                    end_point=Point(x=x2, y=wall1.end_point.y),
                    color=default_color
                )
            if opening is not None:
                can_add = True
                for wall in walls:
                    can_add = can_add and not opening.takeover_rect(wall)
                if can_add:
                    openings.add(opening)
    return openings


def find_inside_and_outside(walls: [Rect]) -> ([Rect], [Rect]):
    openings = find_openings(walls)
    outside_openings = set()
    inside_openings = set()
    for opening in openings:
        is_inside = False
        is_less_y = False
        is_less_x = False
        is_more_y = False
        is_more_x = False
        for wall in list(walls) + list(openings):
            if wall == opening: continue
            is_less_y = is_less_y or wall.start_point.y < opening.start_point.y
            is_less_x = is_less_x or wall.start_point.x < opening.start_point.x
            is_more_y = is_more_y or wall.end_point.y > opening.end_point.y
            is_more_x = is_more_x or wall.start_point.x > opening.start_point.x
            if is_more_x and is_more_y and is_less_y and is_less_x:
                is_inside = True
                break
        if is_inside:
            inside_openings.add(opening)
        else:
            outside_openings.add(opening)
    return outside_openings, inside_openings


def can_create_door(door: Rect, walls: [Rect]) -> bool:
    can_create = True
    for wall in walls:
        can_create = can_create and not door.has_common_part(wall)
        if not can_create:
            return False
    return True


def find_smallest_opening(openings: [Rect]) -> Rect:
    small_opening: Rect = None
    small_width = float('inf')
    for opening in openings:
        if opening.end_point.x - opening.start_point.x < opening.end_point.y - opening.start_point.y:
            width = opening.end_point.y - opening.start_point.y
        else:
            width = opening.end_point.x - opening.start_point.x
        if width < small_width:
            small_width = width
            small_opening = opening
    return small_opening


def create_doors(walls: [Rect], openings: [Rect], width: int, height: int) -> [(Rect, Rect)]:
    opening: Rect
    doors = []
    for opening in openings:
        is_vertical = False
        if opening.end_point.x - opening.start_point.x < opening.end_point.y - opening.start_point.y:
            opening_width = opening.end_point.y - opening.start_point.y
            is_vertical = True
            point1 = Point(x=opening.start_point.x - opening_width, y=opening.start_point.y)
            point2 = Point(x=opening.start_point.x, y=opening.end_point.y)
            point3 = Point(x=opening.end_point.x, y=opening.start_point.y)
            point4 = Point(x=opening.end_point.x + opening_width, y=opening.end_point.y)
        else:
            opening_width = opening.end_point.x - opening.start_point.x
            point1 = Point(x=opening.start_point.x, y=opening.start_point.y - opening_width)
            point2 = Point(x=opening.end_point.x, y=opening.start_point.y)
            point3 = Point(x=opening.start_point.x, y=opening.end_point.y)
            point4 = Point(x=opening.end_point.x, y=opening.end_point.y + opening_width)
        door_was_added = False
        if point1.x >= 0 and point1.y >= 0:
            if is_vertical:
                position_type = PositionType.RIGHT
            else:
                position_type = PositionType.BOTTOM
            door1 = Door(point1, point2, [0, 0, 0], position_type)
            if can_create_door(door1, walls):
                door_was_added = True
                doors.append(door1)
        if point4.x <= width and point4.y <= height and not door_was_added:
            if is_vertical:
                position_type = PositionType.LEFT
            else:
                position_type = PositionType.UP
            door2 = Door(point3, point4, [0, 0, 0], position_type)
            if can_create_door(door2, walls):
                doors.append(door2)
    return doors


def create_windows(openings: [Rect]) -> [Rect]:
    for opening in openings:
        opening.recolor([153, 204, 255])
    return openings


def create_windows_and_doors(walls: [Rect], width: int, height: int) -> [Rect]:
    outside_openings, inside_openings = find_inside_and_outside(walls)
    outside_door = find_smallest_opening(outside_openings)
    doors = create_doors(walls, list(inside_openings) + list([outside_door]), width, height)
    outside_openings.remove(outside_door)
    windows = create_windows(outside_openings)
    return list(doors) + list(windows)
