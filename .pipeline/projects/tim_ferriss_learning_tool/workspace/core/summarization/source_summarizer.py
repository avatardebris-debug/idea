"""Source summarizer for creating structured summaries of gathered content."""

import json
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

import yaml
from openai import OpenAI


@dataclass
class SummarySection:
    """A section within a summary."""
    title: str
    content: str
    section_type: str


@dataclass
class SourceSummary:
    """Summary of a single source."""
    source_id: str
    title: str
    source_type: str
    summary_text: str
    key_points: List[str]
    summary_length: int
    generated_at: str


@dataclass
class TopicSummary:
    """Complete summary for a topic."""
    topic_name: str
    source_summaries: List[SourceSummary]
    overall_summary: str
    total_sources: int
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "source_summaries": [asdict(s) for s in self.source_summaries],
            "overall_summary": self.overall_summary,
            "total_sources": self.total_sources,
            "generated_at": self.generated_at
        }


class SourceSummarizer:
    """
    Creates structured summaries of gathered content.
    
    Supports summarizing:
    - Text files
    - PDFs (after extraction)
    - Video transcripts
    - Podcast transcripts
    - Article content
    - YouTube transcripts
    """
    
    SUPPORTED_TYPES = ["text", "pdf", "video", "podcast", "article", "youtube"]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.3,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Source Summarizer.
        
        Args:
            api_key: OpenAI API key. If None, will try to read from OPENAI_API_KEY env var.
            model: LLM model to use for summarization.
            temperature: Temperature parameter for LLM responses.
            config_path: Path to learning profile configuration file.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=self.api_key)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load learning profile configuration."""
        default_config_path = Path(__file__).parent.parent.parent / "config" / "learning_profiles" / "default_profile.yaml"
        
        if config_path:
            config_path = Path(config_path)
        else:
            config_path = default_config_path
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return {
                "summarization": {
                    "depth": "concise",
                    "include_key_points": True
                }
            }
    
    def _load_prompt_template(self) -> str:
        """Load the summarization prompt template."""
        prompt_path = Path(__file__).parent / "prompts" / "summarize_source.md"
        
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Return default prompt if file doesn't exist
            return self._get_default_prompt_template()
    
    def _get_default_prompt_template(self) -> str:
        """Return a default summarization prompt template."""
        return """You are an expert content summarizer specializing in creating concise, structured summaries for learning purposes.

## Task
Create a structured summary of the provided content that captures the essential information while being concise and actionable.

## Output Requirements
Provide a structured summary with the following sections:

### 1. Executive Summary
A brief 2-3 sentence overview of the main topic and key takeaway.

### 2. Key Points
List the 3-5 most important points from the content, each as a concise bullet point.

### 3. Actionable Insights
Practical takeaways that can be applied immediately.

### 4. Related Concepts
Mention any related concepts or topics that would benefit from further exploration.

## Output Format
Return your response as a structured JSON object with the following schema:

```json
{
  "executive_summary": "string",
  "key_points": ["string"],
  "actionable_insights": ["string"],
  "related_concepts": ["string"]
}
```

## Instructions
1. Read the content carefully
2. Identify the main topic and primary message
3. Extract the most important supporting points
4. Identify practical applications
5. Note any related topics worth exploring
6. Ensure the summary is concise yet comprehensive
7. Return valid JSON matching the schema above
"""
    
    def summarize_text(
        self,
        content: str,
        title: str,
        source_type: str = "text",
        source_id: Optional[str] = None
    ) -> SourceSummary:
        """
        Create a summary of text content.
        
        Args:
            content: The text content to summarize.
            title: Title of the source.
            source_type: Type of source (text, pdf, video, etc.).
            source_id: Optional unique identifier for the source.
        
        Returns:
            SourceSummary object with the summary.
        """
        source_id = source_id or self._generate_source_id(source_type, title)
        
        # Build the prompt
        prompt = self._build_summarization_prompt(content, title, source_type)
        
        # Call LLM API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=1024
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        try:
            summary_data = json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                summary_data = json.loads(json_match.group(1))
            else:
                summary_data = self._extract_json_from_text(content)
        
        # Create summary
        summary = SourceSummary(
            source_id=source_id,
            title=title,
            source_type=source_type,
            summary_text=self._format_summary_text(summary_data),
            key_points=summary_data.get("key_points", []),
            summary_length=len(summary_data.get("executive_summary", "")),
            generated_at=datetime.now().isoformat()
        )
        
        return summary
    
    def _build_summarization_prompt(
        self,
        content: str,
        title: str,
        source_type: str
    ) -> str:
        """Build the prompt for summarization."""
        prompt = f"""
