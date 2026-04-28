"""
Book Outliner Module for AI Author Suite.

This module provides the core functionality for generating complete book
outlines based on topic and niche research data.
"""

from typing import List, Dict, Optional, Any, Tuple
from .models import (
    BookOutline,
    ChapterOutline,
    ChapterBreakdown,
    OutlineFormat,
)


class BookOutliner:
    """
    Generates complete book structures based on topic and niche research.
    
    The BookOutliner class creates comprehensive book outlines with logical
    chapter sequences, proper metadata, and supports multiple output formats.
    """
    
    # Common book structures for different genres
    NON_FICTION_STRUCTURES = {
        "how_to": {
            "description": "Step-by-step instructional structure",
            "chapter_pattern": [
                "Introduction: Understanding the Problem",
                "Chapter 1: Foundations and Basics",
                "Chapter 2: Core Concepts and Principles",
                "Chapter 3: Getting Started",
                "Chapter 4: Building Your First Project",
                "Chapter 5: Advanced Techniques",
                "Chapter 6: Best Practices and Optimization",
                "Chapter 7: Common Pitfalls and How to Avoid Them",
                "Chapter 8: Next Steps and Continued Learning",
                "Conclusion: Your Journey Forward"
            ],
            "purpose_template": "To provide readers with a comprehensive guide to mastering {topic} through practical, actionable steps."
        },
        "explainer": {
            "description": "Deep-dive explanatory structure",
            "chapter_pattern": [
                "Introduction: Why This Matters",
                "Chapter 1: The History and Context",
                "Chapter 2: Key Concepts Explained",
                "Chapter 3: How It Works",
                "Chapter 4: Real-World Applications",
                "Chapter 5: Case Studies and Examples",
                "Chapter 6: Challenges and Controversies",
                "Chapter 7: Future Trends and Developments",
                "Conclusion: What This Means for You"
            ],
            "purpose_template": "To provide readers with a thorough understanding of {topic} and its implications."
        },
        "transformation": {
            "description": "Before-and-after transformation structure",
            "chapter_pattern": [
                "Introduction: The Transformation Journey",
                "Chapter 1: Where You Are Now",
                "Chapter 2: The Vision of Where You Could Be",
                "Chapter 3: Mindset Shifts Required",
                "Chapter 4: Building the Foundation",
                "Chapter 5: Taking Action",
                "Chapter 6: Overcoming Obstacles",
                "Chapter 7: Maintaining Momentum",
                "Chapter 8: The New Normal",
                "Conclusion: Your Transformation Complete"
            ],
            "purpose_template": "To guide readers through a complete transformation in {topic}."
        },
        "comprehensive_guide": {
            "description": "Comprehensive reference structure",
            "chapter_pattern": [
                "Introduction: Navigating This Guide",
                "Chapter 1: Fundamentals of {topic}",
                "Chapter 2: Essential Tools and Resources",
                "Chapter 3: Core Methodologies",
                "Chapter 4: Advanced Strategies",
                "Chapter 5: Specialized Topics",
                "Chapter 6: Integration and Synthesis",
                "Chapter 7: Measurement and Analysis",
                "Chapter 8: Scaling and Expansion",
                "Chapter 9: Future Considerations",
                "Conclusion: Your Path Forward"
            ],
            "purpose_template": "To serve as a comprehensive reference for anyone working with {topic}."
        }
    }
    
    FICTION_STRUCTURES = {
        "hero_journey": {
            "description": "Classic hero's journey structure",
            "chapter_pattern": [
                "Chapter 1: The Ordinary World",
                "Chapter 2: The Call to Adventure",
                "Chapter 3: Refusal of the Call",
                "Chapter 4: Meeting the Mentor",
                "Chapter 5: Crossing the Threshold",
                "Chapter 6: Tests, Allies, and Enemies",
                "Chapter 7: Approach to the Inmost Cave",
                "Chapter 8: The Ordeal",
                "Chapter 9: The Reward",
                "Chapter 10: The Road Back",
                "Chapter 11: The Resurrection",
                "Chapter 12: Return with the Elixir"
            ],
            "purpose_template": "To tell a compelling story of transformation and growth."
        },
        "three_act": {
            "description": "Three-act structure",
            "chapter_pattern": [
                "Chapter 1: Setting the Scene",
                "Chapter 2: The Inciting Incident",
                "Chapter 3: Rising Action Begins",
                "Chapter 4: Complications Arise",
                "Chapter 5: Midpoint Shift",
                "Chapter 6: All Is Lost",
                "Chapter 7: The Climax Builds",
                "Chapter 8: The Climax",
                "Chapter 9: Falling Action",
                "Chapter 10: Resolution"
            ],
            "purpose_template": "To deliver a well-structured narrative with clear progression."
        }
    }
    
    # Default word counts per chapter type
    DEFAULT_WORD_COUNTS = {
        "introduction": 2000,
        "chapter": 3000,
        "advanced": 3500,
        "conclusion": 1500,
        "section": 1000
    }
    
    def __init__(self):
        """Initialize the BookOutliner."""
        self._structure_cache: Dict[str, Dict[str, Any]] = {}
        self._load_structures()
    
    def _load_structures(self) -> None:
        """Load available book structures."""
        self._structure_cache = {
            **self.NON_FICTION_STRUCTURES,
            **self.FICTION_STRUCTURES
        }
    
    def generate_outline(
        self,
        topic: str,
        niche: str,
        num_chapters: int,
        book_type: str = "how_to",
        target_audience: Optional[str] = None,
        book_purpose: Optional[str] = None,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        format: OutlineFormat = OutlineFormat.JSON,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BookOutline:
        """
        Generate a complete book outline based on topic and niche research.
        
        Args:
            topic: The main topic of the book
            niche: The target niche or audience
            num_chapters: Number of chapters to generate
            book_type: Type of book structure (e.g., 'how_to', 'explainer', 'transformation')
            target_audience: Description of target readers (auto-generated if not provided)
            book_purpose: Purpose of the book (auto-generated if not provided)
            format: Output format for the outline
            metadata: Additional metadata to include
            
        Returns:
            BookOutline object with complete chapter structure
        """
        # Determine book type if not specified
        if book_type not in self._structure_cache:
            book_type = "how_to"
        
        structure = self._structure_cache[book_type]
        
        # Generate target audience if not provided
        if not target_audience:
            target_audience = self._generate_target_audience(topic, niche)
        
        # Generate book purpose if not provided
        if not book_purpose:
            purpose_template = structure.get("purpose_template", "To provide comprehensive guidance on {topic}.")
            book_purpose = purpose_template.format(topic=topic)
        
        # Generate chapter titles based on structure pattern
        chapter_titles = self._generate_chapter_titles(
            structure.get("chapter_pattern", []),
            num_chapters,
            topic
        )
        
        # Create chapter outlines
        chapters = self._create_chapter_outlines(
            chapter_titles,
            topic,
            niche,
            book_type
        )
        
        # Calculate total word count
        total_word_count = sum(c.estimated_word_count for c in chapters)
        
        # Prepare metadata
        outline_metadata = metadata or {}
        outline_metadata["book_type"] = book_type
        outline_metadata["structure_used"] = structure.get("description", "Custom structure")
        outline_metadata["topic"] = topic
        outline_metadata["niche"] = niche
        
        # Use custom title/subtitle if provided, otherwise generate them
        final_title = title if title else self._generate_title(topic, niche)
        final_subtitle = subtitle if subtitle else self._generate_subtitle(topic)
        
        # Create and return the book outline
        return BookOutline(
            title=final_title,
            subtitle=final_subtitle,
            topic=topic,
            niche=niche,
            num_chapters=num_chapters,
            target_audience=target_audience,
            book_purpose=book_purpose,
            chapters=chapters,
            total_estimated_word_count=total_word_count,
            metadata=outline_metadata,
            format=format
        )
    
    def _generate_title(self, topic: str, niche: str) -> str:
        """Generate a compelling book title."""
        # Simple title generation - in production, this could use AI
        topic_words = topic.split()
        if len(topic_words) > 2:
            topic = " ".join(topic_words[:2])
        
        niche_words = niche.split()
        if niche_words:
            return f"The Complete Guide to {topic}: A {niche_words[0].capitalize()}'s Handbook"
        return f"The Complete Guide to {topic}"
    
    def _generate_subtitle(self, topic: str) -> str:
        """Generate a book subtitle."""
        return f"Master the Art of {topic} and Transform Your Approach"
    
    def _generate_target_audience(self, topic: str, niche: str) -> str:
        """Generate a target audience description."""
        return f"Readers interested in {topic} who want to develop expertise in the {niche} space"
    
    def _generate_chapter_titles(
        self,
        pattern: List[str],
        num_chapters: int,
        topic: str
    ) -> List[str]:
        """Generate chapter titles based on a pattern."""
        if not pattern:
            # Fallback: generate generic chapter titles
            return [f"Chapter {i+1}: Understanding {topic}" for i in range(num_chapters)]
        
        # Adjust pattern to match requested number of chapters
        if len(pattern) == num_chapters:
            return pattern
        elif len(pattern) > num_chapters:
            # Select subset of chapters
            step = len(pattern) // num_chapters
            return [pattern[i * step] for i in range(num_chapters)]
        else:
            # Expand pattern to match requested number
            expanded = pattern.copy()
            while len(expanded) < num_chapters:
                # Add new chapters based on the last pattern
                last_title = expanded[-1]
                new_title = f"Chapter {len(expanded)+1}: Advanced {topic} Concepts"
                expanded.append(new_title)
            return expanded[:num_chapters]
    
    def _create_chapter_outlines(
        self,
        chapter_titles: List[str],
        topic: str,
        niche: str,
        book_type: str
    ) -> List[ChapterOutline]:
        """Create detailed chapter outlines."""
        chapters = []
        
        for i, title in enumerate(chapter_titles, 1):
            # Determine if this is an intro, conclusion, or regular chapter
            is_intro = i == 1 and ("introduction" in title.lower() or "chapter 1" in title.lower() and "foundation" not in title.lower())
            is_conclusion = i == len(chapter_titles) and ("conclusion" in title.lower() or "forward" in title.lower())
            
            # Generate purpose based on chapter position
            if is_intro:
                purpose = "Set the stage and explain why this book matters"
            elif is_conclusion:
                purpose = "Summarize key learnings and provide next steps"
            else:
                purpose = f"Explore key aspects of {topic} and provide actionable insights"
            
            # Generate key takeaways
            key_takeaways = self._generate_key_takeaways(title, topic)
            
            # Generate sections for the chapter
            sections = self._generate_chapter_sections(title, topic, i, len(chapter_titles))
            
            # Calculate estimated word count
            word_count = self._estimate_word_count(title, is_intro, is_conclusion, sections)
            
            # Create chapter outline
            chapter = ChapterOutline(
                chapter_number=i,
                chapter_index=i,
                title=title,
                purpose=purpose,
                key_takeaways=key_takeaways,
                sections=sections,
                estimated_word_count=word_count,
                related_chapters=self._find_related_chapters(i, len(chapter_titles)),
                research_references=[]
            )
            chapters.append(chapter)
        
        return chapters
    
    def _generate_key_takeaways(self, chapter_title: str, topic: str) -> List[str]:
        """Generate key takeaways for a chapter."""
        # Simple heuristic-based takeaways - in production, use AI
        takeaways = [
            f"Understand the core concepts of {topic} in this chapter",
            f"Learn practical applications of {topic} principles",
            f"Identify how to implement {topic} strategies in your work",
            f"Recognize common challenges and how to overcome them"
        ]
        return takeaways
    
    def _generate_chapter_sections(
        self,
        chapter_title: str,
        topic: str,
        chapter_num: int,
        total_chapters: int
    ) -> List[ChapterBreakdown]:
        """Generate section breakdowns for a chapter."""
        sections = []
        
        # Determine number of sections based on chapter type
        is_intro = "introduction" in chapter_title.lower()
        is_conclusion = "conclusion" in chapter_title.lower()
        
        if is_intro:
            sections = [
                ChapterBreakdown(
                    section_title="Introduction to the Topic",
                    key_points=[
                        "Define the scope and purpose",
                        "Explain why this matters",
                        "Set reader expectations"
                    ],
                    estimated_word_count=1000
                ),
                ChapterBreakdown(
                    section_title="What You'll Learn",
                    key_points=[
                        "Overview of key concepts",
                        "Learning objectives",
                        "How to use this book"
                    ],
                    estimated_word_count=800
                )
            ]
        elif is_conclusion:
            sections = [
                ChapterBreakdown(
                    section_title="Summary of Key Learnings",
                    key_points=[
                        "Review main concepts",
                        "Highlight important takeaways",
                        "Connect concepts together"
                    ],
                    estimated_word_count=800
                ),
                ChapterBreakdown(
                    section_title="Your Next Steps",
                    key_points=[
                        "Action items for readers",
                        "Resources for continued learning",
                        "How to apply what you've learned"
                    ],
                    estimated_word_count=700
                )
            ]
        else:
            # Regular chapter sections
            num_sections = min(4, max(2, total_chapters // 3))
            section_names = [
                "Core Concepts",
                "Practical Applications",
                "Best Practices",
                "Common Challenges"
            ]
            
            for j in range(num_sections):
                section_name = section_names[j % len(section_names)]
                sections.append(ChapterBreakdown(
                    section_title=f"{section_name}: {topic}",
                    key_points=[
                        f"Understand the fundamentals of {section_name.lower()}",
                        f"Learn how to apply {section_name.lower()} in practice",
                        f"Identify opportunities for improvement"
                    ],
                    examples=[
                        f"Case study: Real-world application of {topic}",
                        f"Example: Step-by-step implementation guide",
                        f"Best practice: Industry standard approach"
                    ],
                    transitions={
                        "previous": f"Building on concepts from Chapter {chapter_num - 1}",
                        "next": f"Leading into advanced topics in Chapter {chapter_num + 1}"
                    },
                    estimated_word_count=1500
                ))
        
        return sections
    
    def _estimate_word_count(
        self,
        chapter_title: str,
        is_intro: bool,
        is_conclusion: bool,
        sections: List[ChapterBreakdown]
    ) -> int:
        """Estimate word count for a chapter."""
        if is_intro:
            return self.DEFAULT_WORD_COUNTS["introduction"]
        elif is_conclusion:
            return self.DEFAULT_WORD_COUNTS["conclusion"]
        
        # Sum section word counts
        total = sum(s.estimated_word_count for s in sections)
        return total if total > 0 else self.DEFAULT_WORD_COUNTS["chapter"]
    
    def _find_related_chapters(
        self,
        current_chapter: int,
        total_chapters: int
    ) -> List[int]:
        """Find related chapters for a given chapter."""
        related = []
        
        # Previous chapter if not first
        if current_chapter > 1:
            related.append(current_chapter - 1)
        
        # Next chapter if not last
        if current_chapter < total_chapters:
            related.append(current_chapter + 1)
        
        # Add foundational chapter for advanced chapters
        if current_chapter > total_chapters * 0.7:
            related.append(1)
        
        return related
    
    def get_available_structures(self) -> List[Dict[str, str]]:
        """Get list of available book structures."""
        return [
            {
                "id": book_type,
                "description": structure.get("description", "Custom structure"),
                "num_chapters": len(structure.get("chapter_pattern", []))
            }
            for book_type, structure in self._structure_cache.items()
        ]
    
    def generate_outline_from_research(
        self,
        research_data: Dict[str, Any],
        num_chapters: int,
        format: OutlineFormat = OutlineFormat.JSON
    ) -> BookOutline:
        """
        Generate an outline based on research data from the research module.
        
        Args:
            research_data: Research data including topic, niche, and analysis results
            num_chapters: Number of chapters to generate
            format: Output format for the outline
            
        Returns:
            BookOutline object with research-informed structure
        """
        topic = research_data.get("topic", "General Topic")
        niche = research_data.get("niche", "General Niche")
        target_audience = research_data.get("target_audience")
        book_type = research_data.get("book_type", "how_to")
        
        return self.generate_outline(
            topic=topic,
            niche=niche,
            num_chapters=num_chapters,
            book_type=book_type,
            target_audience=target_audience,
            format=format
        )
