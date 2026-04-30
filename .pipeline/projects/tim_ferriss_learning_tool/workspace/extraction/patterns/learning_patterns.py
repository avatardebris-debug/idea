"""Pattern Generator - Identifies learning patterns and structures using CAFE framework."""

import json
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from pathlib import Path

import yaml
from openai import OpenAI


@dataclass
class LearningPattern:
    """Represents a learning pattern extracted from content."""
    pattern_name: str
    pattern_type: str
    description: str
    evidence: List[str]
    learning_implication: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "pattern_name": self.pattern_name,
            "pattern_type": self.pattern_type,
            "description": self.description,
            "evidence": self.evidence,
            "learning_implication": self.learning_implication
        }


@dataclass
class CompressionOpportunity:
    """Represents a compression opportunity for accelerated learning."""
    type: str
    description: str
    examples: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.type,
            "description": self.description,
            "examples": self.examples
        }


@dataclass
class EncodingStrategy:
    """Represents an encoding strategy for effective learning."""
    strategy_name: str
    strategy_type: str
    description: str
    implementation: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "strategy_name": self.strategy_name,
            "strategy_type": self.strategy_type,
            "description": self.description,
            "implementation": self.implementation
        }


@dataclass
class PatternExtractionResult:
    """Complete result of pattern extraction."""
    topic_name: str
    learning_patterns: List[LearningPattern]
    compression_opportunities: List[CompressionOpportunity]
    frequency_patterns: Dict[str, Any]
    encoding_strategies: List[EncodingStrategy]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "topic_name": self.topic_name,
            "learning_patterns": [lp.to_dict() for lp in self.learning_patterns],
            "compression_opportunities": [co.to_dict() for co in self.compression_opportunities],
            "frequency_patterns": self.frequency_patterns,
            "encoding_strategies": [es.to_dict() for es in self.encoding_strategies]
        }


