"""Progress Manager - Tracks learning progress and provides visualization."""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

import yaml


@dataclass
class LearningProgress:
    """
    Learning progress record for a concept.
    
    Attributes:
        concept_id: Unique identifier for the concept.
        attempts: Number of attempts made.
        average_score: Average score across all attempts.
        total_time_minutes: Total time spent on the concept.
        difficulty_rating: User-rated difficulty (0-10).
        last_attempt_date: Date of the last attempt.
    """
    concept_id: str
    attempts: int = 0
    average_score: float = 0.0
    total_time_minutes: float = 0.0
    difficulty_rating: Optional[float] = None
    last_attempt_date: Optional[datetime] = None


class ProgressStatus(Enum):
    """Status of a learning concept."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    MASTERED = "mastered"
    NEEDS_REVIEW = "needs_review"


class ConceptDifficulty(Enum):
    """Difficulty level of a concept."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class ConceptProgress:
    """Tracks progress for a single concept."""
    concept_id: str
    concept_name: str
    status: str
    mastery_percentage: float
    last_studied: Optional[datetime] = None
    study_sessions: int = 0
    average_score: float = 0.0
    estimated_time_spent: str = "0 min"
    difficulty_level: str = "beginner"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "concept_id": self.concept_id,
            "concept_name": self.concept_name,
            "status": self.status,
            "mastery_percentage": self.mastery_percentage,
            "last_studied": self.last_studied.isoformat() if self.last_studied else None,
            "study_sessions": self.study_sessions,
            "average_score": self.average_score,
            "estimated_time_spent": self.estimated_time_spent,
            "difficulty_level": self.difficulty_level,
            "notes": self.notes
        }


@dataclass
class LearningSession:
    """Represents a single learning session."""
    session_id: str
    topic_name: str
    start_time: datetime
    end_time: datetime
    concepts_studied: List[str]
    activities_completed: List[str]
    score_achieved: Optional[float] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "session_id": self.session_id,
            "topic_name": self.topic_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "concepts_studied": self.concepts_studied,
            "activities_completed": self.activities_completed,
            "score_achieved": self.score_achieved,
            "notes": self.notes
        }


@dataclass
class LearningGoal:
    """Represents a learning goal."""
    goal_id: str
    title: str
    description: str
    target_date: datetime
    status: str  # "active", "completed", "expired"
    progress_percentage: float = 0.0
    created_date: datetime = field(default_factory=datetime.now)
    priority: str = "medium"  # "low", "medium", "high"
    related_concepts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "target_date": self.target_date.isoformat(),
            "status": self.status,
            "progress_percentage": self.progress_percentage,
            "created_date": self.created_date.isoformat(),
            "priority": self.priority,
            "related_concepts": self.related_concepts
        }


