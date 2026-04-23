"""SOP Store — Filesystem-based CRUD for SOP YAML files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .config import get_sops_dir
from .sop_schema import SOP, load_sop


def list_sops(sops_dir: Path | None = None) -> list[str]:
    """Return sorted list of SOP names (without .yaml extension)."""
    sops_dir = sops_dir or get_sops_dir()
    if not sops_dir.exists():
        return []
    return sorted(p.stem for p in sops_dir.glob("*.yaml"))


def get_sop_path(name: str, sops_dir: Path | None = None) -> Path:
    """Return the full path to an SOP YAML file."""
    sops_dir = sops_dir or get_sops_dir()
    return sops_dir / f"{name}.yaml"


def get_sop(name: str, sops_dir: Path | None = None) -> SOP:
    """Load and validate an SOP by name."""
    path = get_sop_path(name, sops_dir)
    return load_sop(path)


def create_sop(
    name: str,
    yaml_content: str | dict,
    sops_dir: Path | None = None,
) -> Path:
    """Write a new SOP YAML file.

    Args:
        name:       SOP name (used as filename stem).
        yaml_content:  Raw YAML string or a dict that will be dumped to YAML.
        sops_dir:     Override the default SOPs directory.

    Returns:
        The path to the created file.
    """
    sops_dir = sops_dir or get_sops_dir()
    sops_dir.mkdir(parents=True, exist_ok=True)
    path = sops_dir / f"{name}.yaml"

    if isinstance(yaml_content, dict):
        import yaml as _yaml
        content = _yaml.dump(yaml_content, default_flow_style=False, sort_keys=False)
    else:
        content = yaml_content

    path.write_text(content, encoding="utf-8")
    return path


def delete_sop(name: str, sops_dir: Path | None = None) -> bool:
    """Remove an SOP file. Returns True if it existed, False otherwise."""
    sops_dir = sops_dir or get_sops_dir()
    path = get_sop_path(name, sops_dir)
    if path.exists():
        path.unlink()
        return True
    return False
