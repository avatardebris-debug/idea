"""Outline Generator - Creates structured learning outlines using DESS framework."""

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
    module_name: str
    module_description: str
    learning_objectives: List[str]
    estimated_time_hours: float
    prerequisites: List[str]
    key_topics: List[str]
    practice_activities: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module_name": self.module_name,
            "module_description": self.module_description,
            "learning_objectives": self.learning_objectives,
            "estimated_time_hours": self.estimated_time_hours,
            "prerequisites": self.prerequisites,
            "key_topics": self.key_topics,
            "practice_activities": self.practice_activities
        }


@dataclass
class LearningActivity:
    """Represents a learning activity for a module."""
    module: str
    reading: List[str]
    practice: List[str]
    projects: List[str]
    assessment: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module": self.module,
            "reading": self.reading,
            "practice": self.practice,
            "projects": self.projects,
            "assessment": self.assessment
        }


@dataclass
class ModuleSequence:
    """Represents the sequence of learning modules."""
    linear_path: List[str]
    parallel_paths: List[List[str]]
    optional_modules: List[str]
    milestones: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "linear_path": self.linear_path,
            "parallel_paths": self.parallel_paths,
            "optional_modules": self.optional_modules,
            "milestones": self.milestones
        }


@dataclass
class TimeEstimates:
    """Represents time estimates for the learning path."""
    total_learning_hours: float
    module_breakdown: Dict[str, float]
    practice_hours: float
    review_hours: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_learning_hours": self.total_learning_hours,
            "module_breakdown": self.module_breakdown,
            "practice_hours": self.practice_hours,
            "review_hours": self.review_hours
        }


@dataclass
class OutlineExtractionResult:
    """Complete result of outline extraction."""
    topic_name: str
    learning_modules: List[LearningModule]
    module_sequence: ModuleSequence
    learning_activities: List[LearningActivity]
    time_estimates: TimeEstimates
    learning_outline: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "topic_name": self.topic_name,
            "learning_modules": [lm.to_dict() for lm in self.learning_modules],
            "module_sequence": self.module_sequence.to_dict(),
            "learning_activities": [la.to_dict() for la in self.learning_activities],
            "time_estimates": self.time_estimates.to_dict()
        }
        if self.learning_outline:
            result["learning_outline"] = self.learning_outline
        return result


class OutlineGenerator:
    """
    Generates structured learning outlines from content summaries.
    
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
        source_summaries: Optional[List[Dict[str, Any]]] = None,
        vital_concepts: Optional[List[str]] = None
    ) -> OutlineExtractionResult:
        """
        Extract a structured learning outline from content summaries.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content including key points.
            source_summaries: Optional list of source summaries for cross-referencing.
            vital_concepts: Optional list of vital concepts to prioritize.
        
        Returns:
            OutlineExtractionResult containing the structured learning outline.
        """
        # Build the prompt
        prompt = self._build_extraction_prompt(topic_name, content_summary, source_summaries, vital_concepts)
        
        # Call LLM API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=3072
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        try:
            extraction_data = json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                extraction_data = json.loads(json_match.group(1))
            else:
                extraction_data = self._extract_json_from_text(content)
        
        # Create result object
        learning_modules = [
            LearningModule(
                module_name=module.get("module_name", ""),
                module_description=module.get("module_description", ""),
                learning_objectives=module.get("learning_objectives", []),
                estimated_time_hours=float(module.get("estimated_time_hours", 0)),
                prerequisites=module.get("prerequisites", []),
                key_topics=module.get("key_topics", []),
                practice_activities=module.get("practice_activities", [])
            )
            for module in extraction_data.get("learning_modules", [])
        ]
        
        module_sequence_data = extraction_data.get("module_sequence", {})
        module_sequence = ModuleSequence(
            linear_path=module_sequence_data.get("linear_path", []),
            parallel_paths=module_sequence_data.get("parallel_paths", []),
            optional_modules=module_sequence_data.get("optional_modules", []),
            milestones=module_sequence_data.get("milestones", [])
        )
        
        learning_activities = [
            LearningActivity(
                module=activity.get("module", ""),
                reading=activity.get("reading", []),
                practice=activity.get("practice", []),
                projects=activity.get("projects", []),
                assessment=activity.get("assessment", "")
            )
            for activity in extraction_data.get("learning_activities", [])
        ]
        
        time_estimates_data = extraction_data.get("time_estimates", {})
        time_estimates = TimeEstimates(
            total_learning_hours=float(time_estimates_data.get("total_learning_hours", 0)),
            module_breakdown=time_estimates_data.get("module_breakdown", {}),
            practice_hours=float(time_estimates_data.get("practice_hours", 0)),
            review_hours=float(time_estimates_data.get("review_hours", 0))
        )
        
        # Build learning_outline dictionary
        learning_outline = {
            "topic_name": topic_name,
            "learning_modules": [lm.to_dict() for lm in learning_modules],
            "module_sequence": module_sequence.to_dict(),
            "learning_activities": [la.to_dict() for la in learning_activities],
            "time_estimates": time_estimates.to_dict()
        }
        
        return OutlineExtractionResult(
            topic_name=topic_name,
            learning_modules=learning_modules,
            module_sequence=module_sequence,
            learning_activities=learning_activities,
            time_estimates=time_estimates,
            learning_outline=learning_outline
        )
    
    def _build_extraction_prompt(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]],
        vital_concepts: Optional[List[str]]
    ) -> str:
        """Build the outline extraction prompt."""
        summary_text = content_summary.get("summary_text", "")
        key_points = content_summary.get("key_points", [])
        
        sources_text = ""
        if source_summaries:
            sources_text = "\n\nSource Summaries:\n"
            for i, source in enumerate(source_summaries, 1):
                sources_text += f"\n--- Source {i}: {source.get('title', 'Unknown')} ---\n"
                sources_text += f"Key Points: {', '.join(source.get('key_points', []))}\n"
        
        vital_concepts_text = ""
        if vital_concepts:
            vital_concepts_text = f"\n\nVital Concepts to Prioritize:\n{chr(10).join([f'- {concept}' for concept in vital_concepts])}\n"
        
        prompt = f"""
