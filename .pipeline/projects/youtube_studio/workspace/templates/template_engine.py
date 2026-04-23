"""
Template Engine Module

This module provides the TemplateEngine class for rendering templates
with variable substitution and formatting.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class RenderResult:
    """Result of template rendering"""
    success: bool
    rendered_content: str
    variables_used: List[str]
    errors: List[str]


class TemplateEngine:
    """
    Engine for rendering templates with variable substitution.
    
    This class provides functionality for substituting variables in templates,
    applying formatting, and validating template structure.
    """
    
    # Default variable delimiters
    DEFAULT_VARIABLE_PREFIX = '{{'
    DEFAULT_VARIABLE_SUFFIX = '}}'
    
    # Regex pattern for matching variables
    VARIABLE_PATTERN = re.compile(r'\{\{([^}]+)\}\}')
    
    # Supported filters
    SUPPORTED_FILTERS = {
        'upper': lambda x: x.upper() if isinstance(x, str) else x,
        'lower': lambda x: x.lower() if isinstance(x, str) else x,
        'title': lambda x: x.title() if isinstance(x, str) else x,
        'capitalize': lambda x: x.capitalize() if isinstance(x, str) else x,
        'strip': lambda x: x.strip() if isinstance(x, str) else x,
        'truncate': lambda x, n=50: x[:n] if isinstance(x, str) else x,
        'default': lambda x, default='': x if x else default,
        'join': lambda x, sep=' ': sep.join(str(item) for item in x) if isinstance(x, (list, tuple)) else x,
        'reverse': lambda x: x[::-1] if isinstance(x, str) else x,
        'length': lambda x: len(x) if hasattr(x, '__len__') else 0,
        'date': lambda x, fmt='%Y-%m-%d': datetime.fromtimestamp(x).strftime(fmt) if isinstance(x, (int, float)) else x,
    }
    
    def __init__(
        self,
        variable_prefix: str = DEFAULT_VARIABLE_PREFIX,
        variable_suffix: str = DEFAULT_VARIABLE_SUFFIX,
        auto_escape: bool = True,
        strict_mode: bool = False
    ):
        """
        Initialize the template engine.
        
        Args:
            variable_prefix: Prefix for template variables
            variable_suffix: Suffix for template variables
            auto_escape: Whether to escape HTML by default
            strict_mode: Whether to raise errors on undefined variables
        """
        self.variable_prefix = variable_prefix
        self.variable_suffix = variable_suffix
        self.auto_escape = auto_escape
        self.strict_mode = strict_mode
        
        # Update regex pattern with custom delimiters
        self.VARIABLE_PATTERN = re.compile(
            re.escape(variable_prefix) + r'([^}]+)' + re.escape(variable_suffix)
        )
    
    def render(self, template: str, variables: Dict[str, Any]) -> RenderResult:
        """
        Render a template with the given variables.
        
        Args:
            template: Template string to render
            variables: Dictionary of variable names and values
            
        Returns:
            RenderResult with rendered content and metadata
        """
        errors = []
        variables_used = []
        
        try:
            # Find all variables in template
            matches = self.VARIABLE_PATTERN.findall(template)
            
            for match in matches:
                # Extract variable name and filters
                var_name, filters = self._parse_variable(match)
                
                if var_name not in variables:
                    if self.strict_mode:
                        errors.append(f"Undefined variable: {var_name}")
                        return RenderResult(
                            success=False,
                            rendered_content='',
                            variables_used=[],
                            errors=errors
                        )
                    else:
                        variables[var_name] = ''
                        errors.append(f"Using default for undefined variable: {var_name}")
                
                variables_used.append(var_name)
            
            # Render the template
            rendered = self._render_template(template, variables)
            
            return RenderResult(
                success=True,
                rendered_content=rendered,
                variables_used=variables_used,
                errors=errors
            )
            
        except Exception as e:
            return RenderResult(
                success=False,
                rendered_content='',
                variables_used=[],
                errors=[str(e)]
            )
    
    def _parse_variable(self, match: str) -> tuple:
        """
        Parse a variable match to extract name and filters.
        
        Args:
            match: Variable match string
            
        Returns:
            Tuple of (variable_name, list of filters)
        """
        parts = match.split('|')
        var_name = parts[0].strip()
        filters = []
        
        for part in parts[1:]:
            filter_parts = part.strip().split(':')
            filter_name = filter_parts[0].strip()
            filter_args = filter_parts[1:] if len(filter_parts) > 1 else []
            filters.append((filter_name, filter_args))
        
        return var_name, filters
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Render template by substituting variables.
        
        Args:
            template: Template string
            variables: Variables dictionary
            
        Returns:
            Rendered template string
        """
        def replace_variable(match):
            var_match = match.group(1)
            var_name, filters = self._parse_variable(var_match)
            
            # Get variable value
            value = variables.get(var_name, '')
            
            # Apply filters
            for filter_name, filter_args in filters:
                value = self._apply_filter(value, filter_name, filter_args)
            
            # Escape HTML if auto_escape is enabled
            if self.auto_escape and isinstance(value, str):
                value = self._escape_html(value)
            
            return str(value)
        
        return self.VARIABLE_PATTERN.sub(replace_variable, template)
    
    def _apply_filter(self, value: Any, filter_name: str, args: List[str]) -> Any:
        """
        Apply a filter to a value.
        
        Args:
            value: Value to filter
            filter_name: Name of the filter
            args: Filter arguments
            
        Returns:
            Filtered value
        """
        if filter_name not in self.SUPPORTED_FILTERS:
            # If filter not supported, return original value
            return value
        
        filter_func = self.SUPPORTED_FILTERS[filter_name]
        
        try:
            # Call filter with arguments
            if args:
                return filter_func(value, *args)
            else:
                return filter_func(value)
        except Exception:
            return value
    
    def _escape_html(self, text: str) -> str:
        """
        Escape HTML characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')
        )
    
    def validate_template(self, template: str) -> tuple:
        """
        Validate a template for syntax errors.
        
        Args:
            template: Template string to validate
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check for mismatched delimiters
        prefix_count = template.count(self.variable_prefix)
        suffix_count = template.count(self.variable_suffix)
        
        if prefix_count != suffix_count:
            issues.append(f"Mismatched delimiters: {prefix_count} prefixes, {suffix_count} suffixes")
        
        # Check for empty variables
        matches = self.VARIABLE_PATTERN.findall(template)
        for match in matches:
            if not match.strip():
                issues.append("Empty variable found")
        
        # Check for invalid characters in variable names
        for match in matches:
            var_name = match.split('|')[0].strip()
            if not var_name.replace('_', '').isalnum():
                issues.append(f"Invalid variable name: {var_name}")
        
        return len(issues) == 0, issues
    
    def extract_variables(self, template: str) -> List[str]:
        """
        Extract all variable names from a template.
        
        Args:
            template: Template string
            
        Returns:
            List of variable names
        """
        variables = []
        
        for match in self.VARIABLE_PATTERN.findall(template):
            var_name = match.split('|')[0].strip()
            if var_name and var_name not in variables:
                variables.append(var_name)
        
        return variables
    
    def get_variable_types(self, template: str) -> Dict[str, str]:
        """
        Infer variable types from template usage.
        
        Args:
            template: Template string
            
        Returns:
            Dictionary mapping variable names to inferred types
        """
        variable_types = {}
        
        for match in self.VARIABLE_PATTERN.findall(template):
            var_name = match.split('|')[0].strip()
            
            # Check for type hints in filters
            if '|date' in match:
                variable_types[var_name] = 'date'
            elif '|length' in match:
                variable_types[var_name] = 'collection'
            elif '|join' in match:
                variable_types[var_name] = 'collection'
            else:
                variable_types[var_name] = 'string'
        
        return variable_types
    
    def format_date(self, timestamp: float, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
        Format a timestamp as a date string.
        
        Args:
            timestamp: Unix timestamp
            format_str: Format string
            
        Returns:
            Formatted date string
        """
        return datetime.fromtimestamp(timestamp).strftime(format_str)
    
    def format_number(self, number: float, decimals: int = 2) -> str:
        """
        Format a number with specified decimal places.
        
        Args:
            number: Number to format
            decimals: Number of decimal places
            
        Returns:
            Formatted number string
        """
        return f"{number:.{decimals}f}"
    
    def create_template_function(self, template: str) -> Callable[[Dict[str, Any]], str]:
        """
        Create a reusable render function from a template.
        
        Args:
            template: Template string
            
        Returns:
            Function that accepts variables dict and returns rendered string
        """
        def render_func(variables: Dict[str, Any]) -> str:
            result = self.render(template, variables)
            if not result.success:
                raise ValueError(f"Template rendering failed: {result.errors}")
            return result.rendered_content
        
        return render_func
    
    def merge_templates(self, base_template: str, overlay_template: str) -> str:
        """
        Merge two templates by combining their variables.
        
        Args:
            base_template: Base template string
            overlay_template: Overlay template string
            
        Returns:
            Merged template string
        """
        base_vars = set(self.extract_variables(base_template))
        overlay_vars = set(self.extract_variables(overlay_template))
        
        # Combine templates
        merged = base_template + '\n' + overlay_template
        
        return merged
    
    def compare_templates(self, template1: str, template2: str) -> Dict:
        """
        Compare two templates for differences.
        
        Args:
            template1: First template
            template2: Second template
            
        Returns:
            Dictionary with comparison results
        """
        vars1 = set(self.extract_variables(template1))
        vars2 = set(self.extract_variables(template2))
        
        return {
            'variables_only_in_first': list(vars1 - vars2),
            'variables_only_in_second': list(vars2 - vars1),
            'common_variables': list(vars1 & vars2),
            'total_variables_template1': len(vars1),
            'total_variables_template2': len(vars2),
            'similarity': len(vars1 & vars2) / max(len(vars1 | vars2), 1)
        }
    
    def generate_example(self, template: str) -> str:
        """
        Generate an example rendering of a template.
        
        Args:
            template: Template string
            
        Returns:
            Example rendered string with placeholder values
        """
        variables = {}
        
        for var in self.extract_variables(template):
            variables[var] = f"[{var.upper()}]"
        
        result = self.render(template, variables)
        return result.rendered_content if result.success else template