class ProgressManager:
    """
    Manages learning progress tracking and visualization.
    
    Provides functionality to:
    - Track progress on individual concepts
    - Record learning sessions
    - Set and track learning goals
    - Generate progress reports and visualizations
    - Identify knowledge gaps
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the progress manager.
        
        Args:
            config_path: Path to progress tracking configuration file.
        """
        self.config = self._load_config(config_path)
        self.concept_progress: Dict[str, ConceptProgress] = {}
        self.sessions: List[LearningSession] = []
        self.goals: List[LearningGoal] = []
        self._learning_progress: Dict[str, LearningProgress] = {}
        self.data_dir = Path("data/progress_tracker")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_data()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load progress tracking configuration."""
        default_config = {
            "auto_save": True,
            "session_timeout_minutes": 120,
            "mastery_threshold": 80.0,
            "review_interval_days": 7,
            "visualization_enabled": True
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    default_config.update(loaded_config)
        
        return default_config
    
    def _load_data(self):
        """Load existing progress data from files."""
        # Load concept progress
        progress_file = self.data_dir / "concept_progress.json"
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("concepts", []):
                    last_studied = datetime.fromisoformat(item["last_studied"]) if item.get("last_studied") else None
                    progress = ConceptProgress(
                        concept_id=item["concept_id"],
                        concept_name=item["concept_name"],
                        status=item["status"],
                        mastery_percentage=item["mastery_percentage"],
                        last_studied=last_studied,
                        study_sessions=item["study_sessions"],
                        average_score=item["average_score"],
                        estimated_time_spent=item["estimated_time_spent"],
                        difficulty_level=item["difficulty_level"],
                        notes=item.get("notes", "")
                    )
                    self.concept_progress[item["concept_id"]] = progress
        
        # Load sessions
        sessions_file = self.data_dir / "sessions.json"
        if sessions_file.exists():
            with open(sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("sessions", []):
                    start_time = datetime.fromisoformat(item["start_time"])
                    end_time = datetime.fromisoformat(item["end_time"])
                    session = LearningSession(
                        session_id=item["session_id"],
                        topic_name=item["topic_name"],
                        start_time=start_time,
                        end_time=end_time,
                        concepts_studied=item["concepts_studied"],
                        activities_completed=item["activities_completed"],
                        score_achieved=item.get("score_achieved"),
                        notes=item.get("notes", "")
                    )
                    self.sessions.append(session)
        
        # Load goals
        goals_file = self.data_dir / "goals.json"
        if goals_file.exists():
            with open(goals_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("goals", []):
                    target_date = datetime.fromisoformat(item["target_date"])
                    created_date = datetime.fromisoformat(item["created_date"])
                    goal = LearningGoal(
                        goal_id=item["goal_id"],
                        title=item["title"],
                        description=item["description"],
                        target_date=target_date,
                        status=item["status"],
                        progress_percentage=item["progress_percentage"],
                        created_date=created_date,
                        priority=item["priority"],
                        related_concepts=item.get("related_concepts", [])
                    )
                    self.goals.append(goal)
        
        # Load learning progress
        progress_file = self.data_dir / "learning_progress.json"
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("progress", []):
                    last_attempt_date = datetime.fromisoformat(item["last_attempt_date"]) if item.get("last_attempt_date") else None
                    progress = LearningProgress(
                        concept_id=item["concept_id"],
                        attempts=item["attempts"],
                        average_score=item["average_score"],
                        total_time_minutes=item["total_time_minutes"],
                        difficulty_rating=item.get("difficulty_rating"),
                        last_attempt_date=last_attempt_date
                    )
                    self._learning_progress[item["concept_id"]] = progress
    
    def save_data(self):
        """Save all progress data to files."""
        # Save concept progress
        with open(self.data_dir / "concept_progress.json", 'w', encoding='utf-8') as f:
            json.dump({
                "concepts": [p.to_dict() for p in self.concept_progress.values()]
            }, f, indent=2)
        
        # Save sessions
        with open(self.data_dir / "sessions.json", 'w', encoding='utf-8') as f:
            json.dump({
                "sessions": [s.to_dict() for s in self.sessions]
            }, f, indent=2)
        
        # Save goals
        with open(self.data_dir / "goals.json", 'w', encoding='utf-8') as f:
            json.dump({
                "goals": [g.to_dict() for g in self.goals]
            }, f, indent=2)
        
        # Save learning progress
        with open(self.data_dir / "learning_progress.json", 'w', encoding='utf-8') as f:
            json.dump({
                "progress": [
                    {
                        "concept_id": p.concept_id,
                        "attempts": p.attempts,
                        "average_score": p.average_score,
                        "total_time_minutes": p.total_time_minutes,
                        "difficulty_rating": p.difficulty_rating,
                        "last_attempt_date": p.last_attempt_date.isoformat() if p.last_attempt_date else None
                    }
                    for p in self._learning_progress.values()
                ]
            }, f, indent=2)
    
    def initialize_concept(self, concept_id: str, concept_name: str, 
                          difficulty_level: str = "beginner") -> ConceptProgress:
        """
        Initialize tracking for a new concept.
        
        Args:
            concept_id: Unique identifier for the concept.
            concept_name: Human-readable name of the concept.
            difficulty_level: Initial difficulty level.
        
        Returns:
            Created ConceptProgress object.
        """
        if concept_id in self.concept_progress:
            return self.concept_progress[concept_id]
        
        progress = ConceptProgress(
            concept_id=concept_id,
            concept_name=concept_name,
            status=ProgressStatus.NOT_STARTED.value,
            mastery_percentage=0.0,
            difficulty_level=difficulty_level
        )
        
        self.concept_progress[concept_id] = progress
        self.save_data()
        return progress
    
    def update_concept_progress(
        self,
        concept_id: str,
        mastery_percentage: float,
        score: Optional[float] = None,
        study_time: str = "30 min",
        notes: str = ""
    ) -> Optional[ConceptProgress]:
        """
        Update progress for a concept.
        
        Args:
            concept_id: ID of the concept to update.
            mastery_percentage: New mastery percentage (0-100).
            score: Score achieved in the session.
            study_time: Time spent studying.
            notes: Additional notes.
        
        Returns:
            Updated ConceptProgress or None if not found.
        """
        if concept_id not in self.concept_progress:
            return None
        
        progress = self.concept_progress[concept_id]
        progress.mastery_percentage = mastery_percentage
        progress.last_studied = datetime.now()
        progress.study_sessions += 1
        
        if score is not None:
            # Update average score
            if progress.study_sessions == 1:
                progress.average_score = score
            else:
                progress.average_score = (
                    (progress.average_score * (progress.study_sessions - 1) + score) 
                    / progress.study_sessions
                )
        
        progress.estimated_time_spent = study_time
        
        # Update status based on mastery
        if mastery_percentage >= self.config.get("mastery_threshold", 80.0):
            progress.status = ProgressStatus.MASTERED.value
        elif mastery_percentage > 0:
            progress.status = ProgressStatus.IN_PROGRESS.value
        else:
            progress.status = ProgressStatus.NOT_STARTED.value
        
        if notes:
            progress.notes = notes
        
        self.save_data()
        return progress
    
    def record_session(
        self,
        topic_name: str,
        concepts_studied: List[str],
        activities_completed: List[str],
        score_achieved: Optional[float] = None,
        notes: str = ""
    ) -> LearningSession:
        """
        Record a learning session.
        
        Args:
            topic_name: Name of the topic being studied.
            concepts_studied: List of concept IDs studied.
            activities_completed: List of activity titles completed.
            score_achieved: Score achieved in the session.
            notes: Additional notes.
        
        Returns:
            Created LearningSession object.
        """
        session = LearningSession(
            session_id=f"session_{len(self.sessions) + 1}",
            topic_name=topic_name,
            start_time=datetime.now(),
            end_time=datetime.now(),
            concepts_studied=concepts_studied,
            activities_completed=activities_completed,
            score_achieved=score_achieved,
            notes=notes
        )
        
        self.sessions.append(session)
        
        # Update concept progress for studied concepts
        for concept_id in concepts_studied:
            if concept_id in self.concept_progress:
                self.concept_progress[concept_id].last_studied = datetime.now()
                self.concept_progress[concept_id].study_sessions += 1
        
        self.save_data()
        return session
    
    def create_learning_goal(
        self,
        title: str,
        description: str,
        target_date: datetime,
        priority: str = "medium",
        related_concepts: Optional[List[str]] = None
    ) -> LearningGoal:
        """
        Create a new learning goal.
        
        Args:
            title: Goal title.
            description: Goal description.
            target_date: Target completion date.
            priority: Goal priority level.
            related_concepts: List of related concept IDs.
        
        Returns:
            Created LearningGoal object.
        """
        goal = LearningGoal(
            goal_id=f"goal_{len(self.goals) + 1}",
            title=title,
            description=description,
            target_date=target_date,
            status="active",
            priority=priority,
            related_concepts=related_concepts or []
        )
        
        self.goals.append(goal)
        self.save_data()
        return goal
    
    def update_goal_progress(self, goal_id: str, progress_percentage: float) -> Optional[LearningGoal]:
        """
        Update progress for a learning goal.
        
        Args:
            goal_id: ID of the goal to update.
            progress_percentage: New progress percentage (0-100).
        
        Returns:
            Updated LearningGoal or None if not found.
        """
        for goal in self.goals:
            if goal.goal_id == goal_id:
                goal.progress_percentage = progress_percentage
                
                # Update status based on progress and date
                if progress_percentage >= 100:
                    goal.status = "completed"
                elif datetime.now() > goal.target_date:
                    goal.status = "expired"
                else:
                    goal.status = "active"
                
                self.save_data()
                return goal
        
        return None
    
    def record_progress(
        self,
        concept_id: str,
        score: float,
        time_spent_minutes: float,
        difficulty_rating: Optional[float] = None
    ) -> LearningProgress:
        """
        Record progress for a concept.
        
        Args:
            concept_id: ID of the concept.
            score: Score achieved (0-100).
            time_spent_minutes: Time spent on the concept.
            difficulty_rating: User-rated difficulty (0-10).
        
        Returns:
            Updated LearningProgress object.
        """
        # Initialize if not exists
        if concept_id not in self.concept_progress:
            self.initialize_concept(concept_id, concept_id, "intermediate")
        
        # Get existing progress or create new
        existing = self._get_learning_progress(concept_id)
        if existing:
            # Update existing
            existing.attempts += 1
            existing.total_time_minutes += time_spent_minutes
            existing.average_score = (
                (existing.average_score * (existing.attempts - 1) + score) / existing.attempts
            )
            if difficulty_rating is not None:
                existing.difficulty_rating = difficulty_rating
            existing.last_attempt_date = datetime.now()
        else:
            # Create new
            existing = LearningProgress(
                concept_id=concept_id,
                attempts=1,
                average_score=score,
                total_time_minutes=time_spent_minutes,
                difficulty_rating=difficulty_rating,
                last_attempt_date=datetime.now()
            )
            self._learning_progress[concept_id] = existing
        
        self.save_data()
        return existing
    
    def get_learning_progress(self, concept_id: str) -> Optional[LearningProgress]:
        """Get learning progress for a concept."""
        return self._get_learning_progress(concept_id)
    
    def _get_learning_progress(self, concept_id: str) -> Optional[LearningProgress]:
        """Get or create learning progress for a concept."""
        if concept_id not in self._learning_progress:
            return None
        return self._learning_progress[concept_id]
    
    def get_all_learning_progress(self) -> List[LearningProgress]:
        """Get all learning progress records."""
        return list(self._learning_progress.values())
    
    def get_learning_progress_summary(self) -> Dict[str, Any]:
        """Get summary of all learning progress."""
        progress_list = self.get_all_learning_progress()
        total_concepts = len(progress_list)
        total_attempts = sum(p.attempts for p in progress_list)
        average_score = (
            sum(p.average_score for p in progress_list) / total_concepts
            if total_concepts > 0 else 0.0
        )
        
        return {
            "total_concepts_tracked": total_concepts,
            "total_attempts": total_attempts,
            "average_score": round(average_score, 2)
        }
    
    def get_concept_status(self, concept_id: str) -> Optional[ConceptProgress]:
        """Get the current status of a concept."""
        return self.concept_progress.get(concept_id)
    
    def get_all_concepts(self) -> List[ConceptProgress]:
        """Get all tracked concepts."""
        return list(self.concept_progress.values())
    
    def get_concepts_by_status(self, status: str) -> List[ConceptProgress]:
        """Get concepts filtered by status."""
        return [c for c in self.concept_progress.values() if c.status == status]
    
    def get_knowledge_gaps(self, threshold: float = 50.0) -> List[ConceptProgress]:
        """
        Identify concepts that need review.
        
        Args:
            threshold: Mastery percentage below which concept is considered a gap.
        
        Returns:
            List of concepts with low mastery.
        """
        return [
            c for c in self.concept_progress.values()
            if c.mastery_percentage < threshold and c.status != ProgressStatus.NOT_STARTED.value
        ]
    
    def get_study_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive study statistics.
        
        Returns:
            Dictionary with study statistics.
        """
        total_study_time = sum(
            int(c.estimated_time_spent.replace(" min", "").replace("h", "h"))
            for c in self.concept_progress.values()
        )
        
        mastered_concepts = len([c for c in self.concept_progress.values() 
                                if c.status == ProgressStatus.MASTERED.value])
        
        in_progress_concepts = len([c for c in self.concept_progress.values() 
                                   if c.status == ProgressStatus.IN_PROGRESS.value])
        
        return {
            "total_concepts": len(self.concept_progress),
            "mastered_concepts": mastered_concepts,
            "in_progress_concepts": in_progress_concepts,
            "total_study_sessions": len(self.sessions),
            "total_study_time_minutes": total_study_time,
            "average_mastery": (
                sum(c.mastery_percentage for c in self.concept_progress.values()) 
                / len(self.concept_progress)
                if self.concept_progress else 0
            ),
            "active_goals": len([g for g in self.goals if g.status == "active"]),
            "completed_goals": len([g for g in self.goals if g.status == "completed"])
        }
    
    def get_recent_sessions(self, limit: int = 10) -> List[LearningSession]:
        """Get recent learning sessions."""
        return self.sessions[-limit:]
    
    def get_active_goals(self) -> List[LearningGoal]:
        """Get all active learning goals."""
        return [g for g in self.goals if g.status == "active"]
    
    def get_overdue_goals(self) -> List[LearningGoal]:
        """Get goals that are past their target date."""
        return [g for g in self.goals if datetime.now() > g.target_date and g.status != "completed"]
    
    def generate_progress_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive progress report.
        
        Returns:
            Dictionary with progress report data.
        """
        stats = self.get_study_statistics()
        gaps = self.get_knowledge_gaps()
        
        return {
            "report_date": datetime.now().isoformat(),
            "statistics": stats,
            "knowledge_gaps": [c.to_dict() for c in gaps],
            "recent_activity": [s.to_dict() for s in self.get_recent_sessions(5)],
            "active_goals": [g.to_dict() for g in self.get_active_goals()],
            "recommendations": self._generate_recommendations(gaps, stats)
        }
    
    def _generate_recommendations(self, gaps: List[ConceptProgress], 
                                 stats: Dict[str, Any]) -> List[str]:
        """Generate personalized learning recommendations."""
        recommendations = []
        
        if len(gaps) > 0:
            recommendations.append(
                f"Focus on {len(gaps)} concept(s) that need review"
            )
        
        if stats["total_study_sessions"] == 0:
            recommendations.append("Start your learning journey by completing your first session")
        
        if stats["average_mastery"] < 50:
            recommendations.append("Consider breaking down complex concepts into smaller topics")
        
        if stats["active_goals"] > 3:
            recommendations.append("You have many active goals. Consider focusing on fewer at a time")
        
        if not recommendations:
            recommendations.append("Keep up the great progress!")
        
        return recommendations
