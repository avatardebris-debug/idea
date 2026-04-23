"""Tests for udemy_training_tool.recommender module."""

import pytest
from udemy_training_tool.models import Course
from udemy_training_tool.recommender import (
    recommend_courses,
    compare_courses,
    _skill_match,
    _score_course,
    _normalize_student_count,
    _normalize_price,
    _normalize_lectures,
    _score_instructor,
)


class TestSkillMatch:
    """Tests for the _skill_match function."""

    def test_match_in_title(self):
        """Test skill match in course title."""
        course = Course(title="Python Bootcamp", description="")
        assert _skill_match(course, "Python") is True

    def test_match_in_description(self):
        """Test skill match in course description."""
        course = Course(title="Coding", description="Learn Python programming")
        assert _skill_match(course, "Python") is True

    def test_match_in_tags(self):
        """Test skill match in course tags."""
        course = Course(title="Coding", description="", tags=["python", "programming"])
        assert _skill_match(course, "Python") is True

    def test_match_in_category(self):
        """Test skill match in course category."""
        course = Course(title="Coding", description="", category="Python Development")
        assert _skill_match(course, "Python") is True

    def test_no_match(self):
        """Test no match when skill is not found."""
        course = Course(title="Java Bootcamp", description="Learn Java")
        assert _skill_match(course, "Python") is False

    def test_case_insensitive(self):
        """Test skill match is case insensitive."""
        course = Course(title="Python Bootcamp", description="")
        assert _skill_match(course, "python") is True
        assert _skill_match(course, "PYTHON") is True

    def test_empty_target_skill(self):
        """Test empty target skill returns True."""
        course = Course(title="Any Course", description="")
        assert _skill_match(course, "") is True

    def test_partial_match(self):
        """Test partial word match."""
        course = Course(title="Python Programming", description="")
        assert _skill_match(course, "Python") is True

    def test_match_multiple_words(self):
        """Test match with multi-word skill."""
        course = Course(title="Python Programming", description="")
        assert _skill_match(course, "Python Programming") is True

    def test_match_instructor_name(self):
        """Test skill match does NOT match instructor name (by design)."""
        course = Course(title="Coding", description="", instructor="Python Jones")
        assert _skill_match(course, "Python") is False  # instructor not searched


class TestNormalizeStudentCount:
    """Tests for the _normalize_student_count function."""

    def test_zero_students(self):
        """Test zero students returns median imputation."""
        assert _normalize_student_count(0) == 50.0

    def test_negative_students(self):
        """Test negative students returns median imputation."""
        assert _normalize_student_count(-100) == 50.0

    def test_one_student(self):
        """Test one student returns low score."""
        score = _normalize_student_count(1)
        assert 0 < score < 50

    def test_max_students(self):
        """Test max students returns 100."""
        assert _normalize_student_count(1_000_000) == 100.0

    def test_over_max_students(self):
        """Test over max students returns 100."""
        assert _normalize_student_count(2_000_000) == 100.0

    def test_mid_range(self):
        """Test mid-range student count."""
        score = _normalize_student_count(100_000)
        assert 50 < score < 100

    def test_monotonic(self):
        """Test that score increases with student count."""
        s1 = _normalize_student_count(100)
        s2 = _normalize_student_count(1000)
        s3 = _normalize_student_count(10000)
        assert s1 < s2 < s3


class TestNormalizePrice:
    """Tests for the _normalize_price function."""

    def test_free_course(self):
        """Test free course returns max score."""
        assert _normalize_price(0) == 100.0

    def test_negative_price(self):
        """Test negative price returns max score."""
        assert _normalize_price(-10) == 100.0

    def test_max_price(self):
        """Test max price returns 0 score."""
        assert _normalize_price(200.0) == 0.0

    def test_over_max_price(self):
        """Test over max price returns 0 score."""
        assert _normalize_price(300.0) == 0.0

    def test_mid_price(self):
        """Test mid-range price."""
        score = _normalize_price(100.0)
        assert 0 < score < 100

    def test_monotonic(self):
        """Test that score decreases with price."""
        s1 = _normalize_price(10.0)
        s2 = _normalize_price(50.0)
        s3 = _normalize_price(100.0)
        assert s1 > s2 > s3


