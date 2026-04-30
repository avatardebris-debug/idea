"""Assessment Generator - Creates progressive assessments with mastery tracking."""

import json
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from openai import OpenAI


@dataclass
class AssessmentQuestion:
    """Represents a single assessment question."""
    question_id: str
    question_text: str
    question_type: str  # "multiple_choice", "true_false", "short_answer", "essay"
    correct_answer: str
    explanation: str
    difficulty: str  # "beginner", "intermediate", "advanced"
    points: int
    learning_objective: str
    distractors: List[str] = field(default_factory=list)  # For multiple choice

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "difficulty": self.difficulty,
            "points": self.points,
            "learning_objective": self.learning_objective,
            "distractors": self.distractors
        }


@dataclass
class Assessment:
    """Represents a complete assessment."""
    assessment_id: str
    title: str
    description: str
    questions: List[AssessmentQuestion]
    total_points: int
    passing_score: float  # Percentage
    time_limit: str
    prerequisites: List[str]  # Other assessments that should be completed first

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "assessment_id": self.assessment_id,
            "title": self.title,
            "description": self.description,
            "questions": [q.to_dict() for q in self.questions],
            "total_points": self.total_points,
            "passing_score": self.passing_score,
            "time_limit": self.time_limit,
            "prerequisites": self.prerequisites
        }


@dataclass
class MasteryLevel:
    """Represents a learner's mastery level for a concept."""
    concept: str
    mastery_percentage: float  # 0-100
    status: str  # "not_started", "learning", "proficient", "mastered"
    last_attempted: Optional[str] = None
    attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "concept": self.concept,
            "mastery_percentage": self.mastery_percentage,
            "status": self.status,
            "last_attempted": self.last_attempted,
            "attempts": self.attempts
        }


@dataclass
class AssessmentResult:
    """Complete result of assessment generation."""
    topic_name: str
    assessments: List[Assessment]
    mastery_tracking: List[MasteryLevel]
    assessment_sequence: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "assessments": [a.to_dict() for a in self.assessments],
            "mastery_tracking": [m.to_dict() for m in self.mastery_tracking],
            "assessment_sequence": self.assessment_sequence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssessmentResult":
        """Create AssessmentResult from dictionary."""
        assessments = [
            Assessment(
                assessment_id=a.get("assessment_id", f"assess_{i+1}"),
                title=a.get("title", f"Assessment {i+1}"),
                description=a.get("description", ""),
                questions=[
                    AssessmentQuestion(
                        question_id=q.get("question_id", f"q{j+1}"),
                        question_text=q.get("question_text", ""),
                        question_type=q.get("question_type", "multiple_choice"),
                        correct_answer=q.get("correct_answer", ""),
                        explanation=q.get("explanation", ""),
                        difficulty=q.get("difficulty", "intermediate"),
                        points=q.get("points", 1),
                        learning_objective=q.get("learning_objective", ""),
                        distractors=q.get("distractors", [])
                    )
                    for j, q in enumerate(a.get("questions", []))
                ],
                total_points=a.get("total_points", 0),
                passing_score=a.get("passing_score", 70.0),
                time_limit=a.get("time_limit", "60 minutes"),
                prerequisites=a.get("prerequisites", [])
            )
            for i, a in enumerate(data.get("assessments", []))
        ]
        
        mastery_tracking = [
            MasteryLevel(
                concept=m.get("concept", ""),
                mastery_percentage=m.get("mastery_percentage", 0.0),
                status=m.get("status", "not_started"),
                last_attempted=m.get("last_attempted"),
                attempts=m.get("attempts", 0)
            )
            for m in data.get("mastery_tracking", [])
        ]
        
        return cls(
            topic_name=data.get("topic_name", "Unknown Topic"),
            assessments=assessments,
            mastery_tracking=mastery_tracking,
            assessment_sequence=data.get("assessment_sequence", [])
        )


