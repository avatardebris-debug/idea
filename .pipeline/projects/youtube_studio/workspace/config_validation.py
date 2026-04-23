"""Configuration validation for YouTube Studio.

This module provides robust configuration validation with support for
type checking, range validation, and custom validators.
"""

from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import fields, is_dataclass
import re


class ValidationError(Exception):
    """Exception raised for configuration validation errors."""
    
    def __init__(self, message: str, field: str = None):
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Configuration field that failed validation
        """
        self.field = field
        self.message = message
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format the error message."""
        if self.field:
            return f"Validation error in '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class ConfigValidator:
    """Configuration validator with support for various validation rules."""
    
    def __init__(self):
        """Initialize the validator."""
        self._validators: Dict[str, List[Callable[[Any], bool]]] = {}
        self._messages: Dict[str, str] = {}
        self._errors: List[ValidationError] = []
    
    def add_validator(
        self,
        field: str,
        validator: Callable[[Any], bool],
        message: str = 'Validation failed'
    ) -> 'ConfigValidator':
        """Add a custom validator for a field.
        
        Args:
            field: Field name to validate
            validator: Validation function that returns True if valid
            message: Error message if validation fails
            
        Returns:
            Self for method chaining
        """
        if field not in self._validators:
            self._validators[field] = []
        
        self._validators[field].append(validator)
        self._messages[field] = message
        return self
    
    def validate_range(
        self,
        field: str,
        min_value: Any = None,
        max_value: Any = None,
        inclusive: bool = True
    ) -> 'ConfigValidator':
        """Add range validation for a field.
        
        Args:
            field: Field name to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            inclusive: Whether to include min/max in range
            
        Returns:
            Self for method chaining
        """
        def validator(value: Any) -> bool:
            if value is None:
                return True
            
            if min_value is not None:
                if inclusive:
                    if value < min_value:
                        return False
                else:
                    if value <= min_value:
                        return False
            
            if max_value is not None:
                if inclusive:
                    if value > max_value:
                        return False
                else:
                    if value >= max_value:
                        return False
            
            return True
        
        self.add_validator(field, validator)
        return self
    
    def validate_length(
        self,
        field: str,
        min_length: int = None,
        max_length: int = None
    ) -> 'ConfigValidator':
        """Add length validation for string/list fields.
        
        Args:
            field: Field name to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            
        Returns:
            Self for method chaining
        """
        def validator(value: Any) -> bool:
            if value is None:
                return True
            
            if not isinstance(value, (str, list)):
                return False
            
            length = len(value)
            
            if min_length is not None and length < min_length:
                return False
            
            if max_length is not None and length > max_length:
                return False
            
            return True
        
        self.add_validator(field, validator)
        return self
    
    def validate_type(
        self,
        field: str,
        expected_type: type,
        allow_none: bool = True
    ) -> 'ConfigValidator':
        """Add type validation for a field.
        
        Args:
            field: Field name to validate
            expected_type: Expected type
            allow_none: Whether None is acceptable
            
        Returns:
            Self for method chaining
        """
        def validator(value: Any) -> bool:
            if value is None:
                return allow_none
            
            return isinstance(value, expected_type)
        
        self.add_validator(field, validator)
        return self
    
    def validate_required(self, field: str) -> 'ConfigValidator':
        """Mark a field as required.
        
        Args:
            field: Field name to validate
            
        Returns:
            Self for method chaining
        """
        def validator(value: Any) -> bool:
            return value is not None
        
        self.add_validator(field, validator, message='Required field')
        return self
    
    def validate_enum(
        self,
        field: str,
        allowed_values: List[Any],
        case_sensitive: bool = True
    ) -> 'ConfigValidator':
        """Add enum validation for a field.
        
        Args:
            field: Field name to validate
            allowed_values: List of allowed values
            case_sensitive: Whether validation is case-sensitive
            
        Returns:
            Self for method chaining
        """
        if not case_sensitive:
            allowed_values = [str(v).lower() for v in allowed_values]
        
        def validator(value: Any) -> bool:
            if value is None:
                return True
            
            if not case_sensitive:
                value = str(value).lower()
            
            return value in allowed_values
        
        self.add_validator(field, validator)
        return self
    
    def validate_regex(
        self,
        field: str,
        pattern: str,
        message: str = 'Invalid format'
    ) -> 'ConfigValidator':
        """Add regex validation for a field.
        
        Args:
            field: Field name to validate
            pattern: Regular expression pattern
            message: Error message if validation fails
            
        Returns:
            Self for method chaining
        """
        compiled_pattern = re.compile(pattern)
        
        def validator(value: Any) -> bool:
            if value is None:
                return True
            
            if not isinstance(value, str):
                return False
            
            return bool(compiled_pattern.match(value))
        
        self.add_validator(field, validator, message=message)
        return self
    
    def validate(self, config: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """Validate a configuration dictionary.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        self._errors = []
        
        for field, validators in self._validators.items():
            value = config.get(field)
            
            for validator in validators:
                try:
                    if not validator(value):
                        error = ValidationError(
                            self._messages.get(field, 'Validation failed'),
                            field
                        )
                        self._errors.append(error)
                        break
                except Exception as e:
                    error = ValidationError(
                        f"Validator error: {str(e)}",
                        field
                    )
                    self._errors.append(error)
        
        return len(self._errors) == 0, self._errors


def validate_seo_config(seo_config: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
    """Validate SEO configuration.
    
    Args:
        seo_config: SEO configuration dictionary
        
    Returns:
        Tuple of (is_valid, list of errors)
    """
    validator = ConfigValidator()
    
    validator.validate_range('max_title_length', min_value=10, max_value=200)
    validator.validate_range('min_title_length', min_value=10, max_value=150)
    validator.validate_range('max_keywords', min_value=1, max_value=100)
    validator.validate_range('min_relevance_score', min_value=0.0, max_value=1.0)
    validator.validate_range('title_length_weight', min_value=0.0, max_value=1.0)
    validator.validate_range('keyword_count_weight', min_value=0.0, max_value=1.0)
    validator.validate_range('keyword_diversity_weight', min_value=0.0, max_value=1.0)
    validator.validate_range('keyword_match_weight', min_value=0.0, max_value=1.0)
    validator.validate_range('content_relevance_weight', min_value=0.0, max_value=1.0)
    
    return validator.validate(seo_config)


def validate_thumbnail_config(thumbnail_config: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
    """Validate thumbnail configuration.
    
    Args:
        thumbnail_config: Thumbnail configuration dictionary
        
    Returns:
        Tuple of (is_valid, list of errors)
    """
    validator = ConfigValidator()
    
    validator.validate_enum(
        'default_style',
        ['bold', 'minimal', 'playful', 'professional'],
        case_sensitive=False
    )
    validator.validate_enum(
        'default_size',
        ['small', 'medium', 'large'],
        case_sensitive=False
    )
    
    validator.validate_length('styles', min_length=1, max_length=20)
    validator.validate_length('sizes', min_length=1, max_length=20)
    validator.validate_length('color_schemes', min_length=1, max_length=20)
    
    return validator.validate(thumbnail_config)


def validate_transcript_config(transcript_config: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
    """Validate transcript configuration.
    
    Args:
        transcript_config: Transcript configuration dictionary
        
    Returns:
        Tuple of (is_valid, list of errors)
    """
    validator = ConfigValidator()
    
    validator.validate_enum(
        'default_format',
        ['srt', 'vtt', 'txt'],
        case_sensitive=False
    )
    validator.validate_enum(
        'supported_formats',
        ['srt', 'vtt', 'txt'],
        case_sensitive=False
    )
    validator.validate_range('timestamp_precision', min_value=100, max_value=10000)
    validator.validate_range('default_duration_seconds', min_value=1, max_value=3600)
    
    return validator.validate(transcript_config)


def validate_template_config(template_config: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
    """Validate template configuration.
    
    Args:
        template_config: Template configuration dictionary
        
    Returns:
        Tuple of (is_valid, list of errors)
    """
    validator = ConfigValidator()
    
    validator.validate_required('template_directory')
    validator.validate_length('template_directory', min_length=1)
    validator.validate_length('file_extension', min_length=1, max_length=10)
    validator.validate_type('auto_load', bool)
    validator.validate_length('required_fields', min_length=1)
    
    return validator.validate(template_config)


def validate_config(config_dict: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
    """Validate complete YouTube Studio configuration.
    
    Args:
        config_dict: Complete configuration dictionary
        
    Returns:
        Tuple of (is_valid, list of errors)
    """
    all_errors: List[ValidationError] = []
    
    # Validate SEO config
    seo_config = config_dict.get('seo', {})
    is_valid, errors = validate_seo_config(seo_config)
    all_errors.extend(errors)
    
    # Validate thumbnail config
    thumbnail_config = config_dict.get('thumbnail', {})
    is_valid, errors = validate_thumbnail_config(thumbnail_config)
    all_errors.extend(errors)
    
    # Validate transcript config
    transcript_config = config_dict.get('transcript', {})
    is_valid, errors = validate_transcript_config(transcript_config)
    all_errors.extend(errors)
    
    # Validate template config
    template_config = config_dict.get('templates', {})
    is_valid, errors = validate_template_config(template_config)
    all_errors.extend(errors)
    
    # Validate general config
    validator = ConfigValidator()
    validator.validate_enum('log_level', ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    validator.validate_type('default_category', str)
    validator.validate_length('supported_formats', min_length=1)
    
    is_valid, errors = validator.validate(config_dict)
    all_errors.extend(errors)
    
    return len(all_errors) == 0, all_errors


if __name__ == '__main__':
    # Test configuration validation
    
    # Valid config
    valid_config = {
        'seo': {
            'max_title_length': 60,
            'min_title_length': 30,
            'max_keywords': 15,
            'min_relevance_score': 0.3,
            'title_length_weight': 0.3,
            'keyword_count_weight': 0.3,
            'keyword_diversity_weight': 0.2,
            'keyword_match_weight': 0.1,
            'content_relevance_weight': 0.1
        },
        'thumbnail': {
            'default_style': 'bold',
            'default_size': 'large',
            'styles': ['bold', 'minimal', 'playful', 'professional'],
            'sizes': ['small', 'medium', 'large'],
            'color_schemes': ['default', 'dark', 'light', 'gradient']
        },
        'transcript': {
            'supported_formats': ['srt', 'vtt', 'txt'],
            'default_format': 'srt',
            'timestamp_precision': 1000,
            'auto_duration': True,
            'default_duration_seconds': 30
        },
        'templates': {
            'template_directory': './templates',
            'file_extension': '.json',
            'auto_load': True,
            'required_fields': ['title', 'description', 'tags']
        },
        'supported_formats': ['mp4', 'avi', 'mov'],
        'default_category': 'general',
        'log_level': 'INFO'
    }
    
    is_valid, errors = validate_config(valid_config)
    print(f"Valid config test: {'PASSED' if is_valid else 'FAILED'}")
    if not is_valid:
        for error in errors:
            print(f"  - {error}")
    
    # Invalid config (max_title_length too high)
    invalid_config = {
        'seo': {
            'max_title_length': 300,
            'min_title_length': 30,
            'max_keywords': 15,
            'min_relevance_score': 0.3
        },
        'thumbnail': {
            'default_style': 'bold',
            'default_size': 'large'
        },
        'transcript': {
            'supported_formats': ['srt', 'vtt', 'txt'],
            'default_format': 'srt'
        },
        'templates': {
            'template_directory': './templates',
            'file_extension': '.json',
            'auto_load': True,
            'required_fields': ['title', 'description', 'tags']
        }
    }
    
    is_valid, errors = validate_config(invalid_config)
    print(f"Invalid config test: {'PASSED (correctly detected error)' if not is_valid else 'FAILED (should have detected error)'}")
    if not is_valid:
        for error in errors:
            print(f"  - {error}")
