"""Tests for the Adaptive Sequencer module."""

import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from .adaptive_sequencer import (
    AdaptiveSequencer,
    LearningSequence,
    PerformanceLevel,
    PerformanceMetrics,
    SequenceRecommendation,
    SequenceStrategy,
)


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics dataclass."""

    def test_performance_metrics_creation(self):
        """Test basic creation of PerformanceMetrics."""
        metrics = PerformanceMetrics(concept_id="test_concept_1")
        assert metrics.concept_id == "test_concept_1"
        assert metrics.total_attempts == 0
        assert metrics.successful_attempts == 0
        assert metrics.average_score == 0.0
        assert metrics.time_spent_minutes == 0.0
        assert metrics.last_attempt_date is None
        assert metrics.performance_trend == []
        assert metrics.difficulty_rating == 0.0

    def test_performance_metrics_to_dict(self):
        """Test conversion to dictionary."""
        test_date = datetime(2024, 1, 15, 10, 30, 0)
        metrics = PerformanceMetrics(
            concept_id="test_concept_2",
            total_attempts=10,
            successful_attempts=8,
            average_score=85.5,
            time_spent_minutes=120.5,
            last_attempt_date=test_date,
            performance_trend=[80, 85, 90],
            difficulty_rating=6.5
        )
        
        result = metrics.to_dict()
        
        assert result["concept_id"] == "test_concept_2"
        assert result["total_attempts"] == 10
        assert result["successful_attempts"] == 8
        assert result["average_score"] == 85.5
        assert result["time_spent_minutes"] == 120.5
        assert result["last_attempt_date"] == "2024-01-15T10:30:00"
        assert result["performance_trend"] == [80, 85, 90]
        assert result["difficulty_rating"] == 6.5


class TestSequenceRecommendation:
    """Tests for SequenceRecommendation dataclass."""

    def test_sequence_recommendation_creation(self):
        """Test basic creation of SequenceRecommendation."""
        rec = SequenceRecommendation(
            recommendation_id="rec_1",
            concept_id="concept_1",
            concept_name="Introduction to Python",
            recommended_action="Continue practice",
            priority=5.0,
            reasoning="Good performance",
            confidence_score=8.5,
            suggested_duration_minutes=20,
            optimal_time_of_day="afternoon"
        )
        
        assert rec.recommendation_id == "rec_1"
        assert rec.concept_id == "concept_1"
        assert rec.concept_name == "Introduction to Python"
        assert rec.recommended_action == "Continue practice"
        assert rec.priority == 5.0
        assert rec.reasoning == "Good performance"
        assert rec.confidence_score == 8.5
        assert rec.suggested_duration_minutes == 20
        assert rec.optimal_time_of_day == "afternoon"

    def test_sequence_recommendation_to_dict(self):
        """Test conversion to dictionary."""
        rec = SequenceRecommendation(
            recommendation_id="rec_2",
            concept_id="concept_2",
            concept_name="Data Structures",
            recommended_action="Review and reinforce",
            priority=2.0,
            reasoning="Concept mastered",
            confidence_score=9.0,
            suggested_duration_minutes=15,
            optimal_time_of_day="morning"
        )
        
        result = rec.to_dict()
        
        assert result["recommendation_id"] == "rec_2"
        assert result["concept_id"] == "concept_2"
        assert result["concept_name"] == "Data Structures"
        assert result["recommended_action"] == "Review and reinforce"
        assert result["priority"] == 2.0
        assert result["reasoning"] == "Concept mastered"
        assert result["confidence_score"] == 9.0
        assert result["suggested_duration_minutes"] == 15
        assert result["optimal_time_of_day"] == "morning"


class TestLearningSequence:
    """Tests for LearningSequence dataclass."""

    def test_learning_sequence_creation(self):
        """Test basic creation of LearningSequence."""
        start_date = datetime(2024, 1, 1, 9, 0, 0)
        end_date = datetime(2024, 1, 15, 17, 0, 0)
        
        sequence = LearningSequence(
            sequence_id="seq_1",
            topic_name="Python Fundamentals",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="adaptive",
            start_date=start_date,
            end_date=end_date,
            status="completed",
            current_position=3,
            completion_percentage=100.0
        )
        
        assert sequence.sequence_id == "seq_1"
        assert sequence.topic_name == "Python Fundamentals"
        assert sequence.concepts == ["concept_1", "concept_2", "concept_3"]
        assert sequence.sequence_type == "adaptive"
        assert sequence.start_date == start_date
        assert sequence.end_date == end_date
        assert sequence.status == "completed"
        assert sequence.current_position == 3
        assert sequence.completion_percentage == 100.0

    def test_learning_sequence_to_dict(self):
        """Test conversion to dictionary."""
        start_date = datetime(2024, 1, 1, 9, 0, 0)
        end_date = datetime(2024, 1, 15, 17, 0, 0)
        
        sequence = LearningSequence(
            sequence_id="seq_2",
            topic_name="Advanced Python",
            concepts=["concept_4", "concept_5"],
            sequence_type="spiral",
            start_date=start_date,
            end_date=end_date,
            status="completed",
            current_position=2,
            completion_percentage=100.0
        )
        
        result = sequence.to_dict()
        
        assert result["sequence_id"] == "seq_2"
        assert result["topic_name"] == "Advanced Python"
        assert result["concepts"] == ["concept_4", "concept_5"]
        assert result["sequence_type"] == "spiral"
        assert result["start_date"] == "2024-01-01T09:00:00"
        assert result["end_date"] == "2024-01-15T17:00:00"
        assert result["status"] == "completed"
        assert result["current_position"] == 2
        assert result["completion_percentage"] == 100.0


class TestPerformanceLevel:
    """Tests for PerformanceLevel enum."""

    def test_performance_level_values(self):
        """Test all performance level values."""
        assert PerformanceLevel.EXCELLENT.value == "excellent"
        assert PerformanceLevel.GOOD.value == "good"
        assert PerformanceLevel.AVERAGE.value == "average"
        assert PerformanceLevel.NEEDS_IMPROVEMENT.value == "needs_improvement"
        assert PerformanceLevel.STRUGGLING.value == "struggling"


class TestSequenceStrategy:
    """Tests for SequenceStrategy enum."""

    def test_sequence_strategy_values(self):
        """Test all sequence strategy values."""
        assert SequenceStrategy.PROGRESSIVE.value == "progressive"
        assert SequenceStrategy.SPIRAL.value == "spiral"
        assert SequenceStrategy.INTERLEAVED.value == "interleaved"
        assert SequenceStrategy.MASTERY_BASED.value == "mastery_based"
        assert SequenceStrategy.ADAPTIVE.value == "adaptive"
        assert SequenceStrategy.RANDOM.value == "random"


class TestAdaptiveSequencerInit:
    """Tests for AdaptiveSequencer initialization."""

    def test_sequencer_initialization(self):
        """Test basic initialization of AdaptiveSequencer."""
        sequencer = AdaptiveSequencer()
        
        assert sequencer.config is not None
        assert sequencer.performance_metrics == {}
        assert sequencer.recommendations == []
        assert sequencer.sequences == []
        assert sequencer.data_dir.exists()

    def test_sequencer_with_custom_config(self):
        """Test initialization with custom config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            custom_config = {
                "auto_save": False,
                "performance_thresholds": {
                    "excellent": 95.0,
                    "good": 80.0,
                    "average": 65.0,
                    "needs_improvement": 45.0
                },
                "max_recommendations": 15,
                "confidence_threshold": 0.8,
                "trend_window": 10
            }
            yaml.dump(custom_config, f)
            config_path = f.name
        
        try:
            sequencer = AdaptiveSequencer(config_path=config_path)
            
            assert sequencer.config["auto_save"] == False
            assert sequencer.config["performance_thresholds"]["excellent"] == 95.0
            assert sequencer.config["max_recommendations"] == 15
            assert sequencer.config["confidence_threshold"] == 0.8
            assert sequencer.config["trend_window"] == 10
        finally:
            os.unlink(config_path)

    def test_sequencer_with_nonexistent_config(self):
        """Test initialization with nonexistent config file."""
        sequencer = AdaptiveSequencer(config_path="/nonexistent/path/config.yaml")
        
        # Should use default config
        assert sequencer.config["auto_save"] == True
        assert sequencer.config["performance_thresholds"]["excellent"] == 90.0


