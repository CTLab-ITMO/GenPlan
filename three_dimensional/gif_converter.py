from typing import List
import open3d as o3d
import os
from tqdm import tqdm
import shutil
from PIL import Image

from dto.mesh import ConstructionMesh


def save_meashes_as_gif_format(meshes: List[ConstructionMesh], output_path: str):
    print("Creating GIF for 3D")

    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False)
    for mesh in meshes:
        vis.add_geometry(mesh.mesh)
    duration = 10_000
    shot_step = 15
    shots_count = 2160 // shot_step
    vis.get_render_option().mesh_show_back_face = True
    vis.get_view_control().rotate(0, 650 + 1080)

    directory = "gif_shots"
    if not os.path.isdir(directory):
        os.mkdir(directory)

    images = []

    for i in tqdm(range(shots_count - 4)):
        angle = i * shot_step
        vis.get_view_control().rotate(shot_step, 0)
        vis.poll_events()
        vis.update_renderer()

        filename = os.path.join(directory, f"shot_view_{angle}.png")
        vis.capture_screen_image(filename)
        images.append(Image.open(filename))

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration // shots_count,
        loop=0,
        optimize=True
    )

    vis.destroy_window()
    shutil.rmtree(directory)
