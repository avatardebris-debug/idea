"""
Editor Module for AI Author Suite.

This module provides comprehensive editing capabilities including:
- Deep content analysis and structural issue detection
- Content reorganization for better flow
- Formatting optimization
- Style enhancement and clarity improvement

Usage:
    from editor import DeepEditor, RestructureTool, FormatOptimizer, StyleEnhancer
    
    # Initialize components
    editor = DeepEditor()
    restructure = RestructureTool()
    formatter = FormatOptimizer()
    style_enhancer = StyleEnhancer()
    
    # Analyze content
    result = editor.analyze_content(chapter_content)
    
    # Generate restructure suggestions
    restructure_result = restructure.analyze(chapter_content)
    
    # Optimize formatting
    format_result = formatter.optimize(chapter_content)
    
    # Enhance style
    style_result = style_enhancer.enhance_content(chapter_content.introduction)
"""

# Import all editor components
from .models import (
    EditResult,
    EditSuggestion,
    SuggestionType,
    SeverityLevel,
    IssueType,
    StructureIssue,
    StyleAnalysis,
    EditorReport,
)
from .deep_editor import DeepEditor
from .restructure_tool import RestructureTool
from .format_optimizer import FormatOptimizer
from .style_enhancer import StyleEnhancer, StyleEnhancementResult

# Export all public classes and functions
__all__ = [
    # Models
    "EditResult",
    "EditSuggestion",
    "SuggestionType",
    "SeverityLevel",
    "IssueType",
    "StructureIssue",
    "StyleAnalysis",
    "EditorReport",
    # Editor classes
    "DeepEditor",
    "RestructureTool",
    "FormatOptimizer",
    "StyleEnhancer",
    "StyleEnhancementResult",
]