class TestPerformanceMetricsRecording:
    """Tests for recording performance metrics."""

    def test_record_first_performance(self):
        """Test recording first performance for a concept."""
        sequencer = AdaptiveSequencer()
        
        metrics = sequencer.record_performance(
            concept_id="concept_1",
            score=85.0,
            time_spent_minutes=30.0,
            difficulty_rating=5.0
        )
        
        assert metrics.concept_id == "concept_1"
        assert metrics.total_attempts == 1
        assert metrics.successful_attempts == 1
        assert metrics.average_score == 85.0
        assert metrics.time_spent_minutes == 30.0
        assert metrics.difficulty_rating == 5.0
        assert metrics.performance_trend == [85.0]

    def test_record_multiple_performances(self):
        """Test recording multiple performances for a concept."""
        sequencer = AdaptiveSequencer()
        
        # First attempt
        metrics1 = sequencer.record_performance(
            concept_id="concept_2",
            score=70.0,
            time_spent_minutes=25.0
        )
        
        # Second attempt
        metrics2 = sequencer.record_performance(
            concept_id="concept_2",
            score=80.0,
            time_spent_minutes=20.0
        )
        
        # Third attempt
        metrics3 = sequencer.record_performance(
            concept_id="concept_2",
            score=85.0,
            time_spent_minutes=15.0
        )
        
        assert metrics3.total_attempts == 3
        assert metrics3.successful_attempts == 3
        # Average should be (70 + 80 + 85) / 3 = 78.33
        assert abs(metrics3.average_score - 78.33) < 0.01
        assert metrics3.time_spent_minutes == 60.0
        assert metrics3.performance_trend == [70.0, 80.0, 85.0]

    def test_performance_trend_window(self):
        """Test that performance trend respects the window size."""
        sequencer = AdaptiveSequencer()
        
        # Record more attempts than the trend window (default 5)
        for i in range(8):
            sequencer.record_performance(
                concept_id="concept_3",
                score=60 + i * 5,
                time_spent_minutes=10.0
            )
        
        metrics = sequencer.performance_metrics["concept_3"]
        # Should only keep last 5 scores
        assert len(metrics.performance_trend) == 5
        assert metrics.performance_trend == [75.0, 80.0, 85.0, 90.0, 95.0]

    def test_record_performance_without_difficulty(self):
        """Test recording performance without difficulty rating."""
        sequencer = AdaptiveSequencer()
        
        metrics = sequencer.record_performance(
            concept_id="concept_4",
            score=75.0,
            time_spent_minutes=20.0
        )
        
        assert metrics.difficulty_rating == 0.0

    def test_generate_recommendation_on_performance_update(self):
        """Test that recommendations are generated when performance is updated."""
        sequencer = AdaptiveSequencer()
        
        # Initially no recommendations
        assert len(sequencer.recommendations) == 0
        
        # Record performance - should generate recommendation
        sequencer.record_performance(
            concept_id="concept_5",
            score=50.0,
            time_spent_minutes=30.0
        )
        
        # Should have generated a recommendation
        assert len(sequencer.recommendations) == 1
        assert sequencer.recommendations[0].concept_id == "concept_5"


