"""
Transcript Builder Module

This module provides the TranscriptBuilder class for creating and managing
video transcripts with timestamps, sections, and multiple output formats.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re


class TranscriptFormat(Enum):
    """Supported transcript output formats"""
    SRT = 'srt'
    VTT = 'vtt'
    TXT = 'txt'
    JSON = 'json'
    YAML = 'yaml'


@dataclass
class TranscriptSection:
    """A section within a transcript"""
    title: str
    start_time: float  # in seconds
    end_time: float  # in seconds
    content: str
    timestamp: str = ""  # ISO format timestamp of when section was created


class TranscriptBuilder:
    """
    Builder for creating structured video transcripts.
    
    This class provides functionality for building transcripts from text,
    adding timestamps, organizing into sections, and exporting in various formats.
    """
    
    # Default timestamp format
    DEFAULT_TIMESTAMP_FORMAT = '%H:%M:%S'
    
    # SRT timestamp format
    SRT_TIMESTAMP_FORMAT = '%H:%M:%S,%f'[:-3]  # HH:MM:SS,ms
    
    def __init__(self, title: str = "Untitled Transcript"):
        """
        Initialize the transcript builder.
        
        Args:
            title: Title of the transcript
        """
        self.title = title
        self._sections: List[TranscriptSection] = []
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    def add_section(self, title: str, content: str, start_time: float = 0.0,
                   end_time: Optional[float] = None) -> 'TranscriptBuilder':
        """
        Add a section to the transcript.
        
        Args:
            title: Section title
            content: Section content
            start_time: Start time in seconds
            end_time: End time in seconds (calculated if not provided)
            
        Returns:
            Self for method chaining
        """
        # Calculate end time if not provided
        if end_time is None:
            end_time = start_time + self._estimate_duration(content)
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        section = TranscriptSection(
            title=title,
            start_time=start_time,
            end_time=end_time,
            content=content,
            timestamp=timestamp
        )
        
        self._sections.append(section)
        self._updated_at = datetime.now()
        
        return self
    
    def _estimate_duration(self, content: str) -> float:
        """
        Estimate duration of content based on word count.
        
        Args:
            content: Text content
            
        Returns:
            Estimated duration in seconds
        """
        # Average speaking rate: 150 words per minute
        words = len(content.split())
        duration = (words / 150.0) * 60.0
        
        # Add minimum 5 seconds per section
        return max(duration, 5.0)
    
    def set_section_timestamps(self, start_time: float = 0.0, 
                               end_time: Optional[float] = None) -> 'TranscriptBuilder':
        """
        Set timestamps for all sections.
        
        Args:
            start_time: Starting timestamp for first section
            end_time: End timestamp for last section (calculated if not provided)
            
        Returns:
            Self for method chaining
        """
        if not self._sections:
            return self
        
        # Set first section timestamp
        self._sections[0].start_time = start_time
        
        # Set last section end time
        if end_time:
            self._sections[-1].end_time = end_time
        
        # Calculate intermediate timestamps
        total_duration = end_time - start_time if end_time else 0
        num_sections = len(self._sections)
        
        if num_sections > 1 and total_duration > 0:
            duration_per_section = total_duration / num_sections
            for i, section in enumerate(self._sections):
                if i > 0:
                    section.start_time = start_time + (i * duration_per_section)
                if i < num_sections - 1:
                    section.end_time = start_time + ((i + 1) * duration_per_section)
                else:
                    section.end_time = end_time or start_time + duration_per_section
        
        return self
    
    def get_sections(self) -> List[TranscriptSection]:
        """
        Get all sections in the transcript.
        
        Returns:
            List of TranscriptSection objects
        """
        return self._sections.copy()
    
    def get_total_duration(self) -> float:
        """
        Get total duration of the transcript.
        
        Returns:
            Total duration in seconds
        """
        if not self._sections:
            return 0.0
        
        first_start = min(s.start_time for s in self._sections)
        last_end = max(s.end_time for s in self._sections)
        
        return last_end - first_start
    
    def get_summary(self) -> Dict:
        """
        Get a summary of the transcript.
        
        Returns:
            Dictionary containing transcript summary
        """
        total_words = sum(len(s.content.split()) for s in self._sections)
        total_chars = sum(len(s.content) for s in self._sections)
        
        return {
            'title': self.title,
            'num_sections': len(self._sections),
            'total_duration_seconds': round(self.get_total_duration(), 2),
            'total_words': total_words,
            'total_characters': total_chars,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
    
    def export_to_srt(self, output_path: Optional[str] = None) -> str:
        """
        Export transcript to SRT format.
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Path to exported file
        """
        srt_content = self._generate_srt_content()
        
        path = output_path or f"{self.title.lower().replace(' ', '_')}.srt"
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            return path
        except IOError as e:
            print(f"Error exporting to SRT: {e}")
            return ''
    
    def _generate_srt_content(self) -> str:
        """Generate SRT formatted content"""
        lines = []
        sequence = 1
        
        for section in self._sections:
            start_time = self._format_timestamp(section.start_time)
            end_time = self._format_timestamp(section.end_time)
            
            lines.append(str(sequence))
            lines.append(f"{start_time} --> {end_time}")
            lines.append(section.content)
            lines.append("")
            
            sequence += 1
        
        return '\n'.join(lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as SRT timestamp.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def export_to_vtt(self, output_path: Optional[str] = None) -> str:
        """
        Export transcript to VTT format.
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Path to exported file
        """
        vtt_content = self._generate_vtt_content()
        
        path = output_path or f"{self.title.lower().replace(' ', '_')}.vtt"
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(vtt_content)
            return path
        except IOError as e:
            print(f"Error exporting to VTT: {e}")
            return ''
    
    def _generate_vtt_content(self) -> str:
        """Generate VTT formatted content"""
        lines = []
        lines.append("WEBVTT")
        lines.append("")
        
        for section in self._sections:
            start_time = self._format_vtt_timestamp(section.start_time)
            end_time = self._format_vtt_timestamp(section.end_time)
            
            lines.append(f"{start_time} --> {end_time}")
            lines.append(section.content)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _format_vtt_timestamp(self, seconds: float) -> str:
        """
        Format seconds as VTT timestamp.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def export_to_txt(self, output_path: Optional[str] = None) -> str:
        """
        Export transcript to plain text format.
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Path to exported file
        """
        txt_content = self._generate_txt_content()
        
        path = output_path or f"{self.title.lower().replace(' ', '_')}.txt"
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(txt_content)
            return path
        except IOError as e:
            print(f"Error exporting to TXT: {e}")
            return ''
    
    def _generate_txt_content(self) -> str:
        """Generate plain text content"""
        lines = []
        
        for section in self._sections:
            lines.append(f"[{self._format_timestamp(section.start_time)} - {self._format_timestamp(section.end_time)}]")
            lines.append(section.title)
            lines.append(section.content)
            lines.append("")
        
        return '\n'.join(lines)
    
    def export_to_json(self, output_path: Optional[str] = None) -> str:
        """
        Export transcript to JSON format.
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Path to exported file
        """
        import json
        
        data = {
            'title': self.title,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat(),
            'sections': [
                {
                    'title': section.title,
                    'start_time': section.start_time,
                    'end_time': section.end_time,
                    'content': section.content,
                    'timestamp': section.timestamp
                }
                for section in self._sections
            ],
            'summary': self.get_summary()
        }
        
        path = output_path or f"{self.title.lower().replace(' ', '_')}.json"
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return path
        except IOError as e:
            print(f"Error exporting to JSON: {e}")
            return ''
    
    def export_to_yaml(self, output_path: Optional[str] = None) -> str:
        """
        Export transcript to YAML format.
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Path to exported file
        """
        try:
            import yaml
        except ImportError:
            print("PyYAML not installed. Please install it with: pip install pyyaml")
            return ''
        
        data = {
            'title': self.title,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat(),
            'sections': [
                {
                    'title': section.title,
                    'start_time': section.start_time,
                    'end_time': section.end_time,
                    'content': section.content,
                    'timestamp': section.timestamp
                }
                for section in self._sections
            ],
            'summary': self.get_summary()
        }
        
        path = output_path or f"{self.title.lower().replace(' ', '_')}.yaml"
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            return path
        except ImportError:
            print("PyYAML not installed. Please install it with: pip install pyyaml")
            return ''
        except IOError as e:
            print(f"Error exporting to YAML: {e}")
            return ''
    
    def export_all_formats(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Export transcript in all supported formats.
        
        Args:
            output_dir: Optional output directory
            
        Returns:
            Dictionary mapping format names to file paths
        """
        import os
        
        output_dir = output_dir or os.getcwd()
        base_name = self.title.lower().replace(' ', '_')
        
        exports = {}
        
        formats = [
            ('srt', self.export_to_srt),
            ('vtt', self.export_to_vtt),
            ('txt', self.export_to_txt),
            ('json', self.export_to_json),
            ('yaml', self.export_to_yaml),
        ]
        
        for format_name, export_func in formats:
            output_path = os.path.join(output_dir, f"{base_name}.{format_name}")
            result = export_func(output_path)
            if result:
                exports[format_name] = result
        
        return exports
    
    def clear(self):
        """Clear all sections from the transcript"""
        self._sections.clear()
        self._updated_at = datetime.now()
    
    def merge_sections(self, section_indices: List[int]) -> 'TranscriptBuilder':
        """
        Merge specified sections into one.
        
        Args:
            section_indices: Indices of sections to merge
            
        Returns:
            Self for method chaining
        """
        if not section_indices or len(section_indices) < 2:
            return self
        
        # Sort indices
        section_indices = sorted(section_indices)
        
        # Get sections to merge
        sections_to_merge = [self._sections[i] for i in section_indices if i < len(self._sections)]
        
        if not sections_to_merge:
            return self
        
        # Create merged section
        merged_content = '\n'.join(s.content for s in sections_to_merge)
        merged_start = min(s.start_time for s in sections_to_merge)
        merged_end = max(s.end_time for s in sections_to_merge)
        merged_title = ' '.join(s.title for s in sections_to_merge)
        
        # Remove original sections
        for i in sorted(section_indices, reverse=True):
            if i < len(self._sections):
                del self._sections[i]
        
        # Add merged section
        timestamp = datetime.now().isoformat()
        merged_section = TranscriptSection(
            title=merged_title,
            start_time=merged_start,
            end_time=merged_end,
            content=merged_content,
            timestamp=timestamp
        )
        
        self._sections.append(merged_section)
        self._updated_at = datetime.now()
        
        return self
    
    def get_timestamp_range(self) -> Tuple[float, float]:
        """
        Get the timestamp range of the transcript.
        
        Returns:
            Tuple of (start_time, end_time) in seconds
        """
        if not self._sections:
            return (0.0, 0.0)
        
        start_time = min(s.start_time for s in self._sections)
        end_time = max(s.end_time for s in self._sections)
        
        return (start_time, end_time)
    
    def get_section_by_time(self, time: float) -> Optional[TranscriptSection]:
        """
        Get the section that contains a specific time.
        
        Args:
            time: Time in seconds
            
        Returns:
            TranscriptSection if found, None otherwise
        """
        for section in self._sections:
            if section.start_time <= time <= section.end_time:
                return section
        
        return None
