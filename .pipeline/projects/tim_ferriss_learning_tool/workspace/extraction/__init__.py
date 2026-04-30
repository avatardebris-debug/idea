"""
80/20 Learning Extraction Pipeline

This package provides tools for extracting vital concepts, learning patterns,
and structured learning outlines from content using Tim Ferriss's frameworks.

Modules:
- eighty_twenty.vital_extractor: Extracts vital 20% concepts using frequency analysis
- patterns.learning_patterns: Identifies learning patterns using CAFE framework
- outline.outline_generator: Creates structured learning outlines using DESS framework
- pipeline: Orchestrates the complete extraction pipeline
- integration.orchestrator: Main orchestrator for running the complete extraction pipeline
- integration.summary_generator: Generates human-readable summaries of extraction results
"""

from .pipeline import ExtractionPipeline, ExtractionPipelineResult, create_pipeline
from .eighty_twenty.vital_extractor import VitalExtractor, VitalConcept, ConceptRelationship, VitalExtractionResult
from .patterns.learning_patterns import (
    PatternGenerator,
    PatternExtractionResult,
    LearningPattern,
    CompressionOpportunity,
    EncodingStrategy
)
from .patterns.pattern_extractor import PatternExtractor
from .outline.outline_generator import (
    OutlineGenerator,
    OutlineExtractionResult,
    LearningModule,
    LearningActivity,
    ModuleSequence,
    TimeEstimates
)
from .outline.outline_extractor import OutlineExtractor
from .integration.orchestrator import ExtractionOrchestrator, LearningExtractionOrchestrator, ExtractionResult
from .integration.summary_generator import SummaryGenerator

__version__ = "1.0.0"
__all__ = [
    "ExtractionPipeline",
    "ExtractionPipelineResult",
    "create_pipeline",
    "VitalExtractor",
    "VitalConcept",
    "PatternGenerator",
    "PatternExtractionResult",
    "LearningPattern",
    "CompressionOpportunity",
    "EncodingStrategy",
    "PatternExtractor",
    "OutlineGenerator",
    "OutlineExtractionResult",
    "LearningModule",
    "LearningActivity",
    "ModuleSequence",
    "TimeEstimates",
    "OutlineExtractor",
    "ExtractionOrchestrator",
    "LearningExtractionOrchestrator",
    "ExtractionResult",
    "SummaryGenerator"
]