class TestGetPerformanceLevel:
    """Tests for getting performance level."""

    def test_get_performance_level_excellent(self):
        """Test getting EXCELLENT performance level."""
        sequencer = AdaptiveSequencer()
        
        # Record high scores
        for _ in range(5):
            sequencer.record_performance(
                concept_id="excellent_concept",
                score=95.0,
                time_spent_minutes=10.0
            )
        
        level = sequencer.get_performance_level("excellent_concept")
        assert level == PerformanceLevel.EXCELLENT

    def test_get_performance_level_good(self):
        """Test getting GOOD performance level."""
        sequencer = AdaptiveSequencer()
        
        # Record good scores
        for _ in range(5):
            sequencer.record_performance(
                concept_id="good_concept",
                score=80.0,
                time_spent_minutes=10.0
            )
        
        level = sequencer.get_performance_level("good_concept")
        assert level == PerformanceLevel.GOOD

    def test_get_performance_level_average(self):
        """Test getting AVERAGE performance level."""
        sequencer = AdaptiveSequencer()
        
        # Record average scores
        for _ in range(5):
            sequencer.record_performance(
                concept_id="average_concept",
                score=70.0,
                time_spent_minutes=10.0
            )
        
        level = sequencer.get_performance_level("average_concept")
        assert level == PerformanceLevel.AVERAGE

    def test_get_performance_level_needs_improvement(self):
        """Test getting NEEDS_IMPROVEMENT performance level."""
        sequencer = AdaptiveSequencer()
        
        # Record low scores
        for _ in range(5):
            sequencer.record_performance(
                concept_id="needs_improvement_concept",
                score=45.0,
                time_spent_minutes=10.0
            )
        
        level = sequencer.get_performance_level("needs_improvement_concept")
        assert level == PerformanceLevel.NEEDS_IMPROVEMENT

    def test_get_performance_level_struggling(self):
        """Test getting STRUGGLING performance level."""
        sequencer = AdaptiveSequencer()
        
        # Record very low scores
        for _ in range(5):
            sequencer.record_performance(
                concept_id="struggling_concept",
                score=30.0,
                time_spent_minutes=10.0
            )
        
        level = sequencer.get_performance_level("struggling_concept")
        assert level == PerformanceLevel.STRUGGLING

    def test_get_performance_level_unknown_concept(self):
        """Test getting performance level for unknown concept."""
        sequencer = AdaptiveSequencer()
        
        level = sequencer.get_performance_level("unknown_concept")
        assert level == PerformanceLevel.STRUGGLING


