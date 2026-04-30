"""Learning Analytics - Comprehensive tracking and analytics for learning activities.

This module provides a complete tracking system for learning activities,
including progress tracking, metrics collection, and analytics dashboards.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .progress_tracker import ProgressTracker, LearningActivity
from .metrics_collector import MetricsCollector
from .analytics_dashboard import AnalyticsDashboard


class LearningAnalytics:
    """
    Main class for learning analytics and tracking.
    
    Integrates progress tracking, metrics collection, and analytics
    into a unified system for monitoring learning activities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the learning analytics system.
        
        Args:
            config_path: Path to configuration file.
        """
        self.progress_tracker = ProgressTracker(config_path)
        self.metrics_collector = MetricsCollector(config_path)
        self.analytics_dashboard = AnalyticsDashboard(config_path)
        
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration."""
        default_config = {
            "tracking_enabled": True,
            "metrics_enabled": True,
            "dashboard_enabled": True,
            "auto_save": True
        }
        
        if config_path:
            import yaml
            import os
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        default_config.update(loaded_config)
        
        return default_config
    
    def create_learning_activity(
        self,
        name: str,
        description: str,
        target_completion: float = 100.0,
        estimated_duration_hours: float = 10.0
    ) -> LearningActivity:
        """
        Create a new learning activity to track.
        
        Args:
            name: Name of the activity.
            description: Description of the activity.
            target_completion: Target completion percentage.
            estimated_duration_hours: Estimated time to complete.
        
        Returns:
            Created LearningActivity object.
        """
        activity = self.progress_tracker.create_activity(
            name=name,
            description=description,
            target_completion=target_completion,
            estimated_duration_hours=estimated_duration_hours
        )
        
        # Initialize metrics for this activity
        self.metrics_collector.collect_completion_rate(0.0, activity.activity_id)
        
        return activity
    
    def update_activity_progress(
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
        activity = self.progress_tracker.update_progress(
            activity_id=activity_id,
            progress_percentage=progress_percentage,
            notes=notes
        )
        
        if activity:
            # Update metrics
            self.metrics_collector.collect_completion_rate(
                progress_percentage,
                activity_id
            )
        
        return activity
    
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
        activity = self.progress_tracker.log_practice_session(
            activity_id=activity_id,
            duration_minutes=duration_minutes,
            notes=notes
        )
        
        if activity:
            # Update metrics
            self.metrics_collector.collect_practice_duration(
                duration_minutes,
                activity_id
            )
        
        return activity
    
    def record_assessment(
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
        activity = self.progress_tracker.record_assessment_score(
            activity_id=activity_id,
            score=score,
            max_score=max_score,
            notes=notes
        )
        
        if activity:
            # Update metrics
            self.metrics_collector.collect_assessment_score(
                score,
                activity_id
            )
        
        return activity
    
    def get_activity_summary(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a comprehensive summary of an activity.
        
        Args:
            activity_id: ID of the activity.
        
        Returns:
            Dictionary with activity summary.
        """
        summary = self.progress_tracker.get_activity_summary(activity_id)
        
        if summary:
            # Add metrics data
            metrics_summary = self.metrics_collector.get_all_metrics_summary()
            if "completion_rate" in metrics_summary:
                summary["metrics"] = metrics_summary["completion_rate"]
        
        return summary
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """
        Get overall progress across all activities.
        
        Returns:
            Dictionary with overall progress statistics.
        """
        progress = self.progress_tracker.get_overall_progress()
        
        # Add metrics insights
        metrics_summary = self.metrics_collector.get_all_metrics_summary()
        progress["metrics_insights"] = metrics_summary
        
        return progress
    
    def get_analytics_insights(self) -> List[Dict[str, Any]]:
        """
        Get actionable insights from analytics data.
        
        Returns:
            List of insight dictionaries.
        """
        insights = self.analytics_dashboard.get_insights()
        
        # Add insights from progress tracker
        progress_insights = self._generate_progress_insights()
        insights.extend(progress_insights)
        
        # Add insights from metrics collector
        metrics_insights = self._generate_metrics_insights()
        insights.extend(metrics_insights)
        
        return insights
    
    def _generate_progress_insights(self) -> List[Dict[str, Any]]:
        """Generate insights from progress data."""
        insights = []
        
        # Analyze progress patterns
        activities = self.progress_tracker.activities
        
        for activity in activities:
            if activity.current_progress < 50 and activity.status == "active":
                insights.append({
                    "type": "progress",
                    "severity": "medium",
                    "activity_id": activity.activity_id,
                    "activity_name": activity.name,
                    "message": f"Activity '{activity.name}' is less than 50% complete",
                    "recommendation": "Review activity goals and adjust if necessary"
                })
        
        return insights
    
    def _generate_metrics_insights(self) -> List[Dict[str, Any]]:
        """Generate insights from metrics data."""
        insights = []
        
        # Analyze metrics trends
        metrics_summary = self.metrics_collector.get_all_metrics_summary()
        
        for metric_name, metric_data in metrics_summary.items():
            if "trend" in metric_data:
                trend = metric_data["trend"]
                if trend["direction"] == "decreasing":
                    insights.append({
                        "type": "metrics",
                        "severity": "medium",
                        "metric_name": metric_name,
                        "message": f"Metric '{metric_name}' is showing a decreasing trend",
                        "recommendation": "Investigate the cause and adjust learning approach"
                    })
        
        return insights
    
    def generate_report(
        self,
        report_type: str = "comprehensive",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive analytics report.
        
        Args:
            report_type: Type of report.
            start_date: Start date for report.
            end_date: End date for report.
        
        Returns:
            Report dictionary.
        """
        report = self.analytics_dashboard.generate_report(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add progress data to report
        report["sections"]["progress_data"] = self.get_overall_progress()
        
        # Add activities data
        report["sections"]["activities_data"] = {
            "activities": [
                self.get_activity_summary(a.activity_id)
                for a in self.progress_tracker.activities
            ]
        }
        
        return report
    
    def export_report(self, report: Dict[str, Any], format: str = "json") -> str:
        """
        Export a report to a file.
        
        Args:
            report: Report dictionary.
            format: Export format (json, csv, pdf).
        
        Returns:
            Path to exported file.
        """
        return self.analytics_dashboard.export_report(report, format)
    
    def get_dashboard_layout(self) -> Dict[str, Any]:
        """
        Get dashboard layout configuration.
        
        Returns:
            Dashboard layout dictionary.
        """
        return self.analytics_dashboard.get_dashboard_layout()
    
    def schedule_auto_export(self, frequency: str = "weekly"):
        """
        Schedule automatic report exports.
        
        Args:
            frequency: Export frequency (daily, weekly, monthly).
        """
        self.analytics_dashboard.schedule_auto_export(frequency)
    
    def disable_auto_export(self):
        """Disable automatic report exports."""
        self.analytics_dashboard.disable_auto_export()
    
    def save_all_data(self):
        """Save all tracking data."""
        if self.config.get("auto_save", True):
            self.progress_tracker.save_data()
            self.metrics_collector.save_data()
            self.analytics_dashboard.save_data()
