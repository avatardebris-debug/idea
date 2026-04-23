"""Integration tests for YouTube Studio.

This module provides end-to-end tests that verify all YouTube Studio
components work together correctly in realistic scenarios.
"""

import os
import tempfile
import unittest
from pathlib import Path

from studio_orchestrator import StudioOrchestrator
from config import YouTubeStudioConfig
from constants import MAX_TITLE_LENGTH, MAX_TAGS
from template_manager import TemplateManager
from template_engine import TemplateEngine


class TestEndToEndMetadataGeneration(unittest.TestCase):
    """Test complete metadata generation workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = StudioOrchestrator()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_complete_workflow(self):
        """Test complete metadata generation workflow."""
        input_data = {
            'title': 'Learn Python Programming from Scratch',
            'description': 'A comprehensive tutorial covering Python basics, variables, functions, and more.',
            'content': 'Python programming tutorial for beginners',
            'category': 'education',
            'keywords': ['python', 'programming', 'tutorial', 'beginner', 'learn']
        }
        
        metadata = self.orchestrator.generate_video_metadata(input_data)
        
        # Verify metadata structure
        self.assertIn('title', metadata)
        self.assertIn('description', metadata)
        self.assertIn('keywords', metadata)
        self.assertIn('seo_score', metadata)
        
        # Verify SEO score
        self.assertIsInstance(metadata['seo_score'], (int, float))
        self.assertGreaterEqual(metadata['seo_score'], 0)
        self.assertLessEqual(metadata['seo_score'], 100)
        
        # Verify title is optimized
        self.assertIn('Python', metadata['title'])
        self.assertLessEqual(len(metadata['title']), MAX_TITLE_LENGTH)
        
        # Verify keywords are optimized
        self.assertGreaterEqual(len(metadata['keywords']), 5)
    
    def test_batch_generation(self):
        """Test batch video metadata generation."""
        videos = [
            {
                'title': 'Python Tutorial',
                'description': 'Learn Python basics',
                'content': 'Python programming',
                'category': 'education'
            },
            {
                'title': 'JavaScript Basics',
                'description': 'Learn JavaScript from scratch',
                'content': 'JavaScript programming',
                'category': 'education'
            }
        ]
        
        # Generate metadata for each video
        results = []
        for video in videos:
            metadata = self.orchestrator.generate_video_metadata(video)
            results.append({
                'title': metadata['title'],
                'seo_score': metadata['seo_score'],
                'keywords': metadata['keywords']
            })
        
        self.assertEqual(len(results), 2)
        
        for result in results:
            # Verify each result has required fields
            self.assertIn('title', result)
            self.assertIn('seo_score', result)
            self.assertIn('keywords', result)
    
    def test_template_rendering(self):
        """Test template-based metadata generation."""
        input_data = {
            'title': 'Python Tutorial',
            'description': 'Learn Python',
            'content': 'Python programming',
            'category': 'education'
        }
        
        metadata = self.orchestrator.generate_video_metadata(input_data)
        
        # Create template engine and render
        engine = TemplateEngine()
        
        template = {
            'title': '{{title|upper}}',
            'description': 'Learn from {{author}} about {{topic}}',
            'tags': '{{keywords|join(", ")}}'
        }
        
        rendered = engine.render_template(template, metadata)
        
        self.assertIn('PYTHON TUTORIAL', rendered['title'])
        self.assertIn('Learn', rendered['description'])


class TestKeywordIntegration(unittest.TestCase):
    """Test keyword generation and optimization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = StudioOrchestrator()
    
    def test_keyword_generation_quality(self):
        """Test quality of generated keywords."""
        input_data = {
            'title': 'Python Tutorial',
            'description': 'Learn Python programming',
            'content': 'Python programming basics',
            'category': 'education'
        }
        
        metadata = self.orchestrator.generate_video_metadata(input_data)
        
        # Verify keywords are generated
        self.assertGreater(len(metadata['keywords']), 0)
        
        # Verify keywords are relevant
        for kw in metadata['keywords'][:5]:
            self.assertIsInstance(kw, str)
            self.assertGreater(len(kw), 0)
    
    def test_keyword_diversity(self):
        """Test keyword diversity in output."""
        input_data = {
            'title': 'Python Tutorial',
            'description': 'Learn Python',
            'content': 'Python programming tutorial',
            'category': 'education'
        }
        
        metadata = self.orchestrator.generate_video_metadata(input_data)
        
        # Verify keywords are diverse
        unique_keywords = set(metadata['keywords'])
        self.assertEqual(len(unique_keywords), len(metadata['keywords']))
    
    def test_keyword_relevance(self):
        """Test keyword relevance to content."""
        input_data = {
            'title': 'Python Programming Tutorial',
            'description': 'Learn Python programming',
            'content': 'Python programming',
            'category': 'education'
        }
        
        metadata = self.orchestrator.generate_video_metadata(input_data)
        
        # Verify 'python' or 'programming' appears in keywords
        keyword_text = ' '.join(metadata['keywords']).lower()
        self.assertTrue('python' in keyword_text or 'programming' in keyword_text)


class TestTemplateIntegration(unittest.TestCase):
    """Test template system integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.template_manager = TemplateManager(self.test_dir)
        self.template_engine = TemplateEngine()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_custom_template_loading(self):
        """Test loading custom templates."""
        # Create a custom template
        template_path = os.path.join(self.test_dir, 'custom.json')
        with open(template_path, 'w') as f:
            f.write('{"title": "{{title|upper}}", "description": "Custom"}')
        
        # Save template
        self.template_manager.save_template('custom', {
            'title': '{{title|upper}}',
            'description': 'Custom description'
        })
        
        # Load and use template
        metadata = self.template_manager.get_template('custom')
        self.assertIsNotNone(metadata)
    
    def test_template_validation(self):
        """Test template validation."""
        valid_template = {
            'title': '{{title}}',
            'description': '{{description}}',
            'tags': '{{tags}}'
        }
        
        invalid_template = {'title': '{{title}}'}  # Missing required fields
        
        # Should not raise exception for valid template
        result = self.template_engine.render_template(valid_template, {'title': 'test'})
        self.assertIn('test', result['title'])


class TestConfigIntegration(unittest.TestCase):
    """Test configuration integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = StudioOrchestrator()
    
    def test_config_application(self):
        """Test that configuration is applied correctly."""
        config = YouTubeStudioConfig()
        config.seo.max_title_length = 70
        config.seo.max_keywords = 20
        
        orchestrator = StudioOrchestrator(config=config)
        
        metadata = orchestrator.generate_video_metadata({
            'title': 'Test Title',
            'description': 'Test description',
            'content': 'Test content',
            'category': 'education'
        })
        
        # Verify title respects config
        self.assertLessEqual(len(metadata['title']), 70)
    
    def test_custom_config(self):
        """Test custom configuration."""
        custom_config = YouTubeStudioConfig()
        custom_config.seo.max_keywords = 25
        
        orchestrator = StudioOrchestrator(config=custom_config)
        
        metadata = orchestrator.generate_video_metadata({
            'title': 'Test',
            'description': 'Test',
            'content': 'Test',
            'category': 'education'
        })
        
        # Verify custom config is applied
        self.assertGreaterEqual(len(metadata['keywords']), 5)


if __name__ == '__main__':
    unittest.main()