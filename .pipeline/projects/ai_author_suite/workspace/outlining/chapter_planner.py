"""
Chapter Planner Module for AI Author Suite.

This module provides functionality for creating detailed chapter breakdowns
from book outlines, including key points, examples, transitions, and word counts.
"""

from typing import List, Dict, Optional, Any
from .models import (
    ChapterOutline,
    ChapterBreakdown,
    BookOutline,
)


class ChapterPlanner:
    """
    Creates detailed chapter breakdowns from book outlines.
    
    The ChapterPlanner class generates comprehensive chapter plans with
    key points, examples, transitions, and estimated word counts.
    """
    
    # Example templates for different chapter types
    EXAMPLE_TEMPLATES = {
        "how_to": [
            "Step-by-step implementation guide",
            "Real-world case study from industry",
            "Common mistakes and how to avoid them",
            "Best practices from experts",
            "Tools and resources recommendation"
        ],
        "explainer": [
            "Historical context and evolution",
            "Key figures and their contributions",
            "Current state and trends",
            "Future developments and predictions",
            "Comparative analysis with alternatives"
        ],
        "transformation": [
            "Before and after transformation stories",
            "Mindset shift exercises",
            "Practical action plans",
            "Obstacle identification and solutions",
            "Sustainability strategies"
        ],
        "academic": [
            "Literature review summary",
            "Methodology explanation",
            "Data analysis and findings",
            "Implications and applications",
            "Future research directions"
        ]
    }
    
    # Transition templates for connecting chapters
    TRANSITION_TEMPLATES = {
        "building_on": "This chapter builds on the concepts introduced in the previous chapter, specifically...",
        "introducing": "This chapter introduces a new concept that will be essential for understanding...",
        "contrasting": "This chapter contrasts with the previous one by examining...",
        "expanding": "This chapter expands on the foundation laid in the previous chapter by exploring..."
    }
    
    def __init__(self):
        """Initialize the ChapterPlanner."""
        self._example_cache: Dict[str, List[str]] = {}
        self._load_examples()
    
    def _load_examples(self) -> None:
        """Load example templates."""
        self._example_cache = self.EXAMPLE_TEMPLATES
    
    def plan_chapter(
        self,
        chapter_outline: ChapterOutline,
        outline_context: Dict[str, Any],
        book_type: str = "how_to"
    ) -> ChapterBreakdown:
        """
        Create a detailed chapter breakdown from a chapter outline.
        
        Args:
            chapter_outline: The chapter outline to plan
            outline_context: Context from the book outline including topic, niche, etc.
            book_type: Type of book for appropriate example selection
            
        Returns:
            ChapterBreakdown with detailed planning information
        """
        topic = outline_context.get("topic", "Topic")
        niche = outline_context.get("niche", "Niche")
        
        # Generate detailed key points
        key_points = self._generate_detailed_key_points(
            chapter_outline.title,
            chapter_outline.purpose,
            topic,
            niche,
            book_type
        )
        
        # Generate examples
        examples = self._generate_examples(
            chapter_outline.title,
            topic,
            book_type
        )
        
        # Generate transitions
        transitions = self._generate_transitions(
            chapter_outline.chapter_index,
            outline_context.get("num_chapters", 10),
            chapter_outline.title,
            topic
        )
        
        # Estimate word count
        word_count = self._estimate_detailed_word_count(
            chapter_outline.estimated_word_count,
            key_points,
            examples
        )
        
        # Generate research references
        research_refs = self._generate_research_references(
            chapter_outline.title,
            topic,
            niche
        )
        
        # Create and return the detailed breakdown
        return ChapterBreakdown(
            section_title=chapter_outline.title,
            key_points=key_points,
            examples=examples,
            transitions=transitions,
            estimated_word_count=word_count,
            research_references=research_refs,
            related_chapters=chapter_outline.related_chapters or []
        )
    
    def plan_complete_book(
        self,
        book_outline: BookOutline,
        book_type: str = "how_to"
    ) -> List[ChapterBreakdown]:
        """
        Create detailed breakdowns for all chapters in a book outline.
        
        Args:
            book_outline: The complete book outline
            book_type: Type of book for appropriate example selection
            
        Returns:
            List of ChapterBreakdown objects for all chapters
        """
        outline_context = {
            "topic": book_outline.topic,
            "niche": book_outline.niche,
            "num_chapters": book_outline.num_chapters,
            "target_audience": book_outline.target_audience,
            "book_purpose": book_outline.book_purpose
        }
        
        return [
            self.plan_chapter(chapter, outline_context, book_type)
            for chapter in book_outline.chapters
        ]
    
    def _generate_detailed_key_points(
        self,
        chapter_title: str,
        chapter_purpose: str,
        topic: str,
        niche: str,
        book_type: str
    ) -> List[str]:
        """Generate detailed key points for a chapter."""
        # Extract key concepts from chapter title
        title_words = chapter_title.split()
        key_concepts = [word for word in title_words if len(word) > 3]
        
        # Generate specific key points based on chapter type
        if "introduction" in chapter_title.lower():
            return [
                "Define the scope and purpose of the book",
                "Explain why this topic matters to readers",
                "Set clear expectations for what readers will learn",
                "Provide an overview of the book structure",
                "Introduce key terminology and concepts"
            ]
        elif "conclusion" in chapter_title.lower():
            return [
                "Summarize the main concepts covered throughout the book",
                "Reinforce the key takeaways and learning objectives",
                "Connect all concepts together into a cohesive framework",
                "Provide actionable next steps for readers",
                "Offer resources for continued learning and growth"
            ]
        else:
            # Generate topic-specific key points
            base_points = [
                f"Understand the fundamental principles of {topic}",
                f"Learn practical applications of {topic} in {niche}",
                f"Identify common challenges and how to overcome them",
                f"Discover best practices and industry standards",
                f"Explore advanced techniques and strategies"
            ]
            
            # Add specific points based on chapter position
            if "foundation" in chapter_title.lower() or "basics" in chapter_title.lower():
                base_points.insert(0, "Master the essential building blocks")
            elif "advanced" in chapter_title.lower() or "expert" in chapter_title.lower():
                base_points.append("Develop expert-level insights and strategies")
            
            return base_points
    
    def _generate_examples(
        self,
        chapter_title: str,
        topic: str,
        book_type: str
    ) -> List[str]:
        """Generate relevant examples for a chapter."""
        # Select appropriate example templates based on book type
        templates = self._example_cache.get(book_type, self._example_cache.get("how_to", []))
        
        # Generate specific examples based on chapter content
        examples = []
        
        if "introduction" in chapter_title.lower():
            examples = [
                "Real-world case study showing the impact of {topic}",
                "Before and after transformation story",
                "Expert quote or testimonial",
                "Statistical data supporting the importance of {topic}"
            ]
        elif "conclusion" in chapter_title.lower():
            examples = [
                "Success story demonstrating the complete journey",
                "Summary of key transformations achieved",
                "Future outlook and predictions",
                "Call to action with specific next steps"
            ]
        else:
            # Generate examples from templates
            for i, template in enumerate(templates[:3]):
                example = template.format(topic=topic)
                examples.append(example)
        
        return examples
    
    def _generate_transitions(
        self,
        chapter_number: int,
        total_chapters: int,
        chapter_title: str,
        topic: str
    ) -> Dict[str, str]:
        """Generate transition information for a chapter."""
        transitions = {}
        
        # Previous chapter connection
        if chapter_number > 1:
            transitions["previous"] = self._generate_previous_connection(
                chapter_number,
                chapter_title,
                topic
            )
        
        # Next chapter connection
        if chapter_number < total_chapters:
            transitions["next"] = self._generate_next_connection(
                chapter_number,
                chapter_title,
                topic
            )
        
        return transitions
    
    def _generate_previous_connection(
        self,
        chapter_number: int,
        chapter_title: str,
        topic: str
    ) -> str:
        """Generate connection to previous chapter."""
        if "foundation" in chapter_title.lower() or "basics" in chapter_title.lower():
            return "This chapter builds on the introduction and sets the foundation for everything that follows."
        elif "advanced" in chapter_title.lower():
            return "This chapter expands on the core concepts introduced in earlier chapters, taking them to a more sophisticated level."
        else:
            return f"This chapter builds on the concepts from Chapter {chapter_number - 1}, specifically focusing on {topic}."
    
    def _generate_next_connection(
        self,
        chapter_number: int,
        chapter_title: str,
        topic: str
    ) -> str:
        """Generate connection to next chapter."""
        if "conclusion" in chapter_title.lower():
            return "This chapter serves as the culmination of everything learned, providing a clear path forward."
        elif "foundation" in chapter_title.lower():
            return "This chapter lays the groundwork for more advanced topics that will be explored in subsequent chapters."
        else:
            return f"This chapter introduces concepts that will be essential for understanding the advanced topics in Chapter {chapter_number + 1}."
    
    def _estimate_detailed_word_count(
        self,
        base_word_count: int,
        key_points: List[str],
        examples: List[str]
    ) -> int:
        """Estimate detailed word count based on content."""
        # Base count from chapter outline
        word_count = base_word_count
        
        # Add word count for key points (approx. 200 words per point)
        word_count += len(key_points) * 200
        
        # Add word count for examples (approx. 300 words per example)
        word_count += len(examples) * 300
        
        # Add word count for transitions (approx. 100 words per transition)
        transitions_count = 2 if "previous" in locals() or "next" in locals() else 0
        word_count += transitions_count * 100
        
        return word_count
    
    def _generate_research_references(
        self,
        chapter_title: str,
        topic: str,
        niche: str
    ) -> List[Dict[str, str]]:
        """Generate research references for a chapter."""
        references = []
        
        # Generate relevant research topics based on chapter
        if "introduction" in chapter_title.lower():
            references = [
                {
                    "type": "statistical",
                    "topic": f"Current state of {topic} in {niche}",
                    "source": "Industry reports and market analysis"
                },
                {
                    "type": "expert",
                    "topic": "Expert perspectives on {topic}",
                    "source": "Industry leaders and thought leaders"
                }
            ]
        elif "conclusion" in chapter_title.lower():
            references = [
                {
                    "type": "case_study",
                    "topic": "Success stories in {topic}",
                    "source": "Real-world implementations"
                },
                {
                    "type": "trend_analysis",
                    "topic": "Future trends in {topic}",
                    "source": "Market research and expert predictions"
                }
            ]
        else:
            # General research references
            references = [
                {
                    "type": "academic",
                    "topic": f"Research on {topic} fundamentals",
                    "source": "Academic journals and studies"
                },
                {
                    "type": "industry",
                    "topic": f"Industry best practices for {topic}",
                    "source": "Industry reports and case studies"
                },
                {
                    "type": "practical",
                    "topic": f"Real-world applications of {topic}",
                    "source": "Case studies and practitioner experiences"
                }
            ]
        
        return references
    
    def enhance_chapter_with_research(
        self,
        chapter_breakdown: ChapterBreakdown,
        research_data: Dict[str, Any]
    ) -> ChapterBreakdown:
        """
        Enhance a chapter breakdown with research data.
        
        Args:
            chapter_breakdown: The chapter breakdown to enhance
            research_data: Research data to incorporate
            
        Returns:
            Enhanced ChapterBreakdown with research integration
        """
        # Add research-specific examples
        if "examples" in research_data:
            existing_examples = chapter_breakdown.examples or []
            chapter_breakdown.examples = existing_examples + research_data["examples"]
        
        # Add research references
        if "references" in research_data:
            existing_refs = chapter_breakdown.research_references or []
            chapter_breakdown.research_references = existing_refs + research_data["references"]
        
        # Update key points if research provides new insights
        if "key_insights" in research_data:
            existing_points = chapter_breakdown.key_points or []
            chapter_breakdown.key_points = existing_points + research_data["key_insights"]
        
        return chapter_breakdown
    
    def generate_chapter_outline_from_breakdown(
        self,
        breakdown: ChapterBreakdown,
        chapter_number: int
    ) -> ChapterOutline:
        """
        Generate a ChapterOutline from a ChapterBreakdown.
        
        Args:
            breakdown: The detailed chapter breakdown
            chapter_number: The chapter number
            
        Returns:
            ChapterOutline object
        """
        return ChapterOutline(
            chapter_number=chapter_number,
            chapter_index=chapter_number,
            title=breakdown.section_title,
            purpose=f"Cover {breakdown.section_title} with detailed exploration",
            key_takeaways=breakdown.key_points,
            sections=[],  # Sections would be derived from key points
            estimated_word_count=breakdown.estimated_word_count,
            related_chapters=breakdown.related_chapters,
            research_references=breakdown.research_references
        )
