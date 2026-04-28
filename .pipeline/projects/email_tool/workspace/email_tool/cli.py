#!/usr/bin/env python3
"""
Email Tool - Command Line Interface

A flexible email processing tool that can parse, match, and dispatch
actions on email files based on configurable rules.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

from email_tool.models import Rule, RuleType, ActionType
from email_tool.processor import EmailProcessor, PipelineBuilder, PipelineConfig


def load_rules_from_file(rules_file: str) -> list:
    """Load rules from a JSON file."""
    with open(rules_file, 'r') as f:
        rules_data = json.load(f)
    
    rules = []
    for rule_data in rules_data:
        rule = Rule(
            name=rule_data["name"],
            rule_type=RuleType(rule_data["rule_type"]),
            pattern=rule_data["pattern"],
            priority=rule_data.get("priority", 50),
            category=rule_data.get("category", "general"),
            labels=rule_data.get("labels", [])
        )
        rules.append(rule)
    
    return rules


def load_actions_from_file(actions_file: str) -> list:
    """Load actions from a JSON file."""
    with open(actions_file, 'r') as f:
        actions_data = json.load(f)
    
    actions = []
    for action_data in actions_data:
        action = (
            ActionType(action_data["action_type"]),
            action_data.get("params", {})
        )
        actions.append(action)
    
    return actions


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Email Tool - Process emails with rules and actions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single email
  python email_tool.py process email.eml --rules rules.json --actions actions.json
  
  # Process a directory of emails
  python email_tool.py process-dir ./emails --rules rules.json --actions actions.json
  
  # Dry run mode
  python email_tool.py process email.eml --rules rules.json --actions actions.json --dry-run
  
  # View statistics
  python email_tool.py stats --archive ./archive
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process a single email")
    process_parser.add_argument("email", help="Path to email file")
    process_parser.add_argument("--rules", "-r", required=True, help="Path to rules JSON file")
    process_parser.add_argument("--actions", "-a", required=True, help="Path to actions JSON file")
    process_parser.add_argument("--dry-run", "-d", action="store_true", help="Run in dry-run mode")
    process_parser.add_argument("--output", "-o", help="Output file for results (JSON)")
    
    # Process directory command
    dir_parser = subparsers.add_parser("process-dir", help="Process all emails in a directory")
    dir_parser.add_argument("directory", help="Directory containing email files")
    dir_parser.add_argument("--rules", "-r", required=True, help="Path to rules JSON file")
    dir_parser.add_argument("--actions", "-a", required=True, help="Path to actions JSON file")
    dir_parser.add_argument("--pattern", "-p", default="*.eml", help="File pattern to match")
    dir_parser.add_argument("--dry-run", "-d", action="store_true", help="Run in dry-run mode")
    dir_parser.add_argument("--output", "-o", help="Output file for results (JSON)")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="View processing statistics")
    stats_parser.add_argument("--archive", "-a", default="./archive", help="Archive directory")
    stats_parser.add_argument("--output", "-o", help="Output file for statistics (JSON)")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate rules and actions files")
    validate_parser.add_argument("--rules", "-r", help="Path to rules JSON file")
    validate_parser.add_argument("--actions", "-a", help="Path to actions JSON file")
    
    return parser


def cmd_process(args):
    """Handle the 'process' command."""
    # Load rules and actions
    rules = load_rules_from_file(args.rules)
    actions = load_actions_from_file(args.actions)
    
    # Create processor
    processor = EmailProcessor(
        base_path="./archive",
        dry_run=args.dry_run
    )
    
    # Process email
    result = processor.process_email(args.email, rules, actions)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(result, indent=2, default=str))
    
    return 0 if result["success"] else 1


def cmd_process_dir(args):
    """Handle the 'process-dir' command."""
    # Load rules and actions
    rules = load_rules_from_file(args.rules)
    actions = load_actions_from_file(args.actions)
    
    # Create processor
    processor = EmailProcessor(
        base_path="./archive",
        dry_run=args.dry_run
    )
    
    # Process directory
    results = processor.process_directory(
        args.directory,
        rules,
        actions,
        file_pattern=args.pattern
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(results, indent=2, default=str))
    
    # Print summary
    success_count = sum(1 for r in results if r["success"])
    print(f"\nProcessed {len(results)} emails: {success_count} successful, {len(results) - success_count} failed")
    
    return 0 if success_count == len(results) else 1


def cmd_stats(args):
    """Handle the 'stats' command."""
    # This would need to read from a stats file or database
    # For now, we'll just show a placeholder
    print("Statistics command - implementation pending")
    print("In a full implementation, this would read from a stats database")
    
    return 0


def cmd_validate(args):
    """Handle the 'validate' command."""
    errors = []
    
    if args.rules:
        try:
            rules = load_rules_from_file(args.rules)
            print(f"✓ Rules file valid: {args.rules}")
            print(f"  Loaded {len(rules)} rules")
        except Exception as e:
            errors.append(f"Rules file error: {e}")
            print(f"✗ Rules file invalid: {args.rules}")
    
    if args.actions:
        try:
            actions = load_actions_from_file(args.actions)
            print(f"✓ Actions file valid: {args.actions}")
            print(f"  Loaded {len(actions)} actions")
        except Exception as e:
            errors.append(f"Actions file error: {e}")
            print(f"✗ Actions file invalid: {args.actions}")
    
    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print("\n✓ All files validated successfully")
    return 0


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Map commands to handlers
    commands = {
        "process": cmd_process,
        "process-dir": cmd_process_dir,
        "stats": cmd_stats,
        "validate": cmd_validate
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
