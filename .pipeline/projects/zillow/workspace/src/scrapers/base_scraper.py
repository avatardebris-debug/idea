"""Base scraper interface and utilities for property data extraction."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.models import Property, PropertyType, ListingStatus


class BaseScraper(ABC):
    """Abstract base class for property scrapers."""
    
    def __init__(self, base_url: str):
        """
        Initialize the scraper.
        
        Args:
            base_url: Base URL for the property listing site
        """
        self.base_url = base_url
        self.session = None
    
    @abstractmethod
    def search(self, location: str, **kwargs) -> List[Property]:
        """
        Search for properties matching criteria.
        
        Args:
            location: Location to search (city, state, ZIP)
            **kwargs: Additional search parameters
            
        Returns:
            List of Property objects
        """
        pass
    
    @abstractmethod
    def get_property_details(self, property_id: str) -> Optional[Property]:
        """
        Get detailed information for a specific property.
        
        Args:
            property_id: Unique identifier for the property
            
        Returns:
            Property object or None if not found
        """
        pass
    
    def _parse_price(self, price_str: str) -> int:
        """Parse price string to integer."""
        if not price_str:
            return 0
        
        # Remove currency symbols and commas
        cleaned = price_str.replace("$", "").replace(",", "").strip()
        
        if not cleaned:
            return 0
        
        try:
            # Handle "from" prices and ranges
            if "from" in cleaned.lower():
                cleaned = cleaned.split("from")[-1].strip()
            
            return int(float(cleaned))
        except ValueError:
            return 0
    
    def _parse_beds_baths(self, text: str) -> tuple:
        """Parse beds and baths from listing text."""
        beds = None
        baths = None
        
        # Look for patterns like "3 bed, 2 bath" or "3bd/2ba"
        import re
        
        beds_match = re.search(r'(\d+)\s*(?:bed|bd)', text, re.IGNORECASE)
        baths_match = re.search(r'(\d+\.?\d*)\s*(?:bath|ba)', text, re.IGNORECASE)
        
        if beds_match:
            beds = int(beds_match.group(1))
        
        if baths_match:
            try:
                baths = float(baths_match.group(1))
            except ValueError:
                baths = None
        
        return beds, baths
    
    def _parse_sqft(self, text: str) -> Optional[int]:
        """Parse square footage from listing text."""
        import re
        
        sqft_match = re.search(r'(\d{3,6})\s*sqft', text, re.IGNORECASE)
        if sqft_match:
            try:
                return int(sqft_match.group(1))
            except ValueError:
                return None
        
        return None
    
    def _parse_listing_date(self, text: str) -> datetime:
        """Parse listing date from text."""
        import re
        from dateutil import parser as date_parser
        
        # Look for date patterns
        date_patterns = [
            r'Listed:\s*([\w\s,]+)',
            r'Listed on\s*([\w\s,]+)',
            r'Available:\s*([\w\s,]+)',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return date_parser.parse(match.group(1))
                except Exception:
                    pass
        
        return datetime.now()
    
    def _get_property_type(self, text: str) -> PropertyType:
        """Determine property type from listing text."""
        text_lower = text.lower()
        
        if "condo" in text_lower or "apartment" in text_lower:
            return PropertyType.CONDO
        elif "townhouse" in text_lower or "town home" in text_lower:
            return PropertyType.TOWNHOUSE
        elif "multi" in text_lower or "duplex" in text_lower or "triplex" in text_lower:
            return PropertyType.MULTI_FAMILY
        elif "land" in text_lower:
            return PropertyType.LAND
        elif "manufactured" in text_lower or "mobile home" in text_lower:
            return PropertyType.MANUFACTURED
        else:
            return PropertyType.HOUSE
    
    def _get_listing_status(self, text: str) -> ListingStatus:
        """Determine listing status from text."""
        text_lower = text.lower()
        
        if "new construction" in text_lower or "new build" in text_lower:
            return ListingStatus.NEW_CONSTRUCTION
        elif "pending" in text_lower:
            return ListingStatus.PENDING
        elif "foreclosure" in text_lower or "pre-foreclosure" in text_lower:
            return ListingStatus.FORECLOSURE
        elif "auction" in text_lower:
            return ListingStatus.AUCTION
        else:
            return ListingStatus.FOR_SALE


class ScraperSession:
    """Utility class for managing HTTP sessions."""
    
    def __init__(self):
        """Initialize the session."""
        self.session = None
    
    def get_session(self):
        """Get or create a requests session."""
        if self.session is None:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            })
        return self.session
    
    def close(self):
        """Close the session."""
        if self.session:
            self.session.close()
            self.session = None
