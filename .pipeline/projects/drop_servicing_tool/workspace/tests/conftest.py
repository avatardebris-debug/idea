"""Shared fixtures for all tests."""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------------------
# tmp_dir fixture — explicitly named so test files can request it
# ---------------------------------------------------------------------------
@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    """Return a fresh temporary directory path for each test."""
    return tmp_path


# ---------------------------------------------------------------------------
# _tmp_env autouse fixture — isolates all DST backing stores
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _tmp_env(tmp_path: Path):
    """Put all DST backing stores under *tmp_path* for every test.

    Also copies the real SOP files (blog_post.yaml) and prompt templates
    into the temporary directories so that tests which rely on
    ``get_sop("blog_post")`` or ``load_prompt_template("default_step")``
    don't hit ``FileNotFoundError``.
    """
    # --- backing-store paths ---
    sops_dir = tmp_path / "sops"
    prompts_dir = tmp_path / "prompts"
    output_dir = tmp_path / "output"
    bulk_dir = tmp_path / "bulk"
    agents_dir = tmp_path / "agents"
    templates_dir = tmp_path / "templates"

    for d in (sops_dir, prompts_dir, output_dir, bulk_dir, agents_dir, templates_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Set env vars
    os.environ["DST_SOPS_DIR"] = str(sops_dir)
    os.environ["DST_PROMPTS_DIR"] = str(prompts_dir)
    os.environ["DST_OUTPUT_DIR"] = str(output_dir)
    os.environ["DST_BULK_BASE_DIR"] = str(bulk_dir)
    os.environ["DST_AGENTS_DIR"] = str(agents_dir)
    os.environ["DST_TEMPLATES_DIR"] = str(templates_dir)

    # --- Copy real SOP files ---
    real_sops_dir = Path(__file__).resolve().parent.parent / "sops"
    if real_sops_dir.is_dir():
        for f in real_sops_dir.glob("*.yaml"):
            shutil.copy2(f, sops_dir / f.name)

    # --- Copy real prompt templates ---
    real_prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    if real_prompts_dir.is_dir():
        for f in real_prompts_dir.glob("*.md"):
            shutil.copy2(f, prompts_dir / f.name)

    yield

    # cleanup env
    for key in (
        "DST_SOPS_DIR",
        "DST_PROMPTS_DIR",
        "DST_OUTPUT_DIR",
        "DST_BULK_BASE_DIR",
        "DST_AGENTS_DIR",
        "DST_TEMPLATES_DIR",
    ):
        os.environ.pop(key, None)
