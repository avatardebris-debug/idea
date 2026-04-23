"""
Keyword Database Module

This module provides the KeywordDatabase class for managing keyword databases,
including local keyword storage and API interfaces for external keyword services.
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import os


@dataclass
class KeywordEntry:
    """A single keyword entry in the database"""
    keyword: str
    category: str
    search_volume: int
    competition: str  # 'low', 'medium', 'high'
    relevance_score: float
    created_at: str


class KeywordDatabase:
    """
    Local keyword database for YouTube SEO optimization.
    
    This class provides functionality for storing, retrieving, and searching
    keywords, as well as interfacing with external keyword APIs.
    """
    
    # Default database file
    DEFAULT_DB_PATH = 'keyword_database.json'
    
    # Sample keywords for initialization
    SAMPLE_KEYWORDS = [
        KeywordEntry(keyword='tutorial', category='education', search_volume=1000000,
                    competition='high', relevance_score=1.0,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='how to', category='education', search_volume=5000000,
                    competition='high', relevance_score=1.0,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='review', category='entertainment', search_volume=2000000,
                    competition='high', relevance_score=0.9,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='tips', category='lifestyle', search_volume=800000,
                    competition='medium', relevance_score=0.85,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='guide', category='education', search_volume=1500000,
                    competition='medium', relevance_score=0.85,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='best', category='entertainment', search_volume=3000000,
                    competition='high', relevance_score=0.8,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='viral', category='entertainment', search_volume=500000,
                    competition='medium', relevance_score=0.75,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='trending', category='entertainment', search_volume=600000,
                    competition='medium', relevance_score=0.75,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='technology', category='technology', search_volume=1200000,
                    competition='high', relevance_score=0.9,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='lifestyle', category='lifestyle', search_volume=900000,
                    competition='medium', relevance_score=0.85,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='beginner', category='education', search_volume=700000,
                    competition='low', relevance_score=0.7,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='advanced', category='education', search_volume=500000,
                    competition='low', relevance_score=0.7,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='2024', category='news', search_volume=2000000,
                    competition='high', relevance_score=0.8,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='new', category='news', search_volume=1800000,
                    competition='high', relevance_score=0.75,
                    created_at=datetime.now().isoformat()),
        KeywordEntry(keyword='latest', category='news', search_volume=1000000,
                    competition='medium', relevance_score=0.75,
                    created_at=datetime.now().isoformat()),
    ]
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the keyword database.
        
        Args:
            db_path: Optional path to the database file
        """
        self.db_path = db_path or os.path.join(os.getcwd(), self.DEFAULT_DB_PATH)
        self._keywords: Dict[str, KeywordEntry] = {}
        self._load_database()
    
    def _load_database(self):
        """Load the database from file"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                
                for item in data:
                    entry = KeywordEntry(
                        keyword=item['keyword'],
                        category=item['category'],
                        search_volume=item['search_volume'],
                        competition=item['competition'],
                        relevance_score=item['relevance_score'],
                        created_at=item['created_at']
                    )
                    self._keywords[entry.keyword] = entry
                    
            except (json.JSONDecodeError, KeyError) as e:
                # Start with sample keywords if loading fails
                self._init_with_sample_keywords()
        else:
            # Initialize with sample keywords
            self._init_with_sample_keywords()
            self._save_database()
    
    def _init_with_sample_keywords(self):
        """Initialize database with sample keywords"""
        for entry in self.SAMPLE_KEYWORDS:
            self._keywords[entry.keyword] = entry
    
    def _save_database(self):
        """Save the database to file"""
        try:
            data = []
            for entry in self._keywords.values():
                data.append({
                    'keyword': entry.keyword,
                    'category': entry.category,
                    'search_volume': entry.search_volume,
                    'competition': entry.competition,
                    'relevance_score': entry.relevance_score,
                    'created_at': entry.created_at
                })
            
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except IOError as e:
            print(f"Error saving database: {e}")
    
    def add_keyword(self, keyword: str, category: str, search_volume: int = 0,
                   competition: str = 'medium', relevance_score: float = 0.5) -> bool:
        """
        Add a keyword to the database.
        
        Args:
            keyword: Keyword to add
            category: Keyword category
            search_volume: Estimated search volume
            competition: Competition level (low, medium, high)
            relevance_score: Relevance score (0.0 to 1.0)
            
        Returns:
            True if keyword was added successfully
        """
        if keyword in self._keywords:
            # Update existing keyword
            entry = self._keywords[keyword]
            entry.search_volume = search_volume or entry.search_volume
            entry.competition = competition or entry.competition
            entry.relevance_score = max(entry.relevance_score, relevance_score)
            return True
        
        # Add new keyword
        entry = KeywordEntry(
            keyword=keyword.lower(),
            category=category.lower(),
            search_volume=search_volume,
            competition=competition,
            relevance_score=relevance_score,
            created_at=datetime.now().isoformat()
        )
        self._keywords[keyword.lower()] = entry
        self._save_database()
        return True
    
    def get_keyword(self, keyword: str) -> Optional[KeywordEntry]:
        """
        Get a keyword from the database.
        
        Args:
            keyword: Keyword to retrieve
            
        Returns:
            KeywordEntry if found, None otherwise
        """
        return self._keywords.get(keyword.lower())
    
    def search_keywords(self, query: str, category: Optional[str] = None,
                       max_results: int = 20) -> List[KeywordEntry]:
        """
        Search for keywords in the database.
        
        Args:
            query: Search query
            category: Optional category filter
            max_results: Maximum number of results to return
            
        Returns:
            List of matching KeywordEntry objects
        """
        query_lower = query.lower()
        results = []
        
        for entry in self._keywords.values():
            # Check if keyword matches query
            if query_lower in entry.keyword:
                # Check category filter
                if category is None or entry.category == category.lower():
                    results.append(entry)
            
            # Check if category matches query
            elif category and query_lower in category and entry.category == category.lower():
                results.append(entry)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:max_results]
    
    def get_keywords_by_category(self, category: str, max_results: int = 50) -> List[KeywordEntry]:
        """
        Get all keywords in a specific category.
        
        Args:
            category: Category to filter by
            max_results: Maximum number of results to return
            
        Returns:
            List of KeywordEntry objects
        """
        results = [
            entry for entry in self._keywords.values()
            if entry.category.lower() == category.lower()
        ]
        
        # Sort by search volume
        results.sort(key=lambda x: x.search_volume, reverse=True)
        
        return results[:max_results]
    
    def get_popular_keywords(self, num_keywords: int = 20) -> List[KeywordEntry]:
        """
        Get the most popular keywords.
        
        Args:
            num_keywords: Number of keywords to return
            
        Returns:
            List of KeywordEntry objects
        """
        sorted_keywords = sorted(
            self._keywords.values(),
            key=lambda x: (x.search_volume, x.relevance_score),
            reverse=True
        )
        
        return sorted_keywords[:num_keywords]
    
    def get_low_competition_keywords(self, num_keywords: int = 20) -> List[KeywordEntry]:
        """
        Get keywords with low competition.
        
        Args:
            num_keywords: Number of keywords to return
            
        Returns:
            List of KeywordEntry objects
        """
        low_competition = [
            entry for entry in self._keywords.values()
            if entry.competition == 'low'
        ]
        
        # Sort by search volume
        low_competition.sort(key=lambda x: x.search_volume, reverse=True)
        
        return low_competition[:num_keywords]
    
    def get_keywords_with_high_relevance(self, min_relevance: float = 0.8,
                                        num_keywords: int = 20) -> List[KeywordEntry]:
        """
        Get keywords with high relevance score.
        
        Args:
            min_relevance: Minimum relevance score (0.0 to 1.0)
            num_keywords: Number of keywords to return
            
        Returns:
            List of KeywordEntry objects
        """
        high_relevance = [
            entry for entry in self._keywords.values()
            if entry.relevance_score >= min_relevance
        ]
        
        # Sort by relevance score
        high_relevance.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return high_relevance[:num_keywords]
    
    def get_keyword_suggestions(self, keyword: str, num_suggestions: int = 10) -> List[str]:
        """
        Get keyword suggestions based on a seed keyword.
        
        Args:
            keyword: Seed keyword
            num_suggestions: Number of suggestions to return
            
        Returns:
            List of suggested keywords
        """
        keyword_lower = keyword.lower()
        suggestions = []
        
        # Find similar keywords
        for entry in self._keywords.values():
            if keyword_lower in entry.keyword or entry.keyword in keyword_lower:
                if entry.keyword != keyword_lower and entry.keyword not in suggestions:
                    suggestions.append(entry.keyword)
            
            if len(suggestions) >= num_suggestions:
                break
        
        # If not enough suggestions, add related terms
        if len(suggestions) < num_suggestions:
            related_terms = [
                f"best {keyword}",
                f"how to {keyword}",
                f"{keyword} tutorial",
                f"{keyword} guide",
                f"learn {keyword}"
            ]
            for term in related_terms:
                if term not in suggestions and len(suggestions) < num_suggestions:
                    suggestions.append(term)
        
        return suggestions[:num_suggestions]
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary containing database statistics
        """
        total_keywords = len(self._keywords)
        categories = set(entry.category for entry in self._keywords.values())
        
        competition_counts = {
            'low': sum(1 for entry in self._keywords.values() if entry.competition == 'low'),
            'medium': sum(1 for entry in self._keywords.values() if entry.competition == 'medium'),
            'high': sum(1 for entry in self._keywords.values() if entry.competition == 'high')
        }
        
        total_search_volume = sum(entry.search_volume for entry in self._keywords.values())
        avg_relevance = sum(entry.relevance_score for entry in self._keywords.values()) / total_keywords if total_keywords > 0 else 0
        
        return {
            'total_keywords': total_keywords,
            'categories': list(categories),
            'competition_distribution': competition_counts,
            'total_search_volume': total_search_volume,
            'average_relevance_score': round(avg_relevance, 2)
        }
    
    def export_to_json(self, output_path: Optional[str] = None) -> str:
        """
        Export the database to a JSON file.
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Path to exported file
        """
        path = output_path or os.path.join(os.getcwd(), 'keyword_database_export.json')
        
        try:
            data = []
            for entry in self._keywords.values():
                data.append({
                    'keyword': entry.keyword,
                    'category': entry.category,
                    'search_volume': entry.search_volume,
                    'competition': entry.competition,
                    'relevance_score': entry.relevance_score,
                    'created_at': entry.created_at
                })
            
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return path
            
        except IOError as e:
            print(f"Error exporting database: {e}")
            return ''
    
    def import_from_json(self, input_path: str) -> bool:
        """
        Import keywords from a JSON file.
        
        Args:
            input_path: Path to JSON file
            
        Returns:
            True if import was successful
        """
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            for item in data:
                self.add_keyword(
                    keyword=item['keyword'],
                    category=item['category'],
                    search_volume=item.get('search_volume', 0),
                    competition=item.get('competition', 'medium'),
                    relevance_score=item.get('relevance_score', 0.5)
                )
            
            return True
            
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error importing database: {e}")
            return False
    
    def clear_database(self):
        """Clear all keywords from the database"""
        self._keywords.clear()
        self._save_database()
    
    def get_all_categories(self) -> List[str]:
        """
        Get all categories in the database.
        
        Returns:
            List of category names
        """
        return list(set(entry.category for entry in self._keywords.values()))
    
    def update_keyword(self, keyword: str, **kwargs) -> bool:
        """
        Update an existing keyword.
        
        Args:
            keyword: Keyword to update
            **kwargs: Fields to update
            
        Returns:
            True if keyword was updated, False if not found
        """
        if keyword.lower() not in self._keywords:
            return False
        
        entry = self._keywords[keyword.lower()]
        
        if 'search_volume' in kwargs:
            entry.search_volume = kwargs['search_volume']
        if 'competition' in kwargs:
            entry.competition = kwargs['competition']
        if 'relevance_score' in kwargs:
            entry.relevance_score = kwargs['relevance_score']
        if 'category' in kwargs:
            entry.category = kwargs['category']
        
        self._save_database()
        return True
