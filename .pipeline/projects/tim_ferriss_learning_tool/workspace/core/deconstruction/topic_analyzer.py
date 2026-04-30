"""Topic Analyzer - Deconstructs topics into learnable components using LLM."""

import json
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path

import yaml
from openai import OpenAI


@dataclass
class SubTopic:
    """Represents a sub-topic in the deconstruction."""
    name: str
    description: str
    estimated_hours: float
    prerequisites: List[str]


@dataclass
class VitalConcept:
    """Represents a vital concept (the 20% that gives 80% results)."""
    name: str
    why_vital: str
    connections: List[str]
    applications: List[str]


@dataclass
class LearningObjective:
    """Represents a learning objective."""
    objective: str
    skill_type: str
    measurable_outcome: str


@dataclass
class CommonPitfall:
    """Represents a common pitfall to avoid."""
    pitfall: str
    why_problematic: str
    how_to_avoid: str


@dataclass
class RecommendedResource:
    """Represents a recommended learning resource."""
    type: str
    title: str
    specific_focus: str


@dataclass
class TopicDeconstruction:
    """Complete deconstruction of a topic."""
    topic_name: str
    sub_topics: List[SubTopic]
    vital_concepts: List[VitalConcept]
    learning_objectives: List[LearningObjective]
    common_pitfalls: List[CommonPitfall]
    recommended_resources: List[RecommendedResource]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "sub_topics": [asdict(st) for st in self.sub_topics],
            "vital_concepts": [asdict(vc) for vc in self.vital_concepts],
            "learning_objectives": [asdict(lo) for lo in self.learning_objectives],
            "common_pitfalls": [asdict(cp) for cp in self.common_pitfalls],
            "recommended_resources": [asdict(rr) for rr in self.recommended_resources]
        }


class TopicAnalyzer:
    """
    Deconstructs topics into learnable components using LLM.
    
    Uses Tim Ferriss's DESS framework to break down any topic into
    logical sub-components, identify the vital 20%, and create
    structured learning objectives.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Topic Analyzer.
        
        Args:
            api_key: OpenAI API key. If None, will try to read from OPENAI_API_KEY env var.
            model: LLM model to use for deconstruction.
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
                "deconstruction": {
                    "depth": "comprehensive",
                    "max_sub_components": 10
                }
            }
    
    def _load_prompt_template(self) -> str:
        """Load the deconstruction prompt template."""
        prompt_path = Path(__file__).parent / "prompts" / "deconstruct_topic.md"
        
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
    
    def deconstruct(
        self,
        topic_name: str,
        topic_description: str,
        learner_background: Optional[str] = None,
        learner_goals: Optional[str] = None
    ) -> TopicDeconstruction:
        """
        Deconstruct a topic into learnable components.
        
        Args:
            topic_name: Name of the topic to deconstruct.
            topic_description: Description of the topic.
            learner_background: Optional background information about the learner.
            learner_goals: Optional learning goals of the learner.
        
        Returns:
            TopicDeconstruction object with structured deconstruction.
        """
        # Build the prompt with topic information
        prompt = self._build_deconstruction_prompt(
            topic_name=topic_name,
            topic_description=topic_description,
            learner_background=learner_background,
            learner_goals=learner_goals
        )
        
        # Call LLM API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=4096
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        try:
            # Try to parse as JSON first
            deconstruction_data = json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                deconstruction_data = json.loads(json_match.group(1))
            else:
                # Last resort: try to find JSON-like structure
                deconstruction_data = self._extract_json_from_text(content)
        
        # Convert to TopicDeconstruction object
        return self._parse_deconstruction_data(deconstruction_data, topic_name)
    
    def _build_deconstruction_prompt(
        self,
        topic_name: str,
        topic_description: str,
        learner_background: Optional[str],
        learner_goals: Optional[str]
    ) -> str:
        """Build the prompt for topic deconstruction."""
        prompt = f"""
Topic Name: {topic_name}

Topic Description: {topic_description}
"""
        if learner_background:
            prompt += f"\nLearner Background: {learner_background}"
        if learner_goals:
            prompt += f"\nLearner Goals: {learner_goals}"
        
        prompt += "\n\nPlease deconstruct this topic according to the DESS framework."
        return prompt
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON-like structure from text response."""
        # Try to find JSON-like patterns
        import re
        json_start = text.find('{')
        json_end = text.rfind('}')
        
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = text[json_start:json_end + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Return a minimal structure if parsing fails
        return {
            "topic_name": "Unknown",
            "sub_topics": [],
            "vital_concepts": [],
            "learning_objectives": [],
            "common_pitfalls": [],
            "recommended_resources": []
        }
    
    def _parse_deconstruction_data(
        self,
        data: Dict[str, Any],
        topic_name: str
    ) -> TopicDeconstruction:
        """Parse deconstruction data into TopicDeconstruction object."""
        sub_topics = [
            SubTopic(
                name=item.get("name", "Unknown"),
                description=item.get("description", ""),
                estimated_hours=float(item.get("estimated_hours", 0)),
                prerequisites=item.get("prerequisites", [])
            )
            for item in data.get("sub_topics", [])
        ]
        
        vital_concepts = [
            VitalConcept(
                name=item.get("name", "Unknown"),
                why_vital=item.get("why_vital", ""),
                connections=item.get("connections", []),
                applications=item.get("applications", [])
            )
            for item in data.get("vital_concepts", [])
        ]
        
        learning_objectives = [
            LearningObjective(
                objective=item.get("objective", ""),
                skill_type=item.get("skill_type", ""),
                measurable_outcome=item.get("measurable_outcome", "")
            )
            for item in data.get("learning_objectives", [])
        ]
        
        common_pitfalls = [
            CommonPitfall(
                pitfall=item.get("pitfall", ""),
                why_problematic=item.get("why_problematic", ""),
                how_to_avoid=item.get("how_to_avoid", "")
            )
            for item in data.get("common_pitfalls", [])
        ]
        
        recommended_resources = [
            RecommendedResource(
                type=item.get("type", ""),
                title=item.get("title", ""),
                specific_focus=item.get("specific_focus", "")
            )
            for item in data.get("recommended_resources", [])
        ]
        
        return TopicDeconstruction(
            topic_name=topic_name,
            sub_topics=sub_topics,
            vital_concepts=vital_concepts,
            learning_objectives=learning_objectives,
            common_pitfalls=common_pitfalls,
            recommended_resources=recommended_resources
        )
    
    def deconstruct_to_dict(
        self,
        topic_name: str,
        topic_description: str,
        learner_background: Optional[str] = None,
        learner_goals: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deconstruct a topic and return as dictionary.
        
        Convenience method that returns the deconstruction as a dictionary
        instead of a TopicDeconstruction object.
        
        Args:
            topic_name: Name of the topic to deconstruct.
            topic_description: Description of the topic.
            learner_background: Optional background information about the learner.
            learner_goals: Optional learning goals of the learner.
        
        Returns:
            Dictionary containing the deconstruction data.
        """
        deconstruction = self.deconstruct(
            topic_name=topic_name,
            topic_description=topic_description,
            learner_background=learner_background,
            learner_goals=learner_goals
        )
        return deconstruction.to_dict()
