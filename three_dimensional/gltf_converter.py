from typing import List

import trimesh
import numpy as np

from dto.mesh import ConstructionMesh


def to_trimesh_meshes(meshes: List[ConstructionMesh]):
    trimesh_meshes = []
    for i, mesh in enumerate(meshes):
        trimesh_mesh = trimesh.Trimesh(
            vertices=np.asarray(mesh.mesh.vertices) / 100,
            faces=np.asarray(mesh.mesh.triangles),
            vertex_normals=np.asarray(mesh.mesh.vertex_normals) / 100,
            face_normals=np.asarray(mesh.mesh.triangle_normals)
        )
        trimesh_mesh.apply_transform(trimesh.transformations.rotation_matrix(3 * np.pi / 2, [1, 0, 0]))
        trimesh_meshes.append(trimesh_mesh)
    return trimesh_meshes


def save_meshes_as_gltf_format(meshes: List[ConstructionMesh], output_path: str):
    scene = trimesh.Scene()
    counts = {}

    for construction_mesh, mesh in zip(meshes, to_trimesh_meshes(meshes)):
        count = 0
        if counts.keys().__contains__(construction_mesh.construction_type.name):
            count = counts[construction_mesh.construction_type.name] + 1
        counts[construction_mesh.construction_type.name] = count
        scene.add_geometry(mesh, node_name=f"{construction_mesh.construction_type.name}_{count}")

    scene.export(file_obj=output_path, file_type='gltf')
