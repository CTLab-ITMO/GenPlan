from typing import List, Tuple, Dict

import numpy as np
import open3d as o3d
import trimesh

from tqdm import tqdm
from collections import deque
from config import WALL_COLOR, DOOR_COLOR, WINDOW_COLOR, ROOF_COLOR, BEAM_COLOR
from dto.enum.construction_type import ConstructionType
from dto.enum.format_type import FormatType
from dto.enum.position_type import PositionType
from dto.mesh import ConstructionMesh, CylinderMesh, PolygonMesh, RectangleMesh, PointsMesh
from dto.point import Point
from dto.polygon import Polygon
from dto.rect import Rect
from dto.enum.rect_type import RectType
from dto.enum.wall_size_type import WallSizeType
from dto.enum.window_size_type import WindowSizeType
from dto.roof.roof import Roof
from metrics.endurance import calculate_endurance_wall
from metrics.illumination import calculate_illumination
from three_dimensional.classifier import classify_windows_and_walls
from three_dimensional.ifc_converter import save_meshes_as_bim_format
from three_dimensional.gltf_converter import save_meshes_as_gltf_format
from three_dimensional.obj_converter import save_meshes_as_obj_format
from three_dimensional.gif_converter import save_meashes_as_gif_format

# default params of door
DEFAULT_DOOR_HEIGHT = 200.0
DEFAULT_DOOR_WIDTH = 90.0
DEFAULT_WALL_THICKNESS = 10
DEFAULT_ROOF_THICKNESS = 10
DEFAULT_ROOF_ANGLE_1 = 15
DEFAULT_ROOF_ANGLE_2 = 30
DEFAULT_ROOF_INDENT = 50
DEFAULT_BEAM_RADIUS = 0.5
DEFAULT_BEAM_THICKNESS = 10
DEFAULT_BEAM_WIDTH = 20
DEFAULT_BEAM_SPACE = 50
# space between angle and vertical beam in 2 slopes roof
DEFAULT_BEAM_ANGLE_SPACE = 70


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


def create_wall_mesh(rect: Rect, wall_height: int, color: List[int]) -> ConstructionMesh:
    return RectangleMesh(
        rect=rect,
        bottom=0,
        top=wall_height,
        color=color,
        construction_type=ConstructionType.WALL
    )


def create_doorway_mesh(rect: Rect, door_height: int, wall_height: int, color: List[int]) -> ConstructionMesh:
    return RectangleMesh(
        rect=rect,
        bottom=door_height,
        top=wall_height,
        color=color,
        construction_type=ConstructionType.WALL
    )


def create_door_mesh(rect: Rect, door_height: int, color: List[int]) -> ConstructionMesh:
    return RectangleMesh(
        rect=rect,
        bottom=0,
        top=door_height,
        color=color,
        construction_type=ConstructionType.DOOR
    )


def create_floor_mesh(polygon: Polygon, thickness: int, color: List[int]) -> ConstructionMesh:
    return PolygonMesh(
        polygon=polygon,
        bottom=-thickness,
        top=0,
        color=color,
        construction_type=ConstructionType.FLOOR,
    )


def create_ceiling_mesh(polygon: Polygon, thickness: int, wall_height: int, color: List[int]) -> ConstructionMesh:
    return PolygonMesh(
        polygon=polygon,
        bottom=wall_height,
        top=wall_height + thickness,
        color=color,
        construction_type=ConstructionType.CEILING,
    )


def create_window_frame_bottom_mesh(
        rect: Rect,
        windows_bottom_height: int,
        color: List[int]
) -> ConstructionMesh:
    return RectangleMesh(
        rect=rect,
        bottom=0,
        top=windows_bottom_height,
        color=color,
        construction_type=ConstructionType.WALL
    )


def create_window_frame_top_mesh(
        rect: Rect,
        windows_top_height: int,
        wall_height: int,
        color: List[int]
) -> ConstructionMesh:
    return RectangleMesh(
        rect=rect,
        bottom=windows_top_height,
        top=wall_height,
        color=color,
        construction_type=ConstructionType.WALL
    )


