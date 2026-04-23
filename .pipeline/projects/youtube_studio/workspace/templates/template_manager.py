"""
Template Manager Module

This module provides the TemplateManager class for managing video templates
including loading, saving, and organizing template files.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import json
import os


@dataclass
class TemplateInfo:
    """Information about a template"""
    name: str
    description: str
    version: str
    created_at: str
    updated_at: str
    file_path: str
    variables: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class TemplateManager:
    """
    Manager for video templates.
    
    This class provides functionality for loading, saving, and organizing
    video templates used for title, keyword, and thumbnail generation.
    """
    
    DEFAULT_TEMPLATE_PATH = 'templates/default_template.json'
    TEMPLATE_EXTENSION = '.json'
    
    def __init__(self, template_dir: str = 'templates'):
        """
        Initialize the template manager.
        
        Args:
            template_dir: Directory path for storing templates
        """
        self.template_dir = Path(template_dir)
        self._templates: Dict[str, TemplateInfo] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all templates from the template directory"""
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for template_file in self.template_dir.glob(f'*{self.TEMPLATE_EXTENSION}'):
            try:
                template_info = self._load_template_info(template_file)
                if template_info:
                    self._templates[template_info.name] = template_info
            except Exception:
                continue
    
    def _load_template_info(self, template_file: Path) -> Optional[TemplateInfo]:
        """
        Load template information from a file.
        
        Args:
            template_file: Path to template file
            
        Returns:
            TemplateInfo object or None if loading fails
        """
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return TemplateInfo(
                name=data.get('name', template_file.stem),
                description=data.get('description', ''),
                version=data.get('version', '1.0.0'),
                created_at=data.get('created_at', datetime.now().isoformat()),
                updated_at=data.get('updated_at', datetime.now().isoformat()),
                file_path=str(template_file),
                variables=data.get('variables', []),
                tags=data.get('tags', [])
            )
        except (json.JSONDecodeError, IOError):
            return None
    
    def get_template(self, name: str) -> Optional[Dict]:
        """
        Get a template by name.
        
        Args:
            name: Template name
            
        Returns:
            Template dictionary or None if not found
        """
        if name not in self._templates:
            return None
        
        template_file = Path(self._templates[name].file_path)
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def get_template_names(self) -> List[str]:
        """
        Get list of all available template names.
        
        Returns:
            List of template names
        """
        return list(self._templates.keys())
    
    def get_template_info(self, name: str) -> Optional[TemplateInfo]:
        """
        Get template information.
        
        Args:
            name: Template name
            
        Returns:
            TemplateInfo object or None if not found
        """
        return self._templates.get(name)
    
    def get_all_templates_info(self) -> List[TemplateInfo]:
        """
        Get information about all templates.
        
        Returns:
            List of TemplateInfo objects
        """
        return list(self._templates.values())
    
    def save_template(
        self,
        name: str,
        content: Dict,
        description: str = '',
        version: str = '1.0.0',
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Save a new template.
        
        Args:
            name: Template name
            content: Template content dictionary
            description: Template description
            version: Template version
            tags: Optional list of tags
            
        Returns:
            True if saved successfully, False otherwise
        """
        if tags is None:
            tags = []
        
        # Check if template already exists
        if name in self._templates:
            return False
        
        # Create template file
        template_file = self.template_dir / f"{name}{self.TEMPLATE_EXTENSION}"
        
        template_data = {
            'name': name,
            'description': description,
            'version': version,
            'variables': content.get('variables', []),
            'tags': tags,
            'content': content.get('content', {}),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)
            
            # Update templates index
            self._templates[name] = TemplateInfo(
                name=name,
                description=description,
                version=version,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                file_path=str(template_file),
                variables=content.get('variables', []),
                tags=tags
            )
            
            return True
        except IOError:
            return False
    
    def update_template(
        self,
        name: str,
        content: Dict,
        description: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Update an existing template.
        
        Args:
            name: Template name
            content: Updated template content
            description: New description (optional)
            version: New version (optional)
            tags: New tags (optional)
            
        Returns:
            True if updated successfully, False otherwise
        """
        if name not in self._templates:
            return False
        
        template_file = Path(self._templates[name].file_path)
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # Update fields
            existing_data['content'] = content.get('content', {})
            existing_data['variables'] = content.get('variables', existing_data.get('variables', []))
            
            if description is not None:
                existing_data['description'] = description
            
            if version is not None:
                existing_data['version'] = version
            
            if tags is not None:
                existing_data['tags'] = tags
            
            existing_data['updated_at'] = datetime.now().isoformat()
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2)
            
            # Update templates index
            self._templates[name] = TemplateInfo(
                name=name,
                description=existing_data.get('description', ''),
                version=existing_data.get('version', '1.0.0'),
                created_at=existing_data.get('created_at', datetime.now().isoformat()),
                updated_at=existing_data.get('updated_at', datetime.now().isoformat()),
                file_path=str(template_file),
                variables=existing_data.get('variables', []),
                tags=existing_data.get('tags', [])
            )
            
            return True
        except (json.JSONDecodeError, IOError):
            return False
    
    def delete_template(self, name: str) -> bool:
        """
        Delete a template.
        
        Args:
            name: Template name
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if name not in self._templates:
            return False
        
        template_file = Path(self._templates[name].file_path)
        
        try:
            template_file.unlink()
            del self._templates[name]
            return True
        except IOError:
            return False
    
    def search_templates(
        self,
        query: str,
        tags: Optional[List[str]] = None
    ) -> List[TemplateInfo]:
        """
        Search for templates by name, description, or tags.
        
        Args:
            query: Search query
            tags: Optional list of tags to filter by
            
        Returns:
            List of matching TemplateInfo objects
        """
        query_lower = query.lower()
        results = []
        
        for template_info in self._templates.values():
            # Check name match
            if query_lower in template_info.name.lower():
                results.append(template_info)
                continue
            
            # Check description match
            if query_lower in template_info.description.lower():
                results.append(template_info)
                continue
            
            # Check tag match
            if tags and any(tag in template_info.tags for tag in tags):
                results.append(template_info)
                continue
            
            # Check variable match
            if any(query_lower in var.lower() for var in template_info.variables):
                results.append(template_info)
        
        return results
    
    def get_variable_names(self, name: str) -> List[str]:
        """
        Get variable names from a template.
        
        Args:
            name: Template name
            
        Returns:
            List of variable names
        """
        template = self.get_template(name)
        if template:
            return template.get('variables', [])
        return []
    
    def validate_template(self, name: str) -> bool:
        """
        Validate a template structure.
        
        Args:
            name: Template name
            
        Returns:
            True if valid, False otherwise
        """
        template = self.get_template(name)
        if not template:
            return False
        
        # Check required fields
        required_fields = ['name', 'version', 'content']
        for field in required_fields:
            if field not in template:
                return False
        
        return True
    
    def export_templates(self, output_path: str) -> bool:
        """
        Export all templates to a single file.
        
        Args:
            output_path: Output file path
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'templates': []
            }
            
            for name, template_info in self._templates.items():
                template = self.get_template(name)
                if template:
                    export_data['templates'].append({
                        'name': name,
                        'info': {
                            'description': template_info.description,
                            'version': template_info.version,
                            'variables': template_info.variables,
                            'tags': template_info.tags
                        },
                        'content': template
                    })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            return True
        except IOError:
            return False
    
    def import_templates(self, input_path: str) -> int:
        """
        Import templates from a file.
        
        Args:
            input_path: Input file path
            
        Returns:
            Number of templates imported
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            
            for template_data in data.get('templates', []):
                name = template_data.get('name')
                content = template_data.get('content', {})
                info = template_data.get('info', {})
                
                if name and self.save_template(
                    name=name,
                    content=content,
                    description=info.get('description', ''),
                    version=info.get('version', '1.0.0'),
                    tags=info.get('tags', [])
                ):
                    imported_count += 1
            
            return imported_count
        except (json.JSONDecodeError, IOError):
            return 0
    
    def get_template_statistics(self) -> Dict:
        """
        Get statistics about all templates.
        
        Returns:
            Dictionary with template statistics
        """
        total_templates = len(self._templates)
        total_variables = sum(len(t.variables) for t in self._templates.values())
        total_tags = sum(len(t.tags) for t in self._templates.values())
        
        versions = {}
        for template in self._templates.values():
            version = template.version
            versions[version] = versions.get(version, 0) + 1
        
        return {
            'total_templates': total_templates,
            'total_variables': total_variables,
            'total_tags': total_tags,
            'versions': versions,
            'oldest_template': min(
                (t.created_at for t in self._templates.values()),
                default=None
            ),
            'newest_template': max(
                (t.updated_at for t in self._templates.values()),
                default=None
            )
        }