class PatternGenerator:
    """
    Generates learning patterns from content summaries using the CAFE framework.
    
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
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> PatternExtractionResult:
        """
        Extract learning patterns from content summaries.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content including key points.
            source_summaries: Optional list of source summaries for cross-referencing.
        
        Returns:
            PatternExtractionResult containing extracted patterns and strategies.
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
        
        # Create result object
        learning_patterns = [
            LearningPattern(
                pattern_name=pattern.get("pattern_name", ""),
                pattern_type=pattern.get("pattern_type", ""),
                description=pattern.get("description", ""),
                evidence=pattern.get("evidence", []),
                learning_implication=pattern.get("learning_implication", "")
            )
            for pattern in extraction_data.get("learning_patterns", [])
        ]
        
        compression_opportunities = [
            CompressionOpportunity(
                type=opp.get("type", ""),
                description=opp.get("description", ""),
                examples=opp.get("examples", [])
            )
            for opp in extraction_data.get("compression_opportunities", [])
        ]
        
        frequency_patterns = extraction_data.get("frequency_patterns", {
            "daily_practices": [],
            "weekly_reviews": [],
            "milestone_checkpoints": [],
            "spaced_repetition_schedule": {
                "review_intervals": [],
                "practice_schedule": []
            }
        })
        
        encoding_strategies = [
            EncodingStrategy(
                strategy_name=strategy.get("strategy_name", ""),
                strategy_type=strategy.get("strategy_type", ""),
                description=strategy.get("description", ""),
                implementation=strategy.get("implementation", "")
            )
            for strategy in extraction_data.get("encoding_strategies", [])
        ]
        
        return PatternExtractionResult(
            topic_name=topic_name,
            learning_patterns=learning_patterns,
            compression_opportunities=compression_opportunities,
            frequency_patterns=frequency_patterns,
            encoding_strategies=encoding_strategies
        )
    
    def _build_extraction_prompt(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build the pattern extraction prompt."""
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

Please extract learning patterns following the output requirements.
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
            "learning_patterns": [],
            "compression_opportunities": [],
            "frequency_patterns": {
                "daily_practices": [],
                "weekly_reviews": [],
                "milestone_checkpoints": [],
                "spaced_repetition_schedule": {
                    "review_intervals": [],
                    "practice_schedule": []
                }
            },
            "encoding_strategies": []
        }
    
    def analyze_compression_opportunities(
        self,
        content_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze content for compression opportunities.
        
        Args:
            content_summary: The content summary to analyze.
        
        Returns:
            List of compression opportunities.
        """
        opportunities = []
        
        # Look for common patterns that indicate compression opportunities
        summary_text = content_summary.get("summary_text", "").lower()
        key_points = content_summary.get("key_points", [])
        
        # Check for shortcut indicators
        shortcut_keywords = ["shortcut", "quick", "fast", "efficient", "direct", "simple"]
        for keyword in shortcut_keywords:
            if keyword in summary_text:
                opportunities.append({
                    "type": "shortcut_method",
                    "description": f"Content mentions '{keyword}' approaches",
                    "examples": []
                })
        
        # Check for concept clustering
        if len(key_points) > 5:
            opportunities.append({
                "type": "concept_cluster",
                "description": "Multiple related concepts that can be learned together",
                "examples": key_points[:5]
            })
        
        return opportunities
    
    def analyze_frequency_patterns(
        self,
        content_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze content for frequency patterns.
        
        Args:
            content_summary: The content summary to analyze.
        
        Returns:
            Dictionary with frequency patterns.
        """
        patterns = {
            "daily_practices": [],
            "weekly_reviews": [],
            "milestone_checkpoints": [],
            "spaced_repetition_schedule": {
                "review_intervals": ["1 day", "3 days", "1 week", "2 weeks", "1 month"],
                "practice_schedule": ["Daily coding", "Weekly projects", "Monthly reviews"]
            }
        }
        
        # Look for frequency indicators
        summary_text = content_summary.get("summary_text", "").lower()
        
        if "daily" in summary_text or "every day" in summary_text:
            patterns["daily_practices"].append("Daily practice recommended")
        
        if "weekly" in summary_text or "each week" in summary_text:
            patterns["weekly_reviews"].append("Weekly review recommended")
        
        # Check for milestone indicators
        milestone_keywords = ["complete", "master", "achieve", "finish", "reach"]
        for keyword in milestone_keywords:
            if keyword in summary_text:
                patterns["milestone_checkpoints"].append(f"Track progress on {keyword} milestones")
                break
        
        return patterns
    
    def analyze_encoding_strategies(
        self,
        content_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze content for encoding strategies.
        
        Args:
            content_summary: The content summary to analyze.
        
        Returns:
            List of encoding strategies.
        """
        strategies = []
        
        # Look for mental model indicators
        summary_text = content_summary.get("summary_text", "").lower()
        
        if "model" in summary_text or "framework" in summary_text:
            strategies.append({
                "strategy_name": "Mental Model",
                "strategy_type": "mental_model",
                "description": "Use conceptual frameworks to organize knowledge",
                "implementation": "Create or adopt existing mental models for the topic"
            })
        
        # Look for practice indicators
        if "practice" in summary_text or "exercise" in summary_text:
            strategies.append({
                "strategy_name": "Active Practice",
                "strategy_type": "practice_method",
                "description": "Learn by doing rather than just reading",
                "implementation": "Set aside dedicated practice time for hands-on learning"
            })
        
        # Look for memory technique indicators
        if "memory" in summary_text or "mnemonic" in summary_text:
            strategies.append({
                "strategy_name": "Memory Techniques",
                "strategy_type": "memory_technique",
                "description": "Use mnemonic devices to improve retention",
                "implementation": "Create or use existing mnemonics for key concepts"
            })
        
        return strategies
    
    def save_extraction_to_file(
        self,
        result: PatternExtractionResult,
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
            output_path = Path.cwd() / f"pattern_extraction_{result.topic_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        return str(output_path)