class TestGetRecommendation:
    """Tests for getting recommendations."""

    def test_get_recommendation_for_excellent_concept(self):
        """Test getting recommendation for excellent concept."""
        sequencer = AdaptiveSequencer()
        
        # Record high scores
        for _ in range(5):
            sequencer.record_performance(
                concept_id="excellent_concept",
                score=95.0,
                time_spent_minutes=10.0
            )
        
        rec = sequencer.get_recommendation("excellent_concept")
        
        assert rec is not None
        assert rec.confidence_score >= 0.8
        assert rec.recommended_action == "Continue practice"
        assert rec.priority == 5.0

    def test_get_recommendation_for_needs_improvement_concept(self):
        """Test getting recommendation for concept needing improvement."""
        sequencer = AdaptiveSequencer()
        
        # Record low scores
        for _ in range(5):
            sequencer.record_performance(
                concept_id="needs_improvement_concept",
                score=45.0,
                time_spent_minutes=10.0
            )
        
        rec = sequencer.get_recommendation("needs_improvement_concept")
        
        assert rec is not None
        assert rec.confidence_score >= 0.8
        assert rec.recommended_action == "Review and reinforce"
        assert rec.priority == 8.0

    def test_get_recommendation_for_unknown_concept(self):
        """Test getting recommendation for unknown concept."""
        sequencer = AdaptiveSequencer()
        
        rec = sequencer.get_recommendation("unknown_concept")
        
        assert rec is not None
        assert rec.confidence_score >= 0.8
        assert rec.recommended_action == "Start learning"
        assert rec.priority == 10.0

    def test_get_recommendation_with_custom_threshold(self):
        """Test getting recommendation with custom confidence threshold."""
        config = {
            "auto_save": False,
            "confidence_threshold": 0.5
        }
        sequencer = AdaptiveSequencer(config=config)
        
        # Record some performance
        for _ in range(3):
            sequencer.record_performance(
                concept_id="custom_threshold_concept",
                score=70.0,
                time_spent_minutes=10.0
            )
        
        rec = sequencer.get_recommendation("custom_threshold_concept")
        
        assert rec is not None
        assert rec.confidence_score >= 0.5


class TestGetNextConcept:
    """Tests for getting next concept in sequence."""

    def test_get_next_concept_progressive(self):
        """Test getting next concept with progressive strategy."""
        sequencer = AdaptiveSequencer()
        
        sequence = LearningSequence(
            sequence_id="seq_1",
            topic_name="Test Sequence",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="progressive",
            start_date=datetime.now(),
            end_date=datetime.now(),
            status="active",
            current_position=0,
            completion_percentage=0.0
        )
        
        sequencer.sequences.append(sequence)
        
        next_concept = sequencer.get_next_concept(sequence.sequence_id)
        
        assert next_concept == "concept_1"

    def test_get_next_concept_interleaved(self):
        """Test getting next concept with interleaved strategy."""
        sequencer = AdaptiveSequencer()
        
        sequence = LearningSequence(
            sequence_id="seq_2",
            topic_name="Test Sequence",
            concepts=["concept_1", "concept_2", "concept_3", "concept_4"],
            sequence_type="interleaved",
            start_date=datetime.now(),
            end_date=datetime.now(),
            status="active",
            current_position=0,
            completion_percentage=0.0
        )
        
        sequencer.sequences.append(sequence)
        
        # First call should return concept_1
        next_concept = sequencer.get_next_concept(sequence.sequence_id)
        assert next_concept == "concept_1"
        
        # Update position
        sequencer.update_sequence_position(sequence.sequence_id, 1)
        
        # Second call should return concept_2
        next_concept = sequencer.get_next_concept(sequence.sequence_id)
        assert next_concept == "concept_2"

    def test_get_next_concept_mastery_based(self):
        """Test getting next concept with mastery-based strategy."""
        sequencer = AdaptiveSequencer()
        
        # Record high performance for concept_1
        for _ in range(5):
            sequencer.record_performance(
                concept_id="concept_1",
                score=95.0,
                time_spent_minutes=10.0
            )
        
        sequence = LearningSequence(
            sequence_id="seq_3",
            topic_name="Test Sequence",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="mastery_based",
            start_date=datetime.now(),
            end_date=datetime.now(),
            status="active",
            current_position=0,
            completion_percentage=0.0
        )
        
        sequencer.sequences.append(sequence)
        
        # Should skip concept_1 and return concept_2
        next_concept = sequencer.get_next_concept(sequence.sequence_id)
        assert next_concept == "concept_2"

    def test_get_next_concept_adaptive(self):
        """Test getting next concept with adaptive strategy."""
        sequencer = AdaptiveSequencer()
        
        # Record low performance for concept_1
        for _ in range(5):
            sequencer.record_performance(
                concept_id="concept_1",
                score=40.0,
                time_spent_minutes=10.0
            )
        
        sequence = LearningSequence(
            sequence_id="seq_4",
            topic_name="Test Sequence",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="adaptive",
            start_date=datetime.now(),
            end_date=datetime.now(),
            status="active",
            current_position=0,
            completion_percentage=0.0
        )
        
        sequencer.sequences.append(sequence)
        
        # Should repeat concept_1 due to poor performance
        next_concept = sequencer.get_next_concept(sequence.sequence_id)
        assert next_concept == "concept_1"

    def test_get_next_concept_random(self):
        """Test getting next concept with random strategy."""
        sequencer = AdaptiveSequencer()
        
        sequence = LearningSequence(
            sequence_id="seq_5",
            topic_name="Test Sequence",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="random",
            start_date=datetime.now(),
            end_date=datetime.now(),
            status="active",
            current_position=0,
            completion_percentage=0.0
        )
        
        sequencer.sequences.append(sequence)
        
        # Should return a random concept
        next_concept = sequencer.get_next_concept(sequence.sequence_id)
        assert next_concept in ["concept_1", "concept_2", "concept_3"]

    def test_get_next_concept_sequence_not_found(self):
        """Test getting next concept when sequence doesn't exist."""
        sequencer = AdaptiveSequencer()
        
        next_concept = sequencer.get_next_concept("nonexistent_sequence")
        
        assert next_concept is None

    def test_get_next_concept_sequence_completed(self):
        """Test getting next concept when sequence is completed."""
        sequencer = AdaptiveSequencer()
        
        sequence = LearningSequence(
            sequence_id="seq_6",
            topic_name="Test Sequence",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="progressive",
            start_date=datetime.now(),
            end_date=datetime.now(),
            status="completed",
            current_position=3,
            completion_percentage=100.0
        )
        
        sequencer.sequences.append(sequence)
        
        next_concept = sequencer.get_next_concept(sequence.sequence_id)
        
        assert next_concept is None


