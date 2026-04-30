"""Lesson Generator - Creates sequenced lesson plans with progressive difficulty."""

import json
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from openai import OpenAI


@dataclass
class LessonActivity:
    """Represents a learning activity within a lesson."""
    activity_type: str  # "read", "watch", "practice", "discuss", "create"
    title: str
    description: str
    estimated_time: str
    resources: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "activity_type": self.activity_type,
            "title": self.title,
            "description": self.description,
            "estimated_time": self.estimated_time,
            "resources": self.resources,
            "success_criteria": self.success_criteria
        }


@dataclass
class LessonPlan:
    """Represents a complete lesson plan."""
    lesson_number: int
    title: str
    learning_objectives: List[str]
    prerequisite_lessons: List[int]
    activities: List[LessonActivity]
    key_concepts: List[str]
    estimated_total_time: str
    difficulty_level: str  # "beginner", "intermediate", "advanced"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "lesson_number": self.lesson_number,
            "title": self.title,
            "learning_objectives": self.learning_objectives,
            "prerequisite_lessons": self.prerequisite_lessons,
            "activities": [a.to_dict() for a in self.activities],
            "key_concepts": self.key_concepts,
            "estimated_total_time": self.estimated_total_time,
            "difficulty_level": self.difficulty_level
        }


@dataclass
class SequencingResult:
    """Complete result of lesson sequencing."""
    topic_name: str
    lesson_plans: List[LessonPlan]
    learning_path: List[int]  # Ordered list of lesson numbers
    total_estimated_time: str
    difficulty_progression: List[str]
    vital_concepts: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "lesson_plans": [lp.to_dict() for lp in self.lesson_plans],
            "learning_path": self.learning_path,
            "total_estimated_time": self.total_estimated_time,
            "difficulty_progression": self.difficulty_progression,
            "vital_concepts": self.vital_concepts,
            "learning_objectives": self.learning_objectives
        }


class LessonGenerator:
    """
    Generates sequenced lesson plans with progressive difficulty.
    
    Creates:
    - Individual lesson plans with clear objectives
    - Prerequisite relationships between lessons
    - Progressive difficulty from beginner to advanced
    - Varied learning activities for engagement
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.3,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Lesson Generator.
        
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
        """Load the lesson generation prompt template."""
        prompt_path = Path(__file__).parent / "prompts" / "generate_lessons.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def _parse_lesson_plans(self, response_content: str) -> SequencingResult:
        """
        Parse the LLM response into a SequencingResult.
        
        Args:
            response_content: Raw response content from the LLM.
        
        Returns:
            Parsed SequencingResult.
        """
        try:
            lesson_data = json.loads(response_content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_content, re.DOTALL)
            if json_match:
                lesson_data = json.loads(json_match.group(1))
            else:
                lesson_data = self._extract_json_from_text(response_content)
        
        # Create lesson plans
        lesson_plans = []
        for lesson in lesson_data.get("lesson_plans", []):
            activities = [
                LessonActivity(
                    activity_type=act.get("activity_type", "read"),
                    title=act.get("title", ""),
                    description=act.get("description", ""),
                    estimated_time=act.get("estimated_time", "30 min"),
                    resources=act.get("resources", []),
                    success_criteria=act.get("success_criteria", [])
                )
                for act in lesson.get("activities", [])
            ]
            
            lesson_plans.append(LessonPlan(
                lesson_number=lesson.get("lesson_number", len(lesson_plans) + 1),
                title=lesson.get("title", f"Lesson {len(lesson_plans) + 1}"),
                learning_objectives=lesson.get("learning_objectives", []),
                prerequisite_lessons=lesson.get("prerequisite_lessons", []),
                activities=activities,
                key_concepts=lesson.get("key_concepts", []),
                estimated_total_time=lesson.get("estimated_total_time", "2 hours"),
                difficulty_level=lesson.get("difficulty_level", "beginner")
            ))
        
        # Determine learning path (topological sort based on prerequisites)
        learning_path = self._determine_learning_path(lesson_plans)
        
        # Calculate total estimated time
        total_time = self._calculate_total_time(lesson_plans)
        
        # Determine difficulty progression
        difficulty_progression = [lp.difficulty_level for lp in lesson_plans]
        
        return SequencingResult(
            topic_name=lesson_data.get("topic_name", "Unknown Topic"),
            lesson_plans=lesson_plans,
            learning_path=learning_path,
            total_estimated_time=total_time,
            difficulty_progression=difficulty_progression,
            vital_concepts=lesson_data.get("vital_concepts", []),
            learning_objectives=lesson_data.get("learning_objectives", [])
        )
    
    def generate_lesson_plans(
        self,
        topic_name: str,
        vital_concepts: Optional[List[str]] = None,
        learning_modules: Optional[List[Dict[str, Any]]] = None,
        learning_profile: Optional[Dict[str, Any]] = None
    ) -> SequencingResult:
        """
        Generate sequenced lesson plans from learning modules.
        
        Args:
            topic_name: Name of the topic being taught.
            vital_concepts: List of vital concepts to cover.
            learning_modules: List of learning modules from outline extraction.
            learner_profile: Optional learner profile for customization.
        
        Returns:
            SequencingResult containing sequenced lesson plans.
        """
        # Build the prompt
        prompt = self._build_generation_prompt(
            topic_name, vital_concepts or [], learning_modules or [], learning_profile
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
        return self._parse_lesson_plans(response.choices[0].message.content)
    
    def _build_generation_prompt(
        self,
        topic_name: str,
        vital_concepts: List[str],
        learning_modules: List[Dict[str, Any]],
        learning_profile: Optional[Dict[str, Any]]
    ) -> str:
        """Build the lesson generation prompt."""
        modules_text = ""
        for i, module in enumerate(learning_modules, 1):
            modules_text += f"\nModule {i}: {module.get('title', 'Untitled')}\n"
            modules_text += f"Objectives: {', '.join(module.get('objectives', []))}\n"
            modules_text += f"Key Concepts: {', '.join(module.get('key_concepts', []))}\n"
            modules_text += f"Exercises: {', '.join(module.get('exercises', []))}\n"
        
        vital_concepts_text = "\n\nVital Concepts to Cover:\n"
        vital_concepts_text += "\n".join([f"- {concept}" for concept in vital_concepts])
        
        learner_profile_text = ""
        if learner_profile:
            learner_profile_text = f"\n\nLearner Profile:\n"
            learner_profile_text += f"Background: {learner_profile.get('background', 'Not specified')}\n"
            learner_profile_text += f"Goals: {learner_profile.get('goals', 'Not specified')}\n"
            learner_profile_text += f"Learning Style: {learner_profile.get('learning_style', 'Not specified')}\n"
        
        prompt = f"""You are an expert instructional designer creating sequenced lesson plans.

Topic: {topic_name}

{vital_concepts_text}

Learning Modules:
{modules_text}

{learner_profile_text}

Create a comprehensive set of sequenced lesson plans with the following requirements:

{{
    "lesson_plans": [
        {{
            "lesson_number": 1,
            "title": "Introduction to [Topic]",
            "learning_objectives": ["Understand X", "Learn Y"],
            "prerequisite_lessons": [],
            "activities": [
                {{
                    "activity_type": "read",
                    "title": "Reading Activity",
                    "description": "Read about X",
                    "estimated_time": "30 min",
                    "resources": ["Resource 1"],
                    "success_criteria": ["Can explain X"]
                }},
                {{
                    "activity_type": "practice",
                    "title": "Practice Exercise",
                    "description": "Practice Y",
                    "estimated_time": "45 min",
                    "resources": [],
                    "success_criteria": ["Can apply Y"]
                }}
            ],
            "key_concepts": ["Concept A", "Concept B"],
            "estimated_total_time": "2 hours",
            "difficulty_level": "beginner"
        }},
        {{
            "lesson_number": 2,
            "title": "Building on Foundations",
            "learning_objectives": ["Master X", "Apply Y"],
            "prerequisite_lessons": [1],
            "activities": [
                {{
                    "activity_type": "discuss",
                    "title": "Discussion",
                    "description": "Discuss X and Y",
                    "estimated_time": "60 min",
                    "resources": [],
                    "success_criteria": ["Can discuss X and Y"]
                }}
            ],
            "key_concepts": ["Advanced A", "Advanced B"],
            "estimated_total_time": "3 hours",
            "difficulty_level": "intermediate"
        }}
    ]
}}

Requirements:
- Create 4-6 lesson plans that build progressively
- Each lesson should have clear, measurable learning objectives
- Include varied activity types (read, watch, practice, discuss, create)
- Specify prerequisite relationships between lessons
- Estimate realistic time commitments
- Progress from beginner to advanced difficulty
- Ensure all vital concepts are covered across lessons
- Include success criteria for each activity

