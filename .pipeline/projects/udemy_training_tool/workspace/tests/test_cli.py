"""Tests for udemy_training_tool.cli module."""

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest
from udemy_training_tool.cli import (
    _build_parser,
    _format_text_comparison,
    _format_text_courses,
    _format_text_recommendations,
    _load_courses,
    _parse_courses,
    cli,
)
from udemy_training_tool.models import Course


class TestParseCourses:
    """Tests for the _parse_courses function."""

    def test_parse_json_array(self):
        """Test parsing JSON array."""
        data = json.dumps([
            {"title": "Course 1", "instructor": "Instructor", "rating": 4.5, "price": 10.0},
            {"title": "Course 2", "instructor": "Instructor", "rating": 4.0, "price": 15.0},
        ])
        courses = _parse_courses(data)
        assert len(courses) == 2
        assert courses[0].title == "Course 1"
        assert courses[1].title == "Course 2"

    def test_parse_json_object(self):
        """Test parsing single JSON object."""
        data = json.dumps({"title": "Course 1", "instructor": "Instructor", "rating": 4.5, "price": 10.0})
        courses = _parse_courses(data)
        assert len(courses) == 1
        assert courses[0].title == "Course 1"

    def test_parse_jsonl(self):
        """Test parsing JSONL format."""
        data = """{"title": "Course 1", "instructor": "Instructor", "rating": 4.5, "price": 10.0}
{"title": "Course 2", "instructor": "Instructor", "rating": 4.0, "price": 15.0}"""
        courses = _parse_courses(data)
        assert len(courses) == 2
        assert courses[0].title == "Course 1"
        assert courses[1].title == "Course 2"

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        courses = _parse_courses("")
        assert courses == []

    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only string."""
        courses = _parse_courses("   \n  \t  ")
        assert courses == []

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON returns empty list."""
        courses = _parse_courses("not valid json")
        assert courses == []

    def test_parse_mixed_valid_invalid(self):
        """Test parsing mixed valid and invalid JSONL."""
        data = """{"title": "Course 1", "instructor": "Instructor", "rating": 4.5, "price": 10.0}
invalid json
{"title": "Course 2", "instructor": "Instructor", "rating": 4.0, "price": 15.0}"""
        courses = _parse_courses(data)
        assert len(courses) == 2
        assert courses[0].title == "Course 1"
        assert courses[1].title == "Course 2"

    def test_parse_missing_required_fields(self):
        """Test parsing course with missing required fields."""
        data = json.dumps({"title": "Course 1"})
        courses = _parse_courses(data)
        assert len(courses) == 1
        # Missing fields should have default values
        assert courses[0].rating == 0.0
        assert courses[0].price == 0.0


class TestLoadCourses:
    """Tests for the _load_courses function."""

    @pytest.fixture
    def sample_json_file(self, tmp_path):
        """Create a temporary JSON file with sample courses."""
        file_path = tmp_path / "courses.json"
        file_path.write_text(json.dumps([
            {"title": "Course 1", "instructor": "Instructor", "rating": 4.5, "price": 10.0},
        ]))
        return str(file_path)

    def test_load_from_file(self, sample_json_file):
        """Test loading courses from file."""
        courses = _load_courses(sample_json_file)
        assert len(courses) == 1
        assert courses[0].title == "Course 1"

    def test_load_nonexistent_file(self, tmp_path, capsys):
        """Test loading from nonexistent file exits with error."""
        with pytest.raises(SystemExit):
            _load_courses(str(tmp_path / "nonexistent.json"))
        captured = capsys.readouterr()
        assert "Error: File not found" in captured.err

    def test_load_from_stdin(self, monkeypatch):
        """Test loading courses from stdin."""
        monkeypatch.setattr("sys.stdin", StringIO('{"title": "Course 1", "instructor": "Instructor", "rating": 4.5, "price": 10.0}'))
        courses = _load_courses(None)
        assert len(courses) == 1
        assert courses[0].title == "Course 1"


