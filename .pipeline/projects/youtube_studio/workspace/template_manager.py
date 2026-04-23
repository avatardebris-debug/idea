"""Template manager for YouTube Studio.

This module provides functionality for loading, saving, and managing
JSON-based video metadata templates.
"""

import json
import os
from typing import Dict, List, Optional
from constants import TEMPLATE_EXTENSION, TEMPLATE_REQUIRED_FIELDS


class TemplateManager:
    """Manager for loading, saving, and managing video templates.
    
    This class provides centralized template management with support
    for loading from JSON files, saving custom templates, and
    retrieving template configurations.
    """
    
    def __init__(self, template_directory: str = 'templates'):
        """Initialize template manager.
        
        Args:
            template_directory: Directory path where templates are stored.
        """
        self._template_directory = template_directory
        self._templates: Dict[str, dict] = {}
        self._ensure_directory_exists()
        self._load_all_templates()
    
    def _ensure_directory_exists(self) -> None:
        """Ensure the template directory exists."""
        if not os.path.exists(self._template_directory):
            os.makedirs(self._template_directory)
    
    def _load_all_templates(self) -> None:
        """Load all templates from the template directory."""
        if not os.path.exists(self._template_directory):
            return
        
        for filename in os.listdir(self._template_directory):
            if filename.endswith(TEMPLATE_EXTENSION):
                template_name = filename[:-len(TEMPLATE_EXTENSION)]
                self.load_template(filename)
    
    def load_template(self, template_name: str) -> Optional[dict]:
        """Load a template from a JSON file.
        
        Args:
            template_name: Name of the template (without extension).
            
        Returns:
            Template dictionary or None if loading fails.
        """
        if not template_name.endswith(TEMPLATE_EXTENSION):
            template_name += TEMPLATE_EXTENSION
        
        filepath = os.path.join(self._template_directory, template_name)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            self._templates[template_name] = template
            return template
            
        except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
            print(f"Error loading template {template_name}: {e}")
            return None
    
    def save_template(self, template_name: str, template: dict) -> bool:
        """Save a template to a JSON file.
        
        Args:
            template_name: Name for the template file.
            template: Template configuration dictionary.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        if not template_name.endswith(TEMPLATE_EXTENSION):
            template_name += TEMPLATE_EXTENSION
        
        filepath = os.path.join(self._template_directory, template_name)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
            
            self._templates[template_name] = template
            return True
            
        except IOError as e:
            print(f"Error saving template {template_name}: {e}")
            return False
    
    def get_template(self, template_name: str) -> Optional[dict]:
        """Get a template by name.
        
        Args:
            template_name: Name of the template.
            
        Returns:
            Template dictionary or None if not found.
        """
        if not template_name.endswith(TEMPLATE_EXTENSION):
            template_name += TEMPLATE_EXTENSION
        
        return self._templates.get(template_name)
    
    def get_all_templates(self) -> List[str]:
        """Get list of all available template names.
        
        Returns:
            List of template file names.
        """
        return list(self._templates.keys())
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a template file.
        
        Args:
            template_name: Name of the template to delete.
            
        Returns:
            True if deleted successfully, False otherwise.
        """
        if not template_name.endswith(TEMPLATE_EXTENSION):
            template_name += TEMPLATE_EXTENSION
        
        filepath = os.path.join(self._template_directory, template_name)
        
        if template_name in self._templates:
            del self._templates[template_name]
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
            
        except OSError:
            return False
    
    def validate_template(self, template: dict) -> bool:
        """Validate a template has required fields.
        
        Args:
            template: Template dictionary to validate.
            
        Returns:
            True if template is valid.
        """
        if not template:
            return False
        
        for field in TEMPLATE_REQUIRED_FIELDS:
            if field not in template:
                return False
        
        return True
    
    def get_template_statistics(self) -> dict:
        """Get statistics about available templates.
        
        Returns:
            Dictionary of template statistics.
        """
        return {
            'total_templates': len(self._templates),
            'template_directory': self._template_directory,
            'templates': list(self._templates.keys())
        }


if __name__ == '__main__':
    # Test template management
    manager = TemplateManager()
    
    print("Template Manager Test:")
    print(f"Available templates: {manager.get_all_templates()}")
    
    # Create a custom template
    custom_template = {
        'title': 'My Custom Template',
        'description': 'A template for custom videos',
        'tags': ['custom', 'template', 'test'],
        'custom_fields': {
            'author': 'Test Author',
            'category': 'Education'
        }
    }
    
    success = manager.save_template('custom_test', custom_template)
    print(f"Saved custom template: {success}")
    
    # Load and verify
    loaded = manager.get_template('custom_test.json')
    print(f"Loaded template: {loaded is not None}")
    
    # Get statistics
    stats = manager.get_template_statistics()
    print(f"Statistics: {stats}")