class TestNormalizeLectures:
    """Tests for the _normalize_lectures function."""

    def test_zero_lectures(self):
        """Test zero lectures returns median imputation."""
        assert _normalize_lectures(0) == 50.0

    def test_negative_lectures(self):
        """Test negative lectures returns median imputation."""
        assert _normalize_lectures(-10) == 50.0

    def test_one_lecture(self):
        """Test one lecture returns low score."""
        score = _normalize_lectures(1)
        assert 0 < score < 50

    def test_max_lectures(self):
        """Test max lectures returns 100."""
        assert _normalize_lectures(500) == 100.0

    def test_over_max_lectures(self):
        """Test over max lectures returns 100."""
        assert _normalize_lectures(600) == 100.0

    def test_mid_range(self):
        """Test mid-range lecture count."""
        score = _normalize_lectures(250)
        assert 50 < score < 100

    def test_monotonic(self):
        """Test that score increases with lecture count."""
        s1 = _normalize_lectures(10)
        s2 = _normalize_lectures(100)
        s3 = _normalize_lectures(250)
        assert s1 < s2 < s3


class TestScoreInstructor:
    """Tests for the _score_instructor function."""

    def test_empty_instructor(self):
        """Test empty instructor returns median imputation."""
        assert _score_instructor("") == 50.0

    def test_none_instructor(self):
        """Test None instructor returns median imputation."""
        assert _score_instructor(None) == 50.0  # type: ignore

    def test_short_name(self):
        """Test short instructor name returns low score."""
        score = _score_instructor("A")
        assert 0 < score < 50

    def test_medium_name(self):
        """Test medium instructor name returns mid score."""
        score = _score_instructor("John Doe")
        assert 50 < score < 100

    def test_long_name(self):
        """Test long instructor name returns high score."""
        score = _score_instructor("John Doe Smith")
        assert 80 < score < 100

    def test_very_long_name(self):
        """Test very long instructor name returns max score."""
        score = _score_instructor("A" * 30)
        assert score == 100.0

    def test_whitespace_only(self):
        """Test whitespace-only instructor name."""
        score = _score_instructor("   ")
        assert score == 50.0  # stripped length is 0


class TestScoreCourse:
    """Tests for the _score_course function."""

    @pytest.fixture
    def sample_course(self):
        """Create a sample course for testing."""
        return Course(
            title="Python Bootcamp",
            instructor="Angela Yu",
            rating=4.7,
            num_students=620000,
            price=12.99,
            level="All Levels",
            category="Development",
            tags=["python", "programming"],
            duration="42 hours",
            num_lectures=380,
            description="Learn Python from scratch",
        )

    def test_score_course_returns_dict(self, sample_course):
        """Test _score_course returns a dict with correct keys."""
        result = _score_course(sample_course)
        assert "course" in result
        assert "score" in result
        assert "breakdown" in result
        assert result["course"] == sample_course

    def test_score_course_breakdown_keys(self, sample_course):
        """Test breakdown has correct keys."""
        result = _score_course(sample_course)
        breakdown = result["breakdown"]
        assert "rating" in breakdown
        assert "students" in breakdown
        assert "price_value" in breakdown
        assert "depth" in breakdown
        assert "instructor" in breakdown

    def test_score_course_rating_component(self, sample_course):
        """Test rating component score."""
        result = _score_course(sample_course)
        # rating 4.7 / 5 * 100 = 94
        assert result["breakdown"]["rating"] == pytest.approx(94.0, abs=0.1)

    def test_score_course_total_score(self, sample_course):
        """Test total score is reasonable."""
        result = _score_course(sample_course)
        assert 0 <= result["score"] <= 100

    def test_score_course_zero_rating(self):
        """Test score with zero rating."""
        course = Course(title="Test", instructor="Instructor", rating=0)
        result = _score_course(course)
        assert result["breakdown"]["rating"] == 0.0

    def test_score_course_free_price(self):
        """Test score with free course."""
        course = Course(title="Test", instructor="Instructor", rating=4.0, price=0)
        result = _score_course(course)
        assert result["breakdown"]["price_value"] == 100.0

    def test_score_course_max_lectures(self):
        """Test score with max lectures."""
        course = Course(title="Test", instructor="Instructor", rating=4.0, num_lectures=500)
        result = _score_course(course)
        assert result["breakdown"]["depth"] == 100.0

    def test_score_course_zero_students(self):
        """Test score with zero students."""
        course = Course(title="Test", instructor="Instructor", rating=4.0, num_students=0)
        result = _score_course(course)
        assert result["breakdown"]["students"] == 50.0


