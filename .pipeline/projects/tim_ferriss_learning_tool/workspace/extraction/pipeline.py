"""Main orchestrator for the 80/20 learning extraction pipeline."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import yaml
from datetime import datetime

from .eighty_twenty.vital_extractor import VitalExtractor
from .patterns.learning_patterns import PatternGenerator
from .outline.outline_generator import OutlineGenerator


@dataclass
class ExtractionPipelineResult:
    """Complete result of the 80/20 extraction pipeline."""
    topic_name: str
    content_summary: Dict[str, Any]
    vital_concepts: List[str]
    pattern_extraction: Dict[str, Any]
    learning_outline: Dict[str, Any]
    extraction_timestamp: str
    vital_extraction: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "topic_name": self.topic_name,
            "content_summary": self.content_summary,
            "vital_concepts": self.vital_concepts,
            "pattern_extraction": self.pattern_extraction,
            "learning_outline": self.learning_outline,
            "extraction_timestamp": self.extraction_timestamp
        }
        if self.vital_extraction:
            result["vital_extraction"] = self.vital_extraction
        return result


class ExtractionPipeline:
    """
    Orchestrates the complete 80/20 learning extraction pipeline.
    
    This pipeline:
    1. Extracts vital concepts using frequency analysis
    2. Identifies learning patterns using CAFE framework
    3. Creates structured learning outlines using DESS framework
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.5,
        config_path: Optional[str] = None
    ):
        """
        Initialize the extraction pipeline.
        
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
        self.vital_extractor = VitalExtractor(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
        
        self.pattern_generator = PatternGenerator(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
        
        self.outline_generator = OutlineGenerator(
            api_key=api_key,
            model=model,
            temperature=temperature,
            config_path=config_path
        )
    
    def run_extraction(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None
    ) -> ExtractionPipelineResult:
        """
        Run the complete extraction pipeline.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
        
        Returns:
            ExtractionPipelineResult containing all extracted information.
        """
        # Step 1: Extract vital concepts
        print(f"Extracting vital concepts for '{topic_name}'...")
        vital_result = self.vital_extractor.extract_vital_concepts(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        vital_concepts = vital_result.vital_concepts
        
        # Step 2: Extract learning patterns
        print(f"Extracting learning patterns for '{topic_name}'...")
        pattern_result = self.pattern_generator.extract_patterns(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        pattern_data = pattern_result.to_dict()
        
        # Step 3: Extract learning outline
        print(f"Creating learning outline for '{topic_name}'...")
        outline_result = self.outline_generator.extract_outline(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        outline_data = outline_result.to_dict()
        
        # Compile results
        result = ExtractionPipelineResult(
            topic_name=topic_name,
            content_summary=content_summary,
            vital_concepts=vital_concepts,
            pattern_extraction=pattern_data,
            learning_outline=outline_data,
            extraction_timestamp=datetime.now().isoformat(),
            vital_extraction=vital_result.to_dict()
        )
        
        return result
    
    def save_results(
        self,
        result: ExtractionPipelineResult,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Save extraction results to files.
        
        Args:
            result: The extraction result to save.
            output_dir: Directory to save files. Defaults to current directory.
        
        Returns:
            Dictionary mapping file types to their paths.
        """
        from datetime import datetime
        
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path.cwd()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_topic_name = result.topic_name.replace(' ', '_').replace('/', '_')
        
        # Save complete result
        result_path = output_dir / f"extraction_result_{safe_topic_name}_{timestamp}.json"
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        # Save vital concepts separately
        vital_path = output_dir / f"vital_concepts_{safe_topic_name}_{timestamp}.json"
        with open(vital_path, 'w', encoding='utf-8') as f:
            json.dump({
                "topic_name": result.topic_name,
                "vital_concepts": result.vital_concepts,
                "extraction_timestamp": result.extraction_timestamp
            }, f, indent=2)
        
        # Save pattern extraction
        pattern_path = output_dir / f"patterns_{safe_topic_name}_{timestamp}.json"
        with open(pattern_path, 'w', encoding='utf-8') as f:
            json.dump(result.pattern_extraction, f, indent=2)
        
        # Save learning outline
        outline_path = output_dir / f"outline_{safe_topic_name}_{timestamp}.json"
        with open(outline_path, 'w', encoding='utf-8') as f:
            json.dump(result.learning_outline, f, indent=2)
        
        return {
            "result": str(result_path),
            "vital_concepts": str(vital_path),
            "patterns": str(pattern_path),
            "outline": str(outline_path)
        }
    
    def extract_all(
        self,
        topic_name: str,
        content_summary: Dict[str, Any],
        source_summaries: Optional[List[Dict[str, Any]]] = None,
        vital_concepts: Optional[List[str]] = None
    ) -> ExtractionPipelineResult:
        """
        Run the complete extraction pipeline.
        
        Args:
            topic_name: Name of the topic being analyzed.
            content_summary: Structured summary of the content.
            source_summaries: Optional list of source summaries.
            vital_concepts: Optional list of vital concepts to prioritize.
        
        Returns:
            ExtractionPipelineResult containing all extracted information.
        """
        # Step 1: Extract vital concepts
        vital_result = self.vital_extractor.extract_vital_concepts(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries
        )
        
        # Step 2: Extract patterns
        pattern_result = self.pattern_generator.extract_patterns(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries,
            vital_concepts=vital_concepts or [c.name for c in vital_result.vital_concepts]
        )
        
        # Step 3: Extract learning outline
        outline_result = self.outline_generator.extract_outline(
            topic_name=topic_name,
            content_summary=content_summary,
            source_summaries=source_summaries,
            vital_concepts=vital_concepts or [c.name for c in vital_result.vital_concepts]
        )
        
        # Compile results
        return ExtractionPipelineResult(
            topic_name=topic_name,
            content_summary=content_summary,
            vital_concepts=[c.name for c in vital_result.vital_concepts],
            pattern_extraction=pattern_result.to_dict(),
            learning_outline=outline_result.to_dict(),
            extraction_timestamp=datetime.now().isoformat(),
            vital_extraction=vital_result.to_dict()
        )
    
    def load_extraction_result(self, result_path: str) -> ExtractionPipelineResult:
        """
        Load an extraction result from a file.
        
        Args:
            result_path: Path to the result file.
        
        Returns:
            ExtractionPipelineResult loaded from the file.
        """
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return ExtractionPipelineResult(
            topic_name=data["topic_name"],
            content_summary=data["content_summary"],
            vital_concepts=data["vital_concepts"],
            pattern_extraction=data["pattern_extraction"],
            learning_outline=data["learning_outline"],
            extraction_timestamp=data["extraction_timestamp"],
            vital_extraction=data.get("vital_extraction")
        )


def create_pipeline(
    api_key: Optional[str] = None,
    model: str = "gpt-4o",
    temperature: float = 0.5,
    config_path: Optional[str] = None
) -> ExtractionPipeline:
    """
    Factory function to create an ExtractionPipeline instance.
    
    Args:
        api_key: OpenAI API key.
        model: LLM model to use.
        temperature: Temperature parameter.
        config_path: Path to configuration file.
    
    Returns:
        Configured ExtractionPipeline instance.
    """
    return ExtractionPipeline(
        api_key=api_key,
        model=model,
        temperature=temperature,
        config_path=config_path
    )
