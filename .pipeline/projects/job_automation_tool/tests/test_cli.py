"""Tests for the CLI interface."""

import json
import subprocess
import sys
from pathlib import Path


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_JOB = FIXTURES_DIR / "sample_job.txt"
CLI = Path(__file__).parent.parent / "job_automation_tool" / "cli.py"


class TestCLIParse:
    def test_parse_subcommand_json(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "parse", str(SAMPLE_JOB), "--output", "json"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["title"] == "Senior Software Engineer"
        assert "TechCorp" in data["company"]
        assert "Python" in data["skills"]

    def test_parse_subcommand_text(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "parse", str(SAMPLE_JOB), "--output", "text"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Senior Software Engineer" in result.stdout
        assert "TechCorp" in result.stdout

    def test_parse_missing_file(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "parse", "/nonexistent/file.txt"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Error" in result.stderr

    def test_parse_stdin(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "parse", "-"],
            input="Dev\nCompany: Co",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["title"] == "Dev"
        assert data["company"] == "Co"


class TestCLIMatch:
    def test_match_subcommand_json(self):
        # Create a temporary candidate skills file
        skills_file = FIXTURES_DIR / "candidate_skills.txt"
        skills_file.write_text("Python\nDocker\nAWS\n")

        result = subprocess.run(
            [sys.executable, str(CLI), "match", str(SAMPLE_JOB), str(skills_file), "--output", "json"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "score" in data
        assert "matched_skills" in data
        assert "missing_skills" in data
        assert "salary_match" in data

    def test_match_subcommand_text(self):
        skills_file = FIXTURES_DIR / "candidate_skills.txt"
        skills_file.write_text("Python\nDocker\nAWS\n")

        result = subprocess.run(
            [sys.executable, str(CLI), "match", str(SAMPLE_JOB), str(skills_file), "--output", "text"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Match Score" in result.stdout

    def test_match_missing_job_file(self):
        skills_file = FIXTURES_DIR / "candidate_skills.txt"
        skills_file.write_text("Python\n")
        result = subprocess.run(
            [sys.executable, str(CLI), "match", "/nonexistent/job.txt", str(skills_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1

    def test_match_missing_candidate_file(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "match", str(SAMPLE_JOB), "/nonexistent/skills.txt"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1


class TestCLIHelp:
    def test_help_flag(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "parse" in result.stdout
        assert "match" in result.stdout

    def test_version_flag(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout
