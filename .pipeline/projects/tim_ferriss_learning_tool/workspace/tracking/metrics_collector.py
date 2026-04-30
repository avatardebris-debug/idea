"""Metrics Collector - Collects and aggregates learning metrics."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class MetricPoint:
    """A single metric data point."""
    metric_name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }


class MetricsCollector:
    """
    Collects and aggregates learning metrics.
    
    Provides functionality for:
    - Collecting various learning metrics
    - Aggregating metrics over time periods
    - Calculating trends and statistics
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the metrics collector.
        
        Args:
            config_path: Path to metrics configuration file.
        """
        self.config = self._load_config(config_path)
        self.metrics: Dict[str, List[MetricPoint]] = {}
        self.data_dir = Path("data/metrics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_data()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load metrics configuration."""
        default_config = {
            "collection_frequency": "realtime",
            "retention_days": 365,
            "aggregation_intervals": ["hourly", "daily", "weekly", "monthly"],
            "metrics_to_track": [
                "practice_duration",
                "assessment_scores",
                "completion_rate",
                "retention_rate",
                "engagement_score"
            ]
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    default_config.update(loaded_config)
        
        return default_config
    
    def _load_data(self):
        """Load existing metrics data from files."""
        metrics_file = self.data_dir / "metrics.json"
        if metrics_file.exists():
            with open(metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for metric_name, points in data.get("metrics", {}).items():
                    loaded_points = []
                    for point in points:
                        # Convert timestamp string back to datetime
                        point_data = point.copy()
                        if "timestamp" in point_data and isinstance(point_data["timestamp"], str):
                            point_data["timestamp"] = datetime.fromisoformat(point_data["timestamp"])
                        loaded_points.append(MetricPoint(**point_data))
                    self.metrics[metric_name] = loaded_points
    
    def save_data(self):
        """Save all metrics data to files."""
        data = {
            "metrics": {
                name: [p.to_dict() for p in points]
                for name, points in self.metrics.items()
            }
        }
        
        with open(self.data_dir / "metrics.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def collect_metric(
        self,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MetricPoint:
        """
        Collect a new metric point.
        
        Args:
            metric_name: Name of the metric.
            value: Metric value.
            metadata: Additional metadata.
        
        Returns:
            Created MetricPoint object.
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        point = MetricPoint(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.metrics[metric_name].append(point)
        self._cleanup_old_data()
        self.save_data()
        
        return point
    
    def collect_practice_duration(self, duration_minutes: float, activity_id: str) -> MetricPoint:
        """Collect practice duration metric."""
        return self.collect_metric(
            metric_name="practice_duration",
            value=duration_minutes,
            metadata={"activity_id": activity_id}
        )
    
    def collect_assessment_score(self, score: float, activity_id: str) -> MetricPoint:
        """Collect assessment score metric."""
        return self.collect_metric(
            metric_name="assessment_scores",
            value=score,
            metadata={"activity_id": activity_id}
        )
    
    def collect_completion_rate(self, rate: float, activity_id: str) -> MetricPoint:
        """Collect completion rate metric."""
        return self.collect_metric(
            metric_name="completion_rate",
            value=rate,
            metadata={"activity_id": activity_id}
        )
    
    def collect_retention_rate(self, rate: float, activity_id: str):
        """Collect retention rate metric."""
        self.collect_metric(
            metric_name="retention_rate",
            value=rate,
            metadata={"activity_id": activity_id}
        )
    
    def collect_engagement_score(self, score: float, activity_id: str):
        """Collect engagement score metric."""
        self.collect_metric(
            metric_name="engagement_score",
            value=score,
            metadata={"activity_id": activity_id}
        )
    
    def _cleanup_old_data(self):
        """Remove old metric data beyond retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.config.get("retention_days", 365))
        
        for metric_name in self.metrics:
            self.metrics[metric_name] = [
                point for point in self.metrics[metric_name]
                if point.timestamp >= cutoff_date
            ]
    
    def get_metric_history(
        self,
        metric_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MetricPoint]:
        """
        Get historical data for a metric.
        
        Args:
            metric_name: Name of the metric.
            start_date: Start date filter.
            end_date: End date filter.
        
        Returns:
            List of MetricPoint objects.
        """
        if metric_name not in self.metrics:
            return []
        
        points = self.metrics[metric_name]
        
        if start_date:
            points = [p for p in points if p.timestamp >= start_date]
        
        if end_date:
            points = [p for p in points if p.timestamp <= end_date]
        
        return sorted(points, key=lambda x: x.timestamp)
    
    def calculate_statistics(
        self,
        metric_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Calculate statistics for a metric.
        
        Args:
            metric_name: Name of the metric.
            start_date: Start date filter.
            end_date: End date filter.
        
        Returns:
            Dictionary with statistical measures.
        """
        points = self.get_metric_history(metric_name, start_date, end_date)
        
        if not points:
            return {
                "count": 0,
                "mean": 0,
                "median": 0,
                "min": 0,
                "max": 0,
                "std_dev": 0
            }
        
        values = [p.value for p in points]
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            "count": n,
            "mean": sum(values) / n,
            "median": sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2,
            "min": min(values),
            "max": max(values),
            "std_dev": self._calculate_std_dev(values, sum(values) / n)
        }
    
    def _calculate_std_dev(self, values: List[float], mean: float) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def calculate_trend(
        self,
        metric_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate trend for a metric.
        
        Args:
            metric_name: Name of the metric.
            start_date: Start date filter.
            end_date: End date filter.
        
        Returns:
            Dictionary with trend information.
        """
        points = self.get_metric_history(metric_name, start_date, end_date)
        
        if len(points) < 2:
            return {
                "trend": "insufficient_data",
                "slope": 0,
                "direction": "neutral"
            }
        
        # Simple linear regression
        n = len(points)
        x_values = list(range(n))
        y_values = [p.value for p in points]
        
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        slope = numerator / denominator if denominator != 0 else 0
        
        return {
            "trend": "increasing" if slope > 0.01 else "decreasing" if slope < -0.01 else "stable",
            "slope": slope,
            "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
            "strength": abs(slope)
        }
    
    def aggregate_metric(
        self,
        metric_name: str,
        interval: str = "daily",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Aggregate metric data by time interval.
        
        Args:
            metric_name: Name of the metric.
            interval: Aggregation interval (hourly, daily, weekly, monthly).
            start_date: Start date filter.
            end_date: End date filter.
        
        Returns:
            List of aggregated data points.
        """
        points = self.get_metric_history(metric_name, start_date, end_date)
        
        if not points:
            return []
        
        aggregated = []
        current_period_start = None
        current_values = []
        
        for point in sorted(points, key=lambda x: x.timestamp):
            period_start = self._get_period_start(point.timestamp, interval)
            
            if current_period_start != period_start:
                if current_period_start:
                    aggregated.append({
                        "period_start": current_period_start.isoformat(),
                        "period_end": period_start.isoformat(),
                        "value": sum(current_values) / len(current_values),
                        "count": len(current_values)
                    })
                
                current_period_start = period_start
                current_values = []
            
            current_values.append(point.value)
        
        # Add last period
        if current_values:
            aggregated.append({
                "period_start": current_period_start.isoformat(),
                "period_end": datetime.now().isoformat(),
                "value": sum(current_values) / len(current_values),
                "count": len(current_values)
            })
        
        return aggregated
    
    def _get_period_start(self, timestamp: datetime, interval: str) -> datetime:
        """Get the start of the period for a timestamp."""
        if interval == "hourly":
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif interval == "daily":
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif interval == "weekly":
            days_since_monday = timestamp.weekday()
            return (timestamp - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        elif interval == "monthly":
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return timestamp
    
    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all collected metrics.
        
        Returns:
            Dictionary with summary statistics for all metrics.
        """
        summary = {}
        
        for metric_name in self.metrics:
            stats = self.calculate_statistics(metric_name)
            trend = self.calculate_trend(metric_name)
            
            summary[metric_name] = {
                "statistics": stats,
                "trend": trend,
                "last_value": self.metrics[metric_name][-1].value if self.metrics[metric_name] else None,
                "last_updated": self.metrics[metric_name][-1].timestamp.isoformat() if self.metrics[metric_name] else None
            }
        
        return summary
