"""Pattern Extractor - Identifies learning patterns and structures using CAFE framework."""

import json
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from pathlib import Path

import yaml
from openai import OpenAI


@dataclass
class PatternExtractionResult:
    """Complete result of pattern extraction."""
    topic_name: str
    patterns: Dict[str, Any]
    extraction_timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "patterns": self.patterns,
            "extraction_timestamp": self.extraction_timestamp
        }


class PatternExtractor:
    """
    Extracts learning patterns from content summaries using the CAFE framework.
    
    Identifies:
    - Compression opportunities (how to learn faster)
    - Frequency patterns (optimal practice schedules)
    - Encoding strategies (effective learning techniques)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.5,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Pattern Extractor.
        
        Args:
            api_key: OpenAI API key. If None, will try to read from OPENAI_API_KEY env var.
            model: LLM model to use for extraction.
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
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_prompt_template(self) -> str:
        """Load the pattern extraction prompt template."""
        prompt_path = Path(__file__).parent / "prompts" / "extract_patterns.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def extract_patterns(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        vital_concepts: Optional[List[str]] = None
    ) -> PatternExtractionResult:
        """
        Extract learning patterns from content summary.
        
        Args:
            topic_name: Name of the topic being extracted.
            content_summary: Summary of the main content with 'summary_text' and 'key_points'.
            vital_concepts: List of vital concepts (optional).
        
        Returns:
            PatternExtractionResult containing all extracted patterns.
        """
        # Prepare prompt
        prompt = self._build_extraction_prompt(topic_name, content_summary, vital_concepts)
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert learning pattern extractor using the CAFE framework."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=2000
        )
        
        # Parse response
        try:
            patterns = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, KeyError):
            # Fallback: extract patterns from text
            patterns = self._extract_patterns_from_text(response.choices[0].message.content)
        
        result = PatternExtractionResult(
            topic_name=topic_name,
            patterns=patterns,
            extraction_timestamp=self._get_timestamp()
        )
        
        return result
    
    def _build_extraction_prompt(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        vital_concepts: Optional[List[str]] = None
    ) -> str:
        """Build the extraction prompt."""
        summary_text = content_summary.get("summary_text", "")
        key_points = content_summary.get("key_points", [])
        
        prompt = f"""You are an expert learning pattern extractor using the CAFE framework (Compression, Abstraction, Frequency, Encoding).

Topic: {topic_name}

Content Summary:
{summary_text}

Key Points:
{chr(10).join([f"- {point}" for point in key_points])}

Extract learning patterns using the CAFE framework:

1. COMPRESSION OPPORTUNITIES:
   - Identify built-in functions, libraries, or tools that can accelerate learning
   - Find shortcuts, patterns, or reusable code snippets
   - Note any frameworks or methodologies that simplify complex tasks
   Format: {{opportunity: string, description: string, example: string}}

2. ABSTRACTION PATTERNS:
   - Identify common patterns, idioms, or design patterns
   - Note reusable structures or templates
   - Find generalizations that apply across multiple scenarios
   Format: {{pattern: string, description: string, examples: [string]}}

3. MENTAL MODELS:
   - Identify conceptual frameworks or mental models
   - Note philosophical principles or design philosophies
   - Find guiding principles for decision-making
   Format: {{model: string, description: string, application: string}}

Return a JSON object with these three categories. Use the examples below as a guide for the format.

Example output format:
{{
    "compression_opportunities": [
        {{"opportunity": "Built-in Functions", "description": "Python has built-in functions for common tasks", "example": "len(), str(), int()"}}
    ],
    "abstraction_patterns": [
        {{"pattern": "Context Managers", "description": "Use 'with' statement for resource management", "examples": ["with open('file.txt') as f:", "with lock:"]}}
    ],
    "mental_models": [
        {{"model": "Zen of Python", "description": "Philosophy of Python design", "application": "Guides code style and design decisions"}}
    ]
}}

Provide your analysis in this exact JSON format."""
        
        return prompt
    
    def _extract_patterns_from_text(self, text: str) -> Dict[str, Any]:
        """Extract patterns from text response (fallback)."""
        # Simple fallback extraction
        return {
            "compression_opportunities": [],
            "abstraction_patterns": [],
            "mental_models": []
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
