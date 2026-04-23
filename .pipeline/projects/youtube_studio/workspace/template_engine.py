"""Template engine for YouTube Studio.

This module provides functionality for rendering templates with
variable substitution and dynamic content insertion.
"""

import re
from typing import Dict, List, Optional, Callable


class TemplateEngine:
    """Engine for rendering templates with variable substitution.
    
    This class handles template rendering with support for:
    - Simple variable substitution {{variable_name}}
    - Conditional blocks {% if condition %}...{% endif %}
    - Loop blocks {% for item in items %}...{% endfor %}
    - Function calls {{variable|function}} and {{variable|function(arg)}}
    """
    
    def __init__(self):
        """Initialize template engine."""
        self._variables: Dict[str, any] = {}
        self._custom_functions: Dict[str, Callable] = {}
        self._load_builtin_functions()
    
    def _load_builtin_functions(self) -> None:
        """Load built-in template functions."""
        self._custom_functions['upper'] = lambda x: x.upper() if isinstance(x, str) else x
        self._custom_functions['lower'] = lambda x: x.lower() if isinstance(x, str) else x
        self._custom_functions['title'] = lambda x: x.title() if isinstance(x, str) else x
        self._custom_functions['capitalize'] = lambda x: x.capitalize() if isinstance(x, str) else x
        self._custom_functions['strip'] = lambda x: x.strip() if isinstance(x, str) else x
        self._custom_functions['len'] = lambda x: len(x) if isinstance(x, (str, list)) else x
        
        # Join function - takes a separator and returns a lambda that joins a list
        def make_join(sep):
            return lambda x: sep.join(x) if isinstance(x, list) else x
        
        self._custom_functions['join'] = make_join
        
        # Default function - takes a default value and returns a lambda
        def make_default(default_val):
            return lambda x: x if x is not None else default_val
        
        self._custom_functions['default'] = make_default
    
    def _parse_function_args(self, func_args: str) -> List:
        """Parse function arguments, handling quoted strings.
        
        Args:
            func_args: Raw argument string.
            
        Returns:
            List of parsed arguments.
        """
        args = []
        current_arg = ""
        in_quotes = False
        quote_char = None
        
        for char in func_args:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                # Include the quote character in the argument
                current_arg += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                # Include the closing quote character
                current_arg += char
            elif char == ',' and not in_quotes:
                # End of argument
                if current_arg.strip():
                    arg = current_arg.strip()
                    # Remove quotes if present
                    if (arg.startswith("'") and arg.endswith("'")) or \
                       (arg.startswith('"') and arg.endswith('"')):
                        arg = arg[1:-1]
                    args.append(arg)
                current_arg = ""
                continue
            else:
                current_arg += char
        
        # Don't forget the last argument
        if current_arg.strip():
            arg = current_arg.strip()
            if (arg.startswith("'") and arg.endswith("'")) or \
               (arg.startswith('"') and arg.endswith('"')):
                arg = arg[1:-1]
            args.append(arg)
        
        return args
    
    def set_variable(self, name: str, value: any) -> None:
        """Set a single variable.
        
        Args:
            name: Variable name.
            value: Variable value.
        """
        self._variables[name] = value
    
    def set_variables(self, variables: Dict[str, any]) -> None:
        """Set multiple variables.
        
        Args:
            variables: Dictionary of variable names and values.
        """
        self._variables.update(variables)
    
    def clear_variables(self) -> None:
        """Clear all variables."""
        self._variables.clear()
    
    def _apply_function(self, value: any, func_name: str, func_args: List = None) -> any:
        """Apply a function to a value.
        
        Args:
            value: Value to apply function to.
            func_name: Name of the function.
            func_args: Optional function arguments.
            
        Returns:
            Result of function application.
        """
        if func_name not in self._custom_functions:
            return value
        
        func = self._custom_functions[func_name]
        
        if func_args:
            # For factory functions (join, default), call with args to get the actual function
            # then apply to value
            actual_func = func(*func_args)
            return actual_func(value)
        
        return func(value)
    
    def _render_conditional(self, condition: str, content: str, variables: Dict) -> str:
        """Render conditional block.
        
        Args:
            condition: Condition variable name (e.g., 'show_greeting').
            content: Content inside conditional block.
            variables: Variables for evaluation.
            
        Returns:
            Rendered content or empty string.
        """
        condition_value = variables.get(condition, False)
        
        if condition_value:
            return content.strip()
        return ''
    
    def _render_loop(self, item_var: str, list_var: str, content: str, variables: Dict) -> str:
        """Render loop block.
        
        Args:
            item_var: Loop item variable name.
            list_var: List variable name.
            content: Content inside loop block.
            variables: Variables for iteration.
            
        Returns:
            Rendered loop content.
        """
        items = variables.get(list_var, [])
        result = []
        
        if isinstance(items, list):
            for item in items:
                loop_vars = variables.copy()
                loop_vars[item_var] = item
                result.append(self.render(content, loop_vars))
        
        return ''.join(result)
    
    def render(self, template: str, variables: Dict = None) -> str:
        """Render a template string.
        
        Args:
            template: Template string to render.
            variables: Optional variables dictionary.
            
        Returns:
            Rendered string.
        """
        if variables is None:
            variables = self._variables.copy()
        else:
            variables = variables.copy()
        
        # Handle conditional blocks
        template = re.sub(
            r'\{%\s*if\s+(\w+)\s*%\}(.+?)\{%\s*endif\s*%\}',
            lambda m: self._render_conditional(m.group(1), m.group(2), variables),
            template,
            flags=re.DOTALL
        )
        
        # Handle loop blocks
        template = re.sub(
            r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.+?)\{%\s*endfor\s*%\}',
            lambda m: self._render_loop(m.group(1), m.group(2), m.group(3), variables),
            template,
            flags=re.DOTALL
        )
        
        # Handle variable substitutions with functions
        def replace_var(match):
            var_name = match.group(1)
            func_name = match.group(2)
            func_args = match.group(3)
            
            # Get value from variables - use None if not found so default function can work
            value = variables.get(var_name, None)
            
            if func_name:
                # Parse function arguments
                args = self._parse_function_args(func_args) if func_args else []
                
                value = self._apply_function(value, func_name, args)
            
            return str(value) if value is not None else ''
        
        template = re.sub(
            r'\{\{(\w+)\|(\w+)(?:\(([^)]*)\))?\}\}',
            replace_var,
            template
        )
        
        # Handle simple variable substitutions
        template = re.sub(
            r'\{\{(\w+)\}\}',
            lambda m: str(variables.get(m.group(1), '')),
            template
        )
        
        return template
    
    def render_template(self, template_config: Dict, data: Dict = None) -> Dict:
        """Render a complete template with data.
        
        Args:
            template_config: Template configuration dictionary.
            data: Data to fill template with.
            
        Returns:
            Rendered template output.
        """
        if data is None:
            data = {}
        
        result = {}
        
        for key, value in template_config.items():
            if isinstance(value, str):
                result[key] = self.render(value, data)
            elif isinstance(value, dict):
                result[key] = self.render_template(value, data)
            else:
                result[key] = value
        
        return result


