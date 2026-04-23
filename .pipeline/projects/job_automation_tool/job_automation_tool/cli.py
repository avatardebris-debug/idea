"""CLI interface for the job automation tool."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from job_automation_tool.parser import parse_job_description
from job_automation_tool.matcher import match_profiles


def main() -> int:
    """Main entry point for the CLI."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "parse":
        return _cmd_parse(args)
    elif args.command == "match":
        return _cmd_match(args)
    else:
        parser.print_help()
        return 1


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    ap = argparse.ArgumentParser(
        prog="job-automation",
        description="Parse job descriptions and match candidates.",
    )
    ap.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = ap.add_subparsers(dest="command", help="Available commands")

    # parse subcommand
    parse_parser = subparsers.add_parser("parse", help="Parse a job description file")
    parse_parser.add_argument("file", nargs="?", default="-", help="Job description file (default: stdin)")
    parse_parser.add_argument("--output", "-o", choices=["json", "text"], default="json", help="Output format")

    # match subcommand
    match_parser = subparsers.add_parser("match", help="Match a candidate against a job")
    match_parser.add_argument("job_file", help="Job description file")
    match_parser.add_argument("candidate_file", help="Candidate skills file (one skill per line)")
    match_parser.add_argument("--experience", "-e", default="mid-level", help="Candidate experience level")
    match_parser.add_argument("--output", "-o", choices=["json", "text"], default="json", help="Output format")

    return ap


def _cmd_parse(args: argparse.Namespace) -> int:
    """Execute the parse command."""
    try:
        if args.file == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.file).read_text()

        result = parse_job_description(text)
        if result is None:
            print("Error: Could not parse job description (empty or invalid input)", file=sys.stderr)
            return 1

        if args.output == "json":
            print(json.dumps(result, indent=2))
        else:
            _print_parse_text(result)

        return 0
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _cmd_match(args: argparse.Namespace) -> int:
    """Execute the match command."""
    try:
        # Read job description
        job_text = Path(args.job_file).read_text()
        job_result = parse_job_description(job_text)
        if job_result is None:
            print("Error: Could not parse job description", file=sys.stderr)
            return 1

        # Read candidate skills
        skills_text = Path(args.candidate_file).read_text()
        candidate_skills = [line.strip() for line in skills_text.strip().splitlines() if line.strip()]

        # Run match
        result = match_profiles(candidate_skills, args.experience, job_result)

        if args.output == "json":
            print(json.dumps(result, indent=2))
        else:
            _print_match_text(result)

        return 0
    except FileNotFoundError as e:
        print(f"Error: File not found: {e.filename}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _print_parse_text(result: dict) -> None:
    """Print parsed result in text format."""
    print(f"Title: {result.get('title', 'N/A')}")
    print(f"Company: {result.get('company', 'N/A')}")
    print(f"Skills: {', '.join(result.get('skills', [])) or 'None'}")
    print(f"Experience: {result.get('experience_level', 'N/A')}")
    sal_min = result.get('salary_min')
    sal_max = result.get('salary_max')
    if sal_min and sal_max:
        print(f"Salary: ${sal_min:,} - ${sal_max:,}")
    else:
        print("Salary: Not specified")
    print(f"Location: {result.get('location', 'N/A')}")
    responsibilities = result.get('responsibilities', [])
    if responsibilities:
        print("Responsibilities:")
        for resp in responsibilities:
            print(f"  - {resp}")


def _print_match_text(result: dict) -> None:
    """Print match result in text format."""
    print(f"Match Score: {result['score']}/100")
    print(f"Matched Skills: {', '.join(result.get('matched_skills', [])) or 'None'}")
    print(f"Missing Skills: {', '.join(result.get('missing_skills', [])) or 'None'}")
    print(f"Salary Match: {'Yes' if result.get('salary_match') else 'No'}")


if __name__ == "__main__":
    sys.exit(main())
