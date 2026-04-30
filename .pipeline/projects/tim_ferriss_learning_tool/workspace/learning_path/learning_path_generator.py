"""Learning Path Generator - Creates structured learning paths using DESS framework."""

import json
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from openai import OpenAI


@dataclass
class LearningPath:
    """Represents a complete learning path."""
    path_name: str
    description: str
    total_duration_hours: float
    difficulty_level: str
    modules: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    success_criteria: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "path_name": self.path_name,
            "description": self.description,
            "total_duration_hours": self.total_duration_hours,
            "difficulty_level": self.difficulty_level,
            "modules": self.modules,
            "milestones": self.milestones,
            "resources": self.resources,
            "success_criteria": self.success_criteria
        }


@dataclass
class LearningPathResult:
    """Complete result of learning path generation."""
    topic_name: str
    learning_paths: List[LearningPath]
    recommended_path: str
    customization_options: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "learning_paths": [lp.to_dict() for lp in self.learning_paths],
            "recommended_path": self.recommended_path,
            "customization_options": self.customization_options
        }


class LearningPathGenerator:
    """
    Generates structured learning paths from content summaries.
    
    Creates multiple path options with different focuses:
    - Speed-focused paths (compressed learning)
    - Depth-focused paths (comprehensive learning)
    - Practice-focused paths (hands-on learning)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.5,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Learning Path Generator.
        
        Args:
            api_key: OpenAI API key. If None, will try to read from OPENAI_API_KEY env var.
            model: LLM model to use for generation.
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
        """Load the learning path generation prompt template."""
        prompt_path = Path(__file__).parent / "prompts" / "generate_path.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def generate_paths(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None,
        learning_patterns: Optional[Dict[str, Any]] = None
    ) -> LearningPathResult:
        """
        Generate learning paths from content summaries.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
            learning_patterns: Optional extracted learning patterns.
        
        Returns:
            LearningPathResult containing generated paths.
        """
        # Build the prompt
        prompt = self._build_generation_prompt(
            topic_name, 
            content_summary, 
            source_summaries,
            learning_patterns
        )
        
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
            generation_data = json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                generation_data = json.loads(json_match.group(1))
            else:
                generation_data = self._extract_json_from_text(content)
        
        # Create learning paths
        learning_paths = []
        for path_data in generation_data.get("learning_paths", []):
            learning_paths.append(LearningPath(
                path_name=path_data.get("path_name", ""),
                description=path_data.get("description", ""),
                total_duration_hours=path_data.get("total_duration_hours", 0),
                difficulty_level=path_data.get("difficulty_level", "intermediate"),
                modules=path_data.get("modules", []),
                milestones=path_data.get("milestones", []),
                resources=path_data.get("resources", []),
                success_criteria=path_data.get("success_criteria", "")
            ))
        
        # Determine recommended path
        recommended_path = self._determine_recommended_path(learning_paths, generation_data)
        
        return LearningPathResult(
            topic_name=topic_name,
            learning_paths=learning_paths,
            recommended_path=recommended_path,
            customization_options=generation_data.get("customization_options", {})
        )
    
    def _build_generation_prompt(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]],
        learning_patterns: Optional[Dict[str, Any]]
    ) -> str:
        """Build the learning path generation prompt."""
        summary_text = content_summary.get("summary_text", "")
        key_points = content_summary.get("key_points", [])
        
        sources_text = ""
        if source_summaries:
            sources_text = "\n\nSource Summaries:\n"
            for i, source in enumerate(source_summaries, 1):
                sources_text += f"\n--- Source {i}: {source.get('title', 'Unknown')} ---\n"
                sources_text += f"Key Points: {', '.join(source.get('key_points', []))}\n"
        
        patterns_text = ""
        if learning_patterns:
            patterns_text = "\n\nExtracted Learning Patterns:\n"
            patterns_text += f"Compression Opportunities: {len(learning_patterns.get('compression_opportunities', []))}\n"
            patterns_text += f"Frequency Patterns: {learning_patterns.get('frequency_patterns', {})}\n"
            patterns_text += f"Encoding Strategies: {len(learning_patterns.get('encoding_strategies', []))}\n"
        
        prompt = f"""
Topic Name: {topic_name}

Content Summary:
{summary_text}

Key Points:
{chr(10).join([f"- {point}" for point in key_points])}

{sources_text}

{patterns_text}

Please generate structured learning paths following the output requirements.
"""
        return prompt
    
    def _determine_recommended_path(
        self,
        learning_paths: List[LearningPath],
        generation_data: Dict[str, Any]
    ) -> str:
        """Determine the recommended learning path."""
        if not learning_paths:
            return ""
        
        # Check for explicit recommendation in generation data
        if "recommended_path" in generation_data:
            return generation_data["recommended_path"]
        
        # Default to first path if no recommendation
        return learning_paths[0].path_name if learning_paths else ""
    
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
            "learning_paths": [],
            "recommended_path": "",
            "customization_options": {}
        }
    
    def generate_customized_path(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        learner_profile: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> LearningPathResult:
        """
        Generate a customized learning path based on learner profile.
        
        Args:
            topic_name: Name of the topic.
            content_summary: Structured summary of the content.
            learner_profile: Profile of the learner (experience level, goals, etc.).
            constraints: Optional constraints (time, resources, etc.).
        
        Returns:
            LearningPathResult with customized path.
        """
        # Build prompt with learner profile
        prompt = f"""
Topic Name: {topic_name}

Content Summary:
{content_summary.get('summary_text', '')}

Key Points:
{chr(10).join([f"- {point}" for point in content_summary.get('key_points', [])])}

Learner Profile:
{json.dumps(learner_profile, indent=2)}

Constraints:
{json.dumps(constraints, indent=2) if constraints else "None"}

Please generate a customized learning path for this learner.
"""
        
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
        
        # Parse and return result (similar to generate_paths)
        content = response.choices[0].message.content
        # ... (same parsing logic as generate_paths)
        
        return self._parse_path_result(content, topic_name)
    
    def _parse_path_result(self, content: str, topic_name: str) -> LearningPathResult:
        """Parse the learning path generation result."""
        try:
            generation_data = json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                generation_data = json.loads(json_match.group(1))
            else:
                generation_data = self._extract_json_from_text(content)
        
        learning_paths = []
        for path_data in generation_data.get("learning_paths", []):
            learning_paths.append(LearningPath(
                path_name=path_data.get("path_name", ""),
                description=path_data.get("description", ""),
                total_duration_hours=path_data.get("total_duration_hours", 0),
                difficulty_level=path_data.get("difficulty_level", "intermediate"),
                modules=path_data.get("modules", []),
                milestones=path_data.get("milestones", []),
                resources=path_data.get("resources", []),
                success_criteria=path_data.get("success_criteria", "")
            ))
        
        return LearningPathResult(
            topic_name=topic_name,
            learning_paths=learning_paths,
            recommended_path=self._determine_recommended_path(learning_paths, generation_data),
            customization_options=generation_data.get("customization_options", {})
        )
    
    def save_paths_to_file(
        self,
        result: LearningPathResult,
        output_path: Optional[str] = None
    ) -> str:
        """
        Save learning paths to a file.
        
        Args:
            result: The learning path result to save.
            output_path: Optional path for output file.
        
        Returns:
            Path to the saved file.
        """
        from datetime import datetime
        
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path.cwd() / f"learning_path_{result.topic_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        return str(output_path)