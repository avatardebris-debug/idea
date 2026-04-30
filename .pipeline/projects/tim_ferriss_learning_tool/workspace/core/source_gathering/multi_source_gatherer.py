"""Multi-source gatherer for collecting learning materials from various formats."""

import json
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime


@dataclass
class SourceMetadata:
    """Metadata for a single source."""
    source_id: str
    title: str
    source_type: str
    url_or_path: str
    description: str
    added_date: str
    tags: List[str]


@dataclass
class SourceContent:
    """Content extracted from a source."""
    source_id: str
    content_type: str
    text_content: str
    metadata: Dict[str, Any]


@dataclass
class GatheredSources:
    """Collection of gathered sources."""
    topic_name: str
    sources: List[SourceMetadata]
    contents: List[SourceContent]
    total_sources: int
    gathered_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "sources": [asdict(s) for s in self.sources],
            "contents": [asdict(c) for c in self.contents],
            "total_sources": self.total_sources,
            "gathered_at": self.gathered_at
        }


class MultiSourceGatherer:
    """
    Aggregates sources from multiple formats for learning materials.
    
    Supports gathering from:
    - Text files
    - PDFs
    - Video transcripts
    - Podcast audio/transcripts
    - Article URLs
    - YouTube videos
    """
    
    SUPPORTED_TYPES = ["text", "pdf", "video", "podcast", "article", "youtube"]
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        storage_format: str = "json"
    ):
        """
        Initialize the Multi Source Gatherer.
        
        Args:
            output_dir: Directory to store gathered sources. Defaults to current directory.
            storage_format: Format for storing sources (json or yaml).
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.storage_format = storage_format
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track gathered sources
        self.sources: List[SourceMetadata] = []
        self.contents: List[SourceContent] = []
    
    def gather_from_text(
        self,
        file_path: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> SourceMetadata:
        """
        Gather content from a text file.
        
        Args:
            file_path: Path to the text file.
            title: Optional title for the source.
            description: Optional description.
            tags: Optional list of tags.
        
        Returns:
            SourceMetadata for the gathered source.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        source_id = self._generate_source_id("text", file_path.name)
        source_title = title or file_path.stem
        source_description = description or f"Text file: {file_path.name}"
        
        metadata = SourceMetadata(
            source_id=source_id,
            title=source_title,
            source_type="text",
            url_or_path=str(file_path),
            description=source_description,
            added_date=datetime.now().isoformat(),
            tags=tags or []
        )
        
        content_obj = SourceContent(
            source_id=source_id,
            content_type="text",
            text_content=content,
            metadata={"file_size": file_path.stat().st_size}
        )
        
        self.sources.append(metadata)
        self.contents.append(content_obj)
        
        return metadata
    
    def gather_from_pdf(
        self,
        file_path: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> SourceMetadata:
        """
        Gather content from a PDF file.
        
        Args:
            file_path: Path to the PDF file.
            title: Optional title for the source.
            description: Optional description.
            tags: Optional list of tags.
        
        Returns:
            SourceMetadata for the gathered source.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Note: PDF extraction would require a library like PyPDF2 or pdfplumber
        # For now, we store metadata and mark content as requiring extraction
        source_id = self._generate_source_id("pdf", file_path.name)
        source_title = title or file_path.stem
        source_description = description or f"PDF document: {file_path.name}"
        
        metadata = SourceMetadata(
            source_id=source_id,
            title=source_title,
            source_type="pdf",
            url_or_path=str(file_path),
            description=source_description,
            added_date=datetime.now().isoformat(),
            tags=tags or []
        )
        
        content_obj = SourceContent(
            source_id=source_id,
            content_type="pdf",
            text_content="",  # PDF text extraction would require additional library
            metadata={
                "file_size": file_path.stat().st_size,
                "extraction_required": True
            }
        )
        
        self.sources.append(metadata)
        self.contents.append(content_obj)
        
        return metadata
    
    def gather_from_video_transcript(
        self,
        transcript_path: str,
        video_url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> SourceMetadata:
        """
        Gather content from a video transcript file.
        
        Args:
            transcript_path: Path to the transcript file.
            video_url: URL of the video.
            title: Optional title for the source.
            description: Optional description.
            tags: Optional list of tags.
        
        Returns:
            SourceMetadata for the gathered source.
        """
        transcript_path = Path(transcript_path)
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        source_id = self._generate_source_id("video", Path(video_url).name)
        source_title = title or f"Video Transcript: {Path(video_url).name}"
        source_description = description or f"Video transcript from {video_url}"
        
        metadata = SourceMetadata(
            source_id=source_id,
            title=source_title,
            source_type="video",
            url_or_path=video_url,
            description=source_description,
            added_date=datetime.now().isoformat(),
            tags=tags or []
        )
        
        content_obj = SourceContent(
            source_id=source_id,
            content_type="video_transcript",
            text_content=content,
            metadata={"transcript_source": str(transcript_path)}
        )
        
        self.sources.append(metadata)
        self.contents.append(content_obj)
        
        return metadata
    
    def gather_from_podcast(
        self,
        podcast_url: str,
        transcript_path: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> SourceMetadata:
        """
        Gather content from a podcast.
        
        Args:
            podcast_url: URL of the podcast.
            transcript_path: Optional path to transcript file.
            title: Optional title for the source.
            description: Optional description.
            tags: Optional list of tags.
        
        Returns:
            SourceMetadata for the gathered source.
        """
        if transcript_path:
            transcript_path = Path(transcript_path)
            if not transcript_path.exists():
                raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
            
            with open(transcript_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        source_id = self._generate_source_id("podcast", Path(podcast_url).name)
        source_title = title or f"Podcast: {Path(podcast_url).name}"
        source_description = description or f"Podcast from {podcast_url}"
        
        metadata = SourceMetadata(
            source_id=source_id,
            title=source_title,
            source_type="podcast",
            url_or_path=podcast_url,
            description=source_description,
            added_date=datetime.now().isoformat(),
            tags=tags or []
        )
        
        content_obj = SourceContent(
            source_id=source_id,
            content_type="podcast",
            text_content=content,
            metadata={"podcast_url": podcast_url}
        )
        
        self.sources.append(metadata)
        self.contents.append(content_obj)
        
        return metadata
    
    def gather_from_article(
        self,
        url: str,
        content: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> SourceMetadata:
        """
        Gather content from an article URL.
        
        Args:
            url: URL of the article.
            content: Extracted text content of the article.
            title: Optional title for the source.
            description: Optional description.
            tags: Optional list of tags.
        
        Returns:
            SourceMetadata for the gathered source.
        """
        source_id = self._generate_source_id("article", Path(url).name)
        source_title = title or f"Article: {Path(url).name}"
        source_description = description or f"Article from {url}"
        
        metadata = SourceMetadata(
            source_id=source_id,
            title=source_title,
            source_type="article",
            url_or_path=url,
            description=source_description,
            added_date=datetime.now().isoformat(),
            tags=tags or []
        )
        
        content_obj = SourceContent(
            source_id=source_id,
            content_type="article",
            text_content=content,
            metadata={"url": url}
        )
        
        self.sources.append(metadata)
        self.contents.append(content_obj)
        
        return metadata
    
    def gather_from_youtube(
        self,
        video_id: str,
        transcript: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> SourceMetadata:
        """
        Gather content from a YouTube video.
        
        Args:
            video_id: YouTube video ID.
            transcript: Transcript of the video.
            title: Optional title for the source.
            description: Optional description.
            tags: Optional list of tags.
        
        Returns:
            SourceMetadata for the gathered source.
        """
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        source_id = self._generate_source_id("youtube", video_id)
        source_title = title or f"YouTube: {video_id}"
        source_description = description or f"YouTube video {video_id}"
        
        metadata = SourceMetadata(
            source_id=source_id,
            title=source_title,
            source_type="youtube",
            url_or_path=video_url,
            description=source_description,
            added_date=datetime.now().isoformat(),
            tags=tags or []
        )
        
        content_obj = SourceContent(
            source_id=source_id,
            content_type="youtube_transcript",
            text_content=transcript,
            metadata={"video_id": video_id}
        )
        
        self.sources.append(metadata)
        self.contents.append(content_obj)
        
        return metadata
    
    def _generate_source_id(self, source_type: str, identifier: str) -> str:
        """Generate a unique source ID."""
        import hashlib
        unique_string = f"{source_type}_{identifier}_{datetime.now().timestamp()}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def gather_from_topic(
        self,
        topic_name: str,
        sources: List[Dict[str, Any]]
    ) -> GatheredSources:
        """
        Gather multiple sources for a topic.
        
        Args:
            topic_name: Name of the topic.
            sources: List of source dictionaries with 'type' and source-specific fields.
        
        Returns:
            GatheredSources object with all gathered sources.
        """
        for source in sources:
            source_type = source.get("type")
            
            if source_type == "text":
                self.gather_from_text(
                    file_path=source["file_path"],
                    title=source.get("title"),
                    description=source.get("description"),
                    tags=source.get("tags")
                )
            elif source_type == "pdf":
                self.gather_from_pdf(
                    file_path=source["file_path"],
                    title=source.get("title"),
                    description=source.get("description"),
                    tags=source.get("tags")
                )
            elif source_type == "video":
                self.gather_from_video_transcript(
                    transcript_path=source["transcript_path"],
                    video_url=source["video_url"],
                    title=source.get("title"),
                    description=source.get("description"),
                    tags=source.get("tags")
                )
            elif source_type == "podcast":
                self.gather_from_podcast(
                    podcast_url=source["podcast_url"],
                    transcript_path=source.get("transcript_path"),
                    title=source.get("title"),
                    description=source.get("description"),
                    tags=source.get("tags")
                )
            elif source_type == "article":
                self.gather_from_article(
                    url=source["url"],
                    content=source["content"],
                    title=source.get("title"),
                    description=source.get("description"),
                    tags=source.get("tags")
                )
            elif source_type == "youtube":
                self.gather_from_youtube(
                    video_id=source["video_id"],
                    transcript=source["transcript"],
                    title=source.get("title"),
                    description=source.get("description"),
                    tags=source.get("tags")
                )
        
        return GatheredSources(
            topic_name=topic_name,
            sources=self.sources.copy(),
            contents=self.contents.copy(),
            total_sources=len(self.sources),
            gathered_at=datetime.now().isoformat()
        )
    
    def save_to_file(self, output_path: Optional[str] = None) -> str:
        """
        Save gathered sources to a file.
        
        Args:
            output_path: Optional path for output file.
        
        Returns:
            Path to the saved file.
        """
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = self.output_dir / f"sources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.storage_format}"
        
        data = {
            "topic_name": "gathered_sources",
            "sources": [asdict(s) for s in self.sources],
            "contents": [asdict(c) for c in self.contents],
            "total_sources": len(self.sources),
            "gathered_at": datetime.now().isoformat()
        }
        
        if self.storage_format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        elif self.storage_format == "yaml":
            try:
                import yaml
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False)
            except ImportError:
                # Fallback to JSON if yaml not available
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
        
        return str(output_path)
    
    def get_sources_by_type(self, source_type: str) -> List[SourceMetadata]:
        """Get all sources of a specific type."""
        return [s for s in self.sources if s.source_type == source_type]
    
    def get_sources_by_tag(self, tag: str) -> List[SourceMetadata]:
        """Get all sources with a specific tag."""
        return [s for s in self.sources if tag in s.tags]
    
    def get_all_sources(self) -> List[SourceMetadata]:
        """Get all gathered sources.
        
        Returns:
            List of all SourceMetadata objects.
        """
        return self.sources.copy()
    
    def clear(self):
        """Clear all gathered sources."""
        self.sources.clear()
        self.contents.clear()
