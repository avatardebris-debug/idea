"""Comprehensive tests for SOP store operations."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from drop_servicing_tool.sop_store import (
    get_sop,
    save_sop,
    list_sops,
    delete_sop,
    get_sop_path,
    _get_sops_dir,
)


@pytest.fixture(autouse=True)
def _tmp_sops_dir(tmp_path: Path):
    """Set up a temporary SOPs directory for each test."""
    original_dir = os.environ.get("DST_SOPS_DIR")
    os.environ["DST_SOPS_DIR"] = str(tmp_path)
    yield tmp_path
    if original_dir:
        os.environ["DST_SOPS_DIR"] = original_dir
    else:
        os.environ.pop("DST_SOPS_DIR", None)


def _create_sop_file(sops_dir: Path, name: str, **kwargs) -> Path:
    """Helper to create a SOP YAML file."""
    sop_data = {
        "name": name,
        "description": f"SOP for {name}",
        "inputs": [{"name": "topic", "type": "string", "required": True}],
        "steps": [
            {
                "name": "step1",
                "description": "First step",
                "prompt_template": "default_step",
                "output_key": "step1_output",
            }
        ],
        "output_format": "string",
        **kwargs,
    }
    path = sops_dir / f"{name}.yaml"
    path.write_text(yaml.dump(sop_data), encoding="utf-8")
    return path


class TestGetSopsDir:
    """Tests for _get_sops_dir function."""

    def test_get_sops_dir_from_env(self, tmp_path):
        """Test getting SOPs directory from environment variable."""
        os.environ["DST_SOPS_DIR"] = str(tmp_path)
        assert _get_sops_dir() == tmp_path

    def test_get_sops_dir_default(self):
        """Test default SOPs directory when env var not set."""
        os.environ.pop("DST_SOPS_DIR", None)
        # Should return a valid Path object
        result = _get_sops_dir()
        assert isinstance(result, Path)


class TestGetSop:
    """Tests for get_sop function."""

    def test_get_existing_sop(self, tmp_path):
        """Test retrieving an existing SOP."""
        _create_sop_file(tmp_path, "test_sop")
        sop = get_sop("test_sop")
        assert sop.name == "test_sop"
        assert len(sop.steps) == 1

    def test_get_nonexistent_sop(self, tmp_path):
        """Test retrieving a non-existent SOP raises error."""
        with pytest.raises(FileNotFoundError, match="not found"):
            get_sop("nonexistent")

    def test_get_sop_with_custom_fields(self, tmp_path):
        """Test retrieving SOP with custom fields."""
        sop_data = {
            "name": "custom",
            "description": "Custom SOP",
            "inputs": [{"name": "topic", "type": "string", "required": True}],
            "steps": [],
            "output_format": "json",
        }
        path = tmp_path / "custom.yaml"
        path.write_text(yaml.dump(sop_data), encoding="utf-8")
        sop = get_sop("custom")
        assert sop.output_format == "json"


class TestSaveSop:
    """Tests for save_sop function."""

    def test_save_new_sop(self, tmp_path):
        """Test saving a new SOP."""
        from drop_servicing_tool.sop_schema import SOP, SOPInput, Step

        sop = SOP(
            name="new_sop",
            description="New SOP",
            inputs=[SOPInput(name="topic", type="string", required=True)],
            steps=[
                Step(
                    name="analyze",
                    description="Analyze",
                    prompt_template="default_step",
                    output_key="analysis",
                )
            ],
            output_format="analysis",
        )
        save_sop(sop)
        assert (tmp_path / "new_sop.yaml").exists()

    def test_save_overwrite_sop(self, tmp_path):
        """Test saving an SOP overwrites existing file."""
        from drop_servicing_tool.sop_schema import SOP, SOPInput, Step

        # Create initial SOP
        initial_sop = SOP(
            name="overwrite",
            description="Initial",
            inputs=[SOPInput(name="topic", type="string", required=True)],
            steps=[],
        )
        save_sop(initial_sop)

        # Overwrite with new SOP
        new_sop = SOP(
            name="overwrite",
            description="Overwritten",
            inputs=[SOPInput(name="topic", type="string", required=True)],
            steps=[
                Step(
                    name="step1",
                    description="Step",
                    prompt_template="default_step",
                    output_key="out",
                )
            ],
        )
        save_sop(new_sop)

        # Verify overwrite
        sop = get_sop("overwrite")
        assert sop.description == "Overwritten"
        assert len(sop.steps) == 1

    def test_save_sop_creates_directory(self, tmp_path):
        """Test that save_sop creates the SOPs directory if it doesn't exist."""
        from drop_servicing_tool.sop_schema import SOP, SOPInput, Step

        # Remove the directory
        import shutil
        shutil.rmtree(tmp_path)

        sop = SOP(
            name="new_sop",
            description="New SOP",
            inputs=[SOPInput(name="topic", type="string", required=True)],
            steps=[],
        )
        save_sop(sop)
        assert (tmp_path / "new_sop.yaml").exists()


class TestListSops:
    """Tests for list_sops function."""

    def test_list_sops_empty(self, tmp_path):
        """Test listing SOPs when directory is empty."""
        sops = list_sops()
        assert sops == []

    def test_list_sops_with_files(self, tmp_path):
        """Test listing SOPs with multiple files."""
        _create_sop_file(tmp_path, "sop1")
        _create_sop_file(tmp_path, "sop2")
        _create_sop_file(tmp_path, "sop3")

        sops = list_sops()
        assert len(sops) == 3
        assert "sop1" in sops
        assert "sop2" in sops
        assert "sop3" in sops

    def test_list_sops_excludes_non_yaml(self, tmp_path):
        """Test that list_sops only returns .yaml files."""
        _create_sop_file(tmp_path, "sop1")
        # Create a non-YAML file
        (tmp_path / "readme.txt").write_text("Not a SOP")
        (tmp_path / "sop2.yaml.bak").write_text("Backup")

        sops = list_sops()
        assert len(sops) == 1
        assert sops[0] == "sop1"


class TestDeleteSop:
    """Tests for delete_sop function."""

    def test_delete_existing_sop(self, tmp_path):
        """Test deleting an existing SOP."""
        _create_sop_file(tmp_path, "to_delete")
        result = delete_sop("to_delete")
        assert result is True
        assert not (tmp_path / "to_delete.yaml").exists()

    def test_delete_nonexistent_sop(self, tmp_path):
        """Test deleting a non-existent SOP."""
        result = delete_sop("nonexistent")
        assert result is False

    def test_delete_sop_removes_file(self, tmp_path):
        """Test that delete_sop actually removes the file."""
        _create_sop_file(tmp_path, "remove_test")
        delete_sop("remove_test")
        assert not (tmp_path / "remove_test.yaml").exists()


class TestGetSopPath:
    """Tests for get_sop_path function."""

    def test_get_path_existing_sop(self, tmp_path):
        """Test getting path for existing SOP."""
        _create_sop_file(tmp_path, "path_test")
        path = get_sop_path("path_test")
        assert path.exists()
        assert path.name == "path_test.yaml"

    def test_get_path_nonexistent_sop(self, tmp_path):
        """Test getting path for non-existent SOP."""
        path = get_sop_path("nonexistent")
        assert path is None

    def test_get_path_returns_path_object(self, tmp_path):
        """Test that get_sop_path returns a Path object."""
        _create_sop_file(tmp_path, "path_test")
        path = get_sop_path("path_test")
        assert isinstance(path, Path)
