"""Command-line interface for YouTube Studio.

This module provides a CLI for generating video metadata, transcripts,
and managing templates from the command line.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from config import YouTubeStudioConfig
from studio_orchestrator import StudioOrchestrator
from transcript_builder import TranscriptBuilder


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='YouTube Studio - SEO-friendly video metadata generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate metadata for a single video
  python -m youtube_studio.cli generate --title "Python Tutorial" --description "Learn Python"

  # Generate metadata for multiple videos (batch)
  python -m youtube_studio.cli batch --input-file videos.json --output-file results.json

  # Create a transcript
  python -m youtube_studio.cli transcript --input sections.json --format srt --output transcript.srt

  # Validate configuration
  python -m youtube_studio.cli validate-config --config config.json

  # Show all available templates
  python -m youtube_studio.cli templates list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate metadata for a single video')
    generate_parser.add_argument('--title', '-t', required=True, help='Video title')
    generate_parser.add_argument('--description', '-d', required=True, help='Video description')
    generate_parser.add_argument('--content', '-c', help='Video content description')
    generate_parser.add_argument('--category', '-cat', default='general', help='Video category')
    generate_parser.add_argument('--author', '-a', help='Video author')
    generate_parser.add_argument('--output', '-o', help='Output file (JSON)')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Generate metadata for multiple videos')
    batch_parser.add_argument('--input-file', '-i', required=True, help='Input JSON file with video data')
    batch_parser.add_argument('--output-file', '-o', required=True, help='Output JSON file')
    
    # Transcript command
    transcript_parser = subparsers.add_parser('transcript', help='Create transcript from sections')
    transcript_parser.add_argument('--input', '-i', required=True, help='Input JSON file with sections')
    transcript_parser.add_argument('--format', '-f', choices=['srt', 'vtt', 'txt'], required=True, help='Output format')
    transcript_parser.add_argument('--output', '-o', help='Output file path')
    
    # Templates command
    templates_parser = subparsers.add_parser('templates', help='Manage templates')
    templates_subparsers = templates_parser.add_subparsers(dest='template_command', help='Template commands')
    
    # List templates
    list_parser = templates_subparsers.add_parser('list', help='List all available templates')
    
    # Show template
    show_parser = templates_subparsers.add_parser('show', help='Show template details')
    show_parser.add_argument('name', help='Template name')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate-config', help='Validate configuration file')
    validate_parser.add_argument('--config', '-c', required=True, help='Configuration file path')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version')
    
    return parser.parse_args()


def cmd_generate(args: argparse.Namespace, orchestrator: StudioOrchestrator) -> Dict[str, Any]:
    """Generate metadata for a single video."""
    input_data = {
        'title': args.title,
        'description': args.description,
        'content': args.content,
        'category': args.category,
        'author': args.author
    }
    
    metadata = orchestrator.generate_video_metadata(input_data)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to {args.output}")
    
    return metadata


def cmd_batch(args: argparse.Namespace, orchestrator: StudioOrchestrator) -> List[Dict[str, Any]]:
    """Generate metadata for multiple videos."""
    with open(args.input_file, 'r') as f:
        videos = json.load(f)
    
    results = orchestrator.generate_batch(videos)
    
    with open(args.output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Generated metadata for {len(results)} videos. Saved to {args.output_file}")
    return results


def cmd_transcript(args: argparse.Namespace) -> str:
    """Create transcript from sections."""
    with open(args.input, 'r') as f:
        sections = json.load(f)
    
    builder = TranscriptBuilder()
    for section in sections:
        builder.add_section(section['text'], section['start_time'], section['end_time'])
    
    output = builder.export_srt() if args.format == 'srt' else \
             builder.export_vtt() if args.format == 'vtt' else \
             builder.export_txt()
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Transcript saved to {args.output}")
    
    return output


def cmd_templates_list(orchestrator: StudioOrchestrator) -> List[str]:
    """List all available templates."""
    templates = orchestrator.template_manager.get_all_templates()
    
    if not templates:
        print("No templates found.")
        return []
    
    print(f"Available templates ({len(templates)}):")
    for template in templates:
        print(f"  - {template}")
    
    return templates


def cmd_templates_show(args: argparse.Namespace, orchestrator: StudioOrchestrator) -> Dict[str, Any]:
    """Show template details."""
    template = orchestrator.template_manager.get_template(args.name)
    
    if template is None:
        print(f"Template '{args.name}' not found.")
        return {}
    
    print(f"Template: {args.name}")
    print(json.dumps(template, indent=2))
    
    return template


def cmd_validate_config(args: argparse.Namespace) -> bool:
    """Validate configuration file."""
    try:
        with open(args.config, 'r') as f:
            config_dict = json.load(f)
        
        config = YouTubeStudioConfig.from_dict(config_dict)
        print(f"Configuration valid: {config.log_level} logging enabled")
        return True
    except FileNotFoundError:
        print(f"Configuration file not found: {args.config}")
        return False
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in configuration file: {e}")
        return False
    except Exception as e:
        print(f"Configuration validation error: {e}")
        return False


def main():
    """Main entry point for CLI."""
    args = parse_args()
    
    # Initialize orchestrator
    orchestrator = StudioOrchestrator()
    
    # Execute command
    if args.command == 'generate':
        result = cmd_generate(args, orchestrator)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'batch':
        result = cmd_batch(args, orchestrator)
        print(f"Generated {len(result)} results")
    
    elif args.command == 'transcript':
        output = cmd_transcript(args)
        if not args.output:
            print(output)
    
    elif args.command == 'templates':
        if args.template_command == 'list':
            cmd_templates_list(orchestrator)
        elif args.template_command == 'show':
            cmd_templates_show(args, orchestrator)
        else:
            print("Invalid template command. Use 'list' or 'show'.")
            sys.exit(1)
    
    elif args.command == 'validate-config':
        success = cmd_validate_config(args)
        sys.exit(0 if success else 1)
    
    elif args.command == 'version':
        from __init__ import __version__
        print(f"YouTube Studio v{__version__}")
    
    else:
        print("Please specify a command. Use --help for usage.")
        sys.exit(1)


if __name__ == '__main__':
    main()