def create_window_mesh(
        rect: Rect,
        windows_bottom_height: int,
        windows_top_height: int,
        color: List[int]
) -> ConstructionMesh:
    return RectangleMesh(
        rect=rect,
        bottom=windows_bottom_height,
        top=windows_top_height,
        color=color,
        construction_type=ConstructionType.WINDOW
    )


def create_roof_mesh(
        points: List[Tuple[int, int, int]],
        color: List[int]
) -> ConstructionMesh:
    return PointsMesh(
        points=points,
        color=color,
        construction_type=ConstructionType.ROOF
    )


def create_wall_roof_mesh(
        points: List[Tuple[int, int, int]],
        color: List[int]
) -> ConstructionMesh:
    return PointsMesh(
        points=points,
        color=color,
        construction_type=ConstructionType.WALL
    )


def create_beam_roof_mesh(
        points: List[Tuple[int, int, int]],
        color: List[int]
) -> ConstructionMesh:
    return PointsMesh(
        points=points,
        color=color,
        construction_type=ConstructionType.BEAM
    )


def calculate_door_height(front_door_rect: Rect) -> int:
    return int((DEFAULT_DOOR_HEIGHT / DEFAULT_DOOR_WIDTH) * front_door_rect.max_size)


def calculate_wall_height(door_height: int, wall_type: WallSizeType) -> int:
    return int(wall_type.value / DEFAULT_DOOR_HEIGHT * door_height)


def calculate_window_height(wall_height: int, window_type: WindowSizeType) -> (int, int):
    bottom_value, top_value = window_type.value
    return int(bottom_value * wall_height), int(top_value * wall_height)


def create_roof(rect: Rect, height: int, position_type: PositionType, slopes_count: int) -> Roof:
    angle_degrees = 45
    if slopes_count == 1:
        angle_degrees = DEFAULT_ROOF_ANGLE_1
    elif slopes_count == 2:
        angle_degrees = DEFAULT_ROOF_ANGLE_2
    return Roof(
        rect=rect,
        roof_thickness=DEFAULT_ROOF_THICKNESS,
        wall_thickness=DEFAULT_WALL_THICKNESS,
        beam_thickness=DEFAULT_BEAM_THICKNESS,
        beam_width=DEFAULT_BEAM_WIDTH,
        beam_space=DEFAULT_BEAM_SPACE,
        beam_angle_space=DEFAULT_BEAM_ANGLE_SPACE,
        angle=angle_degrees,
        slopes_count=slopes_count,
        indent=DEFAULT_ROOF_INDENT,
        height=height + DEFAULT_WALL_THICKNESS,
        position_type=position_type,
    )


def o3d_to_trimesh(o3d_mesh):
    vertices = np.asarray(o3d_mesh.vertices)
    faces = np.asarray(o3d_mesh.triangles)
    return trimesh.Trimesh(vertices=vertices, faces=faces)


