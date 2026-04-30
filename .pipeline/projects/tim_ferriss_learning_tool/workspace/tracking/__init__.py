"""Tracking System - Comprehensive learning analytics and tracking.

This package provides a complete tracking system for learning activities,
including progress tracking, metrics collection, and analytics dashboards.

Components:
- progress_tracker: Tracks learning activity progress and completion
- metrics_collector: Collects and aggregates learning metrics
- analytics_dashboard: Provides visualization and insights
- learning_analytics: Main integration class for all tracking features
"""

from .learning_analytics import LearningAnalytics
from .progress_tracker import ProgressTracker, LearningActivity, ProgressRecord
from .metrics_collector import MetricsCollector, MetricPoint
from .analytics_dashboard import AnalyticsDashboard, DashboardWidget

__all__ = [
    "LearningAnalytics",
    "ProgressTracker",
    "LearningActivity",
    "ProgressRecord",
    "MetricsCollector",
    "MetricPoint",
    "AnalyticsDashboard",
    "DashboardWidget"
]
