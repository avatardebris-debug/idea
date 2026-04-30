"""Tests for the Adaptive Sequencer."""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adaptive_sequencer import (
    AdaptiveSequencer,
    PerformanceLevel,
    SequenceStrategy,
    PerformanceMetrics,
    SequenceRecommendation,
    LearningSequence
)


class TestAdaptiveSequencer:
    """Test suite for AdaptiveSequencer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.sequencer = AdaptiveSequencer(data_dir=self.test_dir)
    
    def teardown_method(self):
        """Clean up after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test that sequencer initializes correctly."""
        assert self.sequencer is not None
        assert self.sequencer.performance_metrics == {}
        assert self.sequencer.recommendations == []
        assert self.sequencer.sequences == []
        assert self.sequencer.data_dir == Path(self.test_dir)
    
    def test_record_performance(self):
        """Test recording performance metrics."""
        metrics = self.sequencer.record_performance(
            concept_id="concept_1",
            score=85.0,
            time_spent_minutes=30.0,
            difficulty_rating=7.0
        )
        
        assert metrics.concept_id == "concept_1"
        assert metrics.total_attempts == 1
        assert metrics.successful_attempts == 1
        assert metrics.average_score == 85.0
        assert metrics.time_spent_minutes == 30.0
        assert metrics.difficulty_rating == 7.0
        assert metrics.performance_trend == [85.0]
    
    def test_record_multiple_performances(self):
        """Test recording multiple performance metrics."""
        self.sequencer.record_performance("concept_1", 80.0, 30.0)
        self.sequencer.record_performance("concept_1", 90.0, 25.0)
        self.sequencer.record_performance("concept_1", 85.0, 35.0)
        
        metrics = self.sequencer.performance_metrics["concept_1"]
        assert metrics.total_attempts == 3
        assert metrics.successful_attempts == 3
        assert abs(metrics.average_score - 85.0) < 0.01
        assert metrics.time_spent_minutes == 90.0
        assert len(metrics.performance_trend) == 3
    
    def test_performance_level_excellent(self):
        """Test performance level calculation for excellent performance."""
        self.sequencer.record_performance("concept_1", 95.0, 30.0)
        self.sequencer.record_performance("concept_1", 92.0, 25.0)
        
        level = self.sequencer.get_performance_level("concept_1")
        assert level == "excellent"
        
        level_enum = self.sequencer.get_performance_level_enum("concept_1")
        assert level_enum == PerformanceLevel.EXCELLENT
    
    def test_performance_level_good(self):
        """Test performance level calculation for good performance."""
        self.sequencer.record_performance("concept_1", 80.0, 30.0)
        self.sequencer.record_performance("concept_1", 78.0, 25.0)
        
        level = self.sequencer.get_performance_level("concept_1")
        assert level == "good"
    
    def test_performance_level_average(self):
        """Test performance level calculation for average performance."""
        self.sequencer.record_performance("concept_1", 65.0, 30.0)
        self.sequencer.record_performance("concept_1", 60.0, 25.0)
        
        level = self.sequencer.get_performance_level("concept_1")
        assert level == "average"
    
    def test_performance_level_needs_improvement(self):
        """Test performance level calculation for needs improvement."""
        self.sequencer.record_performance("concept_1", 45.0, 30.0)
        self.sequencer.record_performance("concept_1", 50.0, 25.0)
        
        level = self.sequencer.get_performance_level("concept_1")
        assert level == "needs_improvement"
    
    def test_performance_level_struggling(self):
        """Test performance level calculation for struggling."""
        self.sequencer.record_performance("concept_1", 30.0, 30.0)
        self.sequencer.record_performance("concept_1", 35.0, 25.0)
        
        level = self.sequencer.get_performance_level("concept_1")
        assert level == "struggling"
    
    def test_performance_trend(self):
        """Test performance trend tracking."""
        self.sequencer.record_performance("concept_1", 60.0, 30.0)
        self.sequencer.record_performance("concept_1", 70.0, 25.0)
        self.sequencer.record_performance("concept_1", 80.0, 35.0)
        
        trend = self.sequencer.get_performance_trend("concept_1")
        assert trend == [60.0, 70.0, 80.0]
    
    def test_performance_trend_direction_improving(self):
        """Test trend direction calculation for improving performance."""
        self.sequencer.record_performance("concept_1", 60.0, 30.0)
        self.sequencer.record_performance("concept_1", 70.0, 25.0)
        self.sequencer.record_performance("concept_1", 80.0, 35.0)
        
        direction = self.sequencer.calculate_performance_trend_direction("concept_1")
        assert direction == "improving"
    
    def test_performance_trend_direction_declining(self):
        """Test trend direction calculation for declining performance."""
        self.sequencer.record_performance("concept_1", 80.0, 30.0)
        self.sequencer.record_performance("concept_1", 70.0, 25.0)
        self.sequencer.record_performance("concept_1", 60.0, 35.0)
        
        direction = self.sequencer.calculate_performance_trend_direction("concept_1")
        assert direction == "declining"
    
    def test_performance_trend_direction_stable(self):
        """Test trend direction calculation for stable performance."""
        self.sequencer.record_performance("concept_1", 75.0, 30.0)
        self.sequencer.record_performance("concept_1", 76.0, 25.0)
        self.sequencer.record_performance("concept_1", 74.0, 35.0)
        
        direction = self.sequencer.calculate_performance_trend_direction("concept_1")
        assert direction == "stable"
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        self.sequencer.record_performance("concept_1", 85.0, 30.0)
        
        recommendation = self.sequencer.generate_recommendations_for_concept("concept_1")
        
        assert recommendation is not None
        assert recommendation.concept_id == "concept_1"
        # Score of 85 is in the 80-90 range, which returns "Continue practice"
        assert recommendation.recommended_action == "Continue practice"
        assert recommendation.priority == 5.0
        assert recommendation.confidence_score == 8.5
        assert recommendation.suggested_duration_minutes == 20
    
    def test_recommendations_for_struggling_concept(self):
        """Test recommendations for struggling concepts."""
        self.sequencer.record_performance("concept_1", 35.0, 30.0)
        
        recommendation = self.sequencer.generate_recommendations_for_concept("concept_1")
        
        assert recommendation is not None
        assert recommendation.recommended_action == "Break down and simplify"
        assert recommendation.priority == 10.0
    
    def test_create_learning_sequence(self):
        """Test creating a learning sequence."""
        sequence = self.sequencer.create_learning_sequence(
            topic_name="Python Basics",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="progressive"
        )
        
        assert sequence.sequence_id.startswith("seq_")
        assert sequence.topic_name == "Python Basics"
        assert sequence.concepts == ["concept_1", "concept_2", "concept_3"]
        assert sequence.sequence_type == "progressive"
        assert sequence.status == "active"
        assert sequence.current_position == 0
        assert sequence.completion_percentage == 0.0
    
    def test_update_sequence_position(self):
        """Test updating sequence position."""
        sequence = self.sequencer.create_learning_sequence(
            topic_name="Python Basics",
            concepts=["concept_1", "concept_2", "concept_3"]
        )
        
        updated = self.sequencer.update_sequence_position(sequence.sequence_id, 1)
        
        assert updated.current_position == 1
        # Use approximate equality for floating-point comparison
        assert abs(updated.completion_percentage - 33.333333333333336) < 0.0001
        assert updated.status == "active"
    
    def test_complete_sequence(self):
        """Test completing a sequence."""
        sequence = self.sequencer.create_learning_sequence(
            topic_name="Python Basics",
            concepts=["concept_1", "concept_2", "concept_3"]
        )
        
        completed = self.sequencer.complete_sequence(sequence.sequence_id)
        
        assert completed.status == "completed"
        assert completed.end_date is not None
        assert completed.completion_percentage == 100.0
    
    def test_get_next_concept(self):
        """Test getting next concept in sequence."""
        sequence = self.sequencer.create_learning_sequence(
            topic_name="Python Basics",
            concepts=["concept_1", "concept_2", "concept_3"]
        )
        
        next_concept = self.sequencer.get_next_concept(sequence.sequence_id)
        assert next_concept == "concept_1"
    
    def test_get_adaptive_sequence(self):
        """Test generating adaptive sequence."""
        # Record different performance levels
        self.sequencer.record_performance("concept_1", 50.0, 30.0)  # needs improvement
        self.sequencer.record_performance("concept_2", 90.0, 25.0)  # excellent
        self.sequencer.record_performance("concept_3", 70.0, 35.0)  # average
        
        adaptive_sequence = self.sequencer.get_adaptive_sequence(
            topic_name="Python Basics",
            available_concepts=["concept_1", "concept_2", "concept_3"]
        )
        
        # Should prioritize concept_1 (needs improvement)
        assert adaptive_sequence[0] == "concept_1"
    
    def test_get_all_sequences(self):
        """Test getting all sequences."""
        self.sequencer.create_learning_sequence("Topic 1", ["c1", "c2"])
        self.sequencer.create_learning_sequence("Topic 2", ["c3", "c4"])
        
        sequences = self.sequencer.get_all_sequences()
        assert len(sequences) == 2
    
    def test_get_active_sequences(self):
        """Test getting active sequences."""
        self.sequencer.create_learning_sequence("Topic 1", ["c1", "c2"])
        self.sequencer.create_learning_sequence("Topic 2", ["c3", "c4"])
        
        active = self.sequencer.get_active_sequences()
        assert len(active) == 2
    
    def test_get_sequence_statistics(self):
        """Test getting sequence statistics."""
        self.sequencer.create_learning_sequence("Topic 1", ["c1", "c2"])
        self.sequencer.create_learning_sequence("Topic 2", ["c3", "c4"])
        self.sequencer.record_performance("c1", 95.0, 30.0)
        
        stats = self.sequencer.get_sequence_statistics()
        
        assert stats["total_sequences"] == 2
        assert stats["active_sequences"] == 2
        assert stats["total_concepts_tracked"] == 1
        assert stats["mastered_concepts"] == 1
    
    def test_save_and_load_state(self):
        """Test saving and loading state."""
        self.sequencer.record_performance("concept_1", 85.0, 30.0)
        self.sequencer.create_learning_sequence("Topic 1", ["c1", "c2"])
        
        # Save state
        state_path = os.path.join(self.test_dir, "state.json")
        self.sequencer.save_state(state_path)
        
        # Create new sequencer and load state
        new_sequencer = AdaptiveSequencer(data_dir=self.test_dir)
        new_sequencer.load_state(state_path)
        
        assert len(new_sequencer.performance_metrics) == 1
        assert len(new_sequencer.sequences) == 1
    
    def test_data_persistence(self):
        """Test that data persists to files."""
        self.sequencer.record_performance("concept_1", 85.0, 30.0)
        self.sequencer.create_learning_sequence("Topic 1", ["c1", "c2"])
        
        # Check that files were created
        assert (Path(self.test_dir) / "performance_metrics.json").exists()
        assert (Path(self.test_dir) / "sequences.json").exists()
        assert (Path(self.test_dir) / "recommendations.json").exists()
    
    def test_get_concept_recommendations(self):
        """Test getting recommendations for a specific concept."""
        self.sequencer.record_performance("concept_1", 85.0, 30.0)
        self.sequencer.generate_recommendations_for_concept("concept_1")
        
        recommendation = self.sequencer.get_concept_recommendations("concept_1")
        assert recommendation is not None
        assert recommendation.concept_id == "concept_1"
    
    def test_get_top_recommendations(self):
        """Test getting top recommendations."""
        self.sequencer.record_performance("concept_1", 85.0, 30.0)
        self.sequencer.record_performance("concept_2", 50.0, 30.0)
        self.sequencer.generate_recommendations_for_concept("concept_1")
        self.sequencer.generate_recommendations_for_concept("concept_2")
        
        top_recs = self.sequencer.get_top_recommendations(limit=2)
        assert len(top_recs) == 2
        assert top_recs[0].priority >= top_recs[1].priority
    
    def test_get_performance_summary(self):
        """Test getting performance summary."""
        self.sequencer.record_performance("concept_1", 85.0, 30.0)
        
        summary = self.sequencer.get_performance_summary("concept_1")
        
        assert summary is not None
        assert summary["concept_id"] == "concept_1"
        assert summary["total_attempts"] == 1
        assert summary["average_score"] == 85.0
        assert summary["success_rate"] == 100.0
    
    def test_get_performance_summary_nonexistent(self):
        """Test getting performance summary for nonexistent concept."""
        summary = self.sequencer.get_performance_summary("nonexistent")
        assert summary is None
    
    def test_get_performance_level_nonexistent(self):
        """Test getting performance level for nonexistent concept."""
        level = self.sequencer.get_performance_level("nonexistent")
        assert level is None
    
    def test_get_performance_trend_nonexistent(self):
        """Test getting performance trend for nonexistent concept."""
        trend = self.sequencer.get_performance_trend("nonexistent")
        assert trend is None
    
    def test_update_sequence_position_complete(self):
        """Test updating sequence position to complete."""
        sequence = self.sequencer.create_learning_sequence(
            topic_name="Python Basics",
            concepts=["concept_1", "concept_2", "concept_3"]
        )
        
        updated = self.sequencer.update_sequence_position(sequence.sequence_id, 3)
        
        assert updated.status == "completed"
        assert updated.completion_percentage == 100.0
        assert updated.end_date is not None
    
    def test_get_next_concept_complete(self):
        """Test getting next concept from completed sequence."""
        sequence = self.sequencer.create_learning_sequence(
            topic_name="Python Basics",
            concepts=["concept_1", "concept_2", "concept_3"]
        )
        
        # Complete the sequence
        self.sequencer.update_sequence_position(sequence.sequence_id, 3)
        
        next_concept = self.sequencer.get_next_concept(sequence.sequence_id)
        assert next_concept is None
    
    def test_create_sequence_alias(self):
        """Test that create_sequence is an alias for create_learning_sequence."""
        sequence = self.sequencer.create_sequence(
            topic_name="Python Basics",
            concepts=["concept_1", "concept_2"],
            sequence_type="spiral"
        )
        
        assert sequence.topic_name == "Python Basics"
        assert sequence.sequence_type == "spiral"
    
    def test_get_recommendation_alias(self):
        """Test that get_recommendation is an alias for get_concept_recommendations."""
        self.sequencer.record_performance("concept_1", 85.0, 30.0)
        self.sequencer.generate_recommendations_for_concept("concept_1")
        
        recommendation = self.sequencer.get_recommendation("concept_1")
        assert recommendation is not None
    
    def test_get_performance_trend_direction_alias(self):
        """Test that get_trend_direction is an alias for calculate_performance_trend_direction."""
        self.sequencer.record_performance("concept_1", 60.0, 30.0)
        self.sequencer.record_performance("concept_1", 70.0, 25.0)
        self.sequencer.record_performance("concept_1", 80.0, 35.0)
        
        direction = self.sequencer.get_trend_direction("concept_1")
        assert direction == "improving"
    
    def test_get_concept_performance_summary_alias(self):
        """Test that get_concept_performance_summary is an alias for get_performance_summary."""
        self.sequencer.record_performance("concept_1", 85.0, 30.0)
        
        summary = self.sequencer.get_concept_performance_summary("concept_1")
        assert summary is not None


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
