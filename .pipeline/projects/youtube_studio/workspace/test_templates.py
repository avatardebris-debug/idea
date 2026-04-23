"""Tests for template system in YouTube Studio.

This module provides comprehensive tests for template management and
rendering functionality.
"""

import os
import tempfile
import unittest
import json
from template_manager import TemplateManager
from template_engine import TemplateEngine


class TestTemplateManager(unittest.TestCase):
    """Test cases for TemplateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.manager = TemplateManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_load_template(self):
        """Test loading a template file."""
        # Create a test template file
        template_path = os.path.join(self.test_dir, 'test_template.json')
        with open(template_path, 'w') as f:
            json.dump({'title': 'Test', 'description': 'A test template'}, f)
        
        template = self.manager.load_template('test_template')
        
        self.assertIsNotNone(template)
        self.assertEqual(template['title'], 'Test')
    
    def test_save_template(self):
        """Test saving a template file."""
        template = {
            'title': 'My Template',
            'description': 'A custom template',
            'tags': ['test', 'template']
        }
        
        success = self.manager.save_template('my_template', template)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'my_template.json')))
    
    def test_get_template(self):
        """Test getting a template by name."""
        # Save a template first
        self.manager.save_template('test_get', {'field': 'value'})
        
        template = self.manager.get_template('test_get')
        
        self.assertIsNotNone(template)
        self.assertEqual(template['field'], 'value')
    
    def test_get_template_not_found(self):
        """Test getting a non-existent template."""
        template = self.manager.get_template('nonexistent')
        
        self.assertIsNone(template)
    
    def test_get_all_templates(self):
        """Test getting all template names."""
        self.manager.save_template('template1', {'field': 'value1'})
        self.manager.save_template('template2', {'field': 'value2'})
        
        templates = self.manager.get_all_templates()
        
        self.assertEqual(len(templates), 2)
        self.assertIn('template1.json', templates)
        self.assertIn('template2.json', templates)
    
    def test_delete_template(self):
        """Test deleting a template."""
        self.manager.save_template('to_delete', {'field': 'value'})
        
        success = self.manager.delete_template('to_delete')
        
        self.assertTrue(success)
        self.assertIsNone(self.manager.get_template('to_delete'))
    
    def test_validate_template(self):
        """Test template validation."""
        valid_template = {
            'title': 'Test',
            'description': 'Test description',
            'tags': ['test'],
            'custom_fields': {}
        }
        
        invalid_template = {'title': 'Test'}  # Missing required fields
        
        self.assertTrue(self.manager.validate_template(valid_template))
        self.assertFalse(self.manager.validate_template(invalid_template))
    
    def test_get_template_statistics(self):
        """Test getting template statistics."""
        self.manager.save_template('stat1', {'field': 'value'})
        self.manager.save_template('stat2', {'field': 'value'})
        
        stats = self.manager.get_template_statistics()
        
        self.assertEqual(stats['total_templates'], 2)
        self.assertEqual(len(stats['templates']), 2)
    
    def test_load_existing_templates_on_init(self):
        """Test that templates are loaded on initialization."""
        # Create templates before manager initialization
        template_path = os.path.join(self.test_dir, 'preloaded.json')
        with open(template_path, 'w') as f:
            json.dump({'title': 'Preloaded'}, f)
        
        manager = TemplateManager(self.test_dir)
        
        self.assertIn('preloaded.json', manager.get_all_templates())


class TestTemplateEngine(unittest.TestCase):
    """Test cases for TemplateEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = TemplateEngine()
    
    def test_simple_variable_substitution(self):
        """Test simple variable substitution."""
        template = "Hello, {{name}}! Welcome to {{channel}}."
        result = self.engine.render(template, {'name': 'John', 'channel': 'TechChannel'})
        
        self.assertEqual(result, "Hello, John! Welcome to TechChannel.")
    
    def test_conditional_block_true(self):
        """Test conditional block when condition is true."""
        template = "{% if show_greeting %}Welcome!{% endif %} Enjoy your stay."
        result = self.engine.render(template, {'show_greeting': True})
        
        self.assertEqual(result, "Welcome! Enjoy your stay.")
    
    def test_conditional_block_false(self):
        """Test conditional block when condition is false."""
        template = "{% if show_greeting %}Welcome!{% endif %} Enjoy your stay."
        result = self.engine.render(template, {'show_greeting': False})
        
        self.assertEqual(result, " Enjoy your stay.")
    
    def test_loop_block(self):
        """Test loop block rendering."""
        template = "Tags: {% for tag in tags %}{{tag}} {% endfor %}"
        result = self.engine.render(template, {'tags': ['python', 'tutorial', 'beginner']})
        
        self.assertIn('Tags:', result)
        self.assertIn('python', result)
        self.assertIn('tutorial', result)
        self.assertIn('beginner', result)
    
    def test_function_calls(self):
        """Test function calls in templates."""
        template = "Title: {{title|upper}}, Author: {{author|title}}"
        result = self.engine.render(template, {
            'title': 'python basics',
            'author': 'john doe'
        })
        
        self.assertIn('Title: PYTHON BASICS', result)
        self.assertIn('Author: John Doe', result)
    
    def test_function_join(self):
        """Test join function."""
        template = "Tags: {{tags|join(', ')}}"
        result = self.engine.render(template, {'tags': ['python', 'tutorial']})
        
        self.assertEqual(result, "Tags: python, tutorial")
    
    def test_function_default(self):
        """Test default function."""
        template = "Author: {{author|default('Unknown')}}"
        result = self.engine.render(template, {})
        
        self.assertEqual(result, "Author: Unknown")
    
    def test_combined_features(self):
        """Test combined template features."""
        template = """
        {% if show_title %}
        # {{title|upper}}
        {% endif %}
        
        Author: {{author|title}}
        
        Tags: {% for tag in tags %}{{tag}} {% endfor %}
        """
        
        result = self.engine.render(template, {
            'show_title': True,
            'title': 'python tutorial',
            'author': 'john doe',
            'tags': ['python', 'tutorial']
        })
        
        self.assertIn('PYTHON TUTORIAL', result)
        self.assertIn('Author: John Doe', result)
        self.assertIn('python', result)
    
    def test_render_template_method(self):
        """Test complete template rendering with data."""
        template_config = {
            'title': '{{title|upper}}',
            'description': 'Learn about {{topic}} from {{author}}',
            'tags': '{{tags|join(", ")}}'
        }
        
        data = {
            'title': 'python for beginners',
            'topic': 'programming',
            'author': 'john doe',
            'tags': ['python', 'tutorial', 'beginner']
        }
        
        result = self.engine.render_template(template_config, data)
        
        self.assertEqual(result['title'], 'PYTHON FOR BEGINNERS')
        self.assertIn('programming', result['description'])
        self.assertIn('python', result['tags'])
    
    def test_set_variables(self):
        """Test setting variables programmatically."""
        self.engine.set_variable('name', 'Alice')
        self.engine.set_variables({'channel': 'TechChannel', 'year': 2024})
        
        template = "Hello {{name}}! Welcome to {{channel}} ({{year}})"
        result = self.engine.render(template)
        
        self.assertEqual(result, "Hello Alice! Welcome to TechChannel (2024)")
    
    def test_clear_variables(self):
        """Test clearing all variables."""
        self.engine.set_variables({'name': 'John', 'channel': 'Test'})
        self.engine.clear_variables()
        
        template = "Hello {{name}}! Welcome to {{channel}}."
        result = self.engine.render(template)
        
        self.assertEqual(result, "Hello ! Welcome to .")


