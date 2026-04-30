"""
Data models for the 80/20 Learning Extraction Pipeline.

This module defines the core data structures used throughout the pipeline.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class VitalConcept:
    """Represents a vital concept extracted from content."""
    concept: str
    importance_score: float
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class CompressionOpportunity:
    """Represents a compression opportunity for faster learning."""
    opportunity: str
    description: str
    example: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class AbstractionPattern:
    """Represents an abstraction pattern for generalization."""
    pattern: str
    description: str
    examples: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class MentalModel:
    """Represents a mental model for conceptual understanding."""
    model: str
    description: str
    application: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class LearningModule:
    """Represents a learning module in the outline."""
    module_number: int
    title: str
    estimated_time: str
    objectives: List[str]
    key_concepts: List[str]
    exercises: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module_number": self.module_number,
            "title": self.title,
            "estimated_time": self.estimated_time,
            "objectives": self.objectives,
            "key_concepts": self.key_concepts,
            "exercises": self.exercises
        }


@dataclass
class ExtractionResult:
    """Complete extraction result containing all extracted information."""
    topic_name: str
    content_summary: Dict[str, Any]
    vital_concepts: List[str]
    pattern_extraction: Dict[str, Any]
    learning_outline: Dict[str, Any]
    extraction_timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, file_path: str) -> None:
        """Save extraction result to a JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
