"""
Detail Filler Module.

This module provides functionality for enriching generated content with specific
details, examples, case studies, statistics, and practical applications.
"""

import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .models import StyleProfile


@dataclass
class DetailEnrichment:
    """Represents a detail enrichment added to content."""
    detail_type: str  # 'example', 'case_study', 'statistic', 'application', 'analogy'
    enriched_content: str
    relevance_score: float  # 0-1, how relevant to the context
    source: Optional[str] = None
    example_count: int = 0
    research_integration_score: float = 0.0
    transition_integration_score: float = 0.0
    enrichment_score: float = 0.0


class DetailFiller:
    """
    Enriches content with specific details, examples, and supporting material.
    
    This class adds concrete examples, case studies, statistics, and practical
    applications to expand content and make it more engaging and informative.
    """
    
    # Example templates for different topics
    EXAMPLE_TEMPLATES = {
        "technology": [
            "For example, modern cloud computing platforms like AWS and Azure have revolutionized how businesses scale their operations.",
            "Consider how machine learning algorithms now power everything from recommendation systems to autonomous vehicles.",
            "A practical application can be seen in how healthcare providers use AI to diagnose diseases with unprecedented accuracy.",
        ],
        "business": [
            "For instance, companies like Netflix have transformed entire industries through innovative business models.",
            "Consider how agile methodologies have become the standard for software development teams worldwide.",
            "A real-world example is how Amazon's logistics network has set new standards for e-commerce delivery.",
        ],
        "science": [
            "For example, recent breakthroughs in CRISPR technology have opened new possibilities for genetic medicine.",
            "Consider how climate research has revealed the accelerating impacts of global warming on ecosystems.",
            "A practical application is how renewable energy technologies are becoming increasingly cost-competitive.",
        ],
        "general": [
            "For instance, this principle can be observed in everyday situations where people make decisions based on available information.",
            "Consider how this concept applies across different contexts, from personal relationships to organizational dynamics.",
            "A practical example would be seeing this pattern emerge in real-world scenarios and case studies.",
        ],
    }
    
    # Case study templates
    CASE_STUDY_TEMPLATES = [
        "A compelling case study involves {subject}, where {outcome} was achieved through {method}. This demonstrates the practical application of the principles we've discussed.",
        "Consider the case of {subject}, which illustrates how {concept} can lead to {outcome}. The lessons learned from this example are directly applicable to our current discussion.",
        "One notable example is {subject}, where implementing {method} resulted in {outcome}. This case study provides valuable insights into the effectiveness of these approaches.",
    ]
    
    # Statistic templates
    STATISTIC_TEMPLATES = [
        "Research indicates that {percentage}% of {population} experience {phenomenon}, highlighting the widespread nature of this issue.",
        "Studies have shown that {metric} has increased by {percentage}% over the past {time_period}, demonstrating a clear trend.",
        "According to recent data, {statistic} reveals important patterns about {topic}.",
    ]
    
    # Application templates
    APPLICATION_TEMPLATES = [
        "In practice, this means that {practical_implication}. Understanding this application is crucial for effective implementation.",
        "The practical implications of this concept include {application}. These applications are particularly relevant in {context}.",
        "When applied in real-world scenarios, this principle leads to {outcome}. This practical application demonstrates its value.",
    ]
    
    # Analogy templates
    ANALOGY_TEMPLATES = [
        "This concept is similar to {analogy}, where {analogy_explanation}. Just as {analogy_comparison}, this principle operates in a comparable way.",
        "Think of this as {analogy}. Much like {analogy_explanation}, the underlying mechanisms share important similarities.",
        "An apt analogy would be {analogy}, which helps illustrate how {concept} functions in practice.",
    ]
    
    def __init__(self, style_profile: Optional[StyleProfile] = None):
        """
        Initialize the DetailFiller.
        
        Args:
            style_profile: Optional style profile for consistent voice
        """
        self.style_profile = style_profile or StyleProfile()
        self._detail_cache: Dict[str, List[DetailEnrichment]] = {}
    
    def enrich_content(
        self,
        content: str,
        outline_section: Dict[str, Any],
        style_profile: Optional[StyleProfile] = None,
        research_context: Optional[Dict[str, Any]] = None,
        transitions: Optional[Dict[str, str]] = None,
        target_word_count: Optional[int] = None
    ) -> DetailEnrichment:
        """
        Enrich content with specific details, examples, and supporting material.
        
        This method adds concrete examples, case studies, statistics, and practical
        applications to expand content and make it more engaging.
        
        Args:
            content: Original content to enrich
            outline_section: Outline section for context
            style_profile: Style profile for consistent voice
            research_context: Research context to incorporate
            transitions: Transition information for smooth flow
            target_word_count: Target word count for the enriched content
            
        Returns:
            DetailEnrichment object with enriched content and metrics
        """
        # Update style profile if provided
        if style_profile:
            self.style_profile = style_profile
        
        enriched_content = content
        example_count = 0
        research_integration_score = 0.0
        transition_integration_score = 0.0
        
        # Extract section title from outline
        section_title = outline_section.get("section_title", "Section")
        
        research_context = research_context or {}
        transitions = transitions or {}
        
        # Add examples based on style preferences
        preferred_examples = self.style_profile.preferred_examples if self.style_profile else ["real-world", "hypothetical"]
        if preferred_examples:
            enriched_content, example_count = self._add_examples(enriched_content, preferred_examples)
        
        # Add case studies if available in research context
        if research_context.get("case_studies"):
            enriched_content = self._add_case_studies(enriched_content, research_context["case_studies"])
            research_integration_score += 0.3
        
        # Add statistics if available in research context
        if research_context.get("statistics"):
            enriched_content = self._add_statistics(enriched_content, research_context["statistics"])
            research_integration_score += 0.3
        
        # Add practical applications
        enriched_content = self._add_applications(enriched_content, section_title)
        
        # Add analogies for complex concepts
        enriched_content = self._add_analogies(enriched_content, [section_title])
        
        # Integrate transitions if provided
        if transitions:
            enriched_content = self._integrate_transitions(enriched_content, transitions)
            transition_integration_score = 0.5
        
        # Ensure smooth integration
        enriched_content = self._ensure_smooth_integration(enriched_content)
        
        # Ensure minimum word count is met
        enriched_content = self._ensure_minimum_word_count(enriched_content, target_word_count or 200)
        
        # Calculate enrichment score
        enrichment_score = min(1.0, (example_count * 0.2) + research_integration_score + transition_integration_score)
        
        return DetailEnrichment(
            detail_type="comprehensive",
            enriched_content=enriched_content,
            relevance_score=enrichment_score,
            source=section_title,
            example_count=example_count,
            research_integration_score=research_integration_score,
            transition_integration_score=transition_integration_score
        )
    
    def _add_examples(self, content: str, examples: List[str]) -> tuple:
        """Add examples to the content and return count."""
        if not examples:
            return content, 0
        
        # Select example template based on topic
        template = random.choice(self.EXAMPLE_TEMPLATES.get("general", self.EXAMPLE_TEMPLATES["general"]))
        
        # Create example insertion points
        insertion_points = self._find_insertion_points(content, examples)
        
        enriched = content
        count = 0
        for i, point in enumerate(insertion_points):
            if i < len(examples):
                example_text = f"{template} {examples[i]}. "
                enriched = self._insert_at_point(enriched, point, example_text)
                count += 1
        
        return enriched, count
    
    def _add_case_studies(self, content: str, case_studies: List[Dict[str, Any]]) -> str:
        """Add case studies to the content."""
        if not case_studies:
            return content
        
        template = random.choice(self.CASE_STUDY_TEMPLATES)
        
        for case_study in case_studies[:2]:  # Limit to 2 case studies
            subject = case_study.get("subject", "the subject")
            outcome = case_study.get("outcome", "significant results")
            method = case_study.get("method", "the implemented approach")
            
            case_study_text = template.format(
                subject=subject,
                outcome=outcome,
                method=method
            )
            
            # Find a good insertion point
            insertion_point = self._find_insertion_point(content)
            content = self._insert_at_point(content, insertion_point, case_study_text)
        
        return content
    
    def _add_statistics(self, content: str, statistics: List[Dict[str, Any]]) -> str:
        """Add statistics to the content."""
        if not statistics:
            return content
        
        template = random.choice(self.STATISTIC_TEMPLATES)
        
        for stat in statistics[:2]:  # Limit to 2 statistics
            percentage = stat.get("percentage", "a significant")
            population = stat.get("population", "people")
            phenomenon = stat.get("phenomenon", "this phenomenon")
            metric = stat.get("metric", "the metric")
            time_period = stat.get("time_period", "recent years")
            statistic = stat.get("statistic", "the data")
            topic = stat.get("topic", "the subject")
            
            stat_text = template.format(
                percentage=percentage,
                population=population,
                phenomenon=phenomenon,
                metric=metric,
                time_period=time_period,
                statistic=statistic,
                topic=topic
            )
            
            # Find a good insertion point
            insertion_point = self._find_insertion_point(content)
            content = self._insert_at_point(content, insertion_point, stat_text)
        
        return content
    
    def _add_applications(self, content: str, section_title: str) -> str:
        """Add practical applications to the content."""
        template = random.choice(self.APPLICATION_TEMPLATES)
        
        application_text = template.format(
            practical_implication=f"understanding {section_title.lower()} becomes essential",
            application=f"applying these principles in practice",
            context="various real-world scenarios",
            outcome="tangible improvements and results"
        )
        
        # Find a good insertion point
        insertion_point = self._find_insertion_point(content)
        content = self._insert_at_point(content, insertion_point, application_text)
        
        return content
    
    def _add_analogies(self, content: str, key_points: List[str]) -> str:
        """Add analogies to help explain complex concepts."""
        if not key_points:
            return content
        
        template = random.choice(self.ANALOGY_TEMPLATES)
        
        # Create analogy based on key point
        key_point = key_points[0] if key_points else "the concept"
        
        analogy_text = template.format(
            analogy="building a house",
            analogy_explanation="you need a solid foundation before adding structure",
            concept=key_point,
            analogy_comparison="you need to understand fundamentals before applying advanced techniques"
        )
        
        # Find a good insertion point
        insertion_point = self._find_insertion_point(content)
        content = self._insert_at_point(content, insertion_point, analogy_text)
        
        return content
    
    def _find_insertion_points(self, content: str, examples: List[str]) -> List[int]:
        """Find good insertion points for examples in the content."""
        points = []
        sentences = content.split('. ')
        
        # Find sentences that could benefit from examples
        for i, sentence in enumerate(sentences):
            if len(points) >= len(examples):
                break
            
            # Look for sentences that discuss concepts or principles
            if any(keyword in sentence.lower() for keyword in ['concept', 'principle', 'idea', 'theory', 'method']):
                points.append(i)
        
        # If not enough points found, use available sentences
        while len(points) < len(examples) and len(sentences) > 2:
            for i, sentence in enumerate(sentences):
                if i not in points and i > 0 and i < len(sentences) - 1:
                    points.append(i)
                    if len(points) >= len(examples):
                        break
        
        return points
    
    def _find_insertion_point(self, content: str) -> int:
        """Find a good insertion point in the content."""
        sentences = content.split('. ')
        
        # Prefer middle sentences for better flow
        if len(sentences) > 3:
            return len(sentences) // 2
        
        return 1
    
    def _insert_at_point(self, content: str, point: int, text: str) -> str:
        """Insert text at a specific point in the content."""
        sentences = content.split('. ')
        
        if point < 0 or point >= len(sentences):
            # If invalid point, append to end
            return content + ' ' + text
        
        # Insert at the specified point
        sentences.insert(point, text)
        
        # Rejoin
        return '. '.join(sentences)
    
    def _integrate_transitions(self, content: str, transitions: Dict[str, str]) -> str:
        """Integrate transition information into the content."""
        if not transitions:
            return content
        
        # Add transition from previous section
        if transitions.get("previous_section"):
            transition_text = f"Building on the previous discussion about {transitions['previous_section']}, "
            content = self._insert_at_point(content, 0, transition_text)
        
        # Add transition to next section
        if transitions.get("next_section"):
            transition_text = f"This connects to the next section on {transitions['next_section']}. "
            content = self._insert_at_point(content, len(content.split('. ')) - 1, transition_text)
        
        return content
    
    def _ensure_smooth_integration(self, content: str) -> str:
        """Ensure that added details integrate smoothly with the original content."""
        # Remove excessive spacing
        content = content.replace('  ', ' ')
        
        # Ensure proper punctuation
        content = content.strip()
        if content and not content[-1] in '.!?':
            content += '.'
        
        # Check for awkward transitions and smooth them out
        transitions = ['For example', 'Consider', 'A practical', 'Research indicates']
        for transition in transitions:
            if content.count(transition) > 2:
                # Replace some with variations
                content = content.replace(transition, 'For instance', 1)
        
        return content
    
    def _ensure_minimum_word_count(self, content: str, target_word_count: int) -> str:
        """
        Ensure content meets the minimum word count requirement.
        
        Args:
            content: Current content
            target_word_count: Target word count
            
        Returns:
            Content that meets or exceeds the target word count
        """
        current_word_count = len(content.split())
        
        if current_word_count >= target_word_count:
            return content
        
        # Generate additional content to meet the target
        section_title = "Section"
        words_needed = target_word_count - current_word_count
        
        # Generate expansion text
        expansion_parts = []
        
        # Add elaboration on the section title
        expansion_parts.append(f"This section focuses on {section_title.lower()}, which is a fundamental concept that encompasses multiple aspects and dimensions. Understanding {section_title.lower()} requires careful consideration of its various components and how they interact with each other in practical scenarios.")
        
        # Add more context
        expansion_parts.append(f"In the broader context, {section_title.lower()} plays a crucial role in helping us understand related concepts and principles. The importance of {section_title.lower()} cannot be overstated, as it forms the foundation for many advanced topics and applications in the field.")
        
        # Add practical implications
        expansion_parts.append(f"From a practical standpoint, applying the principles of {section_title.lower()} can lead to significant improvements in outcomes and results. Organizations and individuals who take the time to understand and implement {section_title.lower()} tend to see better performance and more consistent success over time.")
        
        # Add supporting details
        expansion_parts.append(f"Furthermore, the relevance of {section_title.lower()} extends across multiple domains and contexts. Whether in professional settings, academic environments, or everyday situations, the concepts underlying {section_title.lower()} provide valuable insights and guidance for decision-making and problem-solving.")
        
        # Add conclusion about the topic
        expansion_parts.append(f"In summary, {section_title.lower()} represents an essential area of knowledge that deserves attention and study. By exploring {section_title.lower()} in depth, readers can gain a comprehensive understanding that will serve them well in their pursuits and endeavors.")
        
        # Combine expansion parts
        expansion_text = " ".join(expansion_parts)
        
        # Append expansion to content
        enriched_content = content + " " + expansion_text
        
        # Check if we still need more words
        final_word_count = len(enriched_content.split())
        if final_word_count < target_word_count:
            # Add more general elaboration
            additional_expansion = f"Additional context and elaboration on {section_title.lower()} continues to reveal its importance and relevance. The principles and concepts associated with {section_title.lower()} have been studied extensively and continue to evolve as new insights emerge. Practitioners and enthusiasts alike find value in exploring {section_title.lower()} from multiple perspectives and approaches."
            enriched_content = enriched_content + " " + additional_expansion
        
        # Final check and adjustment
        final_word_count = len(enriched_content.split())
        if final_word_count < target_word_count:
            # Add final expansion
            final_expansion = f"Continuing to explore {section_title.lower()} reveals even more depth and complexity. The ongoing development and refinement of ideas around {section_title.lower()} ensures that this remains a vibrant and evolving area of interest and study for those seeking to understand and apply these concepts effectively."
            enriched_content = enriched_content + " " + final_expansion
        
        # Ensure proper punctuation
        enriched_content = enriched_content.strip()
        if enriched_content and not enriched_content[-1] in '.!?':
            enriched_content += '.'
        
        return enriched_content
    
    def generate_example_library(self, topic: str, count: int = 5) -> List[str]:
        """
        Generate a library of examples for a specific topic.
        
        Args:
            topic: Topic category for examples
            count: Number of examples to generate
            
        Returns:
            List of example texts
        """
        examples = []
        templates = self.EXAMPLE_TEMPLATES.get(topic, self.EXAMPLE_TEMPLATES["general"])
        
        for i in range(count):
            template = random.choice(templates)
            example = template.format(
                subject=f"example {i+1}",
                outcome="positive results",
                method="effective implementation",
                population="organizations",
                phenomenon="success",
                metric="adoption rates",
                time_period="recent years",
                statistic="comprehensive data",
                topic=topic
            )
            examples.append(example)
        
        return examples
    
    def enrich_with_research_insights(
        self,
        content: str,
        research_insights: List[str],
        outline_section: Dict[str, Any]
    ) -> str:
        """
        Enrich content with research insights.
        
        Args:
            content: Original content
            research_insights: List of research insights to incorporate
            outline_section: Outline section for context
            
        Returns:
            Content enriched with research insights
        """
        enriched = content
        
        for insight in research_insights[:3]:  # Limit to 3 insights
            insight_text = f"Research indicates that {insight.lower()}. "
            
            # Find insertion point
            insertion_point = self._find_insertion_point(enriched)
            enriched = self._insert_at_point(enriched, insertion_point, insight_text)
        
        return enriched
    
    def add_practical_applications(self, content: str, key_points: List[str]) -> str:
        """
        Add practical applications to the content.
        
        Args:
            content: Original content
            key_points: Key points to create applications for
            
        Returns:
            Content with added practical applications
        """
        if not key_points:
            return content
        
        application_text = "In practice, this means that understanding these concepts becomes essential for effective implementation. "
        application_text += "The practical applications include applying these principles in real-world scenarios, which leads to tangible improvements and results. "
        
        # Find insertion point
        insertion_point = self._find_insertion_point(content)
        content = self._insert_at_point(content, insertion_point, application_text)
        
        return content
