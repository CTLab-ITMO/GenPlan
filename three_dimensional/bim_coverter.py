import ifcopenshell
import ifcopenshell.api

from config import WALL_COLOR, WINDOW_COLOR, DOOR_COLOR, IFC_PATH


def add_element(model, body_context, mesh, element, colors, transparency=0.0):
    element_length = float(abs(mesh.vertices[0][0] - mesh.vertices[2][0]) / 100)
    element_thickness = float(abs(mesh.vertices[0][1] - mesh.vertices[1][1]) / 100)
    element_height = float(abs(mesh.vertices[0][2] - mesh.vertices[4][2]) / 100)

    representation = ifcopenshell.api.run(
        "geometry.add_wall_representation",
        model,
        context=body_context,
        length=element_length,
        height=element_height,
        thickness=element_thickness
    )
    ifcopenshell.api.run(
        "geometry.assign_representation", model,
        product=element,
        representation=representation
    )

    x = mesh.vertices[0][0] / 100
    y = mesh.vertices[0][1] / 100
    z = mesh.vertices[0][2] / 100

    ifcopenshell.api.run(
        "geometry.edit_object_placement",
        model,
        product=element,
        matrix=[
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ]
    )

    style = ifcopenshell.api.run(
        "style.add_style",
        model,
        name="Color"
    )

    ifcopenshell.api.run(
        "style.add_surface_style",
        model,
        style=style,
        ifc_class="IfcSurfaceStyleShading",
        attributes={
            "SurfaceColour": {"Name": None, "Red": colors[0], "Green": colors[1], "Blue": colors[2]},
            "Transparency": transparency
        }
    )

    ifcopenshell.api.run(
        "style.assign_representation_styles",
        model,
        shape_representation=representation,
        styles=[style]
    )


def meshes_to_bim(meshes):
    model = ifcopenshell.file()
    project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name="Project")
    context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    body_context = ifcopenshell.api.run(
        "context.add_context",
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW"
    )

    unit = ifcopenshell.api.run(
        "unit.add_si_unit",
        model,
        unit_type="LENGTHUNIT",
        prefix="MILLI"
    )
    ifcopenshell.api.run("unit.assign_unit", model, units=[unit])

    site = ifcopenshell.api.run(
        "root.create_entity",
        model,
        ifc_class="IfcSite",
        name="Site"
    )
    ifcopenshell.api.run(
        "aggregate.assign_object",
        model,
        relating_object=project,
        products=[site]
    )

    building = ifcopenshell.api.run(
        "root.create_entity", model,
        ifc_class="IfcBuilding",
        name="Building"
    )
    ifcopenshell.api.run(
        "aggregate.assign_object", model,
        relating_object=site,
        products=[building]
    )

    storey = ifcopenshell.api.run(
        "root.create_entity",
        model,
        ifc_class="IfcBuildingStorey",
        name="First floor"
    )
    ifcopenshell.api.run(
        "aggregate.assign_object",
        model,
        relating_object=building,
        products=[storey]
    )

    walls = []
    windows = []
    doors = []
    for mesh in meshes:
        colors = mesh.vertex_colors[0] * 255
        mesh_colors = mesh.vertex_colors[0]
        if all(colors == WALL_COLOR):
            wall = ifcopenshell.api.run(
                "root.create_entity",
                model,
                ifc_class="IfcWall",
                name="Wall",
                predefined_type="STRAIGHT"
            )
            walls.append(wall)
            add_element(model, body_context, mesh, wall, mesh_colors)
        elif all(colors == WINDOW_COLOR):
            pass
            window = ifcopenshell.api.run(
                "root.create_entity",
                model,
                ifc_class="IfcWindow",
                name="Window",
                predefined_type="WINDOW"
            )
            windows.append(window)
            add_element(model, body_context, mesh, window, mesh_colors, transparency=0.5)
        elif all(colors == DOOR_COLOR):
            door = ifcopenshell.api.run(
                "root.create_entity",
                model,
                ifc_class="IfcDoor",
                name="door",
                predefined_type="DOOR"
            )
            doors.append(door)
            add_element(model, body_context, mesh, door, mesh_colors)
        else:
            raise ValueError(f'Unknown RGB color {colors}')

    ifcopenshell.api.run(
        "aggregate.assign_object",
        model,
        relating_object=storey,
        products=walls + windows + doors
    )
    model.write(IFC_PATH)
