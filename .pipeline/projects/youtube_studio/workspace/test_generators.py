"""Tests for content generators in YouTube Studio.

This module provides comprehensive tests for title, thumbnail, and keyword
generation functionality.
"""

import unittest
from config import SEOConfig
from title_generator import TitleGenerator
from thumbnail_generator import ThumbnailGenerator
from keyword_generator import KeywordGenerator, KeywordDatabase


class TestTitleGenerator(unittest.TestCase):
    """Test cases for TitleGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.seo_config = SEOConfig()
        self.generator = TitleGenerator(self.seo_config)
    
    def test_generate_title_balanced(self):
        """Test balanced title generation."""
        title = self.generator.generate_title(
            "Learn Python Programming",
            keywords=['python', 'tutorial'],
            style='balanced'
        )
        self.assertIn('Python', title)
        self.assertLessEqual(len(title), self.seo_config.max_title_length)
    
    def test_generate_title_clicky(self):
        """Test clicky title generation."""
        title = self.generator.generate_title(
            "Python Tutorial",
            keywords=[],
            style='clicky'
        )
        # Clicky titles should be shorter and more engaging
        self.assertLess(len(title), 50)
    
    def test_generate_title_descriptive(self):
        """Test descriptive title generation."""
        title = self.generator.generate_title(
            "Complete Python Programming Course for Beginners",
            keywords=['python', 'programming'],
            style='descriptive'
        )
        # Descriptive titles should be longer
        self.assertGreater(len(title), 60)
    
    def test_generate_title_with_keywords(self):
        """Test title generation with keywords."""
        title = self.generator.generate_title(
            "Python Tutorial",
            keywords=['python', 'beginner', 'tutorial'],
            style='balanced'
        )
        # Should include at least one keyword
        self.assertTrue(any(kw in title.lower() for kw in ['python', 'tutorial']))
    
    def test_generate_title_empty_input(self):
        """Test title generation with empty input."""
        title = self.generator.generate_title("", keywords=[], style='balanced')
        self.assertTrue(len(title) > 0)


class TestThumbnailGenerator(unittest.TestCase):
    """Test cases for ThumbnailGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ThumbnailGenerator()
    
    def test_generate_thumbnail_metadata(self):
        """Test thumbnail metadata generation."""
        metadata = self.generator.generate_thumbnail_metadata(
            "Test Video Title",
            style='bold',
            size='large'
        )
        
        self.assertEqual(metadata['style'], 'bold')
        self.assertEqual(metadata['size'], 'large')
        self.assertIn('color_scheme', metadata)
        self.assertIn('layout', metadata)
    
    def test_generate_thumbnail_default_style(self):
        """Test thumbnail with default style."""
        metadata = self.generator.generate_thumbnail_metadata("Test")
        self.assertEqual(metadata['style'], 'bold')
    
    def test_generate_thumbnail_invalid_style(self):
        """Test thumbnail with invalid style."""
        with self.assertRaises(ValueError):
            self.generator.generate_thumbnail_metadata(
                "Test",
                style='invalid_style'
            )
    
    def test_generate_thumbnail_invalid_size(self):
        """Test thumbnail with invalid size."""
        with self.assertRaises(ValueError):
            self.generator.generate_thumbnail_metadata(
                "Test",
                size='invalid_size'
            )


class TestKeywordGenerator(unittest.TestCase):
    """Test cases for KeywordGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = KeywordGenerator()
    
    def test_generate_keywords_basic(self):
        """Test basic keyword generation."""
        keywords = self.generator.generate_keywords(
            "Python programming tutorial for beginners",
            category='general',
            count=5
        )
        
        self.assertEqual(len(keywords), 5)
        self.assertTrue(all(len(kw['keyword']) > 0 for kw in keywords))
    
    def test_generate_keywords_with_category(self):
        """Test keyword generation with category."""
        keywords = self.generator.generate_keywords(
            "Python tutorial",
            category='technology',
            count=5
        )
        
        self.assertEqual(len(keywords), 5)
    
    def test_generate_keywords_relevance_scores(self):
        """Test keyword generation with relevance scores."""
        keywords = self.generator.generate_keywords(
            "Python programming",
            category='technology',
            count=5
        )
        
        # Each keyword should have a relevance score
        for kw_dict in keywords:
            self.assertIn('keyword', kw_dict)
            self.assertIn('score', kw_dict)
            self.assertIsInstance(kw_dict['score'], float)
            self.assertGreaterEqual(kw_dict['score'], 0)
            self.assertLessEqual(kw_dict['score'], 1)
    
    def test_generate_keyword_limit(self):
        """Test keyword generation respects count limit."""
        keywords = self.generator.generate_keywords(
            "Test content",
            category='general',
            count=10
        )
        
        self.assertEqual(len(keywords), 10)
    
    def test_generate_keywords_empty_content(self):
        """Test keyword generation with empty content."""
        keywords = self.generator.generate_keywords(
            "",
            category='general',
            count=5
        )
        
        self.assertEqual(len(keywords), 5)
        self.assertTrue(all(len(kw['keyword']) > 0 for kw in keywords))


class TestKeywordDatabase(unittest.TestCase):
    """Test cases for KeywordDatabase class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = KeywordDatabase()
    
    def test_add_keyword(self):
        """Test adding a keyword."""
        result = self.db.add_keyword("test keyword", "test_category")
        
        self.assertTrue(result)
        self.assertIn("test keyword", self.db.get_keywords("test_category"))
    
    def test_add_custom_keyword(self):
        """Test adding custom keyword."""
        result = self.db.add_keyword("custom", "custom_category")
        
        self.assertTrue(result)
        self.assertIn("custom", self.db.get_keywords("custom_category"))
    
    def test_remove_keyword(self):
        """Test removing a keyword."""
        self.db.add_keyword("remove me", "test_category")
        
        result = self.db.remove_keyword("remove me", "test_category")
        
        self.assertTrue(result)
        self.assertNotIn("remove me", self.db.get_keywords("test_category"))
    
    def test_get_keyword_relevance(self):
        """Test getting keyword relevance."""
        relevance = self.db.get_keyword_relevance("python")
        self.assertIsInstance(relevance, float)
        self.assertGreaterEqual(relevance, 0)
        self.assertLessEqual(relevance, 1)
    
    def test_get_keyword_relevance_unknown(self):
        """Test getting relevance for unknown keyword."""
        relevance = self.db.get_keyword_relevance("unknown_keyword_xyz")
        self.assertEqual(relevance, 0.0)
    
    def test_get_keywords(self):
        """Test getting keywords for a category."""
        keywords = self.db.get_keywords("technology")
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
    
    def test_search_keywords(self):
        """Test searching keywords."""
        results = self.db.search_keywords("python")
        
        self.assertIsInstance(results, list)
    
    def test_export_import_database(self):
        """Test exporting and importing database."""
        # Add custom keyword
        self.db.add_keyword("custom", "custom_category")
        
        # Export
        exported = self.db.export_database()
        
        # Import to new database
        new_db = KeywordDatabase()
        new_db.import_database(exported)
        
        # Verify custom keyword was imported
        self.assertIn("custom", new_db.get_keywords("custom_category"))


if __name__ == '__main__':
    unittest.main()