class TestSequenceManagement:
    """Tests for sequence management operations."""

    def test_create_new_sequence(self):
        """Test creating a new learning sequence."""
        sequencer = AdaptiveSequencer()
        
        sequence = sequencer.create_sequence(
            topic_name="Python Fundamentals",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="adaptive"
        )
        
        assert sequence.sequence_id is not None
        assert sequence.topic_name == "Python Fundamentals"
        assert sequence.concepts == ["concept_1", "concept_2", "concept_3"]
        assert sequence.sequence_type == "adaptive"
        assert sequence.status == "active"
        assert sequence.current_position == 0
        assert sequence.completion_percentage == 0.0

    def test_update_sequence_position(self):
        """Test updating sequence position."""
        sequencer = AdaptiveSequencer()
        
        sequence = sequencer.create_sequence(
            topic_name="Test Sequence",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="progressive"
        )
        
        sequencer.update_sequence_position(sequence.sequence_id, 2)
        
        assert sequence.current_position == 2
        assert sequence.completion_percentage == 66.67

    def test_update_sequence_position_invalid(self):
        """Test updating sequence position with invalid sequence ID."""
        sequencer = AdaptiveSequencer()
        
        result = sequencer.update_sequence_position("nonexistent", 1)
        
        assert result is False

    def test_complete_sequence(self):
        """Test completing a learning sequence."""
        sequencer = AdaptiveSequencer()
        
        sequence = sequencer.create_sequence(
            topic_name="Test Sequence",
            concepts=["concept_1", "concept_2", "concept_3"],
            sequence_type="progressive"
        )
        
        sequencer.complete_sequence(sequence.sequence_id)
        
        assert sequence.status == "completed"
        assert sequence.completion_percentage == 100.0

    def test_complete_sequence_invalid(self):
        """Test completing a sequence with invalid ID."""
        sequencer = AdaptiveSequencer()
        
        result = sequencer.complete_sequence("nonexistent")
        
        assert result is False

    def test_get_all_sequences(self):
        """Test getting all sequences."""
        sequencer = AdaptiveSequencer()
        
        seq1 = sequencer.create_sequence(
            topic_name="Sequence 1",
            concepts=["concept_1"],
            sequence_type="progressive"
        )
        
        seq2 = sequencer.create_sequence(
            topic_name="Sequence 2",
            concepts=["concept_2"],
            sequence_type="spiral"
        )
        
        sequences = sequencer.get_all_sequences()
        
        assert len(sequences) == 2
        assert seq1.sequence_id in [s.sequence_id for s in sequences]
        assert seq2.sequence_id in [s.sequence_id for s in sequences]

    def test_get_active_sequences(self):
        """Test getting only active sequences."""
        sequencer = AdaptiveSequencer()
        
        seq1 = sequencer.create_sequence(
            topic_name="Active Sequence",
            concepts=["concept_1"],
            sequence_type="progressive"
        )
        
        sequencer.complete_sequence(seq1.sequence_id)
        
        seq2 = sequencer.create_sequence(
            topic_name="Another Active Sequence",
            concepts=["concept_2"],
            sequence_type="spiral"
        )
        
        active_sequences = sequencer.get_active_sequences()
        
        assert len(active_sequences) == 1
        assert active_sequences[0].sequence_id == seq2.sequence_id