class AssessmentGenerator:
    """
    Generates progressive assessments with mastery tracking.
    
    Creates:
    - Multiple assessment types (formative and summative)
    - Questions aligned to learning objectives
    - Mastery tracking for each concept
    - Progressive difficulty across assessments
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.3,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Assessment Generator.
        
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
        """Load the assessment generation prompt template."""
        prompt_path = Path(__file__).parent / "prompts" / "generate_assessments.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def _parse_assessment_response(self, response_content: str) -> AssessmentResult:
        """
        Parse the LLM response into an AssessmentResult.
        
        Args:
            response_content: Raw response content from the LLM.
        
        Returns:
            Parsed AssessmentResult.
        """
        try:
            assessment_data = json.loads(response_content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_content, re.DOTALL)
            if json_match:
                assessment_data = json.loads(json_match.group(1))
            else:
                assessment_data = self._extract_json_from_text(response_content)
        
        # Create assessments
        assessments = []
        for assessment in assessment_data.get("assessments", []):
            questions = [
                AssessmentQuestion(
                    question_id=q.get("question_id", f"q{len(questions)+1}"),
                    question_text=q.get("question_text", ""),
                    question_type=q.get("question_type", "multiple_choice"),
                    correct_answer=q.get("correct_answer", ""),
                    explanation=q.get("explanation", ""),
                    difficulty=q.get("difficulty", "intermediate"),
                    points=q.get("points", 1),
                    learning_objective=q.get("learning_objective", ""),
                    distractors=q.get("distractors", [])
                )
                for q in assessment.get("questions", [])
            ]
            
            assessments.append(Assessment(
                assessment_id=assessment.get("assessment_id", f"assess_{len(assessments)+1}"),
                title=assessment.get("title", f"Assessment {len(assessments) + 1}"),
                description=assessment.get("description", ""),
                questions=questions,
                total_points=assessment.get("total_points", sum(q.points for q in questions)),
                passing_score=assessment.get("passing_score", 70.0),
                time_limit=assessment.get("time_limit", "60 minutes"),
                prerequisites=assessment.get("prerequisites", [])
            ))
        
        # Create mastery tracking
        mastery_tracking = [
            MasteryLevel(
                concept=concept,
                mastery_percentage=0.0,
                status="not_started"
            )
            for concept in assessment_data.get("vital_concepts", [])
        ]
        
        # Determine assessment sequence
        assessment_sequence = [a.assessment_id for a in assessments]
        
        return AssessmentResult(
            topic_name=assessment_data.get("topic_name", "Unknown Topic"),
            assessments=assessments,
            mastery_tracking=mastery_tracking,
            assessment_sequence=assessment_sequence
        )
    
    def generate_assessments(
        self,
        topic_name: str,
        vital_concepts: List[str],
        lesson_plans: List[Dict[str, Any]],
        learning_objectives: List[str]
    ) -> AssessmentResult:
        """
        Generate progressive assessments from lesson plans.
        
        Args:
            topic_name: Name of the topic being assessed.
            vital_concepts: List of vital concepts to assess.
            lesson_plans: List of lesson plans to base assessments on.
            learning_objectives: List of learning objectives to assess.
        
        Returns:
            AssessmentResult containing generated assessments and mastery tracking.
        """
        # Build the prompt
        prompt = self._build_generation_prompt(
            topic_name, vital_concepts, lesson_plans, learning_objectives
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
        response_content = response.choices[0].message.content
        return self._parse_assessment_response(response_content)
    
    def _build_generation_prompt(
        self,
        topic_name: str,
        vital_concepts: List[str],
        lesson_plans: List[Dict[str, Any]],
        learning_objectives: List[str]
    ) -> str:
        """Build the assessment generation prompt."""
        lesson_plans_text = ""
        for lesson in lesson_plans:
            lesson_plans_text += f"\nLesson {lesson.get('lesson_number', 0)}: {lesson.get('title', 'Untitled')}\n"
            lesson_plans_text += f"Objectives: {', '.join(lesson.get('learning_objectives', []))}\n"
            lesson_plans_text += f"Key Concepts: {', '.join(lesson.get('key_concepts', []))}\n"
        
        vital_concepts_text = "\n\nVital Concepts to Assess:\n"
        vital_concepts_text += "\n".join([f"- {concept}" for concept in vital_concepts])
        
        learning_objectives_text = "\n\nLearning Objectives to Assess:\n"
        learning_objectives_text += "\n".join([f"- {objective}" for objective in learning_objectives])
        
        prompt = f"""You are an expert assessment designer creating progressive assessments.

