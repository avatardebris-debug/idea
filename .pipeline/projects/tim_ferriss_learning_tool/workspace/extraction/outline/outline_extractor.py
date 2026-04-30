"""Outline Extractor - Creates structured learning outlines using DESS framework."""

import json
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from pathlib import Path

import yaml
from openai import OpenAI


@dataclass
class LearningModule:
    """Represents a learning module in the outline."""
    module_number: int
    title: str
    estimated_time: str
    objectives: List[str]
    key_concepts: List[str]
    exercises: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module_number": self.module_number,
            "title": self.title,
            "estimated_time": self.estimated_time,
            "objectives": self.objectives,
            "key_concepts": self.key_concepts,
            "exercises": self.exercises
        }


@dataclass
class OutlineExtractionResult:
    """Complete result of outline extraction."""
    topic_name: str
    learning_modules: List[LearningModule]
    extraction_timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "learning_modules": [lm.to_dict() for lm in self.learning_modules],
            "extraction_timestamp": self.extraction_timestamp
        }


class OutlineExtractor:
    """
    Extracts structured learning outlines from content summaries using the DESS framework.
    
    Creates:
    - Learning modules with clear objectives
    - Module sequences with prerequisites
    - Learning activities for each module
    - Time estimates for the learning path
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.5,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Outline Extractor.
        
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
        """Load the outline extraction prompt template."""
        prompt_path = Path(__file__).parent / "prompts" / "extract_outline.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def extract_outline(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        vital_concepts: Optional[List[str]] = None,
        pattern_extraction: Optional[Dict[str, Any]] = None
    ) -> OutlineExtractionResult:
        """
        Extract a structured learning outline from content summary.
        
        Args:
            topic_name: Name of the topic being extracted.
            content_summary: Summary of the main content with 'summary_text' and 'key_points'.
            vital_concepts: List of vital concepts (optional).
            pattern_extraction: Extracted patterns (optional).
        
        Returns:
            OutlineExtractionResult containing the structured learning outline.
        """
        # Prepare prompt
        prompt = self._build_extraction_prompt(topic_name, content_summary, vital_concepts, pattern_extraction)
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert learning outline extractor using the DESS framework."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=2000
        )
        
        # Parse response
        try:
            outline_data = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, KeyError):
            # Fallback: extract outline from text
            outline_data = self._extract_outline_from_text(response.choices[0].message.content)
        
        # Create learning modules
        learning_modules = [
            LearningModule(
                module_number=module.get("module_number", i + 1),
                title=module.get("title", f"Module {i + 1}"),
                estimated_time=module.get("estimated_time", "1 hour"),
                objectives=module.get("objectives", []),
                key_concepts=module.get("key_concepts", []),
                exercises=module.get("exercises", [])
            )
            for i, module in enumerate(outline_data.get("learning_modules", []))
        ]
        
        result = OutlineExtractionResult(
            topic_name=topic_name,
            learning_modules=learning_modules,
            extraction_timestamp=self._get_timestamp()
        )
        
        return result
    
    def _build_extraction_prompt(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        vital_concepts: Optional[List[str]] = None,
        pattern_extraction: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the outline extraction prompt."""
        summary_text = content_summary.get("summary_text", "")
        key_points = content_summary.get("key_points", [])
        
        vital_concepts_text = ""
        if vital_concepts:
            vital_concepts_text = f"\n\nVital Concepts to Include:\n{chr(10).join([f'- {concept}' for concept in vital_concepts])}\n"
        
        patterns_text = ""
        if pattern_extraction:
            patterns_text = f"\n\nLearning Patterns to Consider:\n{chr(10).join([f'- {key}: {value}' for key, value in pattern_extraction.items()])}\n"
        
        prompt = f"""You are an expert learning outline extractor using the DESS framework (Decomposition, Elaboration, Sequencing, Synthesis).

Topic: {topic_name}

Content Summary:
{summary_text}

Key Points:
{chr(10).join([f"- {point}" for point in key_points])}

{vital_concepts_text}{patterns_text}

Create a structured learning outline with the following format:

{{
    "learning_modules": [
        {{
            "module_number": 1,
            "title": "Module Title",
            "estimated_time": "2 hours",
            "objectives": ["Understand X", "Learn Y"],
            "key_concepts": ["Concept A", "Concept B"],
            "exercises": ["Exercise 1", "Exercise 2"]
        }},
        {{
            "module_number": 2,
            "title": "Next Module",
            "estimated_time": "3 hours",
            "objectives": ["Master X", "Apply Y"],
            "key_concepts": ["Advanced A", "Advanced B"],
            "exercises": ["Advanced Exercise 1", "Advanced Exercise 2"]
        }}
    ]
}}

Requirements:
- Create 3-5 learning modules that cover the topic comprehensively
- Each module should have clear, measurable objectives
- Include key concepts that are essential for understanding
- Provide practical exercises for each module
- Estimate realistic time commitments for each module
- Order modules logically from basic to advanced

Return your response as a JSON object with the exact format shown above."""
        
        return prompt
    
    def _extract_outline_from_text(self, text: str) -> Dict[str, Any]:
        """Extract outline from text response (fallback)."""
        # Simple fallback extraction
        return {
            "learning_modules": []
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