def create_fittings_for_wall_mesh(mesh: ConstructionMesh, step: int):
    meshes = []

    tri_mesh = o3d_to_trimesh(mesh)

    min_x = min(point[0] for point in mesh.vertices)
    max_x = max(point[0] for point in mesh.vertices)
    step_x = min(max_x - min_x - 1, step)
    last_x = 0

    min_y = min(point[1] for point in mesh.vertices)
    max_y = max(point[1] for point in mesh.vertices)
    step_y = min(max_y - min_y - 1, step)
    last_y = 0

    min_z = min(point[2] for point in mesh.vertices)
    max_z = max(point[2] for point in mesh.vertices)
    step_z = min(max_z - min_z - 1, step)
    last_z = 0

    # Add vertical
    last_x = 0
    for x in np.arange(min_x + DEFAULT_BEAM_RADIUS, max_x - DEFAULT_BEAM_RADIUS + 0.1, 1.0):
        if last_x % step_x == 0 or x == max_x - DEFAULT_BEAM_RADIUS:
            last_y = 0
            for y in np.arange(min_y + DEFAULT_BEAM_RADIUS, max_y - DEFAULT_BEAM_RADIUS + 0.1, 1.0):
                if last_y % step_y == 0 or y == max_y - DEFAULT_BEAM_RADIUS:
                    first_time = True
                    z1 = -1
                    z2 = -1
                    for z in np.arange(min_z + DEFAULT_BEAM_RADIUS, max_z - DEFAULT_BEAM_RADIUS + 0.1, 1.0):
                        if tri_mesh.contains([[x, y, z]]):
                            if first_time:
                                first_time = False
                                z1 = z
                            z2 = z
                    height = z2 - z1
                    if height > 0:
                        m = CylinderMesh(
                            center_point=[x, y, z1 + height / 2],
                            radius=DEFAULT_BEAM_RADIUS,
                            height=height,
                            color=WALL_COLOR,
                            construction_type=ConstructionType.FITTINGS
                        )
                        meshes.append(m)
                last_y += 1
        last_x += 1

    # Add horizontal x
    last_y = 0
    for y in np.arange(min_y + DEFAULT_BEAM_RADIUS, max_y - DEFAULT_BEAM_RADIUS + 0.1, 1.0):
        if last_y % step_y == 0 or y == max_y - DEFAULT_BEAM_RADIUS:
            last_z = 0
            for z in np.arange(min_z + DEFAULT_BEAM_RADIUS, max_z - DEFAULT_BEAM_RADIUS + 0.1, 1.0):
                if last_z % step_z == 0 or z == max_z - DEFAULT_BEAM_RADIUS:
                    first_time = True
                    x1 = -1
                    x2 = -1
                    for x in np.arange(min_x + DEFAULT_BEAM_RADIUS, max_x - DEFAULT_BEAM_RADIUS + 0.1, 1.0):
                        if tri_mesh.contains([[x, y, z]]):
                            if first_time:
                                first_time = False
                                x1 = x
                            x2 = x
                    height = x2 - x1
                    if height > 0:
                        m = CylinderMesh(
                            center_point=[x1 + height / 2, y, z],
                            radius=DEFAULT_BEAM_RADIUS,
                            height=height,
                            color=WALL_COLOR,
                            rotate_y=90,
                            construction_type=ConstructionType.FITTINGS
                        )
                        meshes.append(m)
                last_z += 1
        last_y += 1

    # Add horizontal y
    last_x = 0
    for x in np.arange(min_x + DEFAULT_BEAM_RADIUS, max_x - DEFAULT_BEAM_RADIUS + 0.1, 1.0):
        if last_x % step_x == 0 or x == max_x - DEFAULT_BEAM_RADIUS:
            last_z = 0
            for z in np.arange(min_z + DEFAULT_BEAM_RADIUS, max_z - DEFAULT_BEAM_RADIUS + 0.1, 1.0):
                if last_z % step_z == 0 or z == max_z - DEFAULT_BEAM_RADIUS:
                    first_time = True
                    y1 = -1
                    y2 = -1
                    for y in np.arange(min_y + DEFAULT_BEAM_RADIUS, max_y - DEFAULT_BEAM_RADIUS + 0.1, 1.0):
                        if tri_mesh.contains([[x, y, z]]):
                            if first_time:
                                first_time = False
                                y1 = y
                            y2 = y
                    height = y2 - y1
                    if height > 0:
                        m = CylinderMesh(
                            center_point=[x, y1 + height / 2, z],
                            radius=DEFAULT_BEAM_RADIUS,
                            height=height,
                            color=WALL_COLOR,
                            rotate_x=90,
                            construction_type=ConstructionType.FITTINGS
                        )
                        meshes.append(m)
                last_z += 1
        last_x += 1

    return meshes


def get_door_type(front_door_rect: Rect, outside_polygon: Polygon) -> PositionType:
    x1 = front_door_rect.start_point.x
    y1 = front_door_rect.start_point.y
    x2 = front_door_rect.end_point.x
    y2 = front_door_rect.end_point.y

    left = 0
    right = 0
    up = 0
    bottom = 0

    mod = 5  # Need to work with inaccuracy of pixels

    for p in outside_polygon.points:
        if abs(p.x - x1) < mod:
            left += 1
        if abs(p.y - y1) < mod:
            up += 1
        if abs(p.x - x2) < mod:
            right += 1
        if abs(p.y - y2) < mod:
            bottom += 1

    if sum(1 for num in [left, right, up, bottom] if num != 0) != 1:
        raise ValueError("Unknown door position")

    if left > 0:
        return PositionType.LEFT
    elif right > 0:
        return PositionType.RIGHT
    elif up > 0:
        return PositionType.UP
    elif bottom > 0:
        return PositionType.BOTTOM


