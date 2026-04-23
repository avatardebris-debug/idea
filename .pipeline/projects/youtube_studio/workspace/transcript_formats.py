"""
Transcript Formats Module

This module provides transcript format definitions and conversion utilities
for various output formats.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum


class TranscriptFormats(Enum):
    """Supported transcript formats"""
    SRT = 'srt'
    VTT = 'vtt'
    TXT = 'txt'
    JSON = 'json'
    YAML = 'yaml'


# Format specifications
FORMAT_SPECS: Dict[str, Dict] = {
    'srt': {
        'name': 'SubRip Subtitle',
        'extension': 'srt',
        'description': 'Standard subtitle format used by most video players',
        'timestamp_format': 'HH:MM:SS,mmm --> HH:MM:SS,mmm',
        'encoding': 'UTF-8',
        'features': ['timestamps', 'sequence_numbers', 'multi-line support']
    },
    'vtt': {
        'name': 'WebVTT',
        'extension': 'vtt',
        'description': 'Web Video Text Tracks format for web-based video players',
        'timestamp_format': 'HH:MM:SS.mmm --> HH:MM:SS.mmm',
        'encoding': 'UTF-8',
        'features': ['timestamps', 'cue settings', 'HTML support', 'metadata']
    },
    'txt': {
        'name': 'Plain Text',
        'extension': 'txt',
        'description': 'Simple text format with timestamps and sections',
        'timestamp_format': '[HH:MM:SS - HH:MM:SS]',
        'encoding': 'UTF-8',
        'features': ['timestamps', 'section headers', 'readable format']
    },
    'json': {
        'name': 'JSON',
        'extension': 'json',
        'description': 'Structured data format for programmatic access',
        'timestamp_format': 'ISO 8601 or float seconds',
        'encoding': 'UTF-8',
        'features': ['structured data', 'metadata', 'easy parsing', 'validation']
    },
    'yaml': {
        'name': 'YAML',
        'extension': 'yaml',
        'description': 'Human-readable data serialization format',
        'timestamp_format': 'ISO 8601 or float seconds',
        'encoding': 'UTF-8',
        'features': ['human-readable', 'structured', 'validation', 'comments']
    }
}


def format_to_extension(format_name: str) -> str:
    """
    Convert format name to file extension.
    
    Args:
        format_name: Format name or enum value
        
    Returns:
        File extension string
    """
    if isinstance(format_name, TranscriptFormats):
        format_name = format_name.value
    
    format_name = format_name.lower()
    
    if format_name in FORMAT_SPECS:
        return FORMAT_SPECS[format_name]['extension']
    
    # Try to match by extension
    for spec in FORMAT_SPECS.values():
        if spec['extension'] == format_name:
            return spec['extension']
    
    raise ValueError(f"Unknown format: {format_name}")


def get_format_spec(format_name: str) -> Dict:
    """
    Get specifications for a format.
    
    Args:
        format_name: Format name or enum value
        
    Returns:
        Dictionary containing format specifications
    """
    if isinstance(format_name, TranscriptFormats):
        format_name = format_name.value
    
    format_name = format_name.lower()
    
    if format_name in FORMAT_SPECS:
        return FORMAT_SPECS[format_name]
    
    raise ValueError(f"Unknown format: {format_name}")


def is_valid_format(format_name: str) -> bool:
    """
    Check if a format name is valid.
    
    Args:
        format_name: Format name to check
        
    Returns:
        True if format is valid, False otherwise
    """
    try:
        get_format_spec(format_name)
        return True
    except ValueError:
        return False


def get_all_formats() -> List[Dict]:
    """
    Get all supported transcript formats.
    
    Returns:
        List of format specifications
    """
    return [
        {
            'name': spec['name'],
            'extension': spec['extension'],
            'description': spec['description'],
            'features': spec['features']
        }
        for spec in FORMAT_SPECS.values()
    ]


def get_format_by_extension(extension: str) -> Optional[str]:
    """
    Get format name by file extension.
    
    Args:
        extension: File extension to match
        
    Returns:
        Format name or None if not found
    """
    extension = extension.lower().lstrip('.')
    
    for format_name, spec in FORMAT_SPECS.items():
        if spec['extension'] == extension:
            return format_name
    
    return None


def get_supported_features(format_name: str) -> List[str]:
    """
    Get supported features for a format.
    
    Args:
        format_name: Format name
        
    Returns:
        List of feature strings
    """
    spec = get_format_spec(format_name)
    return spec['features']


def get_timestamp_formats(format_name: str) -> str:
    """
    Get timestamp format for a format.
    
    Args:
        format_name: Format name
        
    Returns:
        Timestamp format string
    """
    spec = get_format_spec(format_name)
    return spec['timestamp_format']


def get_recommended_encoding(format_name: str) -> str:
    """
    Get recommended encoding for a format.
    
    Args:
        format_name: Format name
        
    Returns:
        Encoding string
    """
    spec = get_format_spec(format_name)
    return spec['encoding']


def format_description(format_name: str) -> str:
    """
    Get human-readable description for a format.
    
    Args:
        format_name: Format name
        
    Returns:
        Description string
    """
    spec = get_format_spec(format_name)
    return spec['description']


def get_formats_by_feature(feature: str) -> List[str]:
    """
    Get formats that support a specific feature.
    
    Args:
        feature: Feature name to search for
        
    Returns:
        List of format names that support the feature
    """
    matching_formats = []
    
    for format_name, spec in FORMAT_SPECS.items():
        if feature.lower() in [f.lower() for f in spec['features']]:
            matching_formats.append(format_name)
    
    return matching_formats


def get_formats_by_name_pattern(pattern: str) -> List[str]:
    """
    Get formats matching a name pattern.
    
    Args:
        pattern: Pattern to match against format names
        
    Returns:
        List of format names matching the pattern
    """
    pattern_lower = pattern.lower()
    
    return [
        format_name for format_name in FORMAT_SPECS.keys()
        if pattern_lower in format_name.lower()
    ]


def get_format_comparison() -> Dict[str, Dict]:
    """
    Get comparison of all formats.
    
    Returns:
        Dictionary with format comparison data
    """
    comparison = {}
    
    for format_name, spec in FORMAT_SPECS.items():
        comparison[format_name] = {
            'name': spec['name'],
            'extension': spec['extension'],
            'description': spec['description'],
            'features': spec['features'],
            'timestamp_format': spec['timestamp_format'],
            'encoding': spec['encoding']
        }
    
    return comparison


def validate_format_spec(format_name: str) -> Tuple[bool, List[str]]:
    """
    Validate a format specification.
    
    Args:
        format_name: Format name to validate
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    
    try:
        spec = get_format_spec(format_name)
        
        # Check required fields
        required_fields = ['name', 'extension', 'description', 'timestamp_format', 'encoding']
        for field in required_fields:
            if field not in spec or not spec[field]:
                issues.append(f"Missing required field: {field}")
        
        # Check extension format
        if not spec['extension'].startswith('.'):
            issues.append(f"Extension should start with '.': {spec['extension']}")
        
        # Check timestamp format
        if not spec['timestamp_format']:
            issues.append("Timestamp format is required")
        
        # Check encoding
        if not spec['encoding']:
            issues.append("Encoding is required")
        
    except ValueError as e:
        issues.append(str(e))
    
    return len(issues) == 0, issues