Topic: {topic_name}

{vital_concepts_text}

{learning_objectives_text}

Lesson Plans:
{lesson_plans_text}

Create a comprehensive set of progressive assessments with the following requirements:

{{
    "assessments": [
        {{
            "assessment_id": "formative_1",
            "title": "Formative Assessment 1: Foundations",
            "description": "Check understanding of basic concepts",
            "questions": [
                {{
                    "question_id": "q1",
                    "question_text": "What is the primary purpose of X?",
                    "question_type": "multiple_choice",
                    "correct_answer": "To achieve Y",
                    "explanation": "X is designed to achieve Y as its primary function.",
                    "difficulty": "beginner",
                    "points": 1,
                    "learning_objective": "Understand X",
                    "distractors": [
                        "To prevent Y",
                        "To complicate Y",
                        "To ignore Y"
                    ]
                }}
            ],
            "total_points": 10,
            "passing_score": 70.0,
            "time_limit": "30 minutes",
            "prerequisites": []
        }},
        {{
            "assessment_id": "formative_2",
            "title": "Formative Assessment 2: Application",
            "description": "Test ability to apply concepts",
            "questions": [
                {{
                    "question_id": "q1",
                    "question_text": "How would you apply X to solve Y?",
                    "question_type": "short_answer",
                    "correct_answer": "Apply X by doing Y",
                    "explanation": "The correct application involves doing Y with X.",
                    "difficulty": "intermediate",
                    "points": 2,
                    "learning_objective": "Apply X",
                    "distractors": []
                }}
            ],
            "total_points": 20,
            "passing_score": 70.0,
            "time_limit": "45 minutes",
            "prerequisites": ["formative_1"]
        }}
    ]
}}

Requirements:
- Create 3-5 assessments that progress from formative to summative
- Include varied question types (multiple choice, true/false, short answer, essay)
- Align questions with specific learning objectives
- Progress from beginner to advanced difficulty
- Include clear explanations for correct answers
- Specify time limits and passing scores
- Include prerequisite relationships between assessments
- Ensure all vital concepts are assessed across all assessments

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
            "assessments": []
        }
    
    def save_assessments_to_file(
        self,
        result: AssessmentResult,
        output_path: Optional[str] = None
    ) -> str:
        """
        Save assessments to a file.
        
        Args:
            result: The assessment result to save.
            output_path: Optional path for output file.
        
        Returns:
            Path to the saved file.
        """
        from datetime import datetime
        
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path.cwd() / f"assessments_{result.topic_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        return str(output_path)
    
    def generate_assessment_summary(
        self,
        result: AssessmentResult
    ) -> str:
        """
        Generate a human-readable summary of the assessments.
        
        Args:
            result: The assessment result.
        
        Returns:
            Human-readable summary string.
        """
        summary = f"Assessment Summary: {result.topic_name}\n"
        summary += "=" * 60 + "\n\n"
        
        for assessment in result.assessments:
            summary += f"Assessment: {assessment.title}\n"
            summary += f"ID: {assessment.assessment_id}\n"
            summary += f"Total Points: {assessment.total_points}\n"
            summary += f"Passing Score: {assessment.passing_score}%\n"
            summary += f"Time Limit: {assessment.time_limit}\n"
            summary += f"Questions: {len(assessment.questions)}\n"
            summary += f"Prerequisites: {', '.join(assessment.prerequisites) if assessment.prerequisites else 'None'}\n"
            summary += "-" * 40 + "\n"
        
        summary += f"\nAssessment Sequence: {' -> '.join(result.assessment_sequence)}\n"
        summary += f"Mastery Concepts: {len(result.mastery_tracking)}\n"
        
        return summary