if __name__ == '__main__':
    # Test template engine
    engine = TemplateEngine()
    
    print("Template Engine Test:")
    
    # Simple substitution
    template = "Hello, {{name}}! Welcome to {{channel}}."
    result = engine.render(template, {'name': 'John', 'channel': 'TechChannel'})
    print(f"\nSimple: {result}")
    
    # Conditional
    template = "{% if show_greeting %}Welcome!{% endif %} Enjoy your stay."
    result = engine.render(template, {'show_greeting': True})
    print(f"\nConditional (true): {result}")
    
    template = "{% if show_greeting %}Welcome!{% endif %} Enjoy your stay."
    result = engine.render(template, {'show_greeting': False})
    print(f"Conditional (false): {result}")
    
    # Loop
    template = "Tags: {% for tag in tags %}{{tag}} {% endfor %}"
    result = engine.render(template, {'tags': ['python', 'tutorial', 'beginner']})
    print(f"\nLoop: {result}")
    
    # Functions
    template = "Title: {{title|upper}}, Author: {{author|title}}"
    result = engine.render(template, {'title': 'python basics', 'author': 'john doe'})
    print(f"\nFunctions: {result}")
    
    # Join
    template = "Tags: {{tags|join(', ')}}"
    result = engine.render(template, {'tags': ['python', 'tutorial']})
    print(f"Join: {result}")
    
    # Default
    template = "Author: {{author|default('Unknown')}}"
    result = engine.render(template, {})
    print(f"Default: {result}")
