#!/usr/bin/env python3
"""CLI interface for the property alert system."""

import argparse
import sys
from datetime import datetime

from src.models import SearchCriteria, Alert, AlertConfig, PropertyType, ListingStatus
from src.orchestrator import PropertyAlertOrchestrator


def cmd_add_criteria(args):
    """Add a new search criteria."""
    orchestrator = PropertyAlertOrchestrator()
    
    criteria = SearchCriteria(
        location=args.location,
        min_price=args.min_price,
        max_price=args.max_price,
        min_beds=args.min_beds,
        min_baths=args.min_baths,
        min_sqft=args.min_sqft,
        property_type=PropertyType(args.property_type) if args.property_type else None,
        listing_status=ListingStatus(args.listing_status) if args.listing_status else None,
        description=args.description
    )
    
    criteria_id = orchestrator.add_search_criteria(criteria)
    print(f"Added search criteria with ID: {criteria_id}")
    orchestrator.close()


def cmd_list_criteria(args):
    """List all search criteria."""
    orchestrator = PropertyAlertOrchestrator()
    criteria_list = orchestrator.list_search_criteria()
    
    if not criteria_list:
        print("No search criteria found.")
        return
    
    print(f"\n{'ID':<36} {'Location':<20} {'Price Range':<20} {'Beds':<8} {'Baths':<8} {'Sqft':<10}")
    print("-" * 100)
    
    for criteria in criteria_list:
        price_range = f"${criteria.min_price or 0} - ${criteria.max_price or '∞'}" if criteria.min_price or criteria.max_price else "Any"
        beds = criteria.min_beds or "Any"
        baths = criteria.min_baths or "Any"
        sqft = criteria.min_sqft or "Any"
        
        print(f"{criteria.id:<36} {criteria.location:<20} {price_range:<20} {beds:<8} {baths:<8} {sqft:<10}")
    
    orchestrator.close()


def cmd_delete_criteria(args):
    """Delete a search criteria."""
    orchestrator = PropertyAlertOrchestrator()
    
    if orchestrator.delete_search_criteria(args.criteria_id):
        print(f"Deleted search criteria: {args.criteria_id}")
    else:
        print(f"Search criteria not found: {args.criteria_id}")
    
    orchestrator.close()


def cmd_add_alert(args):
    """Add a new alert."""
    orchestrator = PropertyAlertOrchestrator()
    
    alert = Alert(
        criteria_id=args.criteria_id,
        email_enabled=args.email,
        sms_enabled=args.sms,
        trigger_interval_hours=args.interval,
        description=args.description
    )
    
    alert_id = orchestrator.add_alert(alert)
    print(f"Added alert with ID: {alert_id}")
    orchestrator.close()


def cmd_list_alerts(args):
    """List all alerts."""
    orchestrator = PropertyAlertOrchestrator()
    alerts_list = orchestrator.list_alerts()
    
    if not alerts_list:
        print("No alerts found.")
        return
    
    print(f"\n{'ID':<36} {'Criteria ID':<36} {'Email':<8} {'SMS':<8} {'Interval (hrs)':<15}")
    print("-" * 100)
    
    for alert in alerts_list:
        email = "Yes" if alert.email_enabled else "No"
        sms = "Yes" if alert.sms_enabled else "No"
        interval = f"{alert.trigger_interval_hours}h"
        
        print(f"{alert.id:<36} {alert.criteria_id:<36} {email:<8} {sms:<8} {interval:<15}")
    
    orchestrator.close()


def cmd_delete_alert(args):
    """Delete an alert."""
    orchestrator = PropertyAlertOrchestrator()
    
    if orchestrator.delete_alert(args.alert_id):
        print(f"Deleted alert: {args.alert_id}")
    else:
        print(f"Alert not found: {args.alert_id}")
    
    orchestrator.close()


def cmd_run(args):
    """Run an alert cycle."""
    orchestrator = PropertyAlertOrchestrator()
    
    print("Running alert cycle...")
    stats = orchestrator.run_cycle()
    
    print(f"\nCycle completed at {stats['end_time']}")
    print(f"Criteria processed: {stats['criteria_processed']}")
    print(f"Properties scraped: {stats['properties_scraped']}")
    print(f"Alerts triggered: {stats['alerts_triggered']}")
    print(f"Notifications sent: {stats['notifications_sent']}")
    
    if stats['errors']:
        print(f"\nErrors encountered:")
        for error in stats['errors']:
            print(f"  - {error}")
    
    orchestrator.close()


