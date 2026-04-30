"""Learning Pipeline - Complete learning system using extraction components."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

from openai import OpenAI

from extraction.eighty_twenty.vital_extractor import VitalExtractor
from extraction.patterns.learning_patterns import PatternGenerator
from extraction.outline.outline_extractor import OutlineExtractor
from extraction.integration.orchestrator import LearningExtractionOrchestrator


@dataclass
class LearningPath:
    """Represents a complete learning path for a topic."""
    topic_name: str
    vital_concepts: List[str]
    learning_modules: List[Dict[str, Any]]
    compression_opportunities: List[Dict[str, Any]]
    encoding_strategies: List[Dict[str, Any]]
    estimated_total_time: str
    difficulty_level: str
    prerequisites: List[str]
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "vital_concepts": self.vital_concepts,
            "learning_modules": self.learning_modules,
            "compression_opportunities": self.compression_opportunities,
            "encoding_strategies": self.encoding_strategies,
            "estimated_total_time": self.estimated_total_time,
            "difficulty_level": self.difficulty_level,
            "prerequisites": self.prerequisites,
            "created_at": self.created_at
        }

    def to_markdown(self) -> str:
        """Convert to markdown format for documentation."""
        md = f"# Learning Path: {self.topic_name}\n\n"
        md += f"**Difficulty Level:** {self.difficulty_level}\n"
        md += f"**Estimated Time:** {self.estimated_total_time}\n"
        md += f"**Prerequisites:** {', '.join(self.prerequisites) if self.prerequisites else 'None'}\n\n"
        
        md += "## Vital Concepts (The 20% that gives 80% of results)\n\n"
        for i, concept in enumerate(self.vital_concepts, 1):
            md += f"{i}. {concept}\n"
        md += "\n"
        
        md += "## Learning Modules\n\n"
        for module in self.learning_modules:
            md += f"### Module {module['module_number']}: {module['title']}\n"
            md += f"**Time:** {module['estimated_time']}\n"
            md += "**Objectives:**\n"
            for obj in module['objectives']:
                md += f"- {obj}\n"
            md += "**Key Concepts:**\n"
            for concept in module['key_concepts']:
                md += f"- {concept}\n"
            md += "**Exercises:**\n"
            for exercise in module['exercises']:
                md += f"- {exercise}\n"
            md += "\n"
        
        if self.compression_opportunities:
            md += "## Compression Opportunities (Learn Faster)\n\n"
            for opp in self.compression_opportunities:
                md += f"### {opp['type']}\n"
                md += f"{opp['description']}\n"
                if opp.get('examples'):
                    md += "**Examples:**\n"
                    for example in opp['examples']:
                        md += f"- {example}\n"
                md += "\n"
        
        if self.encoding_strategies:
            md += "## Encoding Strategies (Learn Better)\n\n"
            for strategy in self.encoding_strategies:
                md += f"### {strategy['strategy_name']}\n"
                md += f"{strategy['description']}\n"
                md += f"**Implementation:** {strategy['implementation']}\n\n"
        
        return md


class LearningPipeline:
    """
    Complete learning pipeline that orchestrates extraction and creates learning paths.
    
    This pipeline:
    1. Extracts vital concepts using frequency analysis
    2. Identifies learning patterns using CAFE framework
    3. Creates structured learning outlines using DESS framework
    4. Generates comprehensive learning paths
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.5,
        config_path: Optional[str] = None
    ):
        """
        Initialize the learning pipeline.
        
        Args:
            api_key: OpenAI API key. If None, will try to read from OPENAI_API_KEY env var.
            model: LLM model to use for extraction.
            temperature: Temperature parameter for LLM responses.
            config_path: Path to learning profile configuration file.
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.config_path = config_path
        
        # Initialize extractors
        self.orchestrator = LearningExtractionOrchestrator(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
    
    def create_learning_path(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> LearningPath:
        """
        Create a complete learning path for a topic.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
        
        Returns:
            LearningPath containing all extracted information.
        """
        # Step 1: Extract vital concepts
        print(f"Extracting vital concepts for '{topic_name}'...")
        vital_result = self.orchestrator.extract_vital_concepts(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        vital_concepts = vital_result.vital_concepts
        
        # Step 2: Extract learning patterns
        print(f"Extracting learning patterns for '{topic_name}'...")
        pattern_result = self.orchestrator.extract_patterns(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        pattern_data = pattern_result.to_dict()
        
        # Step 3: Extract learning outline
        print(f"Creating learning outline for '{topic_name}'...")
        outline_result = self.orchestrator.extract_outline(
            topic_name=topic_name,
            content_summary=content_summary,
            vital_concepts=vital_concepts,
            pattern_extraction=pattern_data
        )
        outline_data = outline_result.to_dict()
        
        # Calculate total estimated time
        total_time = self._calculate_total_time(outline_data.get('learning_modules', []))
        
        # Determine difficulty level
        difficulty = self._determine_difficulty(outline_data.get('learning_modules', []))
        
        # Extract prerequisites
        prerequisites = self._extract_prerequisites(content_summary, outline_data)
        
        # Create learning path
        learning_path = LearningPath(
            topic_name=topic_name,
            vital_concepts=vital_concepts,
            learning_modules=outline_data.get('learning_modules', []),
            compression_opportunities=pattern_data.get('compression_opportunities', []),
            encoding_strategies=pattern_data.get('encoding_strategies', []),
            estimated_total_time=total_time,
            difficulty_level=difficulty,
            prerequisites=prerequisites,
            created_at=datetime.now().isoformat()
        )
        
        return learning_path
    
    def _calculate_total_time(self, modules: List[Dict[str, Any]]) -> str:
        """Calculate total estimated learning time."""
        total_hours = 0
        for module in modules:
            time_str = module.get('estimated_time', '1 hour')
            # Parse time string (e.g., "2 hours", "30 minutes")
            if 'hour' in time_str.lower():
                try:
                    hours = int(''.join(filter(str.isdigit, time_str)))
                    total_hours += hours
                except ValueError:
                    total_hours += 1
            elif 'minute' in time_str.lower():
                try:
                    minutes = int(''.join(filter(str.isdigit, time_str)))
                    total_hours += minutes / 60
                except ValueError:
                    pass
        
        if total_hours >= 24:
            days = total_hours / 24
            return f"{days:.1f} days"
        elif total_hours >= 1:
            return f"{total_hours:.1f} hours"
        else:
            minutes = int(total_hours * 60)
            return f"{minutes} minutes"
    
    def _determine_difficulty(self, modules: List[Dict[str, Any]]) -> str:
        """Determine overall difficulty level based on modules."""
        if not modules:
            return "Unknown"
        
        # Simple heuristic based on module count and complexity
        module_count = len(modules)
        
        if module_count <= 2:
            return "Beginner"
        elif module_count <= 4:
            return "Intermediate"
        else:
            return "Advanced"
    
    def _extract_prerequisites(self, content_summary: Dict[str, Any], outline_data: Dict[str, Any]) -> List[str]:
        """Extract prerequisite knowledge from content."""
        prerequisites = []
        
        # Look for prerequisite indicators in content
        summary_text = content_summary.get('summary_text', '').lower()
        
        if 'basic' in summary_text or 'fundamental' in summary_text:
            prerequisites.append('Basic understanding of the topic')
        
        if 'intermediate' in summary_text:
            prerequisites.append('Intermediate knowledge of related concepts')
        
        # Check for specific prerequisite mentions
        if 'requires' in summary_text or 'prerequisite' in summary_text:
            # Extract prerequisite information
            key_points = content_summary.get('key_points', [])
            for point in key_points:
                if 'require' in point.lower() or 'prerequisite' in point.lower():
                    prerequisites.append(point)
        
        return prerequisites if prerequisites else ['None']
    
    def save_learning_path(
        self,
        learning_path: LearningPath,
        output_dir: Optional[str] = None,
        format: str = "json"
    ) -> str:
        """
        Save learning path to a file.
        
        Args:
            learning_path: The learning path to save.
            output_dir: Directory to save files. Defaults to current directory.
            format: Output format ('json' or 'markdown').
        
        Returns:
            Path to the saved file.
        """
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path.cwd()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_topic_name = learning_path.topic_name.replace(' ', '_').replace('/', '_')
        
        if format == "json":
            output_path = output_dir / f"learning_path_{safe_topic_name}_{timestamp}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(learning_path.to_dict(), f, indent=2)
        elif format == "markdown":
            output_path = output_dir / f"learning_path_{safe_topic_name}_{timestamp}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(learning_path.to_markdown())
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'markdown'.")
        
        return str(output_path)
    
    def load_learning_path(self, path: str) -> LearningPath:
        """
        Load a learning path from a file.
        
        Args:
            path: Path to the learning path file.
        
        Returns:
            LearningPath loaded from the file.
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return LearningPath(
            topic_name=data['topic_name'],
            vital_concepts=data['vital_concepts'],
            learning_modules=data['learning_modules'],
            compression_opportunities=data['compression_opportunities'],
            encoding_strategies=data['encoding_strategies'],
            estimated_total_time=data['estimated_total_time'],
            difficulty_level=data['difficulty_level'],
            prerequisites=data['prerequisites'],
            created_at=data['created_at']
        )


def create_learning_pipeline(
    api_key: Optional[str] = None,
    model: str = "gpt-4o",
    temperature: float = 0.5,
    config_path: Optional[str] = None
) -> LearningPipeline:
    """
    Factory function to create a LearningPipeline instance.
    
    Args:
        api_key: OpenAI API key.
        model: LLM model to use.
        temperature: Temperature parameter.
        config_path: Path to configuration file.
    
    Returns:
        Configured LearningPipeline instance.
    """
    return LearningPipeline(
        api_key=api_key,
        model=model,
        temperature=temperature,
        config_path=config_path
    )