class TestFormatTextCourses:
    """Tests for the _format_text_courses function."""

    def test_format_empty_courses(self):
        """Test formatting empty course list."""
        result = _format_text_courses([])
        assert result == "No courses found."

    def test_format_single_course(self):
        """Test formatting single course."""
        courses = [Course(title="Test Course", instructor="Instructor", rating=4.5, price=10.0)]
        result = _format_text_courses(courses)
        assert "Test Course" in result
        assert "Instructor" in result
        assert "4.5/5" in result
        assert "$10.00" in result

    def test_format_multiple_courses(self):
        """Test formatting multiple courses."""
        courses = [
            Course(title="Course 1", instructor="Instructor 1", rating=4.5, price=10.0),
            Course(title="Course 2", instructor="Instructor 2", rating=4.0, price=15.0),
        ]
        result = _format_text_courses(courses)
        assert result.count("Course 1") == 1
        assert result.count("Course 2") == 1


class TestFormatTextRecommendations:
    """Tests for the _format_text_recommendations function."""

    def test_format_empty_recommendations(self):
        """Test formatting empty recommendations."""
        result = _format_text_recommendations([])
        assert result == "No recommendations found."

    def test_format_single_recommendation(self):
        """Test formatting single recommendation."""
        course = Course(title="Test Course", instructor="Instructor", rating=4.5, price=10.0)
        recommendations = [{
            "course": course,
            "score": 85.5,
            "breakdown": {
                "rating": 4.5,
                "students": 50.0,
                "price_value": 80.0,
                "depth": 90.0,
                "instructor": 75.0,
            }
        }]
        result = _format_text_recommendations(recommendations)
        assert "Test Course" in result
        assert "Score: 85.5/100" in result


class TestFormatTextComparison:
    """Tests for the _format_text_comparison function."""

    def test_format_empty_comparison(self):
        """Test formatting empty comparison."""
        result = _format_text_comparison([])
        assert result == "No courses to compare."

    def test_format_single_comparison(self):
        """Test formatting single comparison."""
        course = Course(title="Test Course", instructor="Instructor", rating=4.5, price=10.0)
        comparisons = [{
            "course": course,
            "score": 85.5,
            "breakdown": {
                "rating": 4.5,
                "students": 50.0,
                "price_value": 80.0,
                "depth": 90.0,
                "instructor": 75.0,
            }
        }]
        result = _format_text_comparison(comparisons)
        assert "Test Course" in result
        assert "Score: 85.5/100" in result


class TestBuildParser:
    """Tests for the _build_parser function."""

    def test_parser_exists(self):
        """Test that parser is created."""
        parser = _build_parser()
        assert parser is not None

    def test_version_flag(self):
        """Test version flag is available."""
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])

    def test_search_subcommand(self):
        """Test search subcommand is available."""
        parser = _build_parser()
        args = parser.parse_args(["search", "file.json", "-q", "test"])
        assert args.command == "search"
        assert args.query == "test"

    def test_compare_subcommand(self):
        """Test compare subcommand is available."""
        parser = _build_parser()
        args = parser.parse_args(["compare", "file.json", "--ids", "1", "2"])
        assert args.command == "compare"
        assert args.ids == [1, 2]

    def test_recommend_subcommand(self):
        """Test recommend subcommand is available."""
        parser = _build_parser()
        args = parser.parse_args(["recommend", "file.json", "-s", "python"])
        assert args.command == "recommend"
        assert args.skill == "python"

    def test_no_command_shows_help(self):
        """Test that no command shows help."""
        parser = _build_parser()
        # When no command is given, parse_args succeeds but returns default values
        args = parser.parse_args([])
        assert args.command is None


