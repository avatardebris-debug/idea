"""Tests for Learning Analytics Tracking System.

This module contains comprehensive tests for the tracking system components:
- ProgressTracker
- MetricsCollector
- AnalyticsDashboard
- LearningAnalytics (integration)
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tracking.progress_tracker import ProgressTracker, LearningActivity, ProgressRecord
from tracking.metrics_collector import MetricsCollector, MetricPoint
from tracking.analytics_dashboard import AnalyticsDashboard, DashboardWidget
from tracking.learning_analytics import LearningAnalytics


class TestProgressTracker:
    """Tests for ProgressTracker class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = ProgressTracker()
    
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_activity(self):
        """Test creating a new learning activity."""
        activity = self.tracker.create_activity(
            name="Test Activity",
            description="Test Description",
            target_completion=100.0,
            estimated_duration_hours=10.0
        )
        
        assert activity is not None
        assert activity.name == "Test Activity"
        assert activity.description == "Test Description"
        assert activity.target_completion == 100.0
        assert activity.estimated_duration_hours == 10.0
        assert activity.current_progress == 0.0
        assert activity.status == "active"
        assert activity.created_date is not None
    
    def test_create_activity_with_custom_target(self):
        """Test creating activity with custom target completion."""
        activity = self.tracker.create_activity(
            name="Test Activity",
            description="Test",
            target_completion=75.0
        )
        
        assert activity.target_completion == 75.0
    
    def test_update_progress(self):
        """Test updating activity progress."""
        activity = self.tracker.create_activity(
            name="Test Activity",
            description="Test"
        )
        
        updated = self.tracker.update_progress(
            activity_id=activity.activity_id,
            progress_percentage=50.0,
            notes="Halfway done"
        )
        
        assert updated is not None
        assert updated.current_progress == 50.0
        assert updated.status == "active"
        assert updated.last_updated is not None
    
    def test_update_progress_completes_activity(self):
        """Test that reaching target completion marks activity as completed."""
        activity = self.tracker.create_activity(
            name="Test Activity",
            description="Test",
            target_completion=100.0
        )
        
        updated = self.tracker.update_progress(
            activity_id=activity.activity_id,
            progress_percentage=100.0
        )
        
        assert updated.status == "completed"
    
    def test_update_progress_paused(self):
        """Test that progress below 100% keeps activity active."""
        activity = self.tracker.create_activity(
            name="Test Activity",
            description="Test",
            target_completion=100.0
        )
        
        updated = self.tracker.update_progress(
            activity_id=activity.activity_id,
            progress_percentage=50.0
        )
        
        assert updated.status == "active"
    
    def test_log_practice_session(self):
        """Test logging a practice session."""
        activity = self.tracker.create_activity(
            name="Test Activity",
            description="Test"
        )
        
        updated = self.tracker.log_practice_session(
            activity_id=activity.activity_id,
            duration_minutes=30,
            notes="Practice session"
        )
        
        assert updated is not None
        assert len(updated.practice_sessions) == 1
        assert updated.practice_sessions[0].duration_minutes == 30
        assert updated.practice_sessions[0].notes == "Practice session"
    
    def test_record_assessment_score(self):
        """Test recording an assessment score."""
        activity = self.tracker.create_activity(
            name="Test Activity",
            description="Test"
        )
        
        updated = self.tracker.record_assessment_score(
            activity_id=activity.activity_id,
            score=85.0,
            max_score=100.0,
            notes="First assessment"
        )
        
        assert updated is not None
        assert len(updated.assessment_scores) == 1
        assert updated.assessment_scores[0].score == 85.0
        assert updated.assessment_scores[0].max_score == 100.0
    
    def test_get_activity_summary(self):
        """Test getting activity summary."""
        activity = self.tracker.create_activity(
            name="Test Activity",
            description="Test",
            target_completion=100.0,
            estimated_duration_hours=10.0
        )
        
        # Add some data
        self.tracker.update_progress(
            activity_id=activity.activity_id,
            progress_percentage=50.0
        )
        self.tracker.log_practice_session(
            activity_id=activity.activity_id,
            duration_minutes=60
        )
        self.tracker.record_assessment_score(
            activity_id=activity.activity_id,
            score=85.0
        )
        
        summary = self.tracker.get_activity_summary(activity.activity_id)
        
        assert summary is not None
        assert summary["activity_id"] == activity.activity_id
        assert summary["name"] == "Test Activity"
        assert summary["current_progress"] == 50.0
        assert summary["status"] == "active"
        assert summary["practice_sessions_count"] == 1
        assert summary["assessment_scores_count"] == 1
    
    def test_get_activity_summary_not_found(self):
        """Test getting summary for non-existent activity."""
        summary = self.tracker.get_activity_summary("non_existent_id")
        assert summary is None
    
    def test_get_overall_progress(self):
        """Test getting overall progress."""
        activity1 = self.tracker.create_activity(
            name="Activity 1",
            description="Test"
        )
        activity2 = self.tracker.create_activity(
            name="Activity 2",
            description="Test"
        )
        
        self.tracker.update_progress(
            activity_id=activity1.activity_id,
            progress_percentage=50.0
        )
        self.tracker.update_progress(
            activity_id=activity2.activity_id,
            progress_percentage=100.0
        )
        
        overall = self.tracker.get_overall_progress()
        
        assert overall["total_activities"] == 2
        assert overall["completed_activities"] == 1
        assert overall["active_activities"] == 1
        assert overall["average_progress"] == 75.0
    
    def test_delete_activity(self):
        """Test deleting an activity."""
        activity = self.tracker.create_activity(
            name="Test Activity",
            description="Test"
        )
        
        result = self.tracker.delete_activity(activity.activity_id)
        
        assert result is True
        assert self.tracker.get_activity_summary(activity.activity_id) is None
    
    def test_delete_non_existent_activity(self):
        """Test deleting non-existent activity."""
        result = self.tracker.delete_activity("non_existent_id")
        assert result is False


