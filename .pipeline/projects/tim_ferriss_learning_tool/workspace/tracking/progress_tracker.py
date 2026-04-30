"""Progress Tracker - Implements comprehensive progress tracking for learning goals."""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

import yaml


class TrackingMetric(Enum):
    """Types of tracking metrics."""
    COMPLETION_PERCENTAGE = "completion_percentage"
    RETENTION_RATE = "retention_rate"
    PRACTICE_FREQUENCY = "practice_frequency"
    ASSESSMENT_SCORE = "assessment_score"
    TIME_SPENT = "time_spent"
    SKILL_ACQUISITION = "skill_acquisition"


@dataclass
class ProgressRecord:
    """Records progress for a specific learning activity."""
    record_id: str
    timestamp: datetime
    metric_type: str
    value: float
    notes: str
    activity_id: str
    activity_name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type,
            "value": self.value,
            "notes": self.notes,
            "activity_id": self.activity_id,
            "activity_name": self.activity_name
        }


@dataclass
class LearningActivity:
    """Represents a learning activity being tracked."""
    activity_id: str
    name: str
    description: str
    target_completion: float  # 0-100
    current_progress: float  # 0-100
    start_date: datetime
    estimated_duration_hours: float
    actual_hours_spent: float
    status: str  # "active", "completed", "paused"
    last_updated: datetime
    assessment_scores: List[float] = field(default_factory=list)
    practice_sessions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "activity_id": self.activity_id,
            "name": self.name,
            "description": self.description,
            "target_completion": self.target_completion,
            "current_progress": self.current_progress,
            "start_date": self.start_date.isoformat(),
            "estimated_duration_hours": self.estimated_duration_hours,
            "actual_hours_spent": self.actual_hours_spent,
            "status": self.status,
            "last_updated": self.last_updated.isoformat(),
            "assessment_scores": self.assessment_scores,
            "practice_sessions": self.practice_sessions
        }


@dataclass
class RetentionData:
    """Data for spaced repetition and retention tracking."""
    item_id: str
    last_reviewed: datetime
    next_review: datetime
    review_count: int
    recall_strength: float  # 0-10
    ease_factor: float  # SM-2 algorithm

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "item_id": self.item_id,
            "last_reviewed": self.last_reviewed.isoformat(),
            "next_review": self.next_review.isoformat(),
            "review_count": self.review_count,
            "recall_strength": self.recall_strength,
            "ease_factor": self.ease_factor
        }


