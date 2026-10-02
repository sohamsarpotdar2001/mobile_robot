#!/usr/bin/env python3

import argparse
import copy
import os
import re
import xml.etree.ElementTree as ET

import numpy as np
import trimesh


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

# Keywords used to classify links.
WHEEL_KEYWORDS = [
    "wheel",
    "left_wheel",
    "right_wheel",
    "front_wheel",
    "rear_wheel",
]

CYLINDER_KEYWORDS = [
    "roller",
    "drum",
]

SPHERE_KEYWORDS = [
    "ball",
    "ball_caster",
    "sphere",
]

BOX_KEYWORDS = [
    "base",
    "chassis",
    "body",
    "plate",
    "cover",
]


# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

def get_mesh_filename(link):
    """Return the mesh filename from the visual geometry."""

    visual = link.find("visual")
    if visual is None:
        return None

    geometry = visual.find("geometry")
    if geometry is None:
        return None

    mesh = geometry.find("mesh")
    if mesh is None:
        return None

    return mesh.get("filename")


def resolve_mesh_path(mesh_filename, urdf_path):
    """
    Resolve mesh path relative to the URDF.

    Supports:
      meshes/foo.stl
      package://my_robot/meshes/foo.stl
      file://...
    """

    if mesh_filename is None:
        return None

    path = mesh_filename

    # ROS package:// URI
    if path.startswith("package://"):
        path = path[len("package://"):]

        # Try relative to URDF first
        parts = path.split("/", 1)

        if len(parts) == 2:
            package_name, relative_path = parts
            urdf_dir = os.path.dirname(os.path.abspath(urdf_path))

            # Search upwards for package directory
            current = urdf_dir

            while True:
                candidate = os.path.join(
                    current,
                    package_name,
                    relative_path,
                )

                if os.path.exists(candidate):
                    return candidate

                parent = os.path.dirname(current)

                if parent == current:
                    break

                current = parent

            # Also try directly
            candidate = os.path.join(urdf_dir, relative_path)

            if os.path.exists(candidate):
                return candidate

            return candidate

    if path.startswith("file://"):
        path = path[len("file://"):]

    if os.path.isabs(path):
        return path

    return os.path.join(
        os.path.dirname(os.path.abspath(urdf_path)),
        path,
    )


def load_mesh(mesh_path):
    """Load a mesh using trimesh."""

    mesh = trimesh.load(
        mesh_path,
        force="mesh",
    )

    if isinstance(mesh, trimesh.Scene):
        meshes = []

        for geometry in mesh.geometry.values():
            if isinstance(geometry, trimesh.Trimesh):
                meshes.append(geometry)

        if not meshes:
            raise RuntimeError(f"No mesh geometry found in {mesh_path}")

        mesh = trimesh.util.concatenate(meshes)

    return mesh


def normalize_name(name):
    """Normalize a link name for keyword matching."""

    name = name.lower()

    # Replace separators with spaces
    name = re.sub(r"[_\-\.]+", " ", name)

    return name


# ------------------------------------------------------------
# Classification
# ------------------------------------------------------------

def classify_link(link_name, mesh_filename):
    """
    Decide collision geometry type.

    Priority:
      wheel -> cylinder
      caster/ball -> sphere
      base/chassis/body -> box
      everything else -> box
    """

    text = normalize_name(
        f"{link_name} {mesh_filename or ''}"
    )

    # Wheels
    for keyword in WHEEL_KEYWORDS:
        if normalize_name(keyword) in text:
            return "cylinder"

    # Spherical casters
    for keyword in SPHERE_KEYWORDS:
        if normalize_name(keyword) in text:
            return "sphere"

    # Explicit cylindrical parts
    for keyword in CYLINDER_KEYWORDS:
        if normalize_name(keyword) in text:
            return "cylinder"

    # Boxes
    for keyword in BOX_KEYWORDS:
        if normalize_name(keyword) in text:
            return "box"

    # Safe default
    return "box"


# ------------------------------------------------------------
# Mesh geometry
# ------------------------------------------------------------

def mesh_bounds(mesh):
    """
    Return:
        min_corner
        max_corner
        center
        dimensions
    """

    bounds = mesh.bounds

    min_corner = bounds[0]
    max_corner = bounds[1]

    center = (min_corner + max_corner) / 2.0
    dimensions = max_corner - min_corner

    return min_corner, max_corner, center, dimensions


def cylinder_dimensions(mesh):
    """
    Estimate wheel cylinder radius and thickness.

    Assumes the wheel's local axis is approximately one of
    X/Y/Z and chooses the smallest bounding-box dimension as
    the cylinder thickness.
    """

    _, _, center, dimensions = mesh_bounds(mesh)

    axis = int(np.argmin(dimensions))

    thickness = dimensions[axis]

    other_axes = [
        i for i in range(3)
        if i != axis
    ]

    diameter = max(dimensions[other_axes])

    radius = diameter / 2.0

    return radius, thickness, center, axis


