"""
Summary Generator for the 80/20 Learning Extraction Pipeline.

This module provides utilities for generating human-readable summaries
of extraction results in various formats.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from extraction.integration.orchestrator import ExtractionResult


class SummaryGenerator:
    """
    Generates human-readable summaries of extraction results.
    
    Supports multiple output formats including markdown, plain text,
    and structured reports.
    """
    
    def __init__(self, result: Optional[ExtractionResult] = None):
        """
        Initialize the summary generator.
        
        Args:
            result: ExtractionResult to generate summary from.
        """
        self.result = result
    
    def generate_markdown_summary(self) -> str:
        """
        Generate a comprehensive markdown summary.
        
        Returns:
            Markdown formatted summary string.
        """
        lines = [
            f"# Learning Extraction Summary: {self.result.topic_name}",
            "",
            f"**Extraction Timestamp:** {self.result.extraction_timestamp}",
            "",
            "## Content Overview",
            "",
            f"{self.result.content_summary.get('summary_text', 'No summary available')}",
            "",
            "### Key Points",
            ""
        ]
        
        for i, point in enumerate(self.result.content_summary.get('key_points', []), 1):
            lines.append(f"{i}. {point}")
        
        lines.extend([
            "",
            "## Vital Concepts (The 20%)",
            ""
        ])
        
        for i, concept in enumerate(self.result.vital_concepts, 1):
            lines.append(f"### {i}. {concept}")
            lines.append("")
        
        lines.extend([
            "",
            "## Learning Patterns",
            ""
        ])
        
        for opp in self.result.pattern_extraction.get('compression_opportunities', []):
            lines.append(f"- **{opp['opportunity']}**: {opp['description']}")
            if opp.get('example'):
                lines.append(f"  - *Example*: {opp['example']}")
            lines.append("")
        
        for pattern in self.result.pattern_extraction.get('abstraction_patterns', []):
            lines.append(f"- **{pattern['pattern']}**: {pattern['description']}")
            if pattern.get('examples'):
                lines.append(f"  - *Examples*: {', '.join(pattern['examples'])}")
            lines.append("")
        
        for model in self.result.pattern_extraction.get('mental_models', []):
            lines.append(f"- **{model['model']}**: {model['description']}")
            if model.get('application'):
                lines.append(f"  - *Application*: {model['application']}")
            lines.append("")
        
        lines.extend([
            "## Learning Outline",
            ""
        ])
        
        for module in self.result.learning_outline.get('learning_modules', []):
            lines.append(f"### Module {module['module_number']}: {module['title']}")
            lines.append(f"**Estimated Time**: {module['estimated_time']}")
            lines.append("")
            
            if module.get('objectives'):
                lines.append("**Objectives**:")
                for obj in module['objectives']:
                    lines.append(f"- {obj}")
                lines.append("")
            
            if module.get('key_concepts'):
                lines.append("**Key Concepts**:")
                for concept in module['key_concepts']:
                    lines.append(f"- {concept}")
                lines.append("")
            
            if module.get('exercises'):
                lines.append("**Exercises**:")
                for exercise in module['exercises']:
                    lines.append(f"- {exercise}")
                lines.append("")
        
        lines.extend([
            "## Summary Statistics",
            "",
            f"- **Total Vital Concepts**: {len(self.result.vital_concepts)}",
            f"- **Compression Opportunities**: {len(self.result.pattern_extraction.get('compression_opportunities', []))}",
            f"- **Abstraction Patterns**: {len(self.result.pattern_extraction.get('abstraction_patterns', []))}",
            f"- **Mental Models**: {len(self.result.pattern_extraction.get('mental_models', []))}",
            f"- **Learning Modules**: {len(self.result.learning_outline.get('learning_modules', []))}",
            ""
        ])
        
        return "\n".join(lines)
    
    def generate_plain_text_summary(self) -> str:
        """
        Generate a plain text summary.
        
        Returns:
            Plain text summary string.
        """
        lines = [
            f"LEARNING EXTRACTION SUMMARY: {self.result.topic_name}",
            "=" * 60,
            "",
            f"Extraction Timestamp: {self.result.extraction_timestamp}",
            "",
            "CONTENT OVERVIEW",
            "-" * 40,
            self.result.content_summary.get('summary_text', 'No summary available'),
            "",
            "KEY POINTS",
            "-" * 40
        ]
        
        for i, point in enumerate(self.result.content_summary.get('key_points', []), 1):
            lines.append(f"{i}. {point}")
        
        lines.extend([
            "",
            "VITAL CONCEPTS (THE 20%)",
            "-" * 40
        ])
        
        for i, concept in enumerate(self.result.vital_concepts, 1):
            lines.append(f"{i}. {concept}")
        
        lines.extend([
            "",
            "LEARNING PATTERNS",
            "-" * 40,
            "",
            "COMPRESSION OPPORTUNITIES"
        ])
        
        for opp in self.result.pattern_extraction.get('compression_opportunities', []):
            lines.append(f"- {opp['opportunity']}: {opp['description']}")
            if opp.get('example'):
                lines.append(f"  Example: {opp['example']}")
        
        lines.extend([
            "",
            "ABSTRACTION PATTERNS"
        ])
        
        for pattern in self.result.pattern_extraction.get('abstraction_patterns', []):
            lines.append(f"- {pattern['pattern']}: {pattern['description']}")
            if pattern.get('examples'):
                lines.append(f"  Examples: {', '.join(pattern['examples'])}")
        
        lines.extend([
            "",
            "MENTAL MODELS"
        ])
        
        for model in self.result.pattern_extraction.get('mental_models', []):
            lines.append(f"- {model['model']}: {model['description']}")
            if model.get('application'):
                lines.append(f"  Application: {model['application']}")
        
        lines.extend([
            "",
            "LEARNING OUTLINE",
            "-" * 40
        ])
        
        for module in self.result.learning_outline.get('learning_modules', []):
            lines.append(f"\nModule {module['module_number']}: {module['title']}")
            lines.append(f"Estimated Time: {module['estimated_time']}")
            
            if module.get('objectives'):
                lines.append("Objectives:")
                for obj in module['objectives']:
                    lines.append(f"  - {obj}")
            
            if module.get('key_concepts'):
                lines.append("Key Concepts:")
                for concept in module['key_concepts']:
                    lines.append(f"  - {concept}")
            
            if module.get('exercises'):
                lines.append("Exercises:")
                for exercise in module['exercises']:
                    lines.append(f"  - {exercise}")
        
        lines.extend([
            "",
            "SUMMARY STATISTICS",
            "-" * 40,
            f"Total Vital Concepts: {len(self.result.vital_concepts)}",
            f"Compression Opportunities: {len(self.result.pattern_extraction.get('compression_opportunities', []))}",
            f"Abstraction Patterns: {len(self.result.pattern_extraction.get('abstraction_patterns', []))}",
            f"Mental Models: {len(self.result.pattern_extraction.get('mental_models', []))}",
            f"Learning Modules: {len(self.result.learning_outline.get('learning_modules', []))}",
            ""
        ])
        
        return "\n".join(lines)
    
    def generate_quick_summary(self) -> str:
        """
        Generate a quick, concise summary.
        
        Returns:
            Quick summary string.
        """
        return f"""