class ProgressTracker:
    """
    Tracks learning progress and provides analytics.
    
    Implements comprehensive tracking for:
    - Completion percentages
    - Retention rates
    - Practice frequency
    - Assessment scores
    - Time spent analysis
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the progress tracker.
        
        Args:
            config_path: Path to tracking configuration file.
        """
        self.config = self._load_config(config_path)
        self.activities: List[LearningActivity] = []
        self.progress_records: List[ProgressRecord] = []
        self.retention_data: List[RetentionData] = []
        self.data_dir = Path("data/tracking")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_data()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load tracking configuration."""
        default_config = {
            "tracking_frequency": "daily",
            "retention_algorithm": "sm2",
            "reminder_enabled": True,
            "analytics_enabled": True,
            "practice_goal_per_week": 5
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    default_config.update(loaded_config)
        
        return default_config
    
    def _load_data(self):
        """Load existing tracking data from files."""
        # Load activities
        activities_file = self.data_dir / "activities.json"
        if activities_file.exists():
            with open(activities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.activities = []
                for item in data.get("activities", []):
                    # Convert timestamp strings to datetime objects
                    item_copy = item.copy()
                    for field in ["start_date", "last_updated"]:
                        if field in item_copy and isinstance(item_copy[field], str):
                            item_copy[field] = datetime.fromisoformat(item_copy[field])
                    self.activities.append(LearningActivity(**item_copy))
        
        # Load progress records
        records_file = self.data_dir / "progress_records.json"
        if records_file.exists():
            with open(records_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.progress_records = []
                for item in data.get("records", []):
                    # Convert timestamp string to datetime object
                    item_copy = item.copy()
                    if "timestamp" in item_copy and isinstance(item_copy["timestamp"], str):
                        item_copy["timestamp"] = datetime.fromisoformat(item_copy["timestamp"])
                    self.progress_records.append(ProgressRecord(**item_copy))
        
        # Load retention data
        retention_file = self.data_dir / "retention.json"
        if retention_file.exists():
            with open(retention_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.retention_data = []
                for item in data.get("data", []):
                    # Convert timestamp strings to datetime objects
                    item_copy = item.copy()
                    for field in ["last_reviewed", "next_review"]:
                        if field in item_copy and isinstance(item_copy[field], str):
                            item_copy[field] = datetime.fromisoformat(item_copy[field])
                    self.retention_data.append(RetentionData(**item_copy))
    
    def save_data(self):
        """Save all tracking data to files."""
        # Save activities
        with open(self.data_dir / "activities.json", 'w', encoding='utf-8') as f:
            json.dump({
                "activities": [a.to_dict() for a in self.activities]
            }, f, indent=2)
        
        # Save progress records
        with open(self.data_dir / "progress_records.json", 'w', encoding='utf-8') as f:
            json.dump({
                "records": [r.to_dict() for r in self.progress_records]
            }, f, indent=2)
        
        # Save retention data
        with open(self.data_dir / "retention.json", 'w', encoding='utf-8') as f:
            json.dump({
                "data": [r.to_dict() for r in self.retention_data]
            }, f, indent=2)
    
    def create_activity(
        self,
        name: str,
        description: str,
        target_completion: float = 100.0,
        estimated_duration_hours: float = 10.0,
        start_date: Optional[datetime] = None
    ) -> LearningActivity:
        """
        Create a new learning activity to track.
        
        Args:
            name: Name of the activity.
            description: Description of the activity.
            target_completion: Target completion percentage.
            estimated_duration_hours: Estimated time to complete.
            start_date: Start date for the activity.
        
        Returns:
            Created LearningActivity object.
        """
        activity = LearningActivity(
            activity_id=self._generate_activity_id(name),
            name=name,
            description=description,
            target_completion=target_completion,
            current_progress=0.0,
            start_date=start_date or datetime.now(),
            estimated_duration_hours=estimated_duration_hours,
            actual_hours_spent=0.0,
            status="active",
            last_updated=datetime.now()
        )
        
        self.activities.append(activity)
        self.save_data()
        return activity
    
    def update_progress(
        self,
        activity_id: str,
        progress_percentage: float,
        notes: str = ""
    ) -> Optional[LearningActivity]:
        """
        Update the progress of a learning activity.
        
        Args:
            activity_id: ID of the activity to update.
            progress_percentage: New progress percentage (0-100).
            notes: Notes about the progress update.
        
        Returns:
            Updated LearningActivity or None if not found.
        """
        for activity in self.activities:
            if activity.activity_id == activity_id:
                activity.current_progress = progress_percentage
                activity.last_updated = datetime.now()
                
                # Check if completed
                if progress_percentage >= 100:
                    activity.status = "completed"
                
                self._create_progress_record(
                    activity_id=activity_id,
                    activity_name=activity.name,
                    metric_type=TrackingMetric.COMPLETION_PERCENTAGE.value,
                    value=progress_percentage,
                    notes=notes
                )
                
                self.save_data()
                return activity
        
        return None
    
    def log_practice_session(
        self,
        activity_id: str,
        duration_minutes: int,
        notes: str = ""
    ) -> Optional[LearningActivity]:
        """
        Log a practice session for an activity.
        
        Args:
            activity_id: ID of the activity.
            duration_minutes: Duration of the session in minutes.
            notes: Notes about the session.
        
        Returns:
            Updated LearningActivity or None if not found.
        """
        for activity in self.activities:
            if activity.activity_id == activity_id:
                activity.practice_sessions += 1
                activity.actual_hours_spent += duration_minutes / 60.0
                activity.last_updated = datetime.now()
                
                self._create_progress_record(
                    activity_id=activity_id,
                    activity_name=activity.name,
                    metric_type=TrackingMetric.PRACTICE_FREQUENCY.value,
                    value=duration_minutes,
                    notes=notes
                )
                
                self.save_data()
                return activity
        
        return None
    
    def record_assessment_score(
        self,
        activity_id: str,
        score: float,
        max_score: float = 100.0,
        notes: str = ""
    ) -> Optional[LearningActivity]:
        """
        Record an assessment score for an activity.
        
        Args:
            activity_id: ID of the activity.
            score: Score achieved.
            max_score: Maximum possible score.
            notes: Notes about the assessment.
        
        Returns:
            Updated LearningActivity or None if not found.
        """
        for activity in self.activities:
            if activity.activity_id == activity_id:
                normalized_score = (score / max_score) * 100
                activity.assessment_scores.append(normalized_score)
                activity.last_updated = datetime.now()
                
                self._create_progress_record(
                    activity_id=activity_id,
                    activity_name=activity.name,
                    metric_type=TrackingMetric.ASSESSMENT_SCORE.value,
                    value=normalized_score,
                    notes=notes
                )
                
                self.save_data()
                return activity
        
        return None
    
    def calculate_retention_rate(self, activity_id: str) -> Optional[float]:
        """
        Calculate the retention rate for an activity.
        
        Args:
            activity_id: ID of the activity.
        
        Returns:
            Retention rate as a percentage, or None if not found.
        """
        for activity in self.activities:
            if activity.activity_id == activity_id:
                if not activity.assessment_scores:
                    return 0.0
                
                # Calculate average of recent assessments
                recent_scores = activity.assessment_scores[-5:] if len(activity.assessment_scores) >= 5 else activity.assessment_scores
                return sum(recent_scores) / len(recent_scores)
        
        return None
    
    def get_practice_frequency(self, activity_id: str) -> Optional[float]:
        """
        Get the practice frequency for an activity.
        
        Args:
            activity_id: ID of the activity.
        
        Returns:
            Average sessions per week, or None if not found.
        """
        for activity in self.activities:
            if activity.activity_id == activity_id:
                if activity.practice_sessions == 0:
                    return 0.0
                
                days_active = (datetime.now() - activity.start_date).days
                if days_active == 0:
                    return 0.0
                
                weeks_active = days_active / 7.0
                return activity.practice_sessions / weeks_active
        
        return None
    
    def schedule_spaced_repetition(
        self,
        item_id: str,
        recall_strength: float = 5.0,
        ease_factor: float = 2.5
    ) -> RetentionData:
        """
        Schedule a spaced repetition review.
        
        Uses the SM-2 algorithm for optimal review timing.
        
        Args:
            item_id: ID of the item to review.
            recall_strength: Initial recall strength (0-10).
            ease_factor: Initial ease factor.
        
        Returns:
            Created RetentionData object.
        """
        retention = RetentionData(
            item_id=item_id,
            last_reviewed=datetime.now(),
            next_review=datetime.now() + timedelta(days=1),
            review_count=1,
            recall_strength=recall_strength,
            ease_factor=ease_factor
        )
        
        self.retention_data.append(retention)
        self.save_data()
        return retention
    
    def update_spaced_repetition(
        self,
        item_id: str,
        recall_strength: float,
        ease_factor: float
    ) -> Optional[RetentionData]:
        """
        Update spaced repetition data after a review.
        
        Args:
            item_id: ID of the item.
            recall_strength: New recall strength after review.
            ease_factor: New ease factor.
        
        Returns:
            Updated RetentionData or None if not found.
        """
        for retention in self.retention_data:
            if retention.item_id == item_id:
                retention.last_reviewed = datetime.now()
                retention.recall_strength = recall_strength
                retention.ease_factor = ease_factor
                retention.review_count += 1
                
                # Calculate next review using SM-2 algorithm
                days_to_next_review = self._calculate_next_review_interval(
                    recall_strength, ease_factor
                )
                retention.next_review = datetime.now() + timedelta(days=days_to_next_review)
                
                self.save_data()
                return retention
        
        return None
    
    def _calculate_next_review_interval(
        self,
        recall_strength: float,
        ease_factor: float
    ) -> int:
        """Calculate days until next review using SM-2 algorithm."""
        if recall_strength >= 8:
            return int(ease_factor * 31)
        elif recall_strength >= 6:
            return int(ease_factor * 16)
        elif recall_strength >= 4:
            return int(ease_factor * 8)
        elif recall_strength >= 3:
            return int(ease_factor * 4)
        else:
            return int(ease_factor * 1)
    
    def _create_progress_record(
        self,
        activity_id: str,
        activity_name: str,
        metric_type: str,
        value: float,
        notes: str
    ):
        """Create a progress record."""
        record = ProgressRecord(
            record_id=self._generate_record_id(),
            timestamp=datetime.now(),
            metric_type=metric_type,
            value=value,
            notes=notes,
            activity_id=activity_id,
            activity_name=activity_name
        )
        self.progress_records.append(record)
    
    def _generate_activity_id(self, name: str) -> str:
        """Generate a unique activity ID."""
        import uuid
        return f"activity_{uuid.uuid4().hex[:8]}"
    
    def _generate_record_id(self) -> str:
        """Generate a unique record ID."""
        import uuid
        return f"record_{uuid.uuid4().hex[:8]}"
    
    def get_activity_summary(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of an activity's progress.
        
        Args:
            activity_id: ID of the activity.
        
        Returns:
            Dictionary with activity summary or None if not found.
        """
        for activity in self.activities:
            if activity.activity_id == activity_id:
                return {
                    "activity_id": activity.activity_id,
                    "name": activity.name,
                    "current_progress": activity.current_progress,
                    "target_completion": activity.target_completion,
                    "status": activity.status,
                    "practice_sessions": activity.practice_sessions,
                    "actual_hours_spent": activity.actual_hours_spent,
                    "estimated_duration_hours": activity.estimated_duration_hours,
                    "average_assessment_score": (
                        sum(activity.assessment_scores) / len(activity.assessment_scores)
                        if activity.assessment_scores else 0
                    ),
                    "retention_rate": self.calculate_retention_rate(activity_id) or 0,
                    "practice_frequency": self.get_practice_frequency(activity_id) or 0,
                    "last_updated": activity.last_updated.isoformat()
                }
        
        return None
    
    def get_all_activities_summary(self) -> List[Dict[str, Any]]:
        """Get summaries for all activities."""
        return [self.get_activity_summary(a.activity_id) for a in self.activities]
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """
        Get overall progress across all activities.
        
        Returns:
            Dictionary with overall progress statistics.
        """
        if not self.activities:
            return {
                "total_activities": 0,
                "completed_activities": 0,
                "active_activities": 0,
                "average_progress": 0,
                "total_practice_sessions": 0,
                "total_hours_spent": 0
            }
        
        completed = [a for a in self.activities if a.status == "completed"]
        active = [a for a in self.activities if a.status == "active"]
        
        return {
            "total_activities": len(self.activities),
            "completed_activities": len(completed),
            "active_activities": len(active),
            "average_progress": sum(a.current_progress for a in self.activities) / len(self.activities),
            "total_practice_sessions": sum(a.practice_sessions for a in self.activities),
            "total_hours_spent": sum(a.actual_hours_spent for a in self.activities)
        }
    
    def get_retention_overview(self) -> List[Dict[str, Any]]:
        """Get overview of all retention items."""
        return [r.to_dict() for r in self.retention_data]
    
    def get_upcoming_reviews(self) -> List[Dict[str, Any]]:
        """Get items that need review soon."""
        today = datetime.now()
        upcoming = []
        
        for retention in self.retention_data:
            if retention.next_review <= today + timedelta(days=7):
                upcoming.append(retention.to_dict())
        
        return sorted(upcoming, key=lambda x: x["next_review"])