class TestMetricsCollector:
    """Tests for MetricsCollector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.collector = MetricsCollector()
    
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_collect_metric(self):
        """Test collecting a metric."""
        point = self.collector.collect_metric(
            metric_name="test_metric",
            value=42.0,
            metadata={"test": True}
        )
        
        assert point is not None
        assert point.metric_name == "test_metric"
        assert point.value == 42.0
        assert point.metadata == {"test": True}
        assert point.timestamp is not None
    
    def test_collect_practice_duration(self):
        """Test collecting practice duration."""
        point = self.collector.collect_practice_duration(
            duration_minutes=30,
            activity_id="activity_123"
        )
        
        assert point.metric_name == "practice_duration"
        assert point.value == 30.0
        assert point.metadata["activity_id"] == "activity_123"
    
    def test_collect_assessment_score(self):
        """Test collecting assessment score."""
        point = self.collector.collect_assessment_score(
            score=85.0,
            activity_id="activity_123"
        )
        
        assert point.metric_name == "assessment_scores"
        assert point.value == 85.0
    
    def test_collect_completion_rate(self):
        """Test collecting completion rate."""
        point = self.collector.collect_completion_rate(
            rate=75.0,
            activity_id="activity_123"
        )
        
        assert point.metric_name == "completion_rate"
        assert point.value == 75.0
    
    def test_get_metric_history(self):
        """Test getting metric history."""
        self.collector.collect_metric(
            metric_name="test_metric",
            value=10.0
        )
        self.collector.collect_metric(
            metric_name="test_metric",
            value=20.0
        )
        self.collector.collect_metric(
            metric_name="test_metric",
            value=30.0
        )
        
        history = self.collector.get_metric_history("test_metric")
        
        assert len(history) == 3
        assert [p.value for p in history] == [10.0, 20.0, 30.0]
    
    def test_get_metric_history_empty(self):
        """Test getting history for non-existent metric."""
        history = self.collector.get_metric_history("non_existent")
        assert len(history) == 0
    
    def test_calculate_statistics(self):
        """Test calculating statistics."""
        for i in range(1, 11):
            self.collector.collect_metric(
                metric_name="test_metric",
                value=float(i)
            )
        
        stats = self.collector.calculate_statistics("test_metric")
        
        assert stats["count"] == 10
        assert stats["mean"] == 5.5
        assert stats["min"] == 1.0
        assert stats["max"] == 10.0
        assert stats["std_dev"] > 0
    
    def test_calculate_statistics_empty(self):
        """Test statistics for empty metric."""
        stats = self.collector.calculate_statistics("non_existent")
        
        assert stats["count"] == 0
        assert stats["mean"] == 0
    
    def test_calculate_trend(self):
        """Test calculating trend."""
        for i in range(1, 11):
            self.collector.collect_metric(
                metric_name="test_metric",
                value=float(i)
            )
        
        trend = self.collector.calculate_trend("test_metric")
        
        assert trend["direction"] == "increasing"
        assert trend["trend"] == "increasing"
        assert trend["slope"] > 0
    
    def test_aggregate_metric_hourly(self):
        """Test aggregating metric by hour."""
        for i in range(1, 11):
            self.collector.collect_metric(
                metric_name="test_metric",
                value=float(i)
            )
        
        aggregated = self.collector.aggregate_metric(
            metric_name="test_metric",
            interval="hourly"
        )
        
        assert len(aggregated) > 0
        assert "period_start" in aggregated[0]
        assert "value" in aggregated[0]
    
    def test_aggregate_metric_daily(self):
        """Test aggregating metric by day."""
        for i in range(1, 11):
            self.collector.collect_metric(
                metric_name="test_metric",
                value=float(i)
            )
        
        aggregated = self.collector.aggregate_metric(
            metric_name="test_metric",
            interval="daily"
        )
        
        assert len(aggregated) > 0


class TestAnalyticsDashboard:
    """Tests for AnalyticsDashboard class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.dashboard = AnalyticsDashboard()
    
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_widget(self):
        """Test creating a dashboard widget."""
        widget = self.dashboard.create_widget(
            widget_type="progress_overview",
            title="Progress Overview",
            description="Overview of progress",
            data_source="progress_tracker",
            config={"show_charts": True}
        )
        
        assert widget is not None
        assert widget.widget_type == "progress_overview"
        assert widget.title == "Progress Overview"
        assert widget.data_source == "progress_tracker"
        assert widget.config == {"show_charts": True}
        assert widget.created_date is not None
    
    def test_get_widget_data(self):
        """Test getting widget data."""
        widget = self.dashboard.create_widget(
            widget_type="progress_overview",
            title="Progress Overview",
            description="Overview",
            data_source="progress_tracker",
            config={}
        )
        
        data = self.dashboard.get_widget_data(widget.widget_id)
        
        assert data is not None
        assert "widget" in data
        assert "data" in data
    
    def test_get_widget_data_not_found(self):
        """Test getting data for non-existent widget."""
        data = self.dashboard.get_widget_data("non_existent_id")
        assert data is None
    
    def test_generate_report(self):
        """Test generating a report."""
        report = self.dashboard.generate_report(
            report_type="comprehensive"
        )
        
        assert report is not None
        assert "report_id" in report
        assert "report_type" in report
        assert "generated_at" in report
        assert "sections" in report
    
    def test_generate_report_invalid_type(self):
        """Test generating report with invalid type."""
        report = self.dashboard.generate_report(
            report_type="invalid_type"
        )
        
        assert report is not None
        assert report["report_type"] == "comprehensive"
    
    def test_get_dashboard_layout(self):
        """Test getting dashboard layout."""
        layout = self.dashboard.get_dashboard_layout()
        
        assert layout is not None
        assert "widgets" in layout
        assert "layout" in layout
        assert "config" in layout
    
    def test_get_insights(self):
        """Test getting insights."""
        insights = self.dashboard.get_insights()
        
        assert isinstance(insights, list)
    
    def test_export_report_json(self):
        """Test exporting report as JSON."""
        report = self.dashboard.generate_report(
            report_type="comprehensive"
        )
        
        filepath = self.dashboard.export_report(report, "json")
        
        assert filepath is not None
        assert os.path.exists(filepath)
        assert filepath.endswith(".json")
        
        with open(filepath, 'r') as f:
            exported_data = json.load(f)
        
        assert exported_data["report_id"] == report["report_id"]
    
    def test_export_report_csv(self):
        """Test exporting report as CSV."""
        report = self.dashboard.generate_report(
            report_type="comprehensive"
        )
        
        filepath = self.dashboard.export_report(report, "csv")
        
        assert filepath is not None
        assert os.path.exists(filepath)
        assert filepath.endswith(".csv")
    
    def test_export_report_pdf(self):
        """Test exporting report as PDF."""
        report = self.dashboard.generate_report(
            report_type="comprehensive"
        )
        
        filepath = self.dashboard.export_report(report, "pdf")
        
        assert filepath is not None
        assert os.path.exists(filepath)
        assert filepath.endswith(".pdf")
    
    def test_schedule_auto_export(self):
        """Test scheduling automatic export."""
        self.dashboard.schedule_auto_export("weekly")
        
        assert self.dashboard.config["auto_export"] is True
        assert self.dashboard.config["export_frequency"] == "weekly"
    
    def test_disable_auto_export(self):
        """Test disabling automatic export."""
        self.dashboard.schedule_auto_export("weekly")
        self.dashboard.disable_auto_export()
        
        assert self.dashboard.config["auto_export"] is False