class TestCLI:
    """Tests for the cli function."""

    @pytest.fixture
    def sample_courses_json(self):
        """Sample courses as JSON string."""
        return json.dumps([
            {
                "title": "Python Bootcamp",
                "instructor": "Angela Yu",
                "rating": 4.7,
                "num_students": 620000,
                "price": 12.99,
                "level": "All Levels",
                "category": "Development",
                "tags": ["python", "programming"],
                "duration": "42 hours",
                "num_lectures": 380,
                "description": "Learn Python from scratch",
            },
            {
                "title": "Java Programming",
                "instructor": "Tim Buchalka",
                "rating": 4.5,
                "num_students": 300000,
                "price": 9.99,
                "level": "Intermediate",
                "category": "Development",
                "tags": ["java", "programming"],
                "duration": "22 hours",
                "num_lectures": 200,
                "description": "Master Java",
            },
        ])

    @pytest.fixture
    def courses_file(self, tmp_path, sample_courses_json):
        """Create a temporary file with sample courses."""
        file_path = tmp_path / "courses.json"
        file_path.write_text(sample_courses_json)
        return str(file_path)

    def test_cli_no_command(self, capsys):
        """Test CLI with no command shows help."""
        result = cli([])
        assert result == 1
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()

    def test_cli_search_command(self, courses_file, capsys):
        """Test search command."""
        result = cli(["search", courses_file, "-q", "Python"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Python Bootcamp" in captured.out

    def test_cli_search_json_output(self, courses_file, capsys):
        """Test search command with JSON output."""
        result = cli(["search", courses_file, "-q", "Python", "-o", "json"])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 1
        assert data[0]["title"] == "Python Bootcamp"

    def test_cli_search_min_rating(self, courses_file, capsys):
        """Test search with min_rating filter."""
        result = cli(["search", courses_file, "-q", "", "--min-rating", "4.6"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Python Bootcamp" in captured.out
        assert "Java Programming" not in captured.out

    def test_cli_search_max_price(self, courses_file, capsys):
        """Test search with max_price filter."""
        result = cli(["search", courses_file, "-q", "", "--max-price", "10.00"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Java Programming" in captured.out
        assert "Python Bootcamp" not in captured.out

    def test_cli_compare_command(self, courses_file, capsys):
        """Test compare command."""
        result = cli(["compare", courses_file, "--ids", "1", "2"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Python Bootcamp" in captured.out
        assert "Java Programming" in captured.out

    def test_cli_compare_with_skill(self, courses_file, capsys):
        """Test compare command with skill filter."""
        result = cli(["compare", courses_file, "--ids", "1", "--skill", "Python"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Python Bootcamp" in captured.out

    def test_cli_compare_json_output(self, courses_file, capsys):
        """Test compare command with JSON output."""
        result = cli(["compare", courses_file, "--ids", "1", "-o", "json"])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 1
        assert "score" in data[0]
        assert "breakdown" in data[0]

    def test_cli_recommend_command(self, courses_file, capsys):
        """Test recommend command."""
        result = cli(["recommend", courses_file, "-s", "Python", "--top-n", "2"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Python Bootcamp" in captured.out

    def test_cli_recommend_json_output(self, courses_file, capsys):
        """Test recommend command with JSON output."""
        result = cli(["recommend", courses_file, "-s", "Python", "-o", "json"])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) > 0
        assert "score" in data[0]
        assert "breakdown" in data[0]

    def test_cli_invalid_file(self, capsys):
        """Test CLI with invalid file path."""
        with pytest.raises(SystemExit):
            cli(["search", "nonexistent.json", "-q", "test"])
        captured = capsys.readouterr()
        assert "Error: File not found" in captured.err

    def test_cli_invalid_course_ids(self, courses_file, capsys):
        """Test compare command with invalid course IDs."""
        result = cli(["compare", courses_file, "--ids", "999"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Error: No valid course IDs" in captured.err

    def test_cli_version_flag(self, capsys):
        """Test version flag."""
        with pytest.raises(SystemExit):
            cli(["--version"])

    def test_cli_search_level_filter(self, courses_file, capsys):
        """Test search with level filter."""
        result = cli(["search", courses_file, "-q", "", "--level", "Intermediate"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Java Programming" in captured.out
        assert "Python Bootcamp" not in captured.out

    def test_cli_search_category_filter(self, courses_file, capsys):
        """Test search with category filter."""
        result = cli(["search", courses_file, "-q", "", "--category", "Development"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Python Bootcamp" in captured.out
        assert "Java Programming" in captured.out

    def test_cli_search_combined_filters(self, courses_file, capsys):
        """Test search with combined filters."""
        result = cli([
            "search", courses_file,
            "-q", "Python",
            "--min-rating", "4.6",
            "--level", "All Levels",
        ])
        assert result == 0
        captured = capsys.readouterr()
        assert "Python Bootcamp" in captured.out
        assert "Java Programming" not in captured.out

    def test_cli_search_no_results(self, courses_file, capsys):
        """Test search with no matching results."""
        result = cli(["search", courses_file, "-q", "Rust"])
        assert result == 0
        captured = capsys.readouterr()
        assert "No courses found" in captured.out

    def test_cli_compare_no_skill(self, courses_file, capsys):
        """Test compare command without skill filter."""
        result = cli(["compare", courses_file, "--ids", "1"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Python Bootcamp" in captured.out

    def test_cli_recommend_top_n(self, courses_file, capsys):
        """Test recommend command with top-n parameter."""
        result = cli(["recommend", courses_file, "-s", "Python", "--top-n", "1"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Python Bootcamp" in captured.out
