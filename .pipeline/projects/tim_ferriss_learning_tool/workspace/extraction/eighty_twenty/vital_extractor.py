"""Vital Extractor - Identifies the vital 20% of content using frequency analysis and semantic importance."""

import json
import os
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path

import yaml
from openai import OpenAI


@dataclass
class ConceptRelationship:
    """Represents a relationship between concepts."""
    concept: str
    prerequisites: List[str] = field(default_factory=list)
    builds_upon: List[str] = field(default_factory=list)


@dataclass
class VitalConcept:
    """Represents a vital concept extracted from content."""
    name: str
    why_vital: str
    impact_score: int
    category: str  # "must-know" or "nice-to-know"
    connections: List[str] = field(default_factory=list)
    practical_applications: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "why_vital": self.why_vital,
            "impact_score": self.impact_score,
            "category": self.category,
            "connections": self.connections,
            "practical_applications": self.practical_applications
        }


@dataclass
class VitalExtractionResult:
    """Complete result of vital concept extraction."""
    topic_name: str
    vital_concepts: List[VitalConcept]
    concept_relationships: List[ConceptRelationship]
    learning_priority: Dict[str, List[str]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "vital_concepts": [vc.to_dict() for vc in self.vital_concepts],
            "concept_relationships": [asdict(cr) for cr in self.concept_relationships],
            "learning_priority": self.learning_priority
        }


