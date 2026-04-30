"""Adaptive Sequencer - Adjusts learning sequence based on performance and feedback."""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

import yaml


class PerformanceLevel(Enum):
    """Performance level classifications."""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    NEEDS_IMPROVEMENT = "needs_improvement"
    STRUGGLING = "struggling"


class SequenceStrategy(Enum):
    """Strategies for sequencing learning content."""
    PROGRESSIVE = "progressive"
    SPIRAL = "spiral"
    INTERLEAVED = "interleaved"
    MASTERY_BASED = "mastery_based"
    ADAPTIVE = "adaptive"
    RANDOM = "random"


@dataclass
class PerformanceMetrics:
    """Tracks performance metrics for a concept."""
    concept_id: str
    total_attempts: int = 0
    successful_attempts: int = 0
    average_score: float = 0.0
    time_spent_minutes: float = 0.0
    last_attempt_date: Optional[datetime] = None
    performance_trend: List[float] = field(default_factory=list)
    difficulty_rating: float = 0.0  # User-rated difficulty 0-10
    performance_level: Optional[str] = None  # Computed performance level

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "concept_id": self.concept_id,
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "average_score": self.average_score,
            "time_spent_minutes": self.time_spent_minutes,
            "last_attempt_date": self.last_attempt_date.isoformat() if self.last_attempt_date else None,
            "performance_trend": self.performance_trend,
            "difficulty_rating": self.difficulty_rating
        }


@dataclass
class SequenceRecommendation:
    """Represents a sequencing recommendation."""
    recommendation_id: str
    concept_id: str
    concept_name: str
    recommended_action: str
    priority: float  # 0-10
    reasoning: str
    confidence_score: float  # 0-10
    suggested_duration_minutes: int
    optimal_time_of_day: str
    created_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "recommendation_id": self.recommendation_id,
            "concept_id": self.concept_id,
            "concept_name": self.concept_name,
            "recommended_action": self.recommended_action,
            "priority": self.priority,
            "reasoning": self.reasoning,
            "confidence_score": self.confidence_score,
            "suggested_duration_minutes": self.suggested_duration_minutes,
            "optimal_time_of_day": self.optimal_time_of_day,
            "created_date": self.created_date.isoformat()
        }


@dataclass
class LearningSequence:
    """Represents a complete learning sequence."""
    sequence_id: str
    topic_name: str
    concepts: List[str]
    sequence_type: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"
    current_position: int = 0
    completion_percentage: float = 0.0
    created_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sequence_id": self.sequence_id,
            "topic_name": self.topic_name,
            "concepts": self.concepts,
            "sequence_type": self.sequence_type,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "current_position": self.current_position,
            "completion_percentage": self.completion_percentage,
            "created_date": self.created_date.isoformat()
        }