# ------------------------------------------------------------
# XML
# ------------------------------------------------------------

def remove_existing_collision(link):
    """Remove existing collision tags."""

    for collision in list(link.findall("collision")):
        link.remove(collision)


def add_box_collision(link, center, dimensions):
    collision = ET.SubElement(link, "collision")

    origin = ET.SubElement(collision, "origin")

    origin.set(
        "xyz",
        "{:.6f} {:.6f} {:.6f}".format(*center)
    )

    origin.set(
        "rpy",
        "0 0 0"
    )

    geometry = ET.SubElement(collision, "geometry")

    box = ET.SubElement(geometry, "box")

    box.set(
        "size",
        "{:.6f} {:.6f} {:.6f}".format(*dimensions)
    )


def add_sphere_collision(link, center, dimensions):
    collision = ET.SubElement(link, "collision")

    origin = ET.SubElement(collision, "origin")

    origin.set(
        "xyz",
        "{:.6f} {:.6f} {:.6f}".format(*center)
    )

    origin.set(
        "rpy",
        "0 0 0"
    )

    geometry = ET.SubElement(collision, "geometry")

    sphere = ET.SubElement(geometry, "sphere")

    radius = max(dimensions) / 2.0

    sphere.set(
        "radius",
        "{:.6f}".format(radius)
    )


def add_cylinder_collision(
    link,
    center,
    radius,
    length,
    axis,
):
    collision = ET.SubElement(link, "collision")

    origin = ET.SubElement(collision, "origin")

    origin.set(
        "xyz",
        "{:.6f} {:.6f} {:.6f}".format(*center)
    )

    # URDF cylinders are aligned along Z.
    #
    # Rotate the cylinder so its axis matches
    # the mesh's smallest bounding-box dimension.
    if axis == 0:
        # X -> Z
        rpy = "0 1.57079632679 0"

    elif axis == 1:
        # Y -> Z
        rpy = "-1.57079632679 0 0"

    else:
        # Z
        rpy = "0 0 0"

    origin.set("rpy", rpy)

    geometry = ET.SubElement(collision, "geometry")

    cylinder = ET.SubElement(
        geometry,
        "cylinder"
    )

    cylinder.set(
        "radius",
        "{:.6f}".format(radius)
    )

    cylinder.set(
        "length",
        "{:.6f}".format(length)
    )


# ------------------------------------------------------------
# Main processing
# ------------------------------------------------------------

def process_urdf(input_urdf, output_urdf):

    print(f"Reading: {input_urdf}")

    tree = ET.parse(input_urdf)
    root = tree.getroot()

    links = root.findall("link")

    print(f"Found {len(links)} links")

    for link in links:

        link_name = link.get("name")

        mesh_filename = get_mesh_filename(link)

        if mesh_filename is None:
            print(
                f"[SKIP] {link_name}: "
                f"no visual mesh"
            )
            continue

        mesh_path = resolve_mesh_path(
            mesh_filename,
            input_urdf,
        )

        if not os.path.exists(mesh_path):
            print(
                f"[SKIP] {link_name}: "
                f"mesh not found: {mesh_path}"
            )
            continue

        try:
            mesh = load_mesh(mesh_path)
        except Exception as e:
            print(
                f"[ERROR] {link_name}: "
                f"failed loading mesh: {e}"
            )
            continue

        geometry_type = classify_link(
            link_name,
            mesh_filename,
        )

        _, _, center, dimensions = mesh_bounds(mesh)

        print(
            f"[{geometry_type.upper():8}] "
            f"{link_name:30} "
            f"size={dimensions}"
        )

        # Remove existing collision geometry
        remove_existing_collision(link)

        if geometry_type == "box":

            add_box_collision(
                link,
                center,
                dimensions,
            )

        elif geometry_type == "sphere":

            add_sphere_collision(
                link,
                center,
                dimensions,
            )

        elif geometry_type == "cylinder":

            radius, length, center, axis = \
                cylinder_dimensions(mesh)

            add_cylinder_collision(
                link,
                center,
                radius,
                length,
                axis,
            )

    # Pretty printing
    ET.indent(tree, space="  ")

    tree.write(
        output_urdf,
        encoding="utf-8",
        xml_declaration=True,
    )

    print()
    print(f"Written: {output_urdf}")


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Automatically add primitive collision "
            "geometry to a robot URDF based on meshes."
        )
    )

    parser.add_argument(
        "input",
        help="Input URDF",
    )

    parser.add_argument(
        "output",
        help="Output URDF",
    )

    args = parser.parse_args()

    process_urdf(
        args.input,
        args.output,
    )


if __name__ == "__main__":
    main()