class VitalExtractor:
    """
    Extracts vital concepts from content summaries using frequency analysis
    and semantic importance scoring.
    
    Uses Tim Ferriss's Pareto Principle to identify the 20% of concepts
    that deliver 80% of learning results.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.5,
        config_path: Optional[str] = None
    ):
        """
        Initialize the Vital Extractor.
        
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
        """Load the vital extraction prompt template."""
        prompt_path = Path(__file__).parent / "prompts" / "extract_vital.md"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def extract_vital_concepts(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> VitalExtractionResult:
        """
        Extract vital concepts from content summaries.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content including key points.
            source_summaries: Optional list of source summaries for cross-referencing.
        
        Returns:
            VitalExtractionResult containing extracted vital concepts and relationships.
        """
        # Build the prompt
        prompt = self._build_extraction_prompt(topic_name, content_summary, source_summaries)
        
        # Call LLM API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=2048
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
        
        # Create result object - handle both dict and string concepts
        vital_concepts = []
        for concept in extraction_data.get("vital_concepts", []):
            if isinstance(concept, dict):
                vital_concepts.append(VitalConcept(
                    name=concept.get("name", ""),
                    why_vital=concept.get("why_vital", ""),
                    impact_score=concept.get("impact_score", 5),
                    category=concept.get("category", "must-know"),
                    connections=concept.get("connections", []),
                    practical_applications=concept.get("practical_applications", [])
                ))
            elif isinstance(concept, str):
                # If concept is a string, use it as the name with defaults
                vital_concepts.append(VitalConcept(
                    name=concept,
                    why_vital="Extracted from content",
                    impact_score=5,
                    category="must-know",
                    connections=[],
                    practical_applications=[]
                ))
        
        concept_relationships = [
            ConceptRelationship(
                concept=rel.get("concept", ""),
                prerequisites=rel.get("prerequisites", []),
                builds_upon=rel.get("builds_upon", [])
            )
            for rel in extraction_data.get("concept_relationships", [])
        ]
        
        learning_priority = extraction_data.get("learning_priority", {
            "phase_1_foundation": [],
            "phase_2_core": [],
            "phase_3_advanced": []
        })
        
        return VitalExtractionResult(
            topic_name=topic_name,
            vital_concepts=vital_concepts,
            concept_relationships=concept_relationships,
            learning_priority=learning_priority
        )
    
    def _build_extraction_prompt(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build the extraction prompt."""
        summary_text = content_summary.get("summary_text", "")
        key_points = content_summary.get("key_points", [])
        
        sources_text = ""
        if source_summaries:
            sources_text = "\n\nSource Summaries:\n"
            for i, source in enumerate(source_summaries, 1):
                sources_text += f"\n--- Source {i}: {source.get('title', 'Unknown')} ---\n"
                sources_text += f"Key Points: {', '.join(source.get('key_points', []))}\n"
        
        prompt = f"""
Topic Name: {topic_name}

Content Summary:
{summary_text}

Key Points:
{chr(10).join([f"- {point}" for point in key_points])}

{sources_text}

Please extract the vital concepts following the output requirements.
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
            "vital_concepts": [],
            "concept_relationships": [],
            "learning_priority": {
                "phase_1_foundation": [],
                "phase_2_core": [],
                "phase_3_advanced": []
            }
        }
    
    def analyze_frequency(
        self,
        key_points: List[str],
        source_summaries: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Analyze frequency of concepts across sources using multiple techniques.
        
        Args:
            key_points: List of key points from all sources.
            source_summaries: List of source summaries.
        
        Returns:
            Dictionary mapping concepts to their frequency counts.
        """
        frequency = {}
        
        # Combine all key points
        all_points = []
        for summary in source_summaries:
            all_points.extend(summary.get("key_points", []))
        all_points.extend(key_points)
        
        # Enhanced frequency analysis
        for point in all_points:
            # Extract potential concepts using multiple patterns
            # 1. Capitalized words (proper nouns, technical terms)
            words = point.split()
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 3:
                    frequency[word] = frequency.get(word, 0) + 1
            
            # 2. Multi-word concepts (look for patterns like "X and Y", "X of Y")
            patterns = [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b',  # Multi-word capitalized phrases
                r'\b([A-Z][a-z]+(?:\s+[a-z]+)+)\b',  # Mixed case phrases
                r'\b([a-z]+(?:\s+[a-z]+)+)\b',  # Lowercase phrases
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, point)
                for match in matches:
                    frequency[match] = frequency.get(match, 0) + 1
        
        return frequency
    
    def calculate_semantic_importance(
        self,
        concept: str,
        content_summary: Dict[str, Any],
        frequency: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Calculate semantic importance of a concept.
        
        Args:
            concept: The concept to analyze.
            content_summary: The content summary for context.
            frequency: Frequency dictionary from analyze_frequency.
        
        Returns:
            Dictionary with importance metrics.
        """
        importance = {
            "frequency_score": 0,
            "centrality_score": 0,
            "impact_score": 0,
            "total_score": 0
        }
        
        # Frequency score (normalized)
        max_freq = max(frequency.values()) if frequency else 1
        importance["frequency_score"] = frequency.get(concept, 0) / max_freq if max_freq > 0 else 0
        
        # Centrality score (how often concept is mentioned in context of other concepts)
        content_text = content_summary.get("summary_text", "") + " ".join(
            content_summary.get("key_points", [])
        )
        centrality_count = content_text.lower().count(concept.lower())
        importance["centrality_score"] = centrality_count / max(1, len(content_text.split())) * 10
        
        # Impact score (based on keywords indicating importance)
        impact_keywords = ["essential", "critical", "fundamental", "core", "vital", "key", "important", "must"]
        impact_count = sum(1 for keyword in impact_keywords if keyword in content_text.lower())
        importance["impact_score"] = min(10, impact_count * 2)
        
        # Total score (weighted combination)
        importance["total_score"] = (
            importance["frequency_score"] * 3 +
            importance["centrality_score"] * 4 +
            importance["impact_score"] * 3
        )
        
        return importance
    
    def rank_concepts(
        self,
        concepts: List[str],
        content_summary: Dict[str, Any],
        frequency: Dict[str, int]
    ) -> List[Tuple[str, float]]:
        """
        Rank concepts by importance.
        
        Args:
            concepts: List of concepts to rank.
            content_summary: The content summary for context.
            frequency: Frequency dictionary from analyze_frequency.
        
        Returns:
            List of (concept, score) tuples sorted by score descending.
        """
        scored_concepts = []
        
        for concept in concepts:
            importance = self.calculate_semantic_importance(concept, content_summary, frequency)
            scored_concepts.append((concept, importance["total_score"]))
        
        # Sort by score descending
        scored_concepts.sort(key=lambda x: x[1], reverse=True)
        
        return scored_concepts
    
    def identify_vital_20(
        self,
        ranked_concepts: List[Tuple[str, float]],
        total_concepts: int
    ) -> List[str]:
        """
        Identify the vital 20% of concepts.
        
        Args:
            ranked_concepts: List of (concept, score) tuples.
            total_concepts: Total number of concepts.
        
        Returns:
            List of vital concepts.
        """
        # Take top 20% (minimum 1 concept)
        num_vital = max(1, int(total_concepts * 0.2))
        return [concept for concept, _ in ranked_concepts[:num_vital]]
    
    def save_extraction_to_file(
        self,
        result: VitalExtractionResult,
        output_path: Optional[str] = None
    ) -> str:
        """
        Save extraction result to a file.
        
        Args:
            result: The extraction result to save.
            output_path: Optional path for output file.
        
        Returns:
            Path to the saved file.
        """
        from datetime import datetime
        
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path.cwd() / f"vital_extraction_{result.topic_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        return str(output_path)
