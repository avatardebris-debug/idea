"""Renderer module — 3D rendering loop with OpenGL via pyglet."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from src.camera import Camera, Vector3


@dataclass
class Vertex:
    """A single vertex with position and color."""
    x: float
    y: float
    z: float
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0
    a: float = 1.0


@dataclass
class Mesh:
    """A simple mesh defined by vertices and triangle indices."""
    vertices: List[Vertex] = field(default_factory=list)
    indices: List[int] = field(default_factory=list)
    name: str = ""

    def add_triangle(self, v0: Vertex, v1: Vertex, v2: Vertex) -> None:
        """Add a triangle to the mesh."""
        idx = len(self.vertices)
        self.vertices.extend([v0, v1, v2])
        self.indices.extend([idx, idx + 1, idx + 2])

    def add_quad(self, v0: Vertex, v1: Vertex, v2: Vertex, v3: Vertex) -> None:
        """Add a quad (two triangles) to the mesh."""
        self.add_triangle(v0, v1, v2)
        self.add_triangle(v0, v2, v3)

    def clear(self) -> None:
        """Clear all vertices and indices."""
        self.vertices.clear()
        self.indices.clear()


def create_box_mesh(
    width: float = 1.0,
    height: float = 1.0,
    depth: float = 0.05,
    color: tuple = (0.3, 0.3, 0.3, 1.0),
) -> Mesh:
    """Create a box mesh centered at origin."""
    w, h, d = width / 2, height / 2, depth / 2
    c = Vertex(0, 0, 0, *color)
    mesh = Mesh(name="box")

    # Front face
    mesh.add_quad(
        Vertex(-w, -h, d, *color),
        Vertex(w, -h, d, *color),
        Vertex(w, h, d, *color),
        Vertex(-w, h, d, *color),
    )
    # Back face
    mesh.add_quad(
        Vertex(w, -h, -d, *color),
        Vertex(-w, -h, -d, *color),
        Vertex(-w, h, -d, *color),
        Vertex(w, h, -d, *color),
    )
    # Top face
    mesh.add_quad(
        Vertex(-w, h, d, *color),
        Vertex(w, h, d, *color),
        Vertex(w, h, -d, *color),
        Vertex(-w, h, -d, *color),
    )
    # Bottom face
    mesh.add_quad(
        Vertex(-w, -h, -d, *color),
        Vertex(w, -h, -d, *color),
        Vertex(w, -h, d, *color),
        Vertex(-w, -h, d, *color),
    )
    # Right face
    mesh.add_quad(
        Vertex(w, -h, d, *color),
        Vertex(w, -h, -d, *color),
        Vertex(w, h, -d, *color),
        Vertex(w, h, d, *color),
    )
    # Left face
    mesh.add_quad(
        Vertex(-w, -h, -d, *color),
        Vertex(-w, -h, d, *color),
        Vertex(-w, h, d, *color),
        Vertex(-w, h, -d, *color),
    )
    return mesh


def create_plane_mesh(
    width: float = 10.0,
    depth: float = 10.0,
    color: tuple = (0.2, 0.2, 0.25, 1.0),
) -> Mesh:
    """Create a flat plane mesh centered at origin."""
    w, d = width / 2, depth / 2
    mesh = Mesh(name="plane")
    mesh.add_quad(
        Vertex(-w, 0, d, *color),
        Vertex(w, 0, d, *color),
        Vertex(w, 0, -d, *color),
        Vertex(-w, 0, -d, *color),
    )
    return mesh


def create_textured_quad_mesh(
    width: float = 1.0,
    height: float = 1.0,
    color: tuple = (1.0, 1.0, 1.0, 1.0),
) -> Mesh:
    """Create a simple quad (for ticker panels)."""
    w, h = width / 2, height / 2
    mesh = Mesh(name="quad")
    mesh.add_quad(
        Vertex(-w, -h, 0, *color),
        Vertex(w, -h, 0, *color),
        Vertex(w, h, 0, *color),
        Vertex(-w, h, 0, *color),
    )
    return mesh


class Renderer:
    """Manages the 3D rendering loop and scene drawing."""

    def __init__(self, camera: Camera):
        self.camera = camera
        self.meshes: List[Mesh] = []
        self.background_color: tuple = (0.05, 0.05, 0.1, 1.0)
        self.fog_enabled: bool = False
        self.fog_color: tuple = (0.05, 0.05, 0.1)
        self.fog_density: float = 0.02
        self.frame_count: int = 0
        self.fps: float = 0.0
        self._last_time: float = 0.0

    def add_mesh(self, mesh: Mesh, position: Optional[Vector3] = None,
                 rotation: Optional[tuple] = None) -> None:
        """Add a mesh to the scene."""
        self.meshes.append(mesh)

    def clear_meshes(self) -> None:
        """Remove all meshes from the scene."""
        self.meshes.clear()

    def set_background(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """Set the background color."""
        self.background_color = (r, g, b, a)

    def enable_fog(self, color: tuple = (0.05, 0.05, 0.1), density: float = 0.02) -> None:
        """Enable fog for depth effect."""
        self.fog_enabled = True
        self.fog_color = color
        self.fog_density = density

    def update(self, dt: float) -> None:
        """Update renderer state (FPS tracking)."""
        self.frame_count += 1
        if self._last_time > 0:
            elapsed = dt
            if elapsed > 0:
                self.fps = self.frame_count / elapsed
        else:
            self._last_time = dt

    def get_render_commands(self) -> List[dict]:
        """Generate render commands for the current frame."""
        commands = []
        view_matrix = self.camera.get_view_matrix()
        proj_matrix = self.camera.get_projection_matrix(1, 1)  # aspect handled by window

        for mesh in self.meshes:
            commands.append({
                "type": "mesh",
                "mesh": mesh,
                "view_matrix": view_matrix,
                "projection_matrix": proj_matrix,
            })

        if self.fog_enabled:
            commands.append({
                "type": "fog",
                "color": self.fog_color,
                "density": self.fog_density,
            })

        return commands

    def reset(self) -> None:
        """Reset renderer state."""
        self.frame_count = 0
        self.fps = 0.0
        self._last_time = 0.0
