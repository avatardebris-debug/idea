"""
Sequencing Package - Integrated Learning Sequencing System

This package provides a comprehensive learning sequencing system that combines:
- Progress tracking and management
- Accountability mechanisms (stakes)
- Adaptive sequencing based on performance

Main Classes:
    LearningSequencer: Integrated learning sequencing system
    ProgressManager: Manages learning progress tracking
    StakesSystem: Manages accountability mechanisms
    AdaptiveSequencer: Manages adaptive learning sequences

Usage:
    from sequencing import LearningSequencer
    
    sequencer = LearningSequencer()
    sequencer.record_progress("concept_1", 85, 30)
    recommendations = sequencer.get_recommendations()
"""

from .sequencing import (
    LearningSequencer,
    create_learning_sequencer,
    LearningProgress
)
from .progress_tracker import (
    ProgressManager,
    ConceptProgress,
    LearningSession,
    LearningGoal,
    ProgressStatus,
    ConceptDifficulty
)
from .stakes import (
    StakesSystem,
    StakesGoal,
    StakesRecord,
    PublicCommitment,
    FinancialPenalty,
    AccountabilityPartner,
    StakesType,
    StakesLevel
)
from .adaptive_sequencer import (
    AdaptiveSequencer,
    PerformanceMetrics,
    SequenceRecommendation,
    LearningSequence,
    PerformanceLevel,
    SequenceStrategy
)

__version__ = "1.0.0"
__all__ = [
    # Main classes
    "LearningSequencer",
    "ProgressManager",
    "StakesSystem",
    "AdaptiveSequencer",
    
    # Data classes
    "LearningProgress",
    "ProgressRecord",
    "StakesGoal",
    "StakesRecord",
    "PublicCommitment",
    "FinancialPenalty",
    "AccountabilityPartner",
    "PerformanceMetrics",
    "SequenceRecommendation",
    "LearningSequence",
    
    # Enums
    "StakesType",
    "StakesLevel",
    "PerformanceLevel",
    "SequenceStrategy",
    
    # Factory function
    "create_learning_sequencer"
]