def show_metrics(nlc: float, endurance: Dict[str, bool]):
    print("Metrics of generated Plan :")
    print(f"- NLC (natural light coefficient) = {nlc:.2f}")
    for key in endurance:
        if endurance[key]:
            checked_str = "meets the standards"
        else:
            checked_str = "does not meet the standards"
        print(f"- {key} {checked_str}")


def save_formats(formats: List[FormatType], meshes: List[ConstructionMesh]):
    if formats is None:
        return
    for format_type in formats:
        if format_type == FormatType.IFC:
            save_meshes_as_bim_format(meshes, format_type.path)
            print(f'3D ifc model saved in file {format_type.path}')
        elif format_type == FormatType.OBJ:
            save_meshes_as_obj_format(meshes, format_type.path)
            print(f'3D obj model saved in file {format_type.path}')
        elif format_type == FormatType.GIF:
            save_meashes_as_gif_format(meshes, format_type.path)
            print(f'3D gif model saved in file {format_type.path}')
        elif format_type == FormatType.GLTF:
            save_meshes_as_gltf_format(meshes, format_type.path)
            print(f'3D gltf model saved in file {format_type.path}')
        elif format_type == FormatType.SHOW:
            o3d.visualization.draw_geometries([m.mesh for m in meshes])


def create_3d(
        front_door_rect: Rect,
        rects: List[Rect],
        description: str,
        width: int,
        height: int,
        formats: List[FormatType],
):
    meshes: List[ConstructionMesh] = []
    windows: List[Rect] = []
    walls: List[Rect] = []

    window_type, wall_type = classify_windows_and_walls(description)

    door_height = calculate_door_height(front_door_rect)
    wall_height = calculate_wall_height(door_height, wall_type)
    windows_bottom_height, windows_top_height = calculate_window_height(wall_height, window_type)

    outside_corner = find_outside_corner_points(width, height, rects + [front_door_rect])
    outside_polygon = Polygon(points=outside_corner, color=WALL_COLOR)
    meshes.append(create_floor_mesh(
        polygon=outside_polygon,
        thickness=DEFAULT_WALL_THICKNESS,
        color=WALL_COLOR,
    ))
    meshes.append(create_ceiling_mesh(
        polygon=outside_polygon,
        thickness=DEFAULT_WALL_THICKNESS,
        wall_height=wall_height,
        color=WALL_COLOR,
    ))

    roof = create_roof(
        rect=outside_polygon.to_rect(),
        height=wall_height,
        position_type=get_door_type(front_door_rect, outside_polygon),
        slopes_count=2
    )
    for wall in roof.get_coordinates_of_walls():
        meshes.append(create_wall_roof_mesh(wall, WALL_COLOR))
    for slope in roof.get_coordinates_of_slopes():
        meshes.append(create_roof_mesh(slope, ROOF_COLOR))
    for beam in roof.get_coordinates_of_beams():
        meshes.append(create_beam_roof_mesh(beam, BEAM_COLOR))

    for rect in rects + [front_door_rect]:
        if rect.rect_type == RectType.WALL:
            walls.append(rect)
            mesh = create_wall_mesh(rect, wall_height=wall_height, color=WALL_COLOR)
            meshes.append(mesh)
        elif rect.rect_type == RectType.DOOR:
            door = create_door_mesh(rect, door_height=door_height, color=DOOR_COLOR)
            meshes.append(door)
            doorway = create_doorway_mesh(rect, door_height=door_height, wall_height=wall_height, color=WALL_COLOR)
            meshes.append(doorway)
        elif rect.rect_type == RectType.WINDOW:
            windows.append(rect)
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
    print("Adding fittings...")
    for mesh in tqdm(meshes):
        if mesh.construction_type == ConstructionType.WALL:
            fittings = create_fittings_for_wall_mesh(mesh, 40)
            for fitting in fittings:
                meshes.append(fitting)
    show_metrics(
        nlc=calculate_illumination(outside_polygon, windows),
        endurance=calculate_endurance_wall(wall_height, walls, DEFAULT_BEAM_RADIUS)
    )
    save_formats(formats, meshes)
