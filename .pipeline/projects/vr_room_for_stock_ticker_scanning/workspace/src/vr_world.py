"""VR World — the main scene system that ties camera, renderer, and scene objects together."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import List, Optional

from src.camera import Camera, Vector3
from src.renderer import Mesh, Renderer, create_box_mesh, create_plane_mesh


@dataclass
class SceneObject:
    """A 3D object in the scene with position, rotation, and mesh."""
    mesh: Mesh
    position: Vector3 = field(default_factory=Vector3)
    rotation: tuple = (0.0, 0.0, 0.0)  # euler angles in radians
    scale: tuple = (1.0, 1.0, 1.0)
    visible: bool = True
    name: str = ""


@dataclass
class VRWorld:
    """The main VR room scene — manages camera, renderer, and scene objects."""

    # Room dimensions
    room_width: float = 10.0
    room_depth: float = 10.0
    room_height: float = 3.0

    # Components
    camera: Camera = field(default_factory=Camera)
    renderer: Optional[Renderer] = None

    # Scene objects
    objects: List[SceneObject] = field(default_factory=list)

    # State
    is_running: bool = False
    is_paused: bool = False
    frame_interval: float = 1.0 / 60.0  # target 60 FPS
    last_frame_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize the VR world with default room geometry."""
        if self.renderer is None:
            self.renderer = Renderer(self.camera)
        self._build_room()

    def _build_room(self) -> None:
        """Build the default VR room (floor, ceiling, walls)."""
        # Floor
        floor = create_plane_mesh(self.room_width, self.room_depth, color=(0.15, 0.15, 0.2, 1.0))
        self.objects.append(SceneObject(
            mesh=floor,
            position=Vector3(0, 0, 0),
            name="floor",
        ))

        # Ceiling
        ceiling = create_plane_mesh(self.room_width, self.room_depth, color=(0.1, 0.1, 0.15, 1.0))
        self.objects.append(SceneObject(
            mesh=ceiling,
            position=Vector3(0, self.room_height, 0),
            name="ceiling",
        ))

        # Back wall
        back_wall = create_plane_mesh(self.room_width, self.room_height, color=(0.12, 0.12, 0.18, 1.0))
        self.objects.append(SceneObject(
            mesh=back_wall,
            position=Vector3(0, self.room_height / 2, -self.room_depth / 2),
            name="back_wall",
        ))

        # Left wall
        left_wall = create_plane_mesh(self.room_depth, self.room_height, color=(0.12, 0.12, 0.18, 1.0))
        self.objects.append(SceneObject(
            mesh=left_wall,
            position=Vector3(-self.room_width / 2, self.room_height / 2, 0),
            rotation=(0, math.pi / 2, 0),
            name="left_wall",
        ))

        # Right wall
        right_wall = create_plane_mesh(self.room_depth, self.room_height, color=(0.12, 0.12, 0.18, 1.0))
        self.objects.append(SceneObject(
            mesh=right_wall,
            position=Vector3(self.room_width / 2, self.room_height / 2, 0),
            rotation=(0, math.pi / 2, 0),
            name="right_wall",
        ))

    def add_object(self, mesh: Mesh, position: Vector3, name: str = "") -> SceneObject:
        """Add a scene object to the VR world."""
        obj = SceneObject(mesh=mesh, position=position, name=name)
        self.objects.append(obj)
        return obj

    def remove_object(self, name: str) -> bool:
        """Remove a scene object by name."""
        for i, obj in enumerate(self.objects):
            if obj.name == name:
                self.objects.pop(i)
                return True
        return False

    def get_object(self, name: str) -> Optional[SceneObject]:
        """Get a scene object by name."""
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None

    def update(self, dt: float) -> None:
        """Update the VR world for one frame."""
        if self.is_paused:
            return
        self.renderer.update(dt)

    def start(self) -> None:
        """Start the VR world."""
        self.is_running = True
        self.is_paused = False
        self.last_frame_time = time.time()

    def stop(self) -> None:
        """Stop the VR world."""
        self.is_running = False

    def toggle_pause(self) -> None:
        """Toggle pause state."""
        self.is_paused = not self.is_paused

    def reset(self) -> None:
        """Reset the VR world to initial state."""
        self.camera.reset()
        self.renderer.reset()
        self.objects.clear()
        self._build_room()
        self.is_running = False
        self.is_paused = False

    def get_render_commands(self) -> List[dict]:
        """Get all render commands for the current frame."""
        return self.renderer.get_render_commands() if self.renderer else []

    def __repr__(self) -> str:
        return (
            f"VRWorld(room={self.room_width}x{self.room_height}x{self.room_depth}, "
            f"objects={len(self.objects)}, running={self.is_running})"
        )