class TestLoadSaveSequencer:
    """Tests for loading and saving sequencer state."""

    def test_save_and_load_sequencer(self):
        """Test saving and loading sequencer state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sequencer = AdaptiveSequencer(data_dir=temp_dir)
            
            # Create some sequences and record performance
            seq1 = sequencer.create_sequence(
                topic_name="Test Sequence",
                concepts=["concept_1", "concept_2"],
                sequence_type="adaptive"
            )
            
            sequencer.record_performance(
                concept_id="concept_1",
                score=85.0,
                time_spent_minutes=30.0
            )
            
            # Save state
            sequencer.save_state()
            
            # Create new sequencer instance
            sequencer2 = AdaptiveSequencer(data_dir=temp_dir)
            sequencer2.load_state()
            
            # Verify state was loaded
            assert len(sequencer2.sequences) == 1
            assert sequencer2.sequences[0].topic_name == "Test Sequence"
            assert "concept_1" in sequencer2.performance_metrics

    def test_save_state_auto_save_enabled(self):
        """Test that state is auto-saved when enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sequencer = AdaptiveSequencer(data_dir=temp_dir)
            
            # Create sequence
            sequencer.create_sequence(
                topic_name="Auto Save Test",
                concepts=["concept_1"],
                sequence_type="adaptive"
            )
            
            # State should be auto-saved
            assert (Path(temp_dir) / "sequencer_state.json").exists()

    def test_save_state_auto_save_disabled(self):
        """Test that state is not auto-saved when disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "auto_save": False,
                "performance_thresholds": {
                    "excellent": 90.0,
                    "good": 80.0,
                    "average": 65.0,
                    "needs_improvement": 45.0
                }
            }
            sequencer = AdaptiveSequencer(data_dir=temp_dir, config=config)
            
            # Create sequence
            sequencer.create_sequence(
                topic_name="No Auto Save Test",
                concepts=["concept_1"],
                sequence_type="adaptive"
            )
            
            # State should not be auto-saved
            assert not (Path(temp_dir) / "sequencer_state.json").exists()

    def test_load_state_from_file(self):
        """Test loading state from saved file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create and save sequencer
            sequencer1 = AdaptiveSequencer(data_dir=temp_dir)
            sequencer1.create_sequence(
                topic_name="Load Test",
                concepts=["concept_1", "concept_2"],
                sequence_type="adaptive"
            )
            sequencer1.save_state()
            
            # Load from file
            sequencer2 = AdaptiveSequencer(data_dir=temp_dir)
            sequencer2.load_state()
            
            assert len(sequencer2.sequences) == 1
            assert sequencer2.sequences[0].topic_name == "Load Test"


class TestPerformanceAnalysis:
    """Tests for performance analysis features."""

    def test_get_concept_performance_summary(self):
        """Test getting performance summary for a concept."""
        sequencer = AdaptiveSequencer()
        
        # Record multiple performances
        for i in range(5):
            sequencer.record_performance(
                concept_id="summary_concept",
                score=70 + i * 5,
                time_spent_minutes=10.0
            )
        
        summary = sequencer.get_concept_performance_summary("summary_concept")
        
        assert summary["concept_id"] == "summary_concept"
        assert summary["total_attempts"] == 5
        assert summary["average_score"] == 82.5
        assert summary["performance_level"] == "good"
        assert summary["trend_direction"] == "improving"

    def test_get_concept_performance_summary_unknown(self):
        """Test getting performance summary for unknown concept."""
        sequencer = AdaptiveSequencer()
        
        summary = sequencer.get_concept_performance_summary("unknown_concept")
        
        assert summary["concept_id"] == "unknown_concept"
        assert summary["total_attempts"] == 0
        assert summary["average_score"] == 0.0
        assert summary["performance_level"] == "struggling"
        assert summary["trend_direction"] == "unknown"

    def test_get_trend_direction_improving(self):
        """Test getting trend direction for improving performance."""
        sequencer = AdaptiveSequencer()
        
        # Record improving scores
        for i in range(5):
            sequencer.record_performance(
                concept_id="improving_concept",
                score=60 + i * 10,
                time_spent_minutes=10.0
            )
        
        direction = sequencer.get_trend_direction("improving_concept")
        
        assert direction == "improving"

    def test_get_trend_direction_declining(self):
        """Test getting trend direction for declining performance."""
        sequencer = AdaptiveSequencer()
        
        # Record declining scores
        for i in range(5):
            sequencer.record_performance(
                concept_id="declining_concept",
                score=90 - i * 10,
                time_spent_minutes=10.0
            )
        
        direction = sequencer.get_trend_direction("declining_concept")
        
        assert direction == "declining"

    def test_get_trend_direction_stable(self):
        """Test getting trend direction for stable performance."""
        sequencer = AdaptiveSequencer()
        
        # Record stable scores
        for i in range(5):
            sequencer.record_performance(
                concept_id="stable_concept",
                score=75,
                time_spent_minutes=10.0
            )
        
        direction = sequencer.get_trend_direction("stable_concept")
        
        assert direction == "stable"

    def test_get_trend_direction_unknown(self):
        """Test getting trend direction for unknown concept."""
        sequencer = AdaptiveSequencer()
        
        direction = sequencer.get_trend_direction("unknown_concept")
        
        assert direction == "unknown"