Return your response as a JSON object with the exact format shown above."""
        
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
            "lesson_plans": []
        }
    
    def _determine_learning_path(self, lesson_plans: List[LessonPlan]) -> List[int]:
        """
        Determine the optimal learning path using topological sort.
        
        Args:
            lesson_plans: List of lesson plans with prerequisites.
        
        Returns:
            Ordered list of lesson numbers.
        """
        if not lesson_plans:
            return []
        
        # Build adjacency list and in-degree count
        graph = {lp.lesson_number: [] for lp in lesson_plans}
        in_degree = {lp.lesson_number: 0 for lp in lesson_plans}
        
        for lesson in lesson_plans:
            for prereq in lesson.prerequisite_lessons:
                if prereq in graph:
                    graph[prereq].append(lesson.lesson_number)
                    in_degree[lesson.lesson_number] += 1
        
        # Kahn's algorithm for topological sort
        queue = [lesson_num for lesson_num, degree in in_degree.items() if degree == 0]
        learning_path = []
        
        while queue:
            # Sort by lesson number for consistent ordering
            queue.sort()
            current = queue.pop(0)
            learning_path.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If not all lessons are in the path, there's a cycle
        if len(learning_path) != len(lesson_plans):
            # Fallback: just return all lesson numbers
            return [lp.lesson_number for lp in lesson_plans]
        
        return learning_path
    
    def _calculate_total_time(self, lesson_plans: List[LessonPlan]) -> str:
        """
        Calculate total estimated time for all lessons.
        
        Args:
            lesson_plans: List of lesson plans.
        
        Returns:
            Total estimated time as a string.
        """
        total_minutes = 0
        
        for lesson in lesson_plans:
            time_str = lesson.estimated_total_time
            # Parse time string (e.g., "2 hours", "90 minutes", "1.5 hours")
            time_match = re.search(r'(\d+\.?\d*)\s*(hours?|minutes?|mins?|hrs?)', time_str.lower())
            if time_match:
                value = float(time_match.group(1))
                unit = time_match.group(2).lower()
                
                if unit in ['hours', 'hour', 'hrs', 'hr']:
                    total_minutes += value * 60
                elif unit in ['minutes', 'minute', 'mins', 'min']:
                    total_minutes += value
        
        # Convert back to human-readable format
        if total_minutes >= 60:
            hours = total_minutes / 60
            if hours == int(hours):
                return f"{int(hours)} hours"
            else:
                return f"{hours:.1f} hours"
        else:
            return f"{int(total_minutes)} minutes"
    
    def save_lesson_plans_to_file(
        self,
        result: SequencingResult,
        output_path: Optional[str] = None
    ) -> str:
        """
        Save lesson plans to a file.
        
        Args:
            result: The sequencing result to save.
            output_path: Optional path for output file.
        
        Returns:
            Path to the saved file.
        """
        from datetime import datetime
        
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path.cwd() / f"lesson_plans_{result.topic_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        return str(output_path)
    
    def generate_lesson_summary(
        self,
        result: SequencingResult
    ) -> str:
        """
        Generate a human-readable summary of the lesson plans.
        
        Args:
            result: The sequencing result.
        
        Returns:
            Human-readable summary string.
        """
        summary = f"Lesson Plan Summary: {result.topic_name}\n"
        summary += "=" * 60 + "\n\n"
        
        for lesson in result.lesson_plans:
            summary += f"Lesson {lesson.lesson_number}: {lesson.title}\n"
            summary += f"Difficulty: {lesson.difficulty_level}\n"
            summary += f"Time: {lesson.estimated_total_time}\n"
            summary += f"Objectives:\n"
            for obj in lesson.learning_objectives:
                summary += f"  - {obj}\n"
            summary += f"Key Concepts: {', '.join(lesson.key_concepts)}\n"
            summary += f"Activities: {len(lesson.activities)}\n"
            summary += "-" * 40 + "\n"
        
        summary += f"\nTotal Estimated Time: {result.total_estimated_time}\n"
        summary += f"Learning Path: {' -> '.join(map(str, result.learning_path))}\n"
        summary += f"Difficulty Progression: {' -> '.join(result.difficulty_progression)}\n"
        
        return summary