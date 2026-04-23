"""Tests for udemy_training_tool.models module."""

import pytest
from udemy_training_tool.models import Course, Lesson, Module, LearningPath


class TestLesson:
    """Tests for the Lesson dataclass."""

    def test_from_dict_basic(self):
        """Test Lesson.from_dict with basic data."""
        data = {"title": "Intro to Python", "duration": "10:30", "type": "video"}
        lesson = Lesson.from_dict(data)
        assert lesson.title == "Intro to Python"
        assert lesson.duration == "10:30"
        assert lesson.lesson_type == "video"

    def test_from_dict_defaults(self):
        """Test Lesson.from_dict with empty dict uses defaults."""
        lesson = Lesson.from_dict({})
        assert lesson.title == ""
        assert lesson.duration == ""
        assert lesson.lesson_type == "video"

    def test_to_dict_basic(self):
        """Test Lesson.to_dict produces correct dict."""
        lesson = Lesson(title="Test", duration="5:00", lesson_type="quiz")
        d = lesson.to_dict()
        assert d == {"title": "Test", "duration": "5:00", "type": "quiz"}

    def test_to_dict_defaults(self):
        """Test Lesson.to_dict with defaults."""
        lesson = Lesson()
        d = lesson.to_dict()
        assert d == {"title": "", "duration": "", "type": "video"}


class TestModule:
    """Tests for the Module dataclass."""

    def test_from_dict_basic(self):
        """Test Module.from_dict with basic data."""
        data = {
            "title": "Basics",
            "order": 1,
            "num_lectures": 10,
            "lessons": [
                {"title": "L1", "duration": "5:00", "type": "video"}
            ],
        }
        mod = Module.from_dict(data)
        assert mod.title == "Basics"
        assert mod.order == 1
        assert mod.num_lectures == 10
        assert len(mod.lessons) == 1
        assert mod.lessons[0].title == "L1"

    def test_from_dict_defaults(self):
        """Test Module.from_dict with empty dict uses defaults."""
        mod = Module.from_dict({})
        assert mod.title == ""
        assert mod.order == 0
        assert mod.num_lectures == 0
        assert mod.lessons == []

    def test_to_dict_basic(self):
        """Test Module.to_dict produces correct dict."""
        mod = Module(title="Test", order=1, num_lectures=5)
        d = mod.to_dict()
        assert d["title"] == "Test"
        assert d["order"] == 1
        assert d["num_lectures"] == 5
        assert d["lessons"] == []

    def test_to_dict_with_lessons(self):
        """Test Module.to_dict with lessons."""
        mod = Module(title="Test", order=1, num_lectures=1)
        mod.lessons.append(Lesson(title="L1", duration="5:00"))
        d = mod.to_dict()
        assert len(d["lessons"]) == 1
        assert d["lessons"][0]["title"] == "L1"


