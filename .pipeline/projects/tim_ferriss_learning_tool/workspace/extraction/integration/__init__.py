"""
Integration module for the 80/20 Learning Extraction Pipeline.

This module provides integration utilities for orchestrating the extraction pipeline
and generating summaries of extraction results.

Modules:
- orchestrator: Main orchestrator for running the complete extraction pipeline
- summary_generator: Generates human-readable summaries of extraction results
"""

from .orchestrator import ExtractionOrchestrator, LearningExtractionOrchestrator, ExtractionResult
from .summary_generator import SummaryGenerator

__all__ = ["ExtractionOrchestrator", "LearningExtractionOrchestrator", "ExtractionResult", "SummaryGenerator"]
