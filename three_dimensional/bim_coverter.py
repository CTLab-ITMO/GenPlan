import ifcopenshell
import ifcopenshell.api
import numpy as np

from config import WALL_COLOR, WINDOW_COLOR, DOOR_COLOR, IFC_PATH, ROOF_COLOR


def add_style(model, representation, colors, transparency):
    style = ifcopenshell.api.style.add_style(
        model,
        name="Color"
    )

    ifcopenshell.api.style.add_surface_style(
        model,
        style=style,
        ifc_class="IfcSurfaceStyleShading",
        attributes={
            "SurfaceColour": {"Name": None, "Red": colors[0], "Green": colors[1], "Blue": colors[2]},
            "Transparency": transparency
        }
    )

    ifcopenshell.api.style.assign_representation_styles(
        model,
        shape_representation=representation,
        styles=[style]
    )


def add_element(model, body_context, mesh, element, colors, transparency=0.0):
    representation = ifcopenshell.api.geometry.add_mesh_representation(
        model,
        context=body_context,
        vertices=[np.asarray(mesh.vertices) / 100],
        faces=[mesh.triangles],
        force_faceted_brep=True
    )
    ifcopenshell.api.geometry.assign_representation(
        model,
        product=element,
        representation=representation
    )
    add_style(model, representation, colors, transparency)


def meshes_to_bim(meshes):
    model = ifcopenshell.file()
    project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name="Project")
    ifcopenshell.api.context.add_context(model, context_type="Model")
    body_context = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW"
    )

    unit = ifcopenshell.api.unit.add_si_unit(
        model,
        unit_type="LENGTHUNIT",
        prefix="MILLI"
    )
    ifcopenshell.api.unit.assign_unit(model, units=[unit])

    site = ifcopenshell.api.root.create_entity(
        model,
        ifc_class="IfcSite",
        name="Site"
    )
    ifcopenshell.api.aggregate.assign_object(
        model,
        relating_object=project,
        products=[site]
    )

    building = ifcopenshell.api.root.create_entity(
        model,
        ifc_class="IfcBuilding",
        name="Building"
    )
    ifcopenshell.api.aggregate.assign_object(
        model,
        relating_object=site,
        products=[building]
    )

    storey = ifcopenshell.api.root.create_entity(
        model,
        ifc_class="IfcBuildingStorey",
        name="First floor"
    )
    ifcopenshell.api.aggregate.assign_object(
        model,
        relating_object=building,
        products=[storey]
    )

    walls = []
    windows = []
    doors = []
    roofs = []
    for mesh in meshes:
        colors = mesh.vertex_colors[0] * 255
        mesh_colors = mesh.vertex_colors[0]
        if all(colors == WALL_COLOR):
            wall = ifcopenshell.api.root.create_entity(
                model,
                ifc_class="IfcWall",
                name="Wall",
                predefined_type="STRAIGHT"
            )
            walls.append(wall)
            add_element(model, body_context, mesh, wall, mesh_colors)
        elif all(colors == WINDOW_COLOR):
            pass
            window = ifcopenshell.api.root.create_entity(
                model,
                ifc_class="IfcWindow",
                name="Window",
                predefined_type="WINDOW"
            )
            windows.append(window)
            add_element(model, body_context, mesh, window, mesh_colors, transparency=0.5)
        elif all(colors == DOOR_COLOR):
            door = ifcopenshell.api.root.create_entity(
                model,
                ifc_class="IfcDoor",
                name="door",
                predefined_type="DOOR"
            )
            doors.append(door)
            add_element(model, body_context, mesh, door, mesh_colors)
        elif all(colors == ROOF_COLOR):
            roof = ifcopenshell.api.root.create_entity(
                model,
                ifc_class="IfcRoof",
                name="roof",
                predefined_type="ROOF"
            )
            roofs.append(roof)
            add_element(model, body_context, mesh, roof, mesh_colors)
        else:
            raise ValueError(f'Unknown RGB color {colors}')

    ifcopenshell.api.aggregate.assign_object(
        model,
        relating_object=storey,
        products=walls + windows + doors + roofs
    )
    model.write(IFC_PATH)