class TestIntegration:
    """Integration tests for the AdaptiveSequencer."""

    def test_full_workflow(self):
        """Test complete workflow of the adaptive sequencer."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sequencer = AdaptiveSequencer(data_dir=temp_dir)
            
            # Create a learning sequence
            sequence = sequencer.create_sequence(
                topic_name="Python Learning Path",
                concepts=["python_basics", "data_structures", "functions"],
                sequence_type="adaptive"
            )
            
            # Record initial performance
            sequencer.record_performance(
                concept_id="python_basics",
                score=60.0,
                time_spent_minutes=45.0
            )
            
            # Get recommendation
            rec = sequencer.get_recommendation("python_basics")
            assert rec is not None
            assert rec.confidence_score >= 0.8
            
            # Get next concept
            next_concept = sequencer.get_next_concept(sequence.sequence_id)
            assert next_concept == "python_basics"  # Should repeat due to low score
            
            # Update position
            sequencer.update_sequence_position(sequence.sequence_id, 1)
            
            # Record better performance
            sequencer.record_performance(
                concept_id="python_basics",
                score=85.0,
                time_spent_minutes=30.0
            )
            
            # Get updated recommendation
            rec = sequencer.get_recommendation("python_basics")
            assert rec.recommended_action == "Continue practice"
            
            # Save and reload
            sequencer.save_state()
            
            sequencer2 = AdaptiveSequencer(data_dir=temp_dir)
            sequencer2.load_state()
            
            assert len(sequencer2.sequences) == 1
            assert sequencer2.sequences[0].topic_name == "Python Learning Path"
            
            # Get performance summary
            summary = sequencer2.get_concept_performance_summary("python_basics")
            assert summary["total_attempts"] == 2
            assert summary["average_score"] == 72.5

    def test_multiple_sequences(self):
        """Test managing multiple learning sequences."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sequencer = AdaptiveSequencer(data_dir=temp_dir)
            
            # Create multiple sequences
            seq1 = sequencer.create_sequence(
                topic_name="Python Basics",
                concepts=["concept_1", "concept_2"],
                sequence_type="progressive"
            )
            
            seq2 = sequencer.create_sequence(
                topic_name="Advanced Topics",
                concepts=["concept_3", "concept_4"],
                sequence_type="spiral"
            )
            
            # Record performance for concepts in both sequences
            sequencer.record_performance(concept_id="concept_1", score=80.0)
            sequencer.record_performance(concept_id="concept_3", score=70.0)
            
            # Get active sequences
            active = sequencer.get_active_sequences()
            assert len(active) == 2
            
            # Get next concepts
            next1 = sequencer.get_next_concept(seq1.sequence_id)
            next2 = sequencer.get_next_concept(seq2.sequence_id)
            
            assert next1 == "concept_1"
            assert next2 == "concept_3"
            
            # Complete one sequence
            sequencer.complete_sequence(seq1.sequence_id)
            
            # Should only have one active sequence now
            active = sequencer.get_active_sequences()
            assert len(active) == 1
            assert active[0].sequence_id == seq2.sequence_id


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_concepts_list(self):
        """Test creating sequence with empty concepts list."""
        sequencer = AdaptiveSequencer()
        
        sequence = sequencer.create_sequence(
            topic_name="Empty Sequence",
            concepts=[],
            sequence_type="progressive"
        )
        
        assert sequence.concepts == []
        assert sequence.current_position == 0
        assert sequence.completion_percentage == 0.0

    def test_single_concept_sequence(self):
        """Test creating sequence with single concept."""
        sequencer = AdaptiveSequencer()
        
        sequence = sequencer.create_sequence(
            topic_name="Single Concept",
            concepts=["concept_1"],
            sequence_type="progressive"
        )
        
        assert sequence.concepts == ["concept_1"]
        assert sequence.current_position == 0
        assert sequence.completion_percentage == 0.0

    def test_very_long_concept_list(self):
        """Test creating sequence with many concepts."""
        sequencer = AdaptiveSequencer()
        
        concepts = [f"concept_{i}" for i in range(100)]
        
        sequence = sequencer.create_sequence(
            topic_name="Long Sequence",
            concepts=concepts,
            sequence_type="progressive"
        )
        
        assert len(sequence.concepts) == 100
        assert sequence.current_position == 0
        assert sequence.completion_percentage == 0.0

    def test_special_characters_in_concept_id(self):
        """Test handling concept IDs with special characters."""
        sequencer = AdaptiveSequencer()
        
        sequencer.record_performance(
            concept_id="concept_with_special_chars_123!@#",
            score=75.0,
            time_spent_minutes=20.0
        )
        
        metrics = sequencer.performance_metrics["concept_with_special_chars_123!@#"]
        assert metrics.average_score == 75.0

    def test_unicode_in_concept_name(self):
        """Test handling Unicode characters in concept names."""
        sequencer = AdaptiveSequencer()
        
        sequence = sequencer.create_sequence(
            topic_name="Unicode Test: 你好世界 🌍",
            concepts=["concept_1"],
            sequence_type="progressive"
        )
        
        assert "你好世界" in sequence.topic_name
        assert "🌍" in sequence.topic_name

    def test_very_high_score(self):
        """Test handling very high scores."""
        sequencer = AdaptiveSequencer()
        
        sequencer.record_performance(
            concept_id="high_score_concept",
            score=100.0,
            time_spent_minutes=10.0
        )
        
        metrics = sequencer.performance_metrics["high_score_concept"]
        assert metrics.average_score == 100.0
        assert metrics.performance_level == "excellent"

    def test_very_low_score(self):
        """Test handling very low scores."""
        sequencer = AdaptiveSequencer()
        
        sequencer.record_performance(
            concept_id="low_score_concept",
            score=0.0,
            time_spent_minutes=10.0
        )
        
        metrics = sequencer.performance_metrics["low_score_concept"]
        assert metrics.average_score == 0.0
        assert metrics.performance_level == "struggling"

    def test_negative_time_spent(self):
        """Test handling negative time spent."""
        sequencer = AdaptiveSequencer()
        
        sequencer.record_performance(
            concept_id="negative_time_concept",
            score=75.0,
            time_spent_minutes=-10.0
        )
        
        metrics = sequencer.performance_metrics["negative_time_concept"]
        assert metrics.time_spent_minutes == -10.0

    def test_score_above_100(self):
        """Test handling scores above 100."""
        sequencer = AdaptiveSequencer()
        
        sequencer.record_performance(
            concept_id="above_100_concept",
            score=150.0,
            time_spent_minutes=10.0
        )
        
        metrics = sequencer.performance_metrics["above_100_concept"]
        assert metrics.average_score == 150.0