class TestRecommendCourses:
    """Tests for the recommend_courses function."""

    @pytest.fixture
    def sample_courses(self):
        """Create a list of sample courses for testing."""
        return [
            Course(
                title="Python Bootcamp",
                instructor="Angela Yu",
                rating=4.7,
                num_students=620000,
                price=12.99,
                level="All Levels",
                category="Development",
                tags=["python", "programming"],
                duration="42 hours",
                num_lectures=380,
                description="Learn Python from scratch",
            ),
            Course(
                title="Java Programming",
                instructor="Tim Buchalka",
                rating=4.5,
                num_students=300000,
                price=9.99,
                level="Intermediate",
                category="Development",
                tags=["java", "programming"],
                duration="22 hours",
                num_lectures=200,
                description="Master Java",
            ),
            Course(
                title="Data Science with Python",
                instructor="Jose Portilla",
                rating=4.6,
                num_students=450000,
                price=14.99,
                level="All Levels",
                category="Data Science",
                tags=["python", "data science", "pandas"],
                duration="22 hours",
                num_lectures=150,
                description="Learn data science",
            ),
            Course(
                title="Web Development Bootcamp",
                instructor="Angela Yu",
                rating=4.8,
                num_students=800000,
                price=11.99,
                level="All Levels",
                category="Web Development",
                tags=["web", "html", "css", "javascript"],
                duration="44 hours",
                num_lectures=420,
                description="Full stack web development",
            ),
            Course(
                title="Machine Learning A-Z",
                instructor="Kirill Eremenko",
                rating=4.4,
                num_students=500000,
                price=13.99,
                level="All Levels",
                category="Data Science",
                tags=["machine learning", "python", "ai"],
                duration="44 hours",
                num_lectures=350,
                description="Learn machine learning",
            ),
        ]

    def test_recommend_returns_list(self, sample_courses):
        """Test recommend_courses returns a list."""
        results = recommend_courses(sample_courses, "Python")
        assert isinstance(results, list)

    def test_recommend_empty_courses(self):
        """Test recommend_courses with empty course list."""
        results = recommend_courses([], "Python")
        assert results == []

    def test_recommend_top_n(self, sample_courses):
        """Test recommend_courses respects top_n parameter."""
        results = recommend_courses(sample_courses, "Python", top_n=3)
        assert len(results) == 3

    def test_recommend_default_top_n(self, sample_courses):
        """Test recommend_courses default top_n is 5."""
        results = recommend_courses(sample_courses, "Python")
        assert len(results) == 5

    def test_recommend_sorted_by_score(self, sample_courses):
        """Test recommend_courses returns results sorted by score descending."""
        results = recommend_courses(sample_courses, "Python")
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_recommend_matches_target_skill(self, sample_courses):
        """Test recommend_courses filters by target skill."""
        results = recommend_courses(sample_courses, "Python")
        titles = [r["course"].title for r in results]
        # Should include Python-related courses
        assert "Python Bootcamp" in titles
        assert "Data Science with Python" in titles
        assert "Machine Learning A-Z" in titles

    def test_recommend_no_match_uses_all(self, sample_courses):
        """Test recommend_courses uses all courses when no match."""
        results = recommend_courses(sample_courses, "Rust")
        assert len(results) == 5
        titles = [r["course"].title for r in results]
        assert "Java Programming" in titles

    def test_recommend_returns_correct_keys(self, sample_courses):
        """Test recommend_courses returns dicts with correct keys."""
        results = recommend_courses(sample_courses, "Python")
        for result in results:
            assert "course" in result
            assert "score" in result
            assert "breakdown" in result

    def test_recommend_score_range(self, sample_courses):
        """Test recommend_courses scores are in valid range."""
        results = recommend_courses(sample_courses, "Python")
        for result in results:
            assert 0 <= result["score"] <= 100

    def test_recommend_tie_breaking_rating(self):
        """Test recommend_courses tie-breaking by rating."""
        courses = [
            Course(title="Course A", instructor="Instructor", rating=4.5, price=10.0),
            Course(title="Course B", instructor="Instructor", rating=4.5, price=10.0),
        ]
        results = recommend_courses(courses, "", top_n=2)
        # Both have same score, so tie-break by rating (same), then price (same)
        # Order should be stable
        assert len(results) == 2

    def test_recommend_tie_breaking_price(self):
        """Test recommend_courses tie-breaking by price."""
        courses = [
            Course(title="Course A", instructor="Instructor", rating=4.5, price=15.0),
            Course(title="Course B", instructor="Instructor", rating=4.5, price=10.0),
        ]
        results = recommend_courses(courses, "", top_n=2)
        # Course B has lower price, so should come first
        assert results[0]["course"].title == "Course B"

    def test_recommend_breakdown_has_all_components(self, sample_courses):
        """Test recommend_courses breakdown has all component scores."""
        results = recommend_courses(sample_courses, "Python")
        for result in results:
            breakdown = result["breakdown"]
            assert "rating" in breakdown
            assert "students" in breakdown
            assert "price_value" in breakdown
            assert "depth" in breakdown
            assert "instructor" in breakdown

    def test_recommend_breakdown_values_valid(self, sample_courses):
        """Test recommend_courses breakdown values are in valid range."""
        results = recommend_courses(sample_courses, "Python")
        for result in results:
            for key, value in result["breakdown"].items():
                assert 0 <= value <= 100

    def test_recommend_single_course(self):
        """Test recommend_courses with single course."""
        courses = [Course(title="Test", instructor="Instructor", rating=4.0)]
        results = recommend_courses(courses, "Test")
        assert len(results) == 1

    def test_recommend_large_top_n(self):
        """Test recommend_courses with top_n larger than course count."""
        courses = [Course(title="Test", instructor="Instructor", rating=4.0)]
        results = recommend_courses(courses, "Test", top_n=100)
        assert len(results) == 1

    def test_recommend_zero_top_n(self):
        """Test recommend_courses with top_n=0."""
        courses = [Course(title="Test", instructor="Instructor", rating=4.0)]
        results = recommend_courses(courses, "Test", top_n=0)
        assert results == []

    def test_recommend_preserves_course_object(self, sample_courses):
        """Test recommend_courses preserves original course objects."""
        original = sample_courses[0]
        results = recommend_courses(sample_courses, "Python")
        for result in results:
            if result["course"].title == original.title:
                assert result["course"] is original


