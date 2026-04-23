#!/usr/bin/env python3
"""
Summarizer Tool - YouTube Summarization CLI

A command-line tool for summarizing YouTube videos using a local LLM.

Usage:
    python -m summarizer_tool.main <url> [options]
"""

import argparse
import sys
import os
from datetime import datetime
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from youtube_summarizer import (
    YouTubeSummarizer,
    YouTubeTranscriptError,
    YouTubeVideoError
)


# Default configuration
DEFAULT_MODEL_PATH = r"/workspace/pipeline/workspace/summarizer-tool/models/Gemma-4-E2B-Uncensored-HauhauCS-Aggressive-Q2_K_P.gguf"
DEFAULT_MAX_LENGTH = 2000
DEFAULT_OUTPUT_DIR = "."


def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_number(num: int) -> str:
    """Format large numbers with commas."""
    return f"{num:,}"


def display_metadata(metadata: dict) -> None:
    """Display video metadata in a formatted way."""
    print("\n" + "=" * 60)
    print("VIDEO INFORMATION")
    print("=" * 60)
    print(f"Title:    {metadata.get('title', 'Unknown')}")
    print(f"Channel:  {metadata.get('channel', 'Unknown')}")
    print(f"Duration: {metadata.get('duration_formatted', 'Unknown')}")
    
    upload_date = metadata.get('upload_date_formatted', 'Unknown')
    print(f"Upload:   {upload_date}")
    
    view_count = metadata.get('view_count', 0)
    if view_count:
        print(f"Views:    {format_number(view_count)}")
    
    like_count = metadata.get('like_count', 0)
    if like_count:
        print(f"Likes:    {format_number(like_count)}")
    
    transcript_info = metadata.get('selected_language', 'Unknown')
    is_auto = metadata.get('is_auto_generated', False)
    
    if is_auto:
        print(f"Transcript: Auto-generated ({transcript_info})")
        print("⚠️  Note: Auto-generated transcripts may have lower accuracy")
    else:
        print(f"Transcript: Manual ({transcript_info})")
    
    available_langs = metadata.get('available_languages', [])
    if len(available_langs) > 1:
        print(f"Available languages: {', '.join(available_langs[:5])}")
        if len(available_langs) > 5:
            print(f"  ... and {len(available_langs) - 5} more")
    
    print("=" * 60)


def display_summary(summary: dict, transcript_info: dict) -> None:
    """Display the generated summary."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(summary.get('summary', 'No summary generated'))
    print("=" * 60)


def display_processing_info(summary: dict) -> None:
    """Display processing information."""
    print("\n" + "-" * 60)
    print("PROCESSING INFO")
    print("-" * 60)
    print(f"Original length:  {summary.get('original_length', 0):,} characters")
    print(f"Processed length: {summary.get('processed_length', 0):,} characters")
    print(f"Processing time:  {summary.get('processing_time', 0):.2f} seconds")
    print("-" * 60)


def create_output_filename(video_id: str, video_title: str) -> str:
    """Create a unique output filename."""
    # Sanitize title for filename
    safe_title = "".join(c if c.isalnum() or c in ' _-' else '_' 
                         for c in video_title[:50])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"youtube_summary_{video_id}_{safe_title}_{timestamp}.txt"


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Summarize YouTube videos using a local LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://youtube.com/watch?v=VIDEO_ID"
  %(prog)s "https://youtu.be/VIDEO_ID" -o output.txt -m /path/to/model.gguf
  %(prog)s "https://youtube.com/watch?v=VIDEO_ID" -l es
  %(prog)s "https://youtube.com/watch?v=VIDEO_ID" --prefer-manual
        """
    )
    
    parser.add_argument(
        "url",
        help="YouTube video URL"
    )
    
    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        help="Output file path (default: auto-generated in output directory)"
    )
    
    parser.add_argument(
        "-m", "--model",
        dest="model_path",
        help="Path to GGUF model file"
    )
    
    parser.add_argument(
        "-l", "--language",
        dest="language",
        help="Language code for transcript (default: auto-detect)"
    )
    
    parser.add_argument(
        "-n", "--max-length",
        type=int,
        default=DEFAULT_MAX_LENGTH,
        help=f"Maximum transcript length to process (default: {DEFAULT_MAX_LENGTH})"
    )
    
    parser.add_argument(
        "-p", "--prompt",
        dest="prompt",
        help="Custom summarization prompt"
    )
    
    parser.add_argument(
        "--prefer-manual",
        action="store_true",
        help="Prefer manual transcripts over auto-generated"
    )
    
    parser.add_argument(
        "--no-prefer-manual",
        action="store_true",
        help="Allow auto-generated transcripts"
    )
    
    parser.add_argument(
        "-d", "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for auto-generated filenames (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Set prefer_manual preference
    prefer_manual = True
    if args.no_prefer_manual:
        prefer_manual = False
    elif args.prefer_manual:
        prefer_manual = True
    
    # Determine model path
    model_path = args.model_path if args.model_path else DEFAULT_MODEL_PATH
    
    # Validate model path exists
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        return 1
    
    try:
        # Initialize summarizer
        summarizer = YouTubeSummarizer(
            llm_model_path=model_path,
            default_language=args.language or 'en',
            prefer_manual=prefer_manual
        )
        
        print(f"Processing video: {args.url}")
        print()
        
        # Extract and display metadata
        metadata = summarizer.extract_metadata(args.url)
        display_metadata(metadata)
        
        # Generate summary
        if args.verbose:
            print("\nExtracting transcript...")
        
        summary = summarizer.summarize_video(
            url=args.url,
            llm_model_path=model_path,
            language=args.language,
            max_length=args.max_length,
            prompt=args.prompt,
            output_file=args.output_file
        )
        
        # Display summary
        display_summary(summary, metadata)
        display_processing_info(summary)
        
        # Output filename info
        if not args.output_file:
            output_name = create_output_filename(
                metadata['video_id'],
                metadata['title']
            )
            output_path = os.path.join(args.output_dir, output_name)
            print(f"\nSummary saved to: {output_path}")
        
        print()
        return 0
        
    except YouTubeVideoError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        print(f"Error type: {e.error_type}", file=sys.stderr)
        if e.video_id:
            print(f"Video ID: {e.video_id}", file=sys.stderr)
        return 1
        
    except YouTubeTranscriptError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        if e.video_id:
            print(f"Video ID: {e.video_id}", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