class TestCourse:
    """Tests for the Course dataclass."""

    def test_from_dict_basic(self):
        """Test Course.from_dict with basic data."""
        data = {
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
            "description": "Learn Python",
            "language": "English",
        }
        course = Course.from_dict(data)
        assert course.title == "Python Bootcamp"
        assert course.instructor == "Angela Yu"
        assert course.rating == 4.7
        assert course.num_students == 620000
        assert course.price == 12.99
        assert course.level == "All Levels"
        assert course.category == "Development"
        assert course.tags == ["python", "programming"]
        assert course.duration == "42 hours"
        assert course.num_lectures == 380
        assert course.description == "Learn Python"
        assert course.language == "English"

    def test_from_dict_defaults(self):
        """Test Course.from_dict with empty dict uses defaults."""
        course = Course.from_dict({})
        assert course.title == ""
        assert course.instructor == ""
        assert course.rating == 0.0
        assert course.num_students == 0
        assert course.price == 0.0
        assert course.level == "All Levels"
        assert course.category == ""
        assert course.tags == []
        assert course.duration == ""
        assert course.num_lectures == 0
        assert course.description == ""
        assert course.language == "English"
        assert course.modules == []

    def test_to_dict_basic(self):
        """Test Course.to_dict produces correct dict."""
        course = Course(title="Test", instructor="Instructor", rating=4.5)
        d = course.to_dict()
        assert d["title"] == "Test"
        assert d["instructor"] == "Instructor"
        assert d["rating"] == 4.5
        assert d["modules"] == []

    def test_validate_valid(self):
        """Test Course.validate passes with valid data."""
        course = Course(title="Test", instructor="Instructor", rating=4.5)
        course.validate()  # Should not raise

    def test_validate_missing_title(self):
        """Test Course.validate raises on missing title."""
        course = Course(instructor="Instructor", rating=4.5)
        with pytest.raises(ValueError, match="title"):
            course.validate()

    def test_validate_missing_instructor(self):
        """Test Course.validate raises on missing instructor."""
        course = Course(title="Test", rating=4.5)
        with pytest.raises(ValueError, match="instructor"):
            course.validate()

    def test_validate_missing_rating(self):
        """Test Course.validate raises on zero rating."""
        course = Course(title="Test", instructor="Instructor")
        with pytest.raises(ValueError, match="rating"):
            course.validate()

    def test_validate_missing_multiple(self):
        """Test Course.validate raises on multiple missing fields."""
        course = Course()
        with pytest.raises(ValueError, match="title"):
            course.validate()

    def test_matches_query_exact(self):
        """Test Course.matches_query with exact match."""
        course = Course(title="Python Bootcamp", description="Learn Python", tags=["python"])
        assert course.matches_query("Python") is True

    def test_matches_query_partial(self):
        """Test Course.matches_query with partial word match."""
        course = Course(title="Python Bootcamp", description="Learn Python", tags=["python"])
        assert course.matches_query("Boot") is True

    def test_matches_query_case_insensitive(self):
        """Test Course.matches_query is case insensitive."""
        course = Course(title="Python Bootcamp", description="Learn Python", tags=["python"])
        assert course.matches_query("python") is True
        assert course.matches_query("PYTHON") is True

    def test_matches_query_no_match(self):
        """Test Course.matches_query returns False on no match."""
        course = Course(title="Java Bootcamp", description="Learn Java", tags=["java"])
        assert course.matches_query("Python") is False

    def test_matches_query_multiple_words(self):
        """Test Course.matches_query with multiple words (all must match)."""
        course = Course(title="Python Bootcamp", description="Learn Python", tags=["python"])
        assert course.matches_query("Python Bootcamp") is True
        assert course.matches_query("Python Java") is False

    def test_matches_query_empty(self):
        """Test Course.matches_query with empty query returns True."""
        course = Course(title="Test")
        assert course.matches_query("") is True

    def test_matches_filters_rating(self):
        """Test Course.matches_filters with min_rating."""
        course = Course(rating=4.5)
        assert course.matches_filters(min_rating=4.0) is True
        assert course.matches_filters(min_rating=5.0) is False

    def test_matches_filters_price(self):
        """Test Course.matches_filters with max_price."""
        course = Course(price=12.99)
        assert course.matches_filters(max_price=15.0) is True
        assert course.matches_filters(max_price=10.0) is False

    def test_matches_filters_level(self):
        """Test Course.matches_filters with level."""
        course = Course(level="All Levels")
        assert course.matches_filters(level="All Levels") is True
        assert course.matches_filters(level="Beginner") is False

    def test_matches_filters_category(self):
        """Test Course.matches_filters with category."""
        course = Course(category="Development")
        assert course.matches_filters(category="Development") is True
        assert course.matches_filters(category="Data Science") is False

    def test_matches_filters_combined(self):
        """Test Course.matches_filters with multiple filters."""
        course = Course(rating=4.5, price=12.99, level="All Levels", category="Development")
        assert course.matches_filters(
            min_rating=4.0, max_price=15.0, level="All Levels", category="Development"
        ) is True
        assert course.matches_filters(min_rating=5.0) is False


class TestLearningPath:
    """Tests for the LearningPath dataclass."""

    def test_from_dict_basic(self):
        """Test LearningPath.from_dict with basic data."""
        data = {
            "title": "Python Path",
            "courses": [
                {"title": "Course 1", "instructor": "Instructor", "rating": 4.5}
            ],
            "target_skill": "Python",
            "estimated_hours": 40.0,
            "difficulty": "Beginner",
        }
        path = LearningPath.from_dict(data)
        assert path.title == "Python Path"
        assert path.target_skill == "Python"
        assert path.estimated_hours == 40.0
        assert path.difficulty == "Beginner"
        assert len(path.courses) == 1

    def test_from_dict_defaults(self):
        """Test LearningPath.from_dict with empty dict uses defaults."""
        path = LearningPath.from_dict({})
        assert path.title == ""
        assert path.courses == []
        assert path.target_skill == ""
        assert path.estimated_hours == 0.0
        assert path.difficulty == "Beginner"

    def test_to_dict_basic(self):
        """Test LearningPath.to_dict produces correct dict."""
        path = LearningPath(title="Test", target_skill="Python")
        d = path.to_dict()
        assert d["title"] == "Test"
        assert d["target_skill"] == "Python"
        assert d["estimated_hours"] == 0.0
        assert d["difficulty"] == "Beginner"
        assert d["courses"] == []

    def test_compute_estimated_hours_hours(self):
        """Test compute_estimated_hours with hour strings."""
        path = LearningPath(
            courses=[
                Course(duration="10 hours"),
                Course(duration="20 hours"),
            ]
        )
        total = path.compute_estimated_hours()
        assert total == 30.0

    def test_compute_estimated_hours_minutes(self):
        """Test compute_estimated_hours with minute strings."""
        path = LearningPath(
            courses=[
                Course(duration="60 minutes"),
            ]
        )
        total = path.compute_estimated_hours()
        assert total == 1.0

    def test_compute_estimated_hours_empty(self):
        """Test compute_estimated_hours with empty duration."""
        path = LearningPath(courses=[Course(duration="")])
        total = path.compute_estimated_hours()
        assert total == 0.0

    def test_compute_estimated_hours_mixed(self):
        """Test compute_estimated_hours with mixed duration formats."""
        path = LearningPath(
            courses=[
                Course(duration="10 hours"),
                Course(duration="30 minutes"),
            ]
        )
        total = path.compute_estimated_hours()
        assert total == 10.5

    def test_parse_duration_invalid(self):
        """Test _parse_duration with invalid string."""
        assert LearningPath._parse_duration("invalid") == 0.0
        assert LearningPath._parse_duration("") == 0.0
        assert LearningPath._parse_duration(None) == 0.0  # type: ignore