class TestConfiguration:
    """Tests for configuration handling."""

    def test_default_configuration(self):
        """Test default configuration values."""
        sequencer = AdaptiveSequencer()
        
        assert sequencer.config["auto_save"] == True
        assert sequencer.config["confidence_threshold"] == 0.8
        assert sequencer.config["trend_window"] == 5
        assert sequencer.config["max_recommendations"] == 10
        assert sequencer.config["performance_thresholds"]["excellent"] == 90.0
        assert sequencer.config["performance_thresholds"]["good"] == 80.0
        assert sequencer.config["performance_thresholds"]["average"] == 65.0
        assert sequencer.config["performance_thresholds"]["needs_improvement"] == 45.0

    def test_custom_performance_thresholds(self):
        """Test custom performance thresholds."""
        config = {
            "auto_save": False,
            "performance_thresholds": {
                "excellent": 95.0,
                "good": 85.0,
                "average": 70.0,
                "needs_improvement": 50.0
            }
        }
        sequencer = AdaptiveSequencer(config=config)
        
        assert sequencer.config["performance_thresholds"]["excellent"] == 95.0
        assert sequencer.config["performance_thresholds"]["good"] == 85.0
        assert sequencer.config["performance_thresholds"]["average"] == 70.0
        assert sequencer.config["performance_thresholds"]["needs_improvement"] == 50.0

    def test_custom_trend_window(self):
        """Test custom trend window size."""
        config = {
            "auto_save": False,
            "trend_window": 20
        }
        sequencer = AdaptiveSequencer(config=config)
        
        assert sequencer.config["trend_window"] == 20

    def test_custom_max_recommendations(self):
        """Test custom maximum recommendations."""
        config = {
            "auto_save": False,
            "max_recommendations": 25
        }
        sequencer = AdaptiveSequencer(config=config)
        
        assert sequencer.config["max_recommendations"] == 25

    def test_custom_confidence_threshold(self):
        """Test custom confidence threshold."""
        config = {
            "auto_save": False,
            "confidence_threshold": 0.5
        }
        sequencer = AdaptiveSequencer(config=config)
        
        assert sequencer.config["confidence_threshold"] == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
