"""Tests for udemy_training_tool.search module."""

import pytest
from udemy_training_tool.models import Course
from udemy_training_tool.search import search_courses


class TestSearchCourses:
    """Tests for the search_courses function."""

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

    def test_search_basic(self, sample_courses):
        """Test basic search returns matching courses."""
        results = search_courses(sample_courses, query="Python")
        assert len(results) == 3
        titles = [c.title for c in results]
        assert "Python Bootcamp" in titles
        assert "Data Science with Python" in titles
        assert "Machine Learning A-Z" in titles

    def test_search_no_results(self, sample_courses):
        """Test search with no matching courses."""
        results = search_courses(sample_courses, query="Rust")
        assert results == []

    def test_search_case_insensitive(self, sample_courses):
        """Test search is case insensitive."""
        results_lower = search_courses(sample_courses, query="python")
        results_upper = search_courses(sample_courses, query="PYTHON")
        assert len(results_lower) == len(results_upper)
        assert [c.title for c in results_lower] == [c.title for c in results_upper]

    def test_search_partial_match(self, sample_courses):
        """Test search with partial word match."""
        results = search_courses(sample_courses, query="Boot")
        assert len(results) == 2
        titles = [c.title for c in results]
        assert "Python Bootcamp" in titles
        assert "Web Development Bootcamp" in titles

    def test_search_multiple_words(self, sample_courses):
        """Test search with multiple words (all must match)."""
        results = search_courses(sample_courses, query="Python Data")
        assert len(results) == 1
        assert results[0].title == "Data Science with Python"

    def test_search_empty_query(self, sample_courses):
        """Test search with empty query returns all courses."""
        results = search_courses(sample_courses, query="")
        assert len(results) == len(sample_courses)

    def test_search_min_rating(self, sample_courses):
        """Test search with min_rating filter."""
        results = search_courses(sample_courses, query="", min_rating=4.7)
        assert len(results) == 2
        titles = [c.title for c in results]
        assert "Python Bootcamp" in titles
        assert "Web Development Bootcamp" in titles

    def test_search_max_price(self, sample_courses):
        """Test search with max_price filter."""
        results = search_courses(sample_courses, query="", max_price=12.0)
        assert len(results) == 2
        titles = [c.title for c in results]
        assert "Java Programming" in titles
        assert "Web Development Bootcamp" in titles

    def test_search_level_filter(self, sample_courses):
        """Test search with level filter."""
        results = search_courses(sample_courses, query="", level="All Levels")
        assert len(results) == 4
        titles = [c.title for c in results]
        assert "Java Programming" not in titles

    def test_search_category_filter(self, sample_courses):
        """Test search with category filter."""
        results = search_courses(sample_courses, query="", category="Data Science")
        assert len(results) == 2
        titles = [c.title for c in results]
        assert "Data Science with Python" in titles
        assert "Machine Learning A-Z" in titles

    def test_search_combined_filters(self, sample_courses):
        """Test search with multiple filters."""
        results = search_courses(
            sample_courses,
            query="Python",
            min_rating=4.5,
            max_price=15.0,
            level="All Levels",
            category="Data Science",
        )
        assert len(results) == 1
        assert results[0].title == "Data Science with Python"

    def test_search_combined_filters_no_results(self, sample_courses):
        """Test search with filters that return no results."""
        results = search_courses(
            sample_courses,
            query="Python",
            min_rating=4.9,
        )
        assert results == []

    def test_search_tags(self, sample_courses):
        """Test search matches tags."""
        results = search_courses(sample_courses, query="pandas")
        assert len(results) == 1
        assert results[0].title == "Data Science with Python"

    def test_search_instructor(self, sample_courses):
        """Test search matches instructor name."""
        results = search_courses(sample_courses, query="Angela")
        assert len(results) == 2
        titles = [c.title for c in results]
        assert "Python Bootcamp" in titles
        assert "Web Development Bootcamp" in titles

    def test_search_description(self, sample_courses):
        """Test search matches description."""
        results = search_courses(sample_courses, query="scratch")
        assert len(results) == 1
        assert results[0].title == "Python Bootcamp"

    def test_search_empty_courses(self):
        """Test search with empty course list."""
        results = search_courses([], query="Python")
        assert results == []

    def test_search_none_query(self, sample_courses):
        """Test search with None query returns all courses."""
        results = search_courses(sample_courses, query=None)
        assert len(results) == len(sample_courses)

    def test_search_none_min_rating(self, sample_courses):
        """Test search with None min_rating (no filter)."""
        results = search_courses(sample_courses, query="", min_rating=None)
        assert len(results) == len(sample_courses)

    def test_search_none_max_price(self, sample_courses):
        """Test search with None max_price (no filter)."""
        results = search_courses(sample_courses, query="", max_price=None)
        assert len(results) == len(sample_courses)

    def test_search_none_level(self, sample_courses):
        """Test search with None level (no filter)."""
        results = search_courses(sample_courses, query="", level=None)
        assert len(results) == len(sample_courses)

    def test_search_none_category(self, sample_courses):
        """Test search with None category (no filter)."""
        results = search_courses(sample_courses, query="", category=None)
        assert len(results) == len(sample_courses)

    def test_search_exact_title_match(self, sample_courses):
        """Test search with exact title match."""
        results = search_courses(sample_courses, query="Java Programming")
        assert len(results) == 1
        assert results[0].title == "Java Programming"

    def test_search_special_characters(self, sample_courses):
        """Test search with special characters in query."""
        results = search_courses(sample_courses, query="A-Z")
        assert len(results) == 1
        assert results[0].title == "Machine Learning A-Z"

    def test_search_unicode(self, sample_courses):
        """Test search with unicode characters."""
        results = search_courses(sample_courses, query="Python")
        assert len(results) == 3

    def test_search_preserves_order(self, sample_courses):
        """Test search preserves original order of matching courses."""
        results = search_courses(sample_courses, query="Python")
        titles = [c.title for c in results]
        assert titles.index("Python Bootcamp") < titles.index("Data Science with Python")
        assert titles.index("Data Science with Python") < titles.index("Machine Learning A-Z")

    def test_search_rating_boundary(self, sample_courses):
        """Test search with rating at boundary."""
        results = search_courses(sample_courses, query="", min_rating=4.6)
        assert len(results) == 3
        titles = [c.title for c in results]
        assert "Python Bootcamp" in titles
        assert "Data Science with Python" in titles
        assert "Web Development Bootcamp" in titles

    def test_search_price_boundary(self, sample_courses):
        """Test search with price at boundary."""
        results = search_courses(sample_courses, query="", max_price=12.99)
        assert len(results) == 3
        titles = [c.title for c in results]
        assert "Python Bootcamp" in titles
        assert "Java Programming" in titles
        assert "Web Development Bootcamp" in titles

    def test_search_level_exact_match(self, sample_courses):
        """Test search with exact level match."""
        results = search_courses(sample_courses, query="", level="Intermediate")
        assert len(results) == 1
        assert results[0].title == "Java Programming"

    def test_search_category_exact_match(self, sample_courses):
        """Test search with exact category match."""
        results = search_courses(sample_courses, query="", category="Development")
        assert len(results) == 2
        titles = [c.title for c in results]
        assert "Python Bootcamp" in titles
        assert "Java Programming" in titles