Topic Name: {topic_name}

Content Summary:
{summary_text}

Key Points:
{chr(10).join([f"- {point}" for point in key_points])}

{vital_concepts_text}{sources_text}

Please create a structured learning outline following the output requirements.
"""
        return prompt
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text that may contain markdown or other formatting."""
        import re
        import json
        
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
            "topic_name": "Unknown",
            "learning_modules": [],
            "module_sequence": {
                "linear_path": [],
                "parallel_paths": [],
                "optional_modules": [],
                "milestones": []
            },
            "learning_activities": [],
            "time_estimates": {
                "total_learning_hours": 0,
                "module_breakdown": {},
                "practice_hours": 0,
                "review_hours": 0
            }
        }
    
    def validate_outline(self, result: OutlineExtractionResult) -> List[str]:
        """
        Validate the extracted outline for completeness and consistency.
        
        Args:
            result: The outline extraction result to validate.
        
        Returns:
            List of validation issues found.
        """
        issues = []
        
        # Check for empty modules
        if not result.learning_modules:
            issues.append("No learning modules extracted")
        
        # Check for missing prerequisites
        for module in result.learning_modules:
            if not module.learning_objectives:
                issues.append(f"Module '{module.module_name}' has no learning objectives")
            if not module.key_topics:
                issues.append(f"Module '{module.module_name}' has no key topics")
        
        # Check for circular dependencies
        module_names = [m.module_name for m in result.learning_modules]
        for module in result.learning_modules:
            for prereq in module.prerequisites:
                if prereq not in module_names:
                    issues.append(f"Module '{module.module_name}' has prerequisite '{prereq}' that doesn't exist")
        
        # Check for time estimate consistency
        total_time = sum(m.estimated_time_hours for m in result.learning_modules)
        if abs(total_time - result.time_estimates.total_learning_hours) > 1:
            issues.append(f"Total module time ({total_time:.1f}h) doesn't match total estimate ({result.time_estimates.total_learning_hours:.1f}h)")
        
        return issues
    
    def save_outline_to_file(
        self,
        result: OutlineExtractionResult,
        output_path: Optional[str] = None
    ) -> str:
        """
        Save outline result to a file.
        
        Args:
            result: The outline result to save.
            output_path: Optional path for output file.
        
        Returns:
            Path to the saved file.
        """
        from datetime import datetime
        
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path.cwd() / f"learning_outline_{result.topic_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        return str(output_path)