class TestTemplateIntegration(unittest.TestCase):
    """Integration tests for template system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.manager = TemplateManager(self.test_dir)
        self.engine = TemplateEngine()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_full_workflow(self):
        """Test complete template workflow."""
        # Create a template
        template = {
            'title': '{{title|upper}}',
            'description': 'In this video, we explore {{topic}}. Learn from {{author}}.',
            'tags': '{{tags|join(", ")}}',
            'custom_fields': {
                'author': '{{author}}',
                'category': '{{category}}'
            }
        }
        
        # Save template
        self.manager.save_template('tutorial', template)
        
        # Load template
        loaded = self.manager.get_template('tutorial')
        self.assertIsNotNone(loaded)
        
        # Render with data
        data = {
            'title': 'python basics',
            'topic': 'programming',
            'author': 'john doe',
            'tags': ['python', 'tutorial', 'beginner'],
            'category': 'education'
        }
        
        result = self.engine.render_template(loaded, data)
        
        # Verify result
        self.assertEqual(result['title'], 'PYTHON BASICS')
        self.assertIn('programming', result['description'])
        self.assertIn('python', result['tags'])
    
    def test_template_persistence(self):
        """Test template persistence across sessions."""
        # Create and save template
        template = {'field': 'value'}
        self.manager.save_template('persistence', template)
        
        # Create new manager (simulating new session)
        new_manager = TemplateManager(self.test_dir)
        
        # Load template
        loaded = new_manager.get_template('persistence')
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['field'], 'value')


if __name__ == '__main__':
    unittest.main()