QUICK SUMMARY: {self.result.topic_name}
{'=' * 40}

VITAL CONCEPTS ({len(self.result.vital_concepts)} total):
{chr(10).join([f'  • {c}' for c in self.result.vital_concepts])}

LEARNING MODULES ({len(self.result.learning_outline.get('learning_modules', []))} total):
{chr(10).join([f'  • {m["title"]} ({m["estimated_time"]})' for m in self.result.learning_outline.get('learning_modules', [])])}

PATTERNS IDENTIFIED:
  Compression Opportunities: {len(self.result.pattern_extraction.get('compression_opportunities', []))}
  Abstraction Patterns: {len(self.result.pattern_extraction.get('abstraction_patterns', []))}
  Mental Models: {len(self.result.pattern_extraction.get('mental_models', []))}
"""
    
    def generate_report(
        self,
        output_path: Optional[str] = None,
        format: str = "markdown"
    ) -> str:
        """
        Generate and optionally save a summary report.
        
        Args:
            output_path: Optional path to save the report.
            format: Output format ('markdown' or 'text').
        
        Returns:
            Generated summary string.
        """
        if format == "markdown":
            summary = self.generate_markdown_summary()
        elif format == "text":
            summary = self.generate_plain_text_summary()
        else:
            summary = self.generate_quick_summary()
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary)
        
        return summary
    
    def generate_comparison_summary(
        self,
        other_results: List['ExtractionResult']
    ) -> str:
        """
        Generate a comparison summary across multiple extractions.
        
        Args:
            other_results: List of other ExtractionResults to compare.
        
        Returns:
            Comparison summary string.
        """
        all_results = [self.result] + other_results
        
        lines = [
            f"COMPARISON SUMMARY: {self.result.topic_name}",
            "",
            "EXTRACTION METRICS",
            "-" * 40
        ]
        
        for result in all_results:
            lines.append(f"\n{result.topic_name} ({result.extraction_timestamp})")
            lines.append(f"  Vital Concepts: {len(result.vital_concepts)}")
            lines.append(f"  Compression Opportunities: {len(result.pattern_extraction.get('compression_opportunities', []))}")
            lines.append(f"  Abstraction Patterns: {len(result.pattern_extraction.get('abstraction_patterns', []))}")
            lines.append(f"  Mental Models: {len(result.pattern_extraction.get('mental_models', []))}")
            lines.append(f"  Learning Modules: {len(result.learning_outline.get('learning_modules', []))}")
        
        return "\n".join(lines)
