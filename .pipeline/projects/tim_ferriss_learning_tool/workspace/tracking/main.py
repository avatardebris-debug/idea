#!/usr/bin/env python3
"""
Tracking System - Main Entry Point

This script provides the main entry point for the learning tracking system.
It integrates progress tracking, metrics collection, and analytics dashboards.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tracking.learning_analytics import LearningAnalytics


def main():
    """Main entry point for the tracking system."""
    parser = argparse.ArgumentParser(
        description="Learning Analytics Tracking System"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--command",
        type=str,
        required=True,
        choices=[
            "create_activity",
            "update_progress",
            "log_practice",
            "record_assessment",
            "get_summary",
            "get_overall",
            "get_insights",
            "generate_report",
            "export_report",
            "dashboard"
        ],
        help="Command to execute"
    )
    parser.add_argument(
        "--activity-id",
        type=str,
        help="Activity ID"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Activity name"
    )
    parser.add_argument(
        "--description",
        type=str,
        help="Activity description"
    )
    parser.add_argument(
        "--progress",
        type=float,
        help="Progress percentage"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Practice duration in minutes"
    )
    parser.add_argument(
        "--score",
        type=float,
        help="Assessment score"
    )
    parser.add_argument(
        "--max-score",
        type=float,
        default=100.0,
        help="Maximum assessment score"
    )
    parser.add_argument(
        "--notes",
        type=str,
        default="",
        help="Notes"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="json",
        choices=["json", "csv", "pdf"],
        help="Export format"
    )
    
    args = parser.parse_args()
    
    # Initialize the analytics system
    analytics = LearningAnalytics(args.config)
    
    # Execute command
    if args.command == "create_activity":
        activity = analytics.create_learning_activity(
            name=args.name or "New Activity",
            description=args.description or "No description",
            estimated_duration_hours=10.0
        )
        print(json.dumps(activity.to_dict(), indent=2))
    
    elif args.command == "update_progress":
        if not args.activity_id:
            print("Error: --activity-id is required")
            sys.exit(1)
        
        activity = analytics.update_activity_progress(
            activity_id=args.activity_id,
            progress_percentage=args.progress or 0,
            notes=args.notes
        )
        if activity:
            print(json.dumps(activity.to_dict(), indent=2))
        else:
            print(f"Error: Activity {args.activity_id} not found")
            sys.exit(1)
    
    elif args.command == "log_practice":
        if not args.activity_id:
            print("Error: --activity-id is required")
            sys.exit(1)
        
        activity = analytics.log_practice_session(
            activity_id=args.activity_id,
            duration_minutes=args.duration or 30,
            notes=args.notes
        )
        if activity:
            print(json.dumps(activity.to_dict(), indent=2))
        else:
            print(f"Error: Activity {args.activity_id} not found")
            sys.exit(1)
    
    elif args.command == "record_assessment":
        if not args.activity_id:
            print("Error: --activity-id is required")
            sys.exit(1)
        
        activity = analytics.record_assessment(
            activity_id=args.activity_id,
            score=args.score or 0,
            max_score=args.max_score,
            notes=args.notes
        )
        if activity:
            print(json.dumps(activity.to_dict(), indent=2))
        else:
            print(f"Error: Activity {args.activity_id} not found")
            sys.exit(1)
    
    elif args.command == "get_summary":
        if not args.activity_id:
            print("Error: --activity-id is required")
            sys.exit(1)
        
        summary = analytics.get_activity_summary(args.activity_id)
        if summary:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Error: Activity {args.activity_id} not found")
            sys.exit(1)
    
    elif args.command == "get_overall":
        progress = analytics.get_overall_progress()
        print(json.dumps(progress, indent=2))
    
    elif args.command == "get_insights":
        insights = analytics.get_analytics_insights()
        print(json.dumps(insights, indent=2))
    
    elif args.command == "generate_report":
        report = analytics.generate_report(
            report_type="comprehensive"
        )
        print(json.dumps(report, indent=2))
    
    elif args.command == "export_report":
        report = analytics.generate_report(
            report_type="comprehensive"
        )
        filepath = analytics.export_report(report, args.format)
        print(f"Report exported to: {filepath}")
    
    elif args.command == "dashboard":
        layout = analytics.get_dashboard_layout()
        print(json.dumps(layout, indent=2))
    
    # Save data
    analytics.save_all_data()


if __name__ == "__main__":
    main()
