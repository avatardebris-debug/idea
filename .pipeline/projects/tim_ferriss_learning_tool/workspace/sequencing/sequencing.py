"""
Sequencing Module - Integrated Learning Sequencing System

This module provides a comprehensive learning sequencing system that combines:
- Progress tracking and management
- Accountability mechanisms (stakes)
- Adaptive sequencing based on performance

Usage:
    from sequencing import LearningSequencer
    
    sequencer = LearningSequencer()
    
    # Track progress
    sequencer.record_progress("concept_1", 85, 30)
    
    # Set up accountability
    sequencer.create_financial_penalty("concept_1", 50.0)
    
    # Get adaptive recommendations
    recommendations = sequencer.get_recommendations()
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from .progress_tracker import (
    ProgressManager,
    ConceptProgress,
    LearningSession,
    LearningGoal,
    LearningProgress
)
from .stakes import (
    StakesSystem,
    PublicCommitment,
    FinancialPenalty,
    AccountabilityPartner,
    StakesType
)
from .adaptive_sequencer import (
    AdaptiveSequencer,
    PerformanceMetrics,
    SequenceRecommendation,
    PerformanceLevel
)


class LearningSequencer:
    """
    Integrated learning sequencing system.
    
    Combines progress tracking, accountability mechanisms, and adaptive sequencing
    to create a comprehensive learning management system.
    
    Attributes:
        progress_manager: Manages learning progress tracking.
        stakes_system: Manages accountability mechanisms.
        adaptive_sequencer: Manages adaptive learning sequences.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the learning sequencer.
        
        Args:
            config_path: Path to configuration file.
        """
        self.progress_manager = ProgressManager(config_path)
        self.stakes_system = StakesSystem(config_path)
        self.adaptive_sequencer = AdaptiveSequencer(config_path)
        
        # Shared configuration
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load shared configuration."""
        default_config = {
            "auto_save": True,
            "integration_enabled": True
        }
        
        if config_path and Path(config_path).exists():
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    default_config.update(loaded_config)
        
        return default_config
    
    # Progress Tracking Methods
    def record_progress(
        self,
        concept_id: str,
        score: float,
        time_spent_minutes: float,
        difficulty_rating: Optional[float] = None,
        notes: str = ""
    ) -> ConceptProgress:
        """
        Record progress for a learning concept.
        
        Args:
            concept_id: ID of the concept.
            score: Score achieved (0-100).
            time_spent_minutes: Time spent on the concept.
            difficulty_rating: User-rated difficulty (0-10).
            notes: Additional notes.
        
        Returns:
            Updated ConceptProgress object.
        """
        # Record in progress manager
        progress = self.progress_manager.initialize_concept(
            concept_id=concept_id,
            concept_name=concept_id,
            difficulty_level="intermediate"
        )
        
        # Update progress
        progress = self.progress_manager.update_concept_progress(
            concept_id=concept_id,
            mastery_percentage=score,
            score=score,
            study_time=f"{int(time_spent_minutes)} min",
            notes=notes
        )
        
        # Record in adaptive sequencer
        self.adaptive_sequencer.record_performance(
            concept_id=concept_id,
            score=score,
            time_spent=time_spent_minutes,
            difficulty_rating=difficulty_rating
        )
        
        return progress
    
    def get_progress(self, concept_id: str) -> Optional[ConceptProgress]:
        """
        Get progress for a specific concept.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            ConceptProgress object or None.
        """
        return self.progress_manager.get_concept_status(concept_id)
    
    def get_all_progress(self) -> List[ConceptProgress]:
        """
        Get all learning progress records.
        
        Returns:
            List of all ConceptProgress objects.
        """
        return self.progress_manager.get_all_concepts()
    
    # Accountability/Stakes Methods
    def create_public_commitment(
        self,
        goal_id: str,
        goal_description: str,
        deadline: datetime,
        public_platform: str = "social_media",
        audience_size: int = 100,
        notes: str = ""
    ) -> PublicCommitment:
        """
        Create a public commitment for a learning goal.
        
        Args:
            goal_id: ID of the goal.
            goal_description: Description of the goal.
            deadline: Deadline for the goal.
            public_platform: Platform for commitment.
            audience_size: Estimated audience size.
            notes: Additional notes.
        
        Returns:
            Created PublicCommitment object.
        """
        return self.stakes_system.create_public_commitment(
            goal_id=goal_id,
            goal_description=goal_description,
            deadline=deadline,
            public_platform=public_platform,
            audience_size=audience_size,
            notes=notes
        )
    
    def create_financial_penalty(
        self,
        goal_id: str,
        amount: float,
        currency: str = "USD",
        trigger_condition: str = "Not completing learning goal by deadline",
        payout_recipient: str = "charity",
        deadline: Optional[datetime] = None,
        notes: str = ""
    ) -> FinancialPenalty:
        """
        Create a financial penalty for a learning goal.
        
        Args:
            goal_id: ID of the goal.
            amount: Penalty amount.
            currency: Currency code.
            trigger_condition: Condition that triggers penalty.
            payout_recipient: Recipient of penalty payment.
            deadline: Deadline for the goal.
            notes: Additional notes.
        
        Returns:
            Created FinancialPenalty object.
        """
        return self.stakes_system.create_financial_penalty(
            goal_id=goal_id,
            amount=amount,
            currency=currency,
            trigger_condition=trigger_condition,
            payout_recipient=payout_recipient,
            deadline=deadline,
            notes=notes
        )
    
    def add_accountability_partner(
        self,
        goal_id: str,
        partner_name: str,
        partner_email: str,
        relationship_type: str = "peer",
        check_in_frequency: str = "weekly",
        shared_goals: Optional[List[str]] = None,
        communication_method: str = "email",
        notes: str = ""
    ) -> AccountabilityPartner:
        """
        Add an accountability partner for a learning goal.
        
        Args:
            goal_id: ID of the goal.
            partner_name: Name of the partner.
            partner_email: Email address.
            relationship_type: Type of relationship.
            check_in_frequency: Frequency of check-ins.
            shared_goals: List of shared goals.
            communication_method: Communication method.
            notes: Additional notes.
        
        Returns:
            Created AccountabilityPartner object.
        """
        return self.stakes_system.add_accountability_partner(
            goal_id=goal_id,
            partner_name=partner_name,
            partner_email=partner_email,
            relationship_type=relationship_type,
            check_in_frequency=check_in_frequency,
            shared_goals=shared_goals,
            communication_method=communication_method,
            notes=notes
        )
    
    # Adaptive Sequencing Methods
    def get_performance_level(self, concept_id: str) -> Optional[PerformanceLevel]:
        """
        Get the performance level for a concept.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            PerformanceLevel or None.
        """
        return self.adaptive_sequencer.get_performance_level(concept_id)
    
    def get_performance_trend(self, concept_id: str) -> Optional[List[float]]:
        """
        Get the performance trend for a concept.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            List of scores or None.
        """
        return self.adaptive_sequencer.get_performance_trend(concept_id)
    
    def get_recommendations(self, limit: int = 5) -> List[SequenceRecommendation]:
        """
        Get top recommendations for learning.
        
        Args:
            limit: Maximum number of recommendations.
        
        Returns:
            List of SequenceRecommendation objects.
        """
        return self.adaptive_sequencer.get_top_recommendations(limit)
    
    def get_concept_recommendation(self, concept_id: str) -> Optional[SequenceRecommendation]:
        """
        Get recommendation for a specific concept.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            SequenceRecommendation or None.
        """
        return self.adaptive_sequencer.get_concept_recommendations(concept_id)
    
    def get_adaptive_sequence(self, topic_name: str, available_concepts: List[str]) -> List[str]:
        """
        Get an adaptive learning sequence.
        
        Args:
            topic_name: Name of the topic.
            available_concepts: List of available concept IDs.
        
        Returns:
            Ordered list of concept IDs.
        """
        return self.adaptive_sequencer.get_adaptive_sequence(
            topic_name=topic_name,
            available_concepts=available_concepts
        )
    
    # Integrated Methods
    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of all systems.
        
        Returns:
            Dictionary with summary from all three systems.
        """
        return {
            "progress_summary": self.progress_manager.get_progress_summary(),
            "stakes_summary": self.stakes_system.get_stakes_summary(),
            "sequencer_summary": self.adaptive_sequencer.get_sequence_statistics(),
            "generated_at": datetime.now().isoformat()
        }
    
    def get_concept_analytics(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive analytics for a concept.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            Dictionary with analytics or None.
        """
        progress = self.get_progress(concept_id)
        performance = self.adaptive_sequencer.get_performance_summary(concept_id)
        
        if not progress or not performance:
            return None
        
        return {
            "concept_id": concept_id,
            "progress": {
                "total_time_minutes": progress.total_time_minutes,
                "attempts": progress.attempts,
                "last_attempt_date": progress.last_attempt_date.isoformat() if progress.last_attempt_date else None,
                "difficulty_rating": progress.difficulty_rating
            },
            "performance": {
                "level": performance["performance_level"],
                "trend": performance["trend_direction"],
                "average_score": performance["average_score"],
                "success_rate": performance["success_rate"],
                "recommendation": performance["recommendation"]
            },
            "stakes": self.stakes_system.get_stakes_for_goal(concept_id)
        }
    
    def save_all(self):
        """Save all data from all systems."""
        self.progress_manager.save_data()
        self.stakes_system.save_data()
        self.adaptive_sequencer.save_data()
    
    def close(self):
        """Clean up resources."""
        self.save_all()


# Convenience function for quick setup
def create_learning_sequencer(config_path: Optional[str] = None) -> LearningSequencer:
    """
    Create a new learning sequencer instance.
    
    Args:
        config_path: Path to configuration file.
    
    Returns:
        LearningSequencer instance.
    """
    return LearningSequencer(config_path)