class AdaptiveSequencer:
    """
    Implements adaptive learning sequencing.
    
    Provides functionality to:
    - Track performance metrics
    - Generate personalized learning sequences
    - Adjust sequence based on performance
    - Recommend optimal learning times
    - Analyze learning patterns
    """
    
    def __init__(self, config_path: Optional[str] = None, data_dir: Optional[str] = None):
        """
        Initialize the adaptive sequencer.
        
        Args:
            config_path: Path to sequencer configuration file.
            data_dir: Directory for storing sequencer data.
        """
        self.config = self._load_config(config_path)
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.recommendations: List[SequenceRecommendation] = []
        self.sequences: List[LearningSequence] = []
        self.data_dir = Path(data_dir) if data_dir else Path("data/sequencer")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_data()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load sequencer configuration."""
        default_config = {
            "auto_save": True,
            "performance_thresholds": {
                "excellent": 90.0,
                "good": 75.0,
                "average": 60.0,
                "needs_improvement": 40.0
            },
            "default_sequence_type": "adaptive",
            "max_recommendations": 10,
            "confidence_threshold": 0.7,
            "trend_window": 5,
            "optimal_study_times": ["morning", "afternoon", "evening"]
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    default_config.update(loaded_config)
        
        return default_config
    
    def _load_data(self):
        """Load existing sequencer data from files."""
        # Load performance metrics
        metrics_file = self.data_dir / "performance_metrics.json"
        if metrics_file.exists():
            with open(metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("metrics", []):
                    last_attempt_date = datetime.fromisoformat(item["last_attempt_date"]) if item.get("last_attempt_date") else None
                    metrics = PerformanceMetrics(
                        concept_id=item["concept_id"],
                        total_attempts=item["total_attempts"],
                        successful_attempts=item["successful_attempts"],
                        average_score=item["average_score"],
                        time_spent_minutes=item["time_spent_minutes"],
                        last_attempt_date=last_attempt_date,
                        performance_trend=item["performance_trend"],
                        difficulty_rating=item["difficulty_rating"]
                    )
                    self.performance_metrics[item["concept_id"]] = metrics
        
        # Load recommendations
        recommendations_file = self.data_dir / "recommendations.json"
        if recommendations_file.exists():
            with open(recommendations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("recommendations", []):
                    created_date = datetime.fromisoformat(item["created_date"])
                    recommendation = SequenceRecommendation(
                        recommendation_id=item["recommendation_id"],
                        concept_id=item["concept_id"],
                        concept_name=item["concept_name"],
                        recommended_action=item["recommended_action"],
                        priority=item["priority"],
                        reasoning=item["reasoning"],
                        confidence_score=item["confidence_score"],
                        suggested_duration_minutes=item["suggested_duration_minutes"],
                        optimal_time_of_day=item["optimal_time_of_day"],
                        created_date=created_date
                    )
                    self.recommendations.append(recommendation)
        
        # Load sequences
        sequences_file = self.data_dir / "sequences.json"
        if sequences_file.exists():
            with open(sequences_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("sequences", []):
                    start_date = datetime.fromisoformat(item["start_date"])
                    end_date = datetime.fromisoformat(item["end_date"]) if item.get("end_date") else None
                    sequence = LearningSequence(
                        sequence_id=item["sequence_id"],
                        topic_name=item["topic_name"],
                        concepts=item["concepts"],
                        sequence_type=item["sequence_type"],
                        start_date=start_date,
                        end_date=end_date,
                        status=item["status"],
                        current_position=item["current_position"],
                        completion_percentage=item["completion_percentage"],
                        created_date=datetime.fromisoformat(item["created_date"])
                    )
                    self.sequences.append(sequence)
    
    def save_data(self):
        """Save all sequencer data to files."""
        # Save performance metrics
        with open(self.data_dir / "performance_metrics.json", 'w', encoding='utf-8') as f:
            json.dump({
                "metrics": [m.to_dict() for m in self.performance_metrics.values()]
            }, f, indent=2)
        
        # Save recommendations
        with open(self.data_dir / "recommendations.json", 'w', encoding='utf-8') as f:
            json.dump({
                "recommendations": [r.to_dict() for r in self.recommendations]
            }, f, indent=2)
        
        # Save sequences
        with open(self.data_dir / "sequences.json", 'w', encoding='utf-8') as f:
            json.dump({
                "sequences": [s.to_dict() for s in self.sequences]
            }, f, indent=2)
    
    def record_performance(
        self,
        concept_id: str,
        score: float,
        time_spent_minutes: float,
        difficulty_rating: Optional[float] = None,
        notes: str = ""
    ) -> PerformanceMetrics:
        """
        Record performance for a concept.
        
        Args:
            concept_id: ID of the concept.
            score: Score achieved (0-100).
            time_spent_minutes: Time spent on the concept.
            difficulty_rating: User-rated difficulty (0-10).
            notes: Additional notes.
        
        Returns:
            Updated PerformanceMetrics object.
        """
        if concept_id not in self.performance_metrics:
            self.performance_metrics[concept_id] = PerformanceMetrics(
                concept_id=concept_id
            )
        
        metrics = self.performance_metrics[concept_id]
        metrics.total_attempts += 1
        metrics.time_spent_minutes += time_spent_minutes
        metrics.last_attempt_date = datetime.now()
        
        # Update average score
        if metrics.total_attempts == 1:
            metrics.average_score = score
        else:
            metrics.average_score = (
                (metrics.average_score * (metrics.total_attempts - 1) + score) 
                / metrics.total_attempts
            )
        
        # Track performance trend
        metrics.performance_trend.append(score)
        if len(metrics.performance_trend) > self.config.get("trend_window", 5):
            metrics.performance_trend.pop(0)
        
        # Update successful attempts
        if score >= self.config.get("performance_thresholds", {}).get("average", 60.0):
            metrics.successful_attempts += 1
        
        # Update difficulty rating if provided
        if difficulty_rating is not None:
            metrics.difficulty_rating = difficulty_rating
        
        # Generate new recommendations based on updated performance
        self.generate_recommendations_for_concept(concept_id)
        
        self.save_data()
        return metrics
    
    def get_performance_level(self, concept_id: str) -> Optional[str]:
        """
        Get the performance level for a concept as a string.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            Performance level string or None if concept not found.
        """
        if concept_id not in self.performance_metrics:
            return None
        
        metrics = self.performance_metrics[concept_id]
        thresholds = self.config.get("performance_thresholds", {})
        
        if metrics.average_score >= thresholds.get("excellent", 90.0):
            level = "excellent"
        elif metrics.average_score >= thresholds.get("good", 75.0):
            level = "good"
        elif metrics.average_score >= thresholds.get("average", 60.0):
            level = "average"
        elif metrics.average_score >= thresholds.get("needs_improvement", 40.0):
            level = "needs_improvement"
        else:
            level = "struggling"
        
        # Update the metrics with the computed level
        metrics.performance_level = level
        return level
    
    def get_performance_level_enum(self, concept_id: str) -> Optional[PerformanceLevel]:
        """
        Get the performance level for a concept as an enum.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            PerformanceLevel enum or None if concept not found.
        """
        level_str = self.get_performance_level(concept_id)
        if level_str is None:
            return None
        
        return PerformanceLevel(level_str)
    
    def get_all_sequences(self) -> List[LearningSequence]:
        """
        Get all learning sequences.
        
        Returns:
            List of all LearningSequence objects.
        """
        return self.sequences.copy()
    
    def get_active_sequences(self) -> List[LearningSequence]:
        """
        Get all active learning sequences.
        
        Returns:
            List of active LearningSequence objects.
        """
        return [s for s in self.sequences if s.status == "active"]
    
    def save_state(self, path: Optional[str] = None):
        """
        Save sequencer state to a file.
        
        Args:
            path: Optional custom path to save to.
        """
        save_path = Path(path) if path else self.data_dir / "sequencer_state.json"
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump({
                "performance_metrics": [m.to_dict() for m in self.performance_metrics.values()],
                "recommendations": [r.to_dict() for r in self.recommendations],
                "sequences": [s.to_dict() for s in self.sequences]
            }, f, indent=2)
    
    def load_state(self, path: str):
        """
        Load sequencer state from a file.
        
        Args:
            path: Path to the state file.
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Clear existing data before loading to prevent duplication
            self.performance_metrics.clear()
            self.recommendations.clear()
            self.sequences.clear()
            
            # Load performance metrics
            for item in data.get("performance_metrics", []):
                last_attempt_date = datetime.fromisoformat(item["last_attempt_date"]) if item.get("last_attempt_date") else None
                metrics = PerformanceMetrics(
                    concept_id=item["concept_id"],
                    total_attempts=item["total_attempts"],
                    successful_attempts=item["successful_attempts"],
                    average_score=item["average_score"],
                    time_spent_minutes=item["time_spent_minutes"],
                    last_attempt_date=last_attempt_date,
                    performance_trend=item["performance_trend"],
                    difficulty_rating=item["difficulty_rating"],
                    performance_level=item.get("performance_level")
                )
                self.performance_metrics[item["concept_id"]] = metrics
            
            # Load recommendations
            for item in data.get("recommendations", []):
                created_date = datetime.fromisoformat(item["created_date"])
                recommendation = SequenceRecommendation(
                    recommendation_id=item["recommendation_id"],
                    concept_id=item["concept_id"],
                    concept_name=item["concept_name"],
                    recommended_action=item["recommended_action"],
                    priority=item["priority"],
                    reasoning=item["reasoning"],
                    confidence_score=item["confidence_score"],
                    suggested_duration_minutes=item["suggested_duration_minutes"],
                    optimal_time_of_day=item["optimal_time_of_day"],
                    created_date=created_date
                )
                self.recommendations.append(recommendation)
            
            # Load sequences
            for item in data.get("sequences", []):
                start_date = datetime.fromisoformat(item["start_date"])
                end_date = datetime.fromisoformat(item["end_date"]) if item.get("end_date") else None
                sequence = LearningSequence(
                    sequence_id=item["sequence_id"],
                    topic_name=item["topic_name"],
                    concepts=item["concepts"],
                    sequence_type=item["sequence_type"],
                    start_date=start_date,
                    end_date=end_date,
                    status=item["status"],
                    current_position=item["current_position"],
                    completion_percentage=item["completion_percentage"],
                    created_date=datetime.fromisoformat(item["created_date"])
                )
                self.sequences.append(sequence)
    
    def get_recommendation(self, concept_id: str) -> Optional[SequenceRecommendation]:
        """
        Get the most recent recommendation for a concept (alias for get_concept_recommendations).
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            Most recent SequenceRecommendation or None.
        """
        return self.get_concept_recommendations(concept_id)
    
    def get_performance_trend(self, concept_id: str) -> Optional[List[float]]:
        """
        Get the performance trend for a concept.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            List of scores representing trend or None if concept not found.
        """
        if concept_id not in self.performance_metrics:
            return None
        
        return self.performance_metrics[concept_id].performance_trend.copy()
    
    def calculate_performance_trend_direction(self, concept_id: str) -> str:
        """
        Calculate the direction of performance trend.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            "improving", "stable", or "declining".
        """
        trend = self.get_performance_trend(concept_id)
        if not trend or len(trend) < 2:
            return "stable"
        
        # Compare first half to second half
        mid = len(trend) // 2
        first_half_avg = sum(trend[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(trend[mid:]) / (len(trend) - mid) if len(trend) > mid else 0
        
        if second_half_avg > first_half_avg + 5:
            return "improving"
        elif second_half_avg < first_half_avg - 5:
            return "declining"
        else:
            return "stable"
    
    def generate_recommendations_for_concept(self, concept_id: str) -> SequenceRecommendation:
        """
        Generate a recommendation for a specific concept.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            SequenceRecommendation object.
        """
        if concept_id not in self.performance_metrics:
            return None
        
        metrics = self.performance_metrics[concept_id]
        performance_level = self.get_performance_level(concept_id)
        trend_direction = self.calculate_performance_trend_direction(concept_id)
        
        # Determine recommended action based on performance
        if performance_level == "excellent":
            recommended_action = "Review and reinforce"
            priority = 2.0
            reasoning = "Concept mastered. Focus on maintenance and application."
            confidence_score = 9.0
            suggested_duration = 15
        elif performance_level == "good":
            recommended_action = "Continue practice"
            priority = 5.0
            reasoning = "Good performance. Continue regular practice to maintain mastery."
            confidence_score = 8.5
            suggested_duration = 20
        elif performance_level == "average":
            recommended_action = "Increase practice frequency"
            priority = 7.0
            reasoning = "Average performance. Increase practice frequency and variety."
            confidence_score = 8.0
            suggested_duration = 25
        elif performance_level == "needs_improvement":
            recommended_action = "Focus on fundamentals"
            priority = 9.0
            reasoning = "Needs improvement. Focus on foundational concepts and basics."
            confidence_score = 7.5
            suggested_duration = 30
        else:  # STRUGGLING
            recommended_action = "Break down and simplify"
            priority = 10.0
            reasoning = "Struggling with concept. Break down into smaller components."
            confidence_score = 7.0
            suggested_duration = 45
        
        # Adjust based on trend
        if trend_direction == "declining":
            priority = min(priority + 2, 10.0)
            reasoning += " Performance is declining. Immediate attention needed."
            confidence_score = min(confidence_score + 0.5, 10.0)
        
        # Adjust based on difficulty rating
        if metrics.difficulty_rating > 7:
            suggested_duration = int(suggested_duration * 1.5)
            reasoning += " High difficulty rating. Allow more time for mastery."
        
        # Determine optimal time of day
        optimal_time = self._determine_optimal_time(concept_id, metrics)
        
        recommendation = SequenceRecommendation(
            recommendation_id=f"rec_{len(self.recommendations) + 1}",
            concept_id=concept_id,
            concept_name=concept_id,  # In real implementation, would get from concept database
            recommended_action=recommended_action,
            priority=priority,
            reasoning=reasoning,
            confidence_score=confidence_score,
            suggested_duration_minutes=suggested_duration,
            optimal_time_of_day=optimal_time
        )
        
        self.recommendations.append(recommendation)
        
        # Keep only top recommendations
        if len(self.recommendations) > self.config.get("max_recommendations", 10):
            self.recommendations.sort(key=lambda x: x.priority, reverse=True)
            self.recommendations = self.recommendations[:self.config.get("max_recommendations", 10)]
        
        self.save_data()
        return recommendation
    
    def _determine_optimal_time(self, concept_id: str, metrics: PerformanceMetrics) -> str:
        """Determine optimal time of day for studying a concept."""
        # In a real implementation, this would analyze historical performance data
        # by time of day to find optimal study times
        
        # For now, use a simple heuristic based on performance level
        if metrics.average_score > 80:
            return "morning"  # Best performance in morning
        elif metrics.average_score > 60:
            return "afternoon"  # Good performance in afternoon
        else:
            return "evening"  # Better focus in evening for difficult concepts
    
    def create_sequence(
        self,
        topic_name: str,
        concepts: List[str],
        sequence_type: str = "adaptive",
        start_date: Optional[datetime] = None
    ) -> LearningSequence:
        """
        Create a new learning sequence (alias for create_learning_sequence).
        
        Args:
            topic_name: Name of the topic.
            concepts: List of concept IDs in the sequence.
            sequence_type: Type of sequence (progressive, spiral, interleaved, etc.).
            start_date: Start date for the sequence.
        
        Returns:
            Created LearningSequence object.
        """
        return self.create_learning_sequence(
            topic_name=topic_name,
            concepts=concepts,
            sequence_type=sequence_type,
            start_date=start_date
        )
    
    def complete_sequence(self, sequence_id: str) -> Optional[LearningSequence]:
        """
        Mark a learning sequence as completed.
        
        Args:
            sequence_id: ID of the sequence to complete.
        
        Returns:
            Updated LearningSequence or None if not found.
        """
        for sequence in self.sequences:
            if sequence.sequence_id == sequence_id:
                sequence.status = "completed"
                sequence.end_date = datetime.now()
                sequence.completion_percentage = 100.0
                self.save_data()
                return sequence
        return None
    
    def get_concept_performance_summary(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a comprehensive performance summary for a concept (alias for get_performance_summary).
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            Dictionary with performance summary or None.
        """
        return self.get_performance_summary(concept_id)
    
    def get_trend_direction(self, concept_id: str) -> str:
        """
        Get the trend direction for a concept (alias for calculate_performance_trend_direction).
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            "improving", "stable", or "declining".
        """
        return self.calculate_performance_trend_direction(concept_id)
    
    def create_learning_sequence(
        self,
        topic_name: str,
        concepts: List[str],
        sequence_type: str = "adaptive",
        start_date: Optional[datetime] = None
    ) -> LearningSequence:
        """
        Create a new learning sequence.
        
        Args:
            topic_name: Name of the topic.
            concepts: List of concept IDs in the sequence.
            sequence_type: Type of sequence (progressive, spiral, interleaved, etc.).
            start_date: Start date for the sequence.
        
        Returns:
            Created LearningSequence object.
        """
        sequence = LearningSequence(
            sequence_id=f"seq_{len(self.sequences) + 1}",
            topic_name=topic_name,
            concepts=concepts,
            sequence_type=sequence_type,
            start_date=start_date or datetime.now(),
            status="active",
            current_position=0,
            completion_percentage=0.0,
            created_date=datetime.now()
        )
        
        self.sequences.append(sequence)
        self.save_data()
        return sequence
    
    def update_sequence_position(self, sequence_id: str, new_position: int) -> Optional[LearningSequence]:
        """
        Update the current position in a learning sequence.
        
        Args:
            sequence_id: ID of the sequence.
            new_position: New position in the sequence.
        
        Returns:
            Updated LearningSequence or None if not found.
        """
        for sequence in self.sequences:
            if sequence.sequence_id == sequence_id:
                sequence.current_position = new_position
                sequence.completion_percentage = round(
                    (new_position / len(sequence.concepts)) * 100, 16
                    if sequence.concepts else 0
                )
                
                # Check if sequence is complete
                if new_position >= len(sequence.concepts):
                    sequence.status = "completed"
                    sequence.end_date = datetime.now()
                
                self.save_data()
                return sequence
        
        return None
    
    def get_next_concept(self, sequence_id: str) -> Optional[str]:
        """
        Get the next concept to study in a sequence.
        
        Args:
            sequence_id: ID of the sequence.
        
        Returns:
            Next concept ID or None if sequence is complete.
        """
        for sequence in self.sequences:
            if sequence.sequence_id == sequence_id:
                if sequence.current_position < len(sequence.concepts):
                    return sequence.concepts[sequence.current_position]
                return None
        
        return None
    
    def get_adaptive_sequence(self, topic_name: str, available_concepts: List[str]) -> List[str]:
        """
        Generate an adaptive learning sequence based on performance.
        
        Args:
            topic_name: Name of the topic.
            available_concepts: List of available concept IDs.
        
        Returns:
            Ordered list of concept IDs for optimal learning.
        """
        # Get performance levels for all concepts
        concept_performance = []
        for concept_id in available_concepts:
            if concept_id in self.performance_metrics:
                performance_level_str = self.get_performance_level(concept_id)
                trend = self.calculate_performance_trend_direction(concept_id)
                # Convert string to enum for consistent sorting
                performance_level = PerformanceLevel(performance_level_str) if performance_level_str else PerformanceLevel.NEEDS_IMPROVEMENT
                concept_performance.append({
                    "concept_id": concept_id,
                    "performance_level": performance_level,
                    "trend": trend,
                    "metrics": self.performance_metrics[concept_id]
                })
            else:
                # New concept - treat as needs improvement
                concept_performance.append({
                    "concept_id": concept_id,
                    "performance_level": PerformanceLevel.NEEDS_IMPROVEMENT,
                    "trend": "stable",
                    "metrics": PerformanceMetrics(concept_id=concept_id)
                })
        
        # Sort by priority (needs improvement first, then struggling, etc.)
        priority_order = {
            PerformanceLevel.NEEDS_IMPROVEMENT: 0,
            PerformanceLevel.STRUGGLING: 1,
            PerformanceLevel.AVERAGE: 2,
            PerformanceLevel.GOOD: 3,
            PerformanceLevel.EXCELLENT: 4
        }
        
        sorted_concepts = sorted(
            concept_performance,
            key=lambda x: (
                priority_order.get(x["performance_level"], 5),
                -x["metrics"].difficulty_rating if x["metrics"].difficulty_rating > 0 else 0,
                0 if x["trend"] == "improving" else 1
            )
        )
        
        return [c["concept_id"] for c in sorted_concepts]
    
    def get_top_recommendations(self, limit: int = 5) -> List[SequenceRecommendation]:
        """
        Get top recommendations sorted by priority.
        
        Args:
            limit: Maximum number of recommendations to return.
        
        Returns:
            List of top SequenceRecommendation objects.
        """
        sorted_recs = sorted(
            self.recommendations,
            key=lambda x: x.priority,
            reverse=True
        )
        return sorted_recs[:limit]
    
    def get_concept_recommendations(self, concept_id: str) -> Optional[SequenceRecommendation]:
        """
        Get the most recent recommendation for a concept.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            Most recent SequenceRecommendation or None.
        """
        concept_recs = [
            r for r in self.recommendations 
            if r.concept_id == concept_id
        ]
        
        if concept_recs:
            return max(concept_recs, key=lambda x: x.created_date)
        return None
    
    def get_sequence_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about learning sequences.
        
        Returns:
            Dictionary with sequence statistics.
        """
        completed_sequences = len([s for s in self.sequences if s.status == "completed"])
        active_sequences = len([s for s in self.sequences if s.status == "active"])
        
        total_concepts_tracked = len(self.performance_metrics)
        mastered_concepts = len([
            m for m in self.performance_metrics.values()
            if self.get_performance_level(m.concept_id) == "excellent"
        ])
        
        return {
            "total_sequences": len(self.sequences),
            "active_sequences": active_sequences,
            "completed_sequences": completed_sequences,
            "total_concepts_tracked": total_concepts_tracked,
            "mastered_concepts": mastered_concepts,
            "total_recommendations": len(self.recommendations),
            "average_recommendation_confidence": (
                sum(r.confidence_score for r in self.recommendations) / len(self.recommendations)
                if self.recommendations else 0
            ),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_performance_summary(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a comprehensive performance summary for a concept.
        
        Args:
            concept_id: ID of the concept.
        
        Returns:
            Dictionary with performance summary or None.
        """
        if concept_id not in self.performance_metrics:
            return None
        
        metrics = self.performance_metrics[concept_id]
        performance_level = self.get_performance_level(concept_id)
        trend_direction = self.calculate_performance_trend_direction(concept_id)
        
        return {
            "concept_id": concept_id,
            "performance_level": performance_level,
            "trend_direction": trend_direction,
            "total_attempts": metrics.total_attempts,
            "successful_attempts": metrics.successful_attempts,
            "success_rate": (
                (metrics.successful_attempts / metrics.total_attempts * 100)
                if metrics.total_attempts > 0 else 0
            ),
            "average_score": metrics.average_score,
            "time_spent_minutes": metrics.time_spent_minutes,
            "difficulty_rating": metrics.difficulty_rating,
            "last_attempt_date": metrics.last_attempt_date.isoformat() if metrics.last_attempt_date else None,
            "recommendation": self.get_concept_recommendations(concept_id)
        }