class TestLearningAnalytics:
    """Integration tests for LearningAnalytics class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.analytics = LearningAnalytics()
    
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_learning_activity(self):
        """Test creating a learning activity through main class."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test Description",
            target_completion=100.0,
            estimated_duration_hours=10.0
        )
        
        assert activity is not None
        assert activity.name == "Test Activity"
        assert activity.current_progress == 0.0
    
    def test_update_activity_progress(self):
        """Test updating activity progress through main class."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test"
        )
        
        updated = self.analytics.update_activity_progress(
            activity_id=activity.activity_id,
            progress_percentage=50.0,
            notes="Halfway done"
        )
        
        assert updated is not None
        assert updated.current_progress == 50.0
    
    def test_log_practice_session(self):
        """Test logging practice session through main class."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test"
        )
        
        updated = self.analytics.log_practice_session(
            activity_id=activity.activity_id,
            duration_minutes=30,
            notes="Practice session"
        )
        
        assert updated is not None
        assert len(updated.practice_sessions) == 1
    
    def test_record_assessment(self):
        """Test recording assessment through main class."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test"
        )
        
        updated = self.analytics.record_assessment(
            activity_id=activity.activity_id,
            score=85.0,
            max_score=100.0,
            notes="Assessment"
        )
        
        assert updated is not None
        assert len(updated.assessment_scores) == 1
    
    def test_get_activity_summary(self):
        """Test getting activity summary through main class."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test"
        )
        
        self.analytics.update_activity_progress(
            activity_id=activity.activity_id,
            progress_percentage=50.0
        )
        
        summary = self.analytics.get_activity_summary(activity.activity_id)
        
        assert summary is not None
        assert summary["activity_id"] == activity.activity_id
        assert summary["current_progress"] == 50.0
    
    def test_get_overall_progress(self):
        """Test getting overall progress through main class."""
        activity1 = self.analytics.create_learning_activity(
            name="Activity 1",
            description="Test"
        )
        activity2 = self.analytics.create_learning_activity(
            name="Activity 2",
            description="Test"
        )
        
        self.analytics.update_activity_progress(
            activity_id=activity1.activity_id,
            progress_percentage=50.0
        )
        self.analytics.update_activity_progress(
            activity_id=activity2.activity_id,
            progress_percentage=100.0
        )
        
        progress = self.analytics.get_overall_progress()
        
        assert progress["total_activities"] == 2
        assert progress["completed_activities"] == 1
    
    def test_get_analytics_insights(self):
        """Test getting analytics insights through main class."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test"
        )
        
        insights = self.analytics.get_analytics_insights()
        
        assert isinstance(insights, list)
    
    def test_generate_report(self):
        """Test generating report through main class."""
        report = self.analytics.generate_report(
            report_type="comprehensive"
        )
        
        assert report is not None
        assert "sections" in report
        assert "progress_data" in report
        assert "activities_data" in report
    
    def test_export_report(self):
        """Test exporting report through main class."""
        report = self.analytics.generate_report(
            report_type="comprehensive"
        )
        
        filepath = self.analytics.export_report(report, "json")
        
        assert filepath is not None
        assert os.path.exists(filepath)
    
    def test_save_all_data(self):
        """Test saving all data."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test"
        )
        
        self.analytics.save_all_data()
        
        # Verify data was saved
        summary = self.analytics.get_activity_summary(activity.activity_id)
        assert summary is not None


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.analytics = LearningAnalytics()
    
    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_progress_percentage_boundary(self):
        """Test progress at boundary values."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test"
        )
        
        # Test 0%
        self.analytics.update_activity_progress(
            activity_id=activity.activity_id,
            progress_percentage=0.0
        )
        
        # Test 100%
        self.analytics.update_activity_progress(
            activity_id=activity.activity_id,
            progress_percentage=100.0
        )
        
        # Test >100% (should be clamped)
        self.analytics.update_activity_progress(
            activity_id=activity.activity_id,
            progress_percentage=150.0
        )
        
        # Verify it's clamped to 100%
        summary = self.analytics.get_activity_summary(activity.activity_id)
        assert summary["current_progress"] == 100.0
    
    def test_negative_duration(self):
        """Test negative practice duration."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test"
        )
        
        # Should handle negative duration gracefully
        self.analytics.log_practice_session(
            activity_id=activity.activity_id,
            duration_minutes=-30,
            notes="Negative duration"
        )
        
        summary = self.analytics.get_activity_summary(activity.activity_id)
        assert summary is not None
    
    def test_invalid_score(self):
        """Test invalid assessment score."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description="Test"
        )
        
        # Test score > max
        self.analytics.record_assessment(
            activity_id=activity.activity_id,
            score=150.0,
            max_score=100.0
        )
        
        summary = self.analytics.get_activity_summary(activity.activity_id)
        assert summary is not None
    
    def test_multiple_activities(self):
        """Test with multiple activities."""
        for i in range(10):
            self.analytics.create_learning_activity(
                name=f"Activity {i}",
                description=f"Test {i}"
            )
        
        progress = self.analytics.get_overall_progress()
        assert progress["total_activities"] == 10
    
    def test_activity_with_special_characters(self):
        """Test activity name with special characters."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity - Special: @#$%",
            description="Test with special chars"
        )
        
        assert activity is not None
        assert activity.name == "Test Activity - Special: @#$%"
    
    def test_empty_description(self):
        """Test activity with empty description."""
        activity = self.analytics.create_learning_activity(
            name="Test Activity",
            description=""
        )
        
        assert activity is not None
        assert activity.description == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
