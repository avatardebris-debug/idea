"""Topic deconstruction using the DESS framework."""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI


@dataclass
class SubTopic:
    """Represents a sub-topic within a topic."""
    name: str
    description: str
    estimated_hours: float
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class VitalConcept:
    """Represents a vital concept within a topic."""
    name: str
    why_vital: str
    connections: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)


@dataclass
class LearningObjective:
    """Represents a learning objective."""
    objective: str
    skill_type: str
    measurable_outcome: str


@dataclass
class CommonPitfall:
    """Represents a common pitfall in learning a topic."""
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
    """Complete deconstruction of a topic using the DESS framework."""
    topic_name: str
    sub_topics: List[SubTopic] = field(default_factory=list)
    vital_concepts: List[VitalConcept] = field(default_factory=list)
    learning_objectives: List[LearningObjective] = field(default_factory=list)
    common_pitfalls: List[CommonPitfall] = field(default_factory=list)
    recommended_resources: List[RecommendedResource] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "sub_topics": [
                {
                    "name": st.name,
                    "description": st.description,
                    "estimated_hours": st.estimated_hours,
                    "prerequisites": st.prerequisites
                } for st in self.sub_topics
            ],
            "vital_concepts": [
                {
                    "name": vc.name,
                    "why_vital": vc.why_vital,
                    "connections": vc.connections,
                    "applications": vc.applications
                } for vc in self.vital_concepts
            ],
            "learning_objectives": [
                {
                    "objective": lo.objective,
                    "skill_type": lo.skill_type,
                    "measurable_outcome": lo.measurable_outcome
                } for lo in self.learning_objectives
            ],
            "common_pitfalls": [
                {
                    "pitfall": cp.pitfall,
                    "why_problematic": cp.why_problematic,
                    "how_to_avoid": cp.how_to_avoid
                } for cp in self.common_pitfalls
            ],
            "recommended_resources": [
                {
                    "type": rr.type,
                    "title": rr.title,
                    "specific_focus": rr.specific_focus
                } for rr in self.recommended_resources
            ]
        }


class TopicAnalyzer:
    """Analyzes and deconstructs topics using the DESS framework."""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.7):
        """Initialize the TopicAnalyzer.
        
        Args:
            model: The OpenAI model to use for deconstruction.
            temperature: Temperature parameter for the LLM.
        """
        self.model = model
        self.temperature = temperature
        self.client = OpenAI()
        self.prompt_template = """You are an expert learning architect using the DESS framework (Deconstruction, Essential Elements, Subtopics, Structure).
Your task is to deconstruct a learning topic into its component parts to create an effective learning path.

DESS Framework Components:
1. Subtopics: Break the topic into manageable learning units
2. Vital Concepts: Identify the 20% of concepts that give 80% of the results
3. Learning Objectives: Define what learners should be able to do
4. Common Pitfalls: Identify where learners typically struggle

Please provide your response in valid JSON format with the following structure:
{
    "sub_topics": [
        {
            "name": "Sub-topic name",
            "description": "Brief description of this sub-topic",
            "estimated_hours": 5.0,
            "prerequisites": ["Prerequisite sub-topic names"]
        }
    ],
    "vital_concepts": [
        {
            "name": "Concept name",
            "why_vital": "Why this concept is critical to master",
            "connections": ["Related concepts"],
            "applications": ["Practical applications"]
        }
    ],
    "learning_objectives": [
        {
            "objective": "What the learner should achieve",
            "skill_type": "knowledge|skill|attitude",
            "measurable_outcome": "How to measure success"
        }
    ],
    "common_pitfalls": [
        {
            "pitfall": "Common mistake or misconception",
            "why_problematic": "Why this is a problem",
            "how_to_avoid": "How to avoid this pitfall"
        }
    ],
    "recommended_resources": [
        {
            "type": "book|video|course|article|other",
            "title": "Resource title",
            "specific_focus": "What aspect this resource covers"
        }
    ]
}

IMPORTANT: Return ONLY valid JSON. Do not include markdown code blocks, explanations, or any other text."""
    
    def deconstruct(
        self,
        topic_name: str,
        topic_description: str,
        learner_background: Optional[str] = None,
        learner_goals: Optional[str] = None
    ) -> TopicDeconstruction:
        """Deconstruct a topic using the DESS framework.
        
        Args:
            topic_name: Name of the topic to deconstruct.
            topic_description: Description of the topic.
            learner_background: Optional background information about the learner.
            learner_goals: Optional learning goals of the learner.
        
        Returns:
            TopicDeconstruction object with the deconstructed topic.
        """
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
