from typing import List

import open3d as o3d

from dto.enum.construction_type import ConstructionType
from dto.mesh import ConstructionMesh


def combine_mashes(meshes: List[ConstructionMesh]) -> ConstructionMesh:
    if len(meshes) == 0:
        raise ValueError('Can\'t combine empty meshes.')
    final_mesh = meshes[0].mesh
    for i in range(0, len(meshes)):
        final_mesh += meshes[i].mesh
    return ConstructionMesh(final_mesh, ConstructionType.COMBINED)


def save_meshes_as_obj_format(meshes: List[ConstructionMesh], output_path: str):
    o3d.io.write_triangle_mesh(output_path, combine_mashes(meshes).mesh)
