"""Tests for the CLI interface."""

import subprocess
import sys
import pytest
from pathlib import Path


@pytest.fixture
def workspace_path() -> Path:
    """Get the workspace path."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_job_file(workspace_path: Path) -> Path:
    """Get path to sample job file."""
    return workspace_path / "tests" / "fixtures" / "sample_job.txt"


@pytest.fixture
def sample_candidate_file(workspace_path: Path) -> Path:
    """Get path to sample candidate skills file."""
    return workspace_path / "tests" / "fixtures" / "sample_candidate_skills.txt"


class TestCLI:
    """Tests for CLI functionality."""

    def test_cli_help(self):
        """Test that --help works."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode == 0
        assert "usage" in result.stdout.lower()

    def test_cli_parse_subcommand(self, sample_job_file: Path):
        """Test the parse subcommand."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli", "parse", str(sample_job_file)],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert "title" in data
        assert "company" in data
        assert "skills" in data

    def test_cli_parse_json_output(self, sample_job_file: Path):
        """Test parse subcommand with JSON output."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli", "parse", str(sample_job_file), "--output", "json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_cli_parse_text_output(self, sample_job_file: Path):
        """Test parse subcommand with text output."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli", "parse", str(sample_job_file), "--output", "text"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode == 0
        assert "Title:" in result.stdout
        assert "Company:" in result.stdout

    def test_cli_match_subcommand(self, sample_job_file: Path, sample_candidate_file: Path):
        """Test the match subcommand."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli", "match",
             str(sample_job_file), str(sample_candidate_file)],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert "score" in data
        assert "matched_skills" in data
        assert "missing_skills" in data

    def test_cli_match_json_output(self, sample_job_file: Path, sample_candidate_file: Path):
        """Test match subcommand with JSON output."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli", "match",
             str(sample_job_file), str(sample_candidate_file), "--output", "json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert isinstance(data["score"], int)

    def test_cli_match_text_output(self, sample_job_file: Path, sample_candidate_file: Path):
        """Test match subcommand with text output."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli", "match",
             str(sample_job_file), str(sample_candidate_file), "--output", "text"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode == 0
        assert "Match Score:" in result.stdout
        assert "Matched Skills:" in result.stdout

    def test_cli_no_command(self):
        """Test running CLI without a command."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode == 0
        assert "usage" in result.stdout.lower()

    def test_cli_parse_nonexistent_file(self):
        """Test parse subcommand with nonexistent file."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli", "parse", "/nonexistent/file.txt"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode != 0

    def test_cli_match_nonexistent_file(self):
        """Test match subcommand with nonexistent file."""
        result = subprocess.run(
            [sys.executable, "-m", "job_automation_tool.cli", "match",
             "/nonexistent/job.txt", "/nonexistent/candidate.txt"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode != 0
