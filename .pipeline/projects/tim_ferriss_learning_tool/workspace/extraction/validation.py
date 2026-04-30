"""
Extraction Validator - Validates extraction results for completeness and consistency.

This module provides validation logic to ensure that extraction results meet
quality standards and contain all required information.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during validation."""
    severity: ValidationSeverity
    field: str
    message: str
    details: Optional[str] = None


@dataclass
class ValidationResults:
    """Results of a validation operation."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    
    @property
    def errors(self) -> List[ValidationIssue]:
        """Get all error-level issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get all warning-level issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]
    
    @property
    def info_messages(self) -> List[ValidationIssue]:
        """Get all info-level issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.INFO]
    
    def add_error(self, field: str, message: str, details: Optional[str] = None):
        """Add an error-level validation issue."""
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR,
            field=field,
            message=message,
            details=details
        ))
        self.is_valid = False
    
    def add_warning(self, field: str, message: str, details: Optional[str] = None):
        """Add a warning-level validation issue."""
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            field=field,
            message=message,
            details=details
        ))
    
    def add_info(self, field: str, message: str, details: Optional[str] = None):
        """Add an info-level validation issue."""
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            field=field,
            message=message,
            details=details
        ))


class ExtractionValidator:
    """
    Validates extraction results for completeness and consistency.
    
    Performs validation checks on:
    - Vital concepts extraction results
    - Learning patterns extraction results
    - Learning outline extraction results
    - Complete extraction pipeline results
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the validator.
        
        Args:
            strict_mode: If True, validation will be more strict and fail on warnings.
        """
        self.strict_mode = strict_mode
    
    def validate_extraction(self, result: Any) -> ValidationResults:
        """
        Validate an extraction pipeline result.
        
        Args:
            result: The extraction pipeline result to validate.
        
        Returns:
            ValidationResults containing validation status and issues.
        """
        validation = ValidationResults(is_valid=True)
        
        # Check if result exists
        if result is None:
            validation.add_error("result", "Extraction result is None")
            return validation
        
        # Check topic_name
        if not hasattr(result, 'topic_name') or not result.topic_name:
            validation.add_error("topic_name", "Topic name is missing or empty")
        elif not isinstance(result.topic_name, str) or len(result.topic_name.strip()) == 0:
            validation.add_error("topic_name", "Topic name must be a non-empty string")
        
        # Validate vital concepts
        if hasattr(result, 'vital_concepts'):
            vital_validation = self._validate_vital_concepts(result.vital_concepts)
            validation.issues.extend(vital_validation.issues)
        
        # Validate learning patterns
        if hasattr(result, 'learning_patterns'):
            patterns_validation = self._validate_learning_patterns(result.learning_patterns)
            validation.issues.extend(patterns_validation.issues)
        
        # Validate learning outline
        if hasattr(result, 'learning_outline'):
            outline_validation = self._validate_learning_outline(result.learning_outline)
            validation.issues.extend(outline_validation.issues)
        
        # Check strict mode
        if self.strict_mode and validation.warnings:
            validation.is_valid = False
        
        return validation
    
    def _validate_vital_concepts(self, vital_concepts: Any) -> ValidationResults:
        """
        Validate vital concepts list.
        
        Args:
            vital_concepts: List of vital concepts to validate.
        
        Returns:
            ValidationResults for vital concepts.
        """
        validation = ValidationResults(is_valid=True)
        
        if vital_concepts is None:
            validation.add_warning("vital_concepts", "Vital concepts is None")
            return validation
        
        if not isinstance(vital_concepts, (list, tuple)):
            validation.add_error("vital_concepts", "Vital concepts must be a list or tuple")
            return validation
        
        if len(vital_concepts) == 0:
            validation.add_warning("vital_concepts", "Vital concepts list is empty")
            return validation
        
        # Validate each vital concept
        for i, concept in enumerate(vital_concepts):
            concept_prefix = f"vital_concepts[{i}]"
            
            # Check if concept has required attributes
            if hasattr(concept, 'name'):
                if not concept.name or not isinstance(concept.name, str):
                    validation.add_error(concept_prefix, "Concept name is missing or invalid")
            elif isinstance(concept, dict):
                if 'name' not in concept or not concept['name']:
                    validation.add_error(concept_prefix, "Concept name is missing or empty")
            else:
                validation.add_warning(concept_prefix, "Concept structure unclear")
            
            # Check for impact_score if available
            if hasattr(concept, 'impact_score'):
                if not isinstance(concept.impact_score, (int, float)):
                    validation.add_error(concept_prefix, "Impact score must be a number")
            elif isinstance(concept, dict) and 'impact_score' in concept:
                if not isinstance(concept['impact_score'], (int, float)):
                    validation.add_error(concept_prefix, "Impact score must be a number")
        
        return validation
    
    def _validate_learning_patterns(self, learning_patterns: Any) -> ValidationResults:
        """
        Validate learning patterns list.
        
        Args:
            learning_patterns: List of learning patterns to validate.
        
        Returns:
            ValidationResults for learning patterns.
        """
        validation = ValidationResults(is_valid=True)
        
        if learning_patterns is None:
            validation.add_warning("learning_patterns", "Learning patterns is None")
            return validation
        
        if not isinstance(learning_patterns, (list, tuple)):
            validation.add_error("learning_patterns", "Learning patterns must be a list or tuple")
            return validation
        
        if len(learning_patterns) == 0:
            validation.add_info("learning_patterns", "Learning patterns list is empty")
            return validation
        
        # Validate each learning pattern
        for i, pattern in enumerate(learning_patterns):
            pattern_prefix = f"learning_patterns[{i}]"
            
            # Check if pattern has required attributes
            if hasattr(pattern, 'pattern_name'):
                if not pattern.pattern_name or not isinstance(pattern.pattern_name, str):
                    validation.add_error(pattern_prefix, "Pattern name is missing or invalid")
            elif isinstance(pattern, dict):
                if 'pattern_name' not in pattern or not pattern['pattern_name']:
                    validation.add_error(pattern_prefix, "Pattern name is missing or empty")
            
            # Check for pattern_type if available
            if hasattr(pattern, 'pattern_type'):
                if not pattern.pattern_type:
                    validation.add_warning(pattern_prefix, "Pattern type is missing")
            elif isinstance(pattern, dict) and 'pattern_type' in pattern:
                if not pattern['pattern_type']:
                    validation.add_warning(pattern_prefix, "Pattern type is missing")
        
        return validation
    
    def _validate_learning_outline(self, learning_outline: Any) -> ValidationResults:
        """
        Validate learning outline structure.
        
        Args:
            learning_outline: Learning outline to validate.
        
        Returns:
            ValidationResults for learning outline.
        """
        validation = ValidationResults(is_valid=True)
        
        if learning_outline is None:
            validation.add_error("learning_outline", "Learning outline is None")
            return validation
        
        if isinstance(learning_outline, dict):
            # Validate dict structure
            if 'topic_name' not in learning_outline:
                validation.add_warning("learning_outline", "Learning outline missing topic_name")
            
            if 'learning_modules' not in learning_outline:
                validation.add_error("learning_outline", "Learning outline missing learning_modules")
            elif not isinstance(learning_outline['learning_modules'], (list, tuple)):
                validation.add_error("learning_outline", "Learning modules must be a list")
            elif len(learning_outline['learning_modules']) == 0:
                validation.add_warning("learning_outline", "Learning modules list is empty")
            
            if 'module_sequence' not in learning_outline:
                validation.add_warning("learning_outline", "Learning outline missing module_sequence")
            
            if 'time_estimates' not in learning_outline:
                validation.add_warning("learning_outline", "Learning outline missing time_estimates")
            
            # Validate each module
            for i, module in enumerate(learning_outline.get('learning_modules', [])):
                module_prefix = f"learning_outline.learning_modules[{i}]"
                
                if isinstance(module, dict):
                    if 'module_name' not in module:
                        validation.add_error(module_prefix, "Module name is missing")
                    if 'learning_objectives' not in module:
                        validation.add_warning(module_prefix, "Learning objectives are missing")
                elif hasattr(module, 'module_name'):
                    if not module.module_name:
                        validation.add_error(module_prefix, "Module name is missing or empty")
                else:
                    validation.add_warning(module_prefix, "Module structure unclear")
        
        elif hasattr(learning_outline, 'learning_modules'):
            # Validate object structure
            if not hasattr(learning_outline, 'topic_name'):
                validation.add_warning("learning_outline", "Learning outline missing topic_name")
            
            if len(learning_outline.learning_modules) == 0:
                validation.add_warning("learning_outline", "Learning modules list is empty")
            
            # Validate each module
            for i, module in enumerate(learning_outline.learning_modules):
                module_prefix = f"learning_outline.learning_modules[{i}]"
                
                if hasattr(module, 'module_name'):
                    if not module.module_name:
                        validation.add_error(module_prefix, "Module name is missing or empty")
                else:
                    validation.add_warning(module_prefix, "Module structure unclear")
        else:
            validation.add_error("learning_outline", "Learning outline has unknown structure")
        
        return validation
    
    def validate_vital_concepts_only(self, vital_concepts: Any) -> ValidationResults:
        """
        Validate only vital concepts.
        
        Args:
            vital_concepts: Vital concepts to validate.
        
        Returns:
            ValidationResults for vital concepts.
        """
        return self._validate_vital_concepts(vital_concepts)
    
    def validate_learning_patterns_only(self, learning_patterns: Any) -> ValidationResults:
        """
        Validate only learning patterns.
        
        Args:
            learning_patterns: Learning patterns to validate.
        
        Returns:
            ValidationResults for learning patterns.
        """
        return self._validate_learning_patterns(learning_patterns)
    
    def validate_learning_outline_only(self, learning_outline: Any) -> ValidationResults:
        """
        Validate only learning outline.
        
        Args:
            learning_outline: Learning outline to validate.
        
        Returns:
            ValidationResults for learning outline.
        """
        return self._validate_learning_outline(learning_outline)
    
    def generate_validation_report(self, validation: ValidationResults) -> str:
        """
        Generate a human-readable validation report.
        
        Args:
            validation: ValidationResults to report on.
        
        Returns:
            Formatted validation report string.
        """
        lines = [
            "=" * 60,
            "EXTRACTION VALIDATION REPORT",
            "=" * 60,
            f"Status: {'✓ PASSED' if validation.is_valid else '✗ FAILED'}",
            f"Total Issues: {len(validation.issues)}",
            f"  Errors: {len(validation.errors)}",
            f"  Warnings: {len(validation.warnings)}",
            f"  Info: {len(validation.info_messages)}",
            ""
        ]
        
        if validation.errors:
            lines.append("ERRORS:")
            for issue in validation.errors:
                lines.append(f"  ✗ [{issue.field}] {issue.message}")
                if issue.details:
                    lines.append(f"    Details: {issue.details}")
            lines.append("")
        
        if validation.warnings:
            lines.append("WARNINGS:")
            for issue in validation.warnings:
                lines.append(f"  ⚠ [{issue.field}] {issue.message}")
                if issue.details:
                    lines.append(f"    Details: {issue.details}")
            lines.append("")
        
        if validation.info_messages:
            lines.append("INFO:")
            for issue in validation.info_messages:
                lines.append(f"  ℹ [{issue.field}] {issue.message}")
                if issue.details:
                    lines.append(f"    Details: {issue.details}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
