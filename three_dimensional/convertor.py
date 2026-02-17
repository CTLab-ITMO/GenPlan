from typing import List

import numpy as np
import open3d as o3d

from collections import deque
from config import GIF_PATH, WALL_COLOR, DOOR_COLOR, WINDOW_COLOR, OBJ_PATH, IFC_PATH
from dto.point import Point
from dto.polygon import Polygon
from dto.rect import Rect
from dto.rect_type import RectType
from dto.wall_size_type import WallSizeType
from dto.window_size_type import WindowSizeType
from three_dimensional.bim_coverter import meshes_to_bim
from three_dimensional.visualization import save_as_gif

# default params of door
DEFAULT_DOOR_HEIGHT = 200.0
DEFAULT_DOOR_WIDTH = 90.0
DEFAULT_THICKNESS = 10


def find_outside_corner_points(width: int, height: int, rects: List[Rect]) -> List[Point]:
    mask = np.zeros((height, width), dtype=np.uint8)
    for rect in rects:
        x1, y1 = rect.start_point.x, rect.start_point.y
        x2, y2 = rect.end_point.x, rect.end_point.y
        mask[y1:y2, x1:x2] = 1

    outside = np.zeros((height, width), dtype=np.uint8)
    queue = deque()

    for y in range(height):
        for x in [0, width - 1]:
            if mask[y, x] == 0 and outside[y, x] == 0:
                outside[y, x] = 1
                queue.append((x, y))
    for x in range(width):
        for y in [0, height - 1]:
            if mask[y, x] == 0 and outside[y, x] == 0:
                outside[y, x] = 1
                queue.append((x, y))

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    while queue:
        x, y = queue.popleft()
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if mask[ny, nx] == 0 and outside[ny, nx] == 0:
                    outside[ny, nx] = 1
                    queue.append((nx, ny))

    contour_points = set()
    for y in range(height):
        for x in range(width):
            if outside[y, x] == 1:
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if mask[ny, nx] == 1:
                            contour_points.add(Point(x, y))
                            break

    corner_points = set()
    for point in contour_points:
        x, y = point.x, point.y
        is_corner = False

        if (y > 0 and x > 0
                and contour_points.__contains__(Point(x, y - 1))
                and contour_points.__contains__(Point(x - 1, y))
        ):
            is_corner = True

        if (x > 0 and y < height - 1
                and contour_points.__contains__(Point(x, y + 1))
                and contour_points.__contains__(Point(x - 1, y))
        ):
            is_corner = True

        if (y > 0 and x < width - 1
                and contour_points.__contains__(Point(x, y - 1))
                and contour_points.__contains__(Point(x + 1, y))
        ):
            is_corner = True

        if (y < height - 1 and x < width - 1
                and contour_points.__contains__(Point(x, y + 1))
                and contour_points.__contains__(Point(x + 1, y))
        ):
            is_corner = True

        if is_corner:
            corner_points.add(point)
    return list(corner_points)


def combine_mashes(meshes: List[o3d.geometry.TriangleMesh]) -> o3d.geometry.TriangleMesh:
    if len(meshes) == 0:
        raise ValueError('Can\'t combine empty meshes.')
    final_mesh = meshes[0]
    for i in range(0, len(meshes)):
        final_mesh += meshes[i]
    return final_mesh


# color - RGB array [0..255, 0..255, 0..255]
def create_mash(vertices, triangles, color: List[int]) -> o3d.geometry.TriangleMesh:
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    mesh.compute_vertex_normals()
    norm_color = [c / 255 for c in color]
    mesh.paint_uniform_color(norm_color)

    return mesh


# color - RGB array [0..255, 0..255, 0..255]
def create_mash_rectangle(rect: Rect, bottom: int, top: int, color: List[int]) -> o3d.geometry.TriangleMesh:
    vertices = [
        [rect.start_point.x, rect.start_point.y, bottom],
        [rect.start_point.x, rect.end_point.y, bottom],
        [rect.end_point.x, rect.end_point.y, bottom],
        [rect.end_point.x, rect.start_point.y, bottom],

        [rect.start_point.x, rect.start_point.y, top],
        [rect.start_point.x, rect.end_point.y, top],
        [rect.end_point.x, rect.end_point.y, top],
        [rect.end_point.x, rect.start_point.y, top],
    ]

    triangles = [
        [0, 1, 2], [0, 2, 3],
        [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1],
        [1, 5, 6], [1, 6, 2],
        [2, 6, 7], [2, 7, 3],
        [3, 7, 4], [3, 4, 0]
    ]
    return create_mash(vertices, triangles, color)


def create_mash_polygon(polygon: Polygon, bottom: int, top: int, color: List[int]) -> o3d.geometry.TriangleMesh:
    vertices = []
    for point in polygon.points:
        vertices.append([point.x, point.y, bottom])
        vertices.append([point.x, point.y, top])

    triangles = []
    if len(polygon.points) < 3:
        raise ValueError("Polygon must have at least 3 points")
    for i in range(len(polygon.points)):
        n = len(polygon.points)
        v1 = i * 2
        v2 = (i + 1) % n * 2
        v3 = (i + 1) % n * 2 + 1
        v4 = i * 2 + 1
        triangles.append([v1, v2, v3])
        triangles.append([v1, v3, v4])
    for i in range(2, len(polygon.points)):
        triangles.append([0, i * 2, (i - 1) * 2])
    for i in range(2, len(polygon.points)):
        triangles.append([1, (i - 1) * 2 + 1, i * 2 + 1])

    return create_mash(vertices, triangles, color)


