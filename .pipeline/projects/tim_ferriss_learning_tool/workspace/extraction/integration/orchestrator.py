"""Integration Orchestrator - Coordinates all extraction components."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

from openai import OpenAI

from extraction.eighty_twenty.vital_extractor import VitalExtractor
from extraction.patterns.learning_patterns import PatternGenerator
from extraction.outline.outline_extractor import OutlineExtractor


@dataclass
class ExtractionResult:
    """Result of the complete extraction pipeline."""
    topic_name: str
    extraction_timestamp: str
    content_summary: Dict[str, Any]
    vital_concepts: List[Dict[str, str]]
    pattern_extraction: Dict[str, Any]
    learning_outline: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "extraction_timestamp": self.extraction_timestamp,
            "content_summary": self.content_summary,
            "vital_concepts": self.vital_concepts,
            "pattern_extraction": self.pattern_extraction,
            "learning_outline": self.learning_outline
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractionResult':
        """Create ExtractionResult from dictionary."""
        return cls(
            topic_name=data.get('topic_name', ''),
            extraction_timestamp=data.get('extraction_timestamp', ''),
            content_summary=data.get('content_summary', {}),
            vital_concepts=data.get('vital_concepts', []),
            pattern_extraction=data.get('pattern_extraction', {}),
            learning_outline=data.get('learning_outline', {})
        )


class ExtractionOrchestrator:
    """
    Legacy orchestrator class for backward compatibility.
    Use LearningExtractionOrchestrator for new code.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.5,
        config_path: Optional[str] = None
    ):
        """
        Initialize the extraction pipeline.
        
        Args:
            api_key: OpenAI API key. If None, will try to read from OPENAI_API_KEY env var.
            model: LLM model to use for extraction.
            temperature: Temperature parameter for LLM responses.
            config_path: Path to learning profile configuration file.
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.config_path = config_path
        
        # Initialize extractors
        self.vital_extractor = VitalExtractor(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
        
        self.pattern_generator = PatternGenerator(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
        
        self.outline_generator = OutlineExtractor(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
    
    def extract_vital_concepts(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Extract vital concepts from content.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
        
        Returns:
            Dictionary containing vital concepts and metadata.
        """
        return self.vital_extractor.extract_vital_concepts(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
    
    def extract_patterns(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Extract learning patterns from content.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
        
        Returns:
            Dictionary containing learning patterns and metadata.
        """
        return self.pattern_generator.extract_patterns(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
    
    def extract_outline(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        vital_concepts: Optional[List[str]] = None,
        pattern_extraction: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured learning outline.
        
        Args:
            topic_name: Name of the topic being extracted.
            content_summary: Summary of the main content.
            vital_concepts: List of vital concepts (optional).
            pattern_extraction: Extracted patterns (optional).
        
        Returns:
            Dictionary containing learning modules and metadata.
        """
        return self.outline_generator.extract_outline(
            topic_name=topic_name,
            content_summary=content_summary,
            vital_concepts=vital_concepts,
            pattern_extraction=pattern_extraction
        )
    
    def run_extraction(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> ExtractionResult:
        """
        Run the complete 80/20 extraction pipeline.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
        
        Returns:
            ExtractionResult containing all extracted information.
        """
        # Step 1: Extract vital concepts
        print(f"Extracting vital concepts for '{topic_name}'...")
        vital_result = self.extract_vital_concepts(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        # Handle both dict and dataclass result types
        if hasattr(vital_result, 'to_dict'):
            vital_concepts = vital_result.vital_concepts
        elif isinstance(vital_result, dict):
            vital_concepts = vital_result.get('vital_concepts', [])
        else:
            vital_concepts = []
        
        # Step 2: Extract learning patterns
        print(f"Extracting learning patterns for '{topic_name}'...")
        pattern_result = self.extract_patterns(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        # Handle both dict and dataclass result types
        if hasattr(pattern_result, 'to_dict'):
            pattern_extraction = pattern_result.to_dict()
        elif isinstance(pattern_result, dict):
            pattern_extraction = pattern_result
        else:
            pattern_extraction = {}
        
        # Step 3: Extract learning outline
        print(f"Creating learning outline for '{topic_name}'...")
        outline_result = self.extract_outline(
            topic_name=topic_name,
            content_summary=content_summary,
            vital_concepts=vital_concepts,
            pattern_extraction=pattern_extraction
        )
        # Handle both dict and dataclass result types
        if hasattr(outline_result, 'to_dict'):
            learning_outline = outline_result.to_dict()
        elif isinstance(outline_result, dict):
            learning_outline = outline_result
        else:
            learning_outline = {}
        
        # Create result
        result = ExtractionResult(
            topic_name=topic_name,
            content_summary=content_summary,
            vital_concepts=vital_concepts,
            pattern_extraction=pattern_extraction,
            learning_outline=learning_outline,
            extraction_timestamp=datetime.now().isoformat()
        )
        
        return result
    
    def save_results(
        self,
        result: ExtractionResult,
        output_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Save extraction result to a file.
        
        Args:
            result: The extraction result to save.
            output_path: Optional path for output file.
        
        Returns:
            Dictionary containing paths to saved files.
        """
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path.cwd() / f"{result.topic_name.replace(' ', '_')}_extraction.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        return {"extraction": str(output_path)}
    
    def validate_extraction(
        self,
        result: ExtractionResult
    ) -> List[str]:
        """
        Validate extraction result for completeness.
        
        Args:
            result: The extraction result to validate.
        
        Returns:
            List of validation issues found.
        """
        issues = []
        
        # Check required fields
        if not result.topic_name:
            issues.append("Missing topic_name")
        
        if not result.content_summary:
            issues.append("Missing content_summary")
        
        if not result.vital_concepts:
            issues.append("Missing vital_concepts")
        
        if not result.pattern_extraction:
            issues.append("Missing pattern_extraction")
        
        if not result.learning_outline:
            issues.append("Missing learning_outline")
        
        return issues


class LearningExtractionOrchestrator:
    """
    Orchestrates the complete 80/20 learning extraction pipeline.
    
    This pipeline:
    1. Extracts vital concepts using frequency analysis
    2. Identifies learning patterns using CAFE framework
    3. Creates structured learning outlines using DESS framework
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.5,
        config_path: Optional[str] = None
    ):
        """
        Initialize the extraction pipeline.
        
        Args:
            api_key: OpenAI API key. If None, will try to read from OPENAI_API_KEY env var.
            model: LLM model to use for extraction.
            temperature: Temperature parameter for LLM responses.
            config_path: Path to learning profile configuration file.
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.config_path = config_path
        
        # Initialize extractors
        self.vital_extractor = VitalExtractor(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
        
        self.pattern_generator = PatternGenerator(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
        
        self.outline_generator = OutlineExtractor(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
    
    def extract_vital_concepts(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Extract vital concepts from content.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
        
        Returns:
            Dictionary containing vital concepts and metadata.
        """
        return self.vital_extractor.extract_vital_concepts(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
    
    def extract_patterns(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Extract learning patterns from content.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
        
        Returns:
            Dictionary containing learning patterns and metadata.
        """
        return self.pattern_generator.extract_patterns(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
    
    def extract_outline(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        vital_concepts: Optional[List[str]] = None,
        pattern_extraction: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured learning outline.
        
        Args:
            topic_name: Name of the topic being extracted.
            content_summary: Summary of the main content.
            vital_concepts: List of vital concepts (optional).
            pattern_extraction: Extracted patterns (optional).
        
        Returns:
            Dictionary containing learning modules and metadata.
        """
        return self.outline_generator.extract_outline(
            topic_name=topic_name,
            content_summary=content_summary,
            vital_concepts=vital_concepts,
            pattern_extraction=pattern_extraction
        )
    
    def run_extraction(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> ExtractionResult:
        """
        Run the complete 80/20 extraction pipeline.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
        
        Returns:
            ExtractionResult containing all extracted information.
        """
        # Step 1: Extract vital concepts
        print(f"Extracting vital concepts for '{topic_name}'...")
        vital_result = self.extract_vital_concepts(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        # Handle both dict and dataclass result types
        if hasattr(vital_result, 'to_dict'):
            vital_concepts = vital_result.vital_concepts
        elif isinstance(vital_result, dict):
            vital_concepts = vital_result.get('vital_concepts', [])
        else:
            vital_concepts = []
        
        # Step 2: Extract learning patterns
        print(f"Extracting learning patterns for '{topic_name}'...")
        pattern_result = self.extract_patterns(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        # Handle both dict and dataclass result types
        if hasattr(pattern_result, 'to_dict'):
            pattern_extraction = pattern_result.to_dict()
        elif isinstance(pattern_result, dict):
            pattern_extraction = pattern_result
        else:
            pattern_extraction = {}
        
        # Step 3: Extract learning outline
        print(f"Creating learning outline for '{topic_name}'...")
        outline_result = self.extract_outline(
            topic_name=topic_name,
            content_summary=content_summary,
            vital_concepts=vital_concepts,
            pattern_extraction=pattern_extraction
        )
        # Handle both dict and dataclass result types
        if hasattr(outline_result, 'to_dict'):
            learning_outline = outline_result.to_dict()
        elif isinstance(outline_result, dict):
            learning_outline = outline_result
        else:
            learning_outline = {}
        
        # Create result
        result = ExtractionResult(
            topic_name=topic_name,
            content_summary=content_summary,
            vital_concepts=vital_concepts,
            pattern_extraction=pattern_extraction,
            learning_outline=learning_outline,
            extraction_timestamp=datetime.now().isoformat()
        )
        
        return result
    
    def save_results(
        self,
        result: ExtractionResult,
        output_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Save extraction result to a file.
        
        Args:
            result: The extraction result to save.
            output_path: Optional path for output file.
        
        Returns:
            Dictionary containing paths to saved files.
        """
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path.cwd() / f"{result.topic_name.replace(' ', '_')}_extraction.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        return {"extraction": str(output_path)}
    
    def validate_extraction(
        self,
        result: ExtractionResult
    ) -> List[str]:
        """
        Validate extraction result for completeness.
        
        Args:
            result: The extraction result to validate.
        
        Returns:
            List of validation issues found.
        """
        issues = []
        
        # Check required fields
        if not result.topic_name:
            issues.append("Missing topic_name")
        
        if not result.content_summary:
            issues.append("Missing content_summary")
        
        if not result.vital_concepts:
            issues.append("Missing vital_concepts")
        
        if not result.pattern_extraction:
            issues.append("Missing pattern_extraction")
        
        if not result.learning_outline:
            issues.append("Missing learning_outline")
        
        return issues
