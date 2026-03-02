import math
from typing import List, Tuple

import numpy as np
import open3d as o3d

from dto.enum.construction_type import ConstructionType
from dto.polygon import Polygon
from dto.rect import Rect


class ConstructionMesh:
    mesh: o3d.geometry.TriangleMesh
    construction_type: ConstructionType
    vertices: List[List[float]]
    triangles: List[List[int]]
    vertex_colors: List[float]

    def __init__(self, mesh: o3d.geometry.TriangleMesh, construction_type: ConstructionType):
        self.mesh = mesh
        self.construction_type = construction_type
        self.vertices = mesh.vertices
        self.triangles = mesh.triangles
        self.vertex_colors = mesh.vertex_colors[0]

    def combine(self, meshes):
        final_mesh = self.mesh
        for m in meshes:
            final_mesh += m.mesh
        return final_mesh


class CylinderMesh(ConstructionMesh):

    def __init__(
            self,
            center_point: List[float],
            radius, height,
            # color - RGB array [0..255, 0..255, 0..255]
            color: List[int],
            construction_type: ConstructionType,
            rotate_x: float = 0.0,
            rotate_y: float = 0.0,
            rotate_z: float = 0.0,
    ):
        mesh = o3d.geometry.TriangleMesh.create_cylinder(radius=radius, height=height, resolution=50)

        rotation = mesh.get_rotation_matrix_from_xyz((math.radians(rotate_x), math.radians(rotate_y), math.radians(rotate_z)))
        mesh.rotate(rotation, center=(0, 0, 0))

        translation = np.array(center_point)
        mesh.translate(translation)
        mesh.compute_vertex_normals()
        norm_color = [c / 255 for c in color]
        mesh.paint_uniform_color(norm_color)
        super().__init__(mesh, construction_type)


class TriangleMesh(ConstructionMesh):

    def __init__(
            self,
            vertices: List[List[int]],
            triangles,
            # color - RGB array [0..255, 0..255, 0..255]
            color: List[int],
            construction_type: ConstructionType
    ):
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh.triangles = o3d.utility.Vector3iVector(triangles)
        mesh.compute_vertex_normals()
        norm_color = [c / 255 for c in color]
        mesh.paint_uniform_color(norm_color)
        super().__init__(mesh, construction_type)


class RectangleMesh(TriangleMesh):

    def __init__(
            self,
            rect: Rect,
            bottom: int,
            top: int,
            color: List[int],
            construction_type: ConstructionType,
    ):
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
        super().__init__(vertices, triangles, color, construction_type)


class PolygonMesh(TriangleMesh):

    def __init__(
            self,
            polygon: Polygon,
            bottom: int,
            top: int,
            color: List[int],
            construction_type: ConstructionType,
    ):
        vertices = []
        for point in polygon.points:
            vertices.append([point.x, point.y, top])
            vertices.append([point.x, point.y, bottom])
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
        super().__init__(vertices, triangles, color, construction_type)


class PointsMesh(TriangleMesh):

    def __init__(
            self,
            points: List[Tuple[int, int, int]],
            color: List[int],
            construction_type: ConstructionType,
    ):
        vertices = []
        for (x, y, z) in points:
            vertices.append([x, y, z])

        if len(points) == 8:
            triangles = [
                [0, 1, 2], [0, 2, 3],
                [4, 6, 5], [4, 7, 6],
                [0, 4, 5], [0, 5, 1],
                [1, 5, 6], [1, 6, 2],
                [2, 6, 7], [2, 7, 3],
                [3, 7, 4], [3, 4, 0]
            ]
        elif len(points) == 6:
            triangles = [
                [0, 1, 2], [3, 5, 4],
                [0, 3, 1], [1, 3, 4],
                [1, 4, 2], [2, 4, 5],
                [2, 5, 0], [0, 5, 3]
            ]
        else:
            raise ValueError(f'Unsupported count of points with {len(points)}.')
        super().__init__(vertices, triangles, color, construction_type)