def create_wall_mesh(rect: Rect, wall_height: int, color: List[int]) -> o3d.geometry.TriangleMesh:
    return create_mash_rectangle(rect, bottom=0, top=wall_height, color=color)


def create_doorway_mesh(rect: Rect, door_height: int, wall_height: int, color: List[int]) -> o3d.geometry.TriangleMesh:
    return create_mash_rectangle(rect, bottom=door_height, top=wall_height, color=color)


def create_door_mesh(rect: Rect, door_height: int, color: List[int]) -> o3d.geometry.TriangleMesh:
    return create_mash_rectangle(rect, bottom=0, top=door_height, color=color)


def create_floor_mesh(polygon: Polygon, thickness: int) -> o3d.geometry.TriangleMesh:
    return create_mash_polygon(polygon, bottom=-thickness, top=0, color=WALL_COLOR)


def create_ceiling_mesh(polygon: Polygon, thickness: int, wall_height: int) -> o3d.geometry.TriangleMesh:
    return create_mash_polygon(polygon, bottom=wall_height, top=wall_height + thickness, color=WALL_COLOR)


def create_window_frame_bottom_mesh(
        rect: Rect,
        windows_bottom_height: int,
        color: List[int]
) -> o3d.geometry.TriangleMesh:
    return create_mash_rectangle(rect, bottom=0, top=windows_bottom_height, color=color)


def create_window_frame_top_mesh(
        rect: Rect,
        windows_top_height: int,
        wall_height: int,
        color: List[int]
) -> o3d.geometry.TriangleMesh:
    return create_mash_rectangle(rect, bottom=windows_top_height, top=wall_height, color=color)


def create_window_mesh(
        rect: Rect,
        windows_bottom_height: int,
        windows_top_height: int,
        color: List[int]
) -> o3d.geometry.TriangleMesh:
    return create_mash_rectangle(rect, bottom=windows_bottom_height, top=windows_top_height, color=color)


def calculate_door_height(front_door_rect: Rect) -> int:
    return int((DEFAULT_DOOR_HEIGHT / DEFAULT_DOOR_WIDTH) * front_door_rect.max_size)


def calculate_wall_height(door_height: int, wall_type: WallSizeType) -> int:
    return int(wall_type.value / DEFAULT_DOOR_HEIGHT * door_height)


def calculate_window_height(wall_height: int, window_type: WindowSizeType) -> (int, int):
    bottom_value, top_value = window_type.value
    return int(bottom_value * wall_height), int(top_value * wall_height)


def create_3d(
        front_door_rect: Rect,
        rects: List[Rect],
        description: str,
        width: int,
        height: int,
        need_save: bool = True,
        need_show: bool = False
):
    meshes = []

    # Todo: Add getting types by description
    wall_type, window_type = WallSizeType.STANDARD, WindowSizeType.STANDARD

    door_height = calculate_door_height(front_door_rect)
    wall_height = calculate_wall_height(door_height, wall_type)
    windows_bottom_height, windows_top_height = calculate_window_height(wall_height, window_type)

    outside_corner = find_outside_corner_points(width, height, rects + [front_door_rect])
    outside_polygon = Polygon(points=outside_corner, color=WALL_COLOR)
    meshes.append(create_floor_mesh(outside_polygon, thickness=DEFAULT_THICKNESS))
    meshes.append(create_ceiling_mesh(outside_polygon, thickness=DEFAULT_THICKNESS, wall_height=wall_height))

    for rect in rects + [front_door_rect]:
        if rect.rect_type == RectType.WALL:
            mesh = create_wall_mesh(rect, wall_height=wall_height, color=WALL_COLOR)
            meshes.append(mesh)
        elif rect.rect_type == RectType.DOOR:
            door = create_door_mesh(rect, door_height=door_height, color=DOOR_COLOR)
            meshes.append(door)
            doorway = create_doorway_mesh(rect, door_height=door_height, wall_height=wall_height, color=WALL_COLOR)
            meshes.append(doorway)
        elif rect.rect_type == RectType.WINDOW:
            window = create_window_mesh(
                rect,
                windows_bottom_height=windows_bottom_height,
                windows_top_height=windows_top_height,
                color=WINDOW_COLOR
            )
            meshes.append(window)
            window_frame_bottom = create_window_frame_bottom_mesh(
                rect,
                windows_bottom_height=windows_bottom_height,
                color=WALL_COLOR
            )
            meshes.append(window_frame_bottom)
            window_frame_top = create_window_frame_top_mesh(
                rect,
                windows_top_height=windows_top_height,
                wall_height=wall_height,
                color=WALL_COLOR
            )
            meshes.append(window_frame_top)
        else:
            raise ValueError(f'Unknown type = {rect.rect_type}')
    if need_save:
        meshes_to_bim(meshes)
        print(f'3D BIM model saved in file {IFC_PATH}')
        o3d.io.write_triangle_mesh(OBJ_PATH, combine_mashes(meshes))
        print(f'3D obj saved in file {OBJ_PATH}')
        save_as_gif(meshes, gif_file_name=GIF_PATH)
        print(f'Gif saved in file {GIF_PATH}')
    if need_show:
        o3d.visualization.draw_geometries(meshes)