class TestCompareCourses:
    """Tests for the compare_courses function."""

    @pytest.fixture
    def sample_courses(self):
        """Create a list of sample courses for testing."""
        return [
            Course(
                title="Python Bootcamp",
                instructor="Angela Yu",
                rating=4.7,
                num_students=620000,
                price=12.99,
                level="All Levels",
                category="Development",
                tags=["python", "programming"],
                duration="42 hours",
                num_lectures=380,
                description="Learn Python from scratch",
            ),
            Course(
                title="Java Programming",
                instructor="Tim Buchalka",
                rating=4.5,
                num_students=300000,
                price=9.99,
                level="Intermediate",
                category="Development",
                tags=["java", "programming"],
                duration="22 hours",
                num_lectures=200,
                description="Master Java",
            ),
            Course(
                title="Data Science with Python",
                instructor="Jose Portilla",
                rating=4.6,
                num_students=450000,
                price=14.99,
                level="All Levels",
                category="Data Science",
                tags=["python", "data science", "pandas"],
                duration="22 hours",
                num_lectures=150,
                description="Learn data science",
            ),
        ]

    def test_compare_returns_list(self, sample_courses):
        """Test compare_courses returns a list."""
        results = compare_courses(sample_courses)
        assert isinstance(results, list)

    def test_compare_empty_courses(self):
        """Test compare_courses with empty course list."""
        results = compare_courses([])
        assert results == []

    def test_compare_all_courses(self, sample_courses):
        """Test compare_courses returns all courses."""
        results = compare_courses(sample_courses)
        assert len(results) == len(sample_courses)

    def test_compare_sorted_by_score(self, sample_courses):
        """Test compare_courses returns results sorted by score descending."""
        results = compare_courses(sample_courses)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_compare_with_target_skill(self, sample_courses):
        """Test compare_courses with target skill."""
        results = compare_courses(sample_courses, target_skill="Python")
        assert len(results) == len(sample_courses)

    def test_compare_returns_correct_keys(self, sample_courses):
        """Test compare_courses returns dicts with correct keys."""
        results = compare_courses(sample_courses)
        for result in results:
            assert "course" in result
            assert "score" in result
            assert "breakdown" in result

    def test_compare_score_range(self, sample_courses):
        """Test compare_courses scores are in valid range."""
        results = compare_courses(sample_courses)
        for result in results:
            assert 0 <= result["score"] <= 100

    def test_compare_breakdown_has_all_components(self, sample_courses):
        """Test compare_courses breakdown has all component scores."""
        results = compare_courses(sample_courses)
        for result in results:
            breakdown = result["breakdown"]
            assert "rating" in breakdown
            assert "students" in breakdown
            assert "price_value" in breakdown
            assert "depth" in breakdown
            assert "instructor" in breakdown

    def test_compare_breakdown_values_valid(self, sample_courses):
        """Test compare_courses breakdown values are in valid range."""
        results = compare_courses(sample_courses)
        for result in results:
            for key, value in result["breakdown"].items():
                assert 0 <= value <= 100

    def test_compare_single_course(self):
        """Test compare_courses with single course."""
        courses = [Course(title="Test", instructor="Instructor", rating=4.0)]
        results = compare_courses(courses)
        assert len(results) == 1

    def test_compare_preserves_course_object(self, sample_courses):
        """Test compare_courses preserves original course objects."""
        original = sample_courses[0]
        results = compare_courses(sample_courses)
        for result in results:
            if result["course"].title == original.title:
                assert result["course"] is original

    def test_compare_empty_target_skill(self, sample_courses):
        """Test compare_courses with empty target skill."""
        results = compare_courses(sample_courses, target_skill="")
        assert len(results) == len(sample_courses)

    def test_compare_none_target_skill(self, sample_courses):
        """Test compare_courses with None target skill."""
        results = compare_courses(sample_courses, target_skill=None)  # type: ignore
        assert len(results) == len(sample_courses)

    def test_compare_tie_breaking(self):
        """Test compare_courses tie-breaking."""
        courses = [
            Course(title="Course A", instructor="Instructor", rating=4.5, price=15.0),
            Course(title="Course B", instructor="Instructor", rating=4.5, price=10.0),
        ]
        results = compare_courses(courses)
        # Course B has lower price, so should come first
        assert results[0]["course"].title == "Course B"