Source Title: {title}
Source Type: {source_type}

Content to summarize:
{content}

Please create a structured summary following the output requirements.
"""
        return prompt
    
    def _format_summary_text(self, summary_data: Dict[str, Any]) -> str:
        """Format the summary data into a readable text format."""
        lines = [
            f"## {summary_data.get('executive_summary', 'Summary')}\n",
            "### Key Points\n"
        ]
        
        for i, point in enumerate(summary_data.get("key_points", []), 1):
            lines.append(f"{i}. {point}")
        
        lines.append("\n### Actionable Insights\n")
        for i, insight in enumerate(summary_data.get("actionable_insights", []), 1):
            lines.append(f"{i}. {insight}")
        
        lines.append("\n### Related Concepts\n")
        for concept in summary_data.get("related_concepts", []):
            lines.append(f"- {concept}")
        
        return "\n".join(lines)
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text that may contain markdown or other formatting."""
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Fallback: create a basic structure
        return {
            "executive_summary": text[:200] + "..." if len(text) > 200 else text,
            "key_points": [text[:100]],
            "actionable_insights": [],
            "related_concepts": []
        }
    
    def summarize_topic(
        self,
        topic_name: str,
        source_summaries: List[SourceSummary]
    ) -> TopicSummary:
        """
        Create an overall summary for a topic based on multiple source summaries.
        
        Args:
            topic_name: Name of the topic.
            source_summaries: List of summaries from individual sources.
        
        Returns:
            TopicSummary object with the overall summary.
        """
        # Combine all key points
        all_key_points = []
        for summary in source_summaries:
            all_key_points.extend(summary.key_points)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_key_points = []
        for point in all_key_points:
            if point not in seen:
                seen.add(point)
                unique_key_points.append(point)
        
        # Create overall summary
        overall_summary = f"""
## Topic: {topic_name}

This topic encompasses {len(source_summaries)} sources covering various aspects of {topic_name}.

### Key Takeaways
"""
        
        for i, point in enumerate(unique_key_points[:10], 1):  # Limit to top 10
            overall_summary += f"{i}. {point}\n"
        
        overall_summary += f"\n### Summary Statistics\n"
        overall_summary += f"- Total sources analyzed: {len(source_summaries)}\n"
        overall_summary += f"- Combined key points: {len(unique_key_points)}\n"
        
        topic_summary = TopicSummary(
            topic_name=topic_name,
            source_summaries=source_summaries,
            overall_summary=overall_summary,
            total_sources=len(source_summaries),
            generated_at=datetime.now().isoformat()
        )
        
        return topic_summary
    
    def _generate_source_id(self, source_type: str, title: str) -> str:
        """Generate a unique source ID."""
        import hashlib
        unique_string = f"{source_type}_{title}_{datetime.now().timestamp()}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def save_summary_to_file(
        self,
        summary: TopicSummary,
        output_path: Optional[str] = None
    ) -> str:
        """
        Save a topic summary to a file.
        
        Args:
            summary: The topic summary to save.
            output_path: Optional path for output file.
        
        Returns:
            Path to the saved file.
        """
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path.cwd() / f"summary_{summary.topic_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary.to_dict(), f, indent=2)
        
        return str(output_path)
    
    def get_summary_statistics(self, topic_summaries: List[TopicSummary]) -> Dict[str, Any]:
        """
        Get statistics across multiple topic summaries.
        
        Args:
            topic_summaries: List of topic summaries.
        
        Returns:
            Dictionary with summary statistics.
        """
        total_sources = sum(ts.total_sources for ts in topic_summaries)
        total_key_points = sum(
            len(ts.source_summaries) for ts in topic_summaries
        )
        
        return {
            "total_topics": len(topic_summaries),
            "total_sources": total_sources,
            "total_key_points": total_key_points,
            "topics": [ts.topic_name for ts in topic_summaries]
        }
