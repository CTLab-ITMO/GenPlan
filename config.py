import os

RESULTS_FOLDER = "results"
PNG_PATH = os.path.join(RESULTS_FOLDER, "input.png")
CLEAN_PNG_PATH = os.path.join(RESULTS_FOLDER, "clean_input.png")
SVG_PATH = os.path.join(RESULTS_FOLDER, "output_2d.svg")
GIF_PATH = os.path.join(RESULTS_FOLDER, "output_3d.gif")
OBJ_PATH = os.path.join(RESULTS_FOLDER, "output_3d.obj")
IFC_PATH = os.path.join(RESULTS_FOLDER, "output_3d.ifc")
GLTF_PATH = os.path.join(RESULTS_FOLDER, "output_3d.gltf")

BLACK_COLOR_BORDER = 10
MAX_PERCENTILE = 0.15
MAX_VALUE = 2000
MIN_THICKNESS = 3
MAX_DEVIATION = 2

# config for 2d
DOOR_WIDTH = 5

DEFAULT_COLOR = [0, 0, 0]
DOOR_COLOR = [150, 80, 50]
WINDOW_COLOR = [153, 204, 255]
WALL_COLOR = [128, 128, 128]
ROOF_COLOR = [69, 21, 13]
BEAM_COLOR = [160, 95, 7]

LOSS_SCALE = 200.0
EDGING_TYPE = "rectangle"  # ["rectangle", "random_mask"]
USE_WHITE_LOSS = True
