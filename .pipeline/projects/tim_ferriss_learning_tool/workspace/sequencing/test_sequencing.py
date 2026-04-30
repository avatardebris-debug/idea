"""
Comprehensive tests for the Sequencing Package.

Tests cover:
- Progress tracking
- Accountability/stakes system
- Adaptive sequencing
- Integration of all components
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

from sequencing import (
    LearningSequencer,
    create_learning_sequencer,
    ProgressManager,
    StakesSystem,
    AdaptiveSequencer,
    LearningProgress,
    PublicCommitment,
    FinancialPenalty,
    AccountabilityPartner,
    PerformanceLevel,
    SequenceStrategy
)


class TestProgressManager:
    """Tests for ProgressManager class."""
    
    def test_record_progress(self):
        """Test recording progress for a concept."""
        manager = ProgressManager()
        progress = manager.record_progress(
            concept_id="test_concept",
            score=85,
            time_spent_minutes=30,
            difficulty_rating=7
        )
        
        assert progress.concept_id == "test_concept"
        assert progress.attempts == 1
        assert progress.average_score == 85.0
        assert progress.total_time_minutes == 30
        assert progress.difficulty_rating == 7
    
    def test_update_progress(self):
        """Test updating existing progress."""
        manager = ProgressManager()
        
        # First record
        manager.record_progress(
            concept_id="test_concept",
            score=80,
            time_spent_minutes=20
        )
        
        # Second record
        progress = manager.record_progress(
            concept_id="test_concept",
            score=90,
            time_spent_minutes=25
        )
        
        assert progress.attempts == 2
        assert progress.average_score == 85.0  # (80 + 90) / 2
        assert progress.total_time_minutes == 45
    
    def test_get_progress(self):
        """Test retrieving progress for a concept."""
        manager = ProgressManager()
        manager.record_progress("concept_1", 85, 30)
        
        progress = manager.get_progress("concept_1")
        assert progress is not None
        assert progress.concept_id == "concept_1"
        
        # Non-existent concept
        progress = manager.get_progress("non_existent")
        assert progress is None
    
    def test_get_all_progress(self):
        """Test retrieving all progress records."""
        manager = ProgressManager()
        manager.record_progress("concept_1", 85, 30)
        manager.record_progress("concept_2", 90, 45)
        
        all_progress = manager.get_all_progress()
        assert len(all_progress) == 2
    
    def test_get_progress_summary(self):
        """Test getting progress summary."""
        manager = ProgressManager()
        manager.record_progress("concept_1", 85, 30)
        manager.record_progress("concept_2", 90, 45)
        
        summary = manager.get_progress_summary()
        
        assert summary["total_concepts_tracked"] == 2
        assert summary["total_attempts"] == 2
        assert summary["average_score"] == 87.5


class TestStakesSystem:
    """Tests for StakesSystem class."""
    
    def test_create_public_commitment(self):
        """Test creating a public commitment."""
        system = StakesSystem()
        commitment = system.create_public_commitment(
            goal_id="goal_1",
            goal_description="Learn Python",
            deadline=datetime.now() + timedelta(days=30),
            public_platform="twitter",
            audience_size=500
        )
        
        assert commitment.goal_id == "goal_1"
        assert commitment.public_platform == "twitter"
        assert commitment.audience_size == 500
        assert commitment.status == "active"
    
    def test_create_financial_penalty(self):
        """Test creating a financial penalty."""
        system = StakesSystem()
        penalty = system.create_financial_penalty(
            goal_id="goal_1",
            amount=100.0,
            currency="USD",
            deadline=datetime.now() + timedelta(days=30)
        )
        
        assert penalty.goal_id == "goal_1"
        assert penalty.amount == 100.0
        assert penalty.currency == "USD"
        assert penalty.status == "active"
    
    def test_add_accountability_partner(self):
        """Test adding an accountability partner."""
        system = StakesSystem()
        partner = system.add_accountability_partner(
            goal_id="goal_1",
            partner_name="John Doe",
            partner_email="john@example.com",
            check_in_frequency="weekly"
        )
        
        assert partner.goal_id == "goal_1"
        assert partner.partner_name == "John Doe"
        assert partner.check_in_frequency == "weekly"
        assert partner.status == "active"
    
    def test_get_stakes_for_goal(self):
        """Test retrieving stakes for a goal."""
        system = StakesSystem()
        system.create_public_commitment("goal_1", "Test", datetime.now() + timedelta(days=30))
        system.create_financial_penalty("goal_1", 100.0)
        
        stakes = system.get_stakes_for_goal("goal_1")
        assert len(stakes) == 2
    
    def test_get_stakes_summary(self):
        """Test getting stakes summary."""
        system = StakesSystem()
        system.create_public_commitment("goal_1", "Test", datetime.now() + timedelta(days=30))
        system.create_financial_penalty("goal_1", 100.0)
        
        summary = system.get_stakes_summary()
        
        assert summary["total_active_stakes"] == 2
        assert summary["total_financial_penalties"] == 1


class TestAdaptiveSequencer:
    """Tests for AdaptiveSequencer class."""
    
    def test_record_performance(self):
        """Test recording performance metrics."""
        sequencer = AdaptiveSequencer()
        metrics = sequencer.record_performance(
            concept_id="concept_1",
            score=85,
            time_spent_minutes=30
        )
        
        assert metrics.concept_id == "concept_1"
        assert metrics.total_attempts == 1
        assert metrics.average_score == 85.0
    
    def test_get_performance_level(self):
        """Test getting performance level."""
        sequencer = AdaptiveSequencer()
        sequencer.record_performance("concept_1", 95, 30)
        
        level = sequencer.get_performance_level("concept_1")
        assert level == PerformanceLevel.EXCELLENT
    
    def test_get_performance_trend(self):
        """Test getting performance trend."""
        sequencer = AdaptiveSequencer()
        sequencer.record_performance("concept_1", 70, 30)
        sequencer.record_performance("concept_1", 80, 30)
        sequencer.record_performance("concept_1", 90, 30)
        
        trend = sequencer.get_performance_trend("concept_1")
        assert trend == [70, 80, 90]
    
    def test_get_recommendations(self):
        """Test getting recommendations."""
        sequencer = AdaptiveSequencer()
        sequencer.record_performance("concept_1", 50, 30)
        sequencer.record_performance("concept_2", 90, 30)
        
        recommendations = sequencer.get_recommendations(limit=5)
        assert len(recommendations) == 2
    
    def test_get_adaptive_sequence(self):
        """Test getting adaptive sequence."""
        sequencer = AdaptiveSequencer()
        
        # Record different performance levels
        sequencer.record_performance("concept_1", 50, 30)  # Needs improvement
        sequencer.record_performance("concept_2", 90, 30)  # Excellent
        sequencer.record_performance("concept_3", 70, 30)  # Good
        
        sequence = sequencer.get_adaptive_sequence(
            topic_name="Test Topic",
            available_concepts=["concept_1", "concept_2", "concept_3"]
        )
        
        # Should prioritize concept_1 (needs improvement)
        assert sequence[0] == "concept_1"
    
    def test_get_sequence_statistics(self):
        """Test getting sequence statistics."""
        sequencer = AdaptiveSequencer()
        sequencer.record_performance("concept_1", 85, 30)
        
        stats = sequencer.get_sequence_statistics()
        
        assert stats["total_concepts_tracked"] == 1
        assert stats["total_recommendations"] > 0


class TestLearningSequencer:
    """Tests for integrated LearningSequencer class."""
    
    def test_init(self):
        """Test initialization."""
        sequencer = LearningSequencer()
        
        assert sequencer.progress_manager is not None
        assert sequencer.stakes_system is not None
        assert sequencer.adaptive_sequencer is not None
    
    def test_record_progress_integration(self):
        """Test recording progress updates all systems."""
        sequencer = LearningSequencer()
        sequencer.record_progress("concept_1", 85, 30)
        
        # Check progress manager
        progress = sequencer.progress_manager.get_progress("concept_1")
        assert progress is not None
        assert progress.attempts == 1
        
        # Check adaptive sequencer
        metrics = sequencer.adaptive_sequencer.get_performance_summary("concept_1")
        assert metrics is not None
        assert metrics["average_score"] == 85.0
    
    def test_create_stakes_integration(self):
        """Test creating stakes updates stakes system."""
        sequencer = LearningSequencer()
        commitment = sequencer.create_public_commitment(
            goal_id="goal_1",
            goal_description="Test goal",
            deadline=datetime.now() + timedelta(days=30)
        )
        
        assert commitment.goal_id == "goal_1"
        
        # Verify it's in the stakes system
        stakes = sequencer.stakes_system.get_stakes_for_goal("goal_1")
        assert len(stakes) == 1
    
    def test_get_comprehensive_summary(self):
        """Test getting comprehensive summary."""
        sequencer = LearningSequencer()
        sequencer.record_progress("concept_1", 85, 30)
        sequencer.create_public_commitment("goal_1", "Test", datetime.now() + timedelta(days=30))
        
        summary = sequencer.get_comprehensive_summary()
        
        assert "progress_summary" in summary
        assert "stakes_summary" in summary
        assert "sequencer_summary" in summary
    
    def test_get_concept_analytics(self):
        """Test getting comprehensive analytics for a concept."""
        sequencer = LearningSequencer()
        sequencer.record_progress("concept_1", 85, 30)
        
        analytics = sequencer.get_concept_analytics("concept_1")
        
        assert analytics is not None
        assert "concept_id" in analytics
        assert "progress" in analytics
        assert "performance" in analytics


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_full_workflow(self):
        """Test complete learning workflow."""
        sequencer = LearningSequencer()
        
        # Step 1: Record initial progress
        sequencer.record_progress("python_basics", 60, 45)
        
        # Step 2: Set up accountability
        sequencer.create_financial_penalty(
            goal_id="python_basics",
            amount=50.0,
            deadline=datetime.now() + timedelta(days=30)
        )
        
        # Step 3: Get recommendations
        recommendations = sequencer.get_recommendations()
        assert len(recommendations) > 0
        
        # Step 4: Record improved performance
        sequencer.record_progress("python_basics", 85, 30)
        
        # Step 5: Check updated performance level
        level = sequencer.get_performance_level("python_basics")
        assert level == PerformanceLevel.GOOD
        
        # Step 6: Get comprehensive analytics
        analytics = sequencer.get_concept_analytics("python_basics")
        assert analytics is not None
        assert analytics["performance"]["average_score"] == 85.0
    
    def test_adaptive_sequencing_workflow(self):
        """Test adaptive sequencing based on performance."""
        sequencer = LearningSequencer()
        
        # Record performance for multiple concepts
        sequencer.record_progress("concept_easy", 95, 20)
        sequencer.record_progress("concept_medium", 75, 40)
        sequencer.record_progress("concept_hard", 50, 60)
        
        # Get adaptive sequence
        sequence = sequencer.get_adaptive_sequence(
            topic_name="Test Topic",
            available_concepts=["concept_easy", "concept_medium", "concept_hard"]
        )
        
        # Should prioritize hardest concept first
        assert sequence[0] == "concept_hard"
    
    def test_save_and_reload(self):
        """Test saving and reloading data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.yaml")
            
            # Create sequencer and record data
            sequencer = LearningSequencer(config_path)
            sequencer.record_progress("concept_1", 85, 30)
            sequencer.create_public_commitment(
                "goal_1",
                "Test",
                datetime.now() + timedelta(days=30)
            )
            
            # Save all data
            sequencer.save_all()
            
            # Create new sequencer instance
            sequencer2 = LearningSequencer(config_path)
            
            # Verify data was loaded
            progress = sequencer2.progress_manager.get_progress("concept_1")
            assert progress is not None
            assert progress.attempts == 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_non_existent_concept(self):
        """Test handling of non-existent concepts."""
        sequencer = LearningSequencer()
        
        progress = sequencer.get_progress("non_existent")
        assert progress is None
        
        level = sequencer.get_performance_level("non_existent")
        assert level is None
    
    def test_zero_attempts(self):
        """Test handling of zero attempts."""
        sequencer = LearningSequencer()
        
        # Record with zero time
        sequencer.record_progress("concept_1", 85, 0)
        
        analytics = sequencer.get_concept_analytics("concept_1")
        assert analytics is not None
    
    def test_extreme_scores(self):
        """Test handling of extreme scores."""
        sequencer = LearningSequencer()
        
        # Perfect score
        sequencer.record_progress("concept_1", 100, 30)
        level = sequencer.get_performance_level("concept_1")
        assert level == PerformanceLevel.EXCELLENT
        
        # Zero score
        sequencer.record_progress("concept_2", 0, 30)
        level = sequencer.get_performance_level("concept_2")
        assert level == PerformanceLevel.STRUGGLING
    
    def test_many_recommendations(self):
        """Test handling of many recommendations."""
        sequencer = LearningSequencer()
        
        # Record many concepts
        for i in range(20):
            sequencer.record_progress(f"concept_{i}", 50 + i * 2, 30)
        
        # Get top recommendations
        recommendations = sequencer.get_recommendations(limit=5)
        assert len(recommendations) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