def cmd_config(args):
    """Manage alert configuration."""
    orchestrator = PropertyAlertOrchestrator()
    config = orchestrator.get_alert_config()
    
    if args.email:
        config.email_enabled = args.email
    if args.sms:
        config.sms_enabled = args.sms
    if args.email_address:
        config.email_address = args.email_address
    if args.sms_number:
        config.sms_number = args.sms_number
    
    orchestrator.update_alert_config(config)
    print("Alert configuration updated.")
    orchestrator.close()


def cmd_properties(args):
    """List all properties."""
    orchestrator = PropertyAlertOrchestrator()
    properties = orchestrator.list_properties()
    
    if not properties:
        print("No properties found.")
        return
    
    print(f"\n{'ZPID':<20} {'Address':<40} {'Price':<15} {'Beds':<6} {'Baths':<6} {'Sqft':<10}")
    print("-" * 100)
    
    for property in properties:
        address = f"{property.address}, {property.city}, {property.state}" if property.city else property.address
        price = f"${property.price:,}" if property.price else "N/A"
        beds = property.beds or "N/A"
        baths = property.baths or "N/A"
        sqft = property.sqft or "N/A"
        
        print(f"{property.zpid:<20} {address:<40} {price:<15} {beds:<6} {baths:<6} {sqft:<10}")
    
    orchestrator.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Property Alert System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search criteria commands
    criteria_parser = subparsers.add_parser("criteria", help="Manage search criteria")
    criteria_subparsers = criteria_parser.add_subparsers(dest="subcommand")
    
    # Add criteria
    add_criteria = criteria_subparsers.add_parser("add", help="Add a new search criteria")
    add_criteria.add_argument("--location", required=True, help="Location to search")
    add_criteria.add_argument("--min-price", type=int, help="Minimum price")
    add_criteria.add_argument("--max-price", type=int, help="Maximum price")
    add_criteria.add_argument("--min-beds", type=int, help="Minimum bedrooms")
    add_criteria.add_argument("--min-baths", type=float, help="Minimum bathrooms")
    add_criteria.add_argument("--min-sqft", type=int, help="Minimum square footage")
    add_criteria.add_argument("--property-type", choices=["HOUSE", "CONDO", "TOWNHOUSE", "MULTI_FAMILY", "LAND", "MOBILE"], help="Property type")
    add_criteria.add_argument("--listing-status", choices=["FOR_SALE", "FOR_RENT", "RECENTLY_SOLD"], help="Listing status")
    add_criteria.add_argument("--description", help="Description of the search")
    add_criteria.set_defaults(func=cmd_add_criteria)
    
    # List criteria
    list_criteria = criteria_subparsers.add_parser("list", help="List all search criteria")
    list_criteria.set_defaults(func=cmd_list_criteria)
    
    # Delete criteria
    delete_criteria = criteria_subparsers.add_parser("delete", help="Delete a search criteria")
    delete_criteria.add_argument("criteria_id", help="Criteria ID to delete")
    delete_criteria.set_defaults(func=cmd_delete_criteria)
    
    # Alert commands
    alert_parser = subparsers.add_parser("alert", help="Manage alerts")
    alert_subparsers = alert_parser.add_subparsers(dest="subcommand")
    
    # Add alert
    add_alert = alert_subparsers.add_parser("add", help="Add a new alert")
    add_alert.add_argument("--criteria-id", required=True, help="Search criteria ID")
    add_alert.add_argument("--email", action="store_true", help="Enable email notifications")
    add_alert.add_argument("--sms", action="store_true", help="Enable SMS notifications")
    add_alert.add_argument("--interval", type=int, default=24, help="Alert interval in hours")
    add_alert.add_argument("--description", help="Description of the alert")
    add_alert.set_defaults(func=cmd_add_alert)
    
    # List alerts
    list_alerts = alert_subparsers.add_parser("list", help="List all alerts")
    list_alerts.set_defaults(func=cmd_list_alerts)
    
    # Delete alert
    delete_alert = alert_subparsers.add_parser("delete", help="Delete an alert")
    delete_alert.add_argument("alert_id", help="Alert ID to delete")
    delete_alert.set_defaults(func=cmd_delete_alert)
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run an alert cycle")
    run_parser.set_defaults(func=cmd_run)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage alert configuration")
    config_parser.add_argument("--email", type=bool, help="Enable email notifications")
    config_parser.add_argument("--sms", type=bool, help="Enable SMS notifications")
    config_parser.add_argument("--email-address", help="Email address for notifications")
    config_parser.add_argument("--sms-number", help="SMS number for notifications")
    config_parser.set_defaults(func=cmd_config)
    
    # Properties command
    properties_parser = subparsers.add_parser("properties", help="List all properties")
    properties_parser.set_defaults(func=cmd_properties)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        args.command_parser.print_help()


if __name__ == "__main__":
    main()
