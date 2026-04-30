"""Redfin property scraper implementation."""

import re
from datetime import datetime
from typing import List, Optional

from src.models import Property, PropertyType, ListingStatus
from src.scrapers.base_scraper import BaseScraper, ScraperSession


class RedfinScraper(BaseScraper):
    """Scraper for Redfin property listings."""
    
    def __init__(self):
        """Initialize the Redfin scraper."""
        super().__init__("https://www.redfin.com")
        self.session_manager = ScraperSession()
    
    def search(self, location: str, **kwargs) -> List[Property]:
        """
        Search for properties on Redfin.
        
        Args:
            location: Location to search (city, state, ZIP)
            **kwargs: Additional search parameters
            
        Returns:
            List of Property objects
        """
        properties = []
        
        try:
            session = self.session_manager.get_session()
            
            # Build search URL
            search_url = f"{self.base_url}/map-search/{location.replace(' ', '-')}"
            
            response = session.get(search_url, timeout=30)
            response.raise_for_status()
            
            # Parse the response
            properties = self._parse_search_results(response.text)
            
        except Exception as e:
            print(f"Error searching Redfin: {e}")
        
        return properties
    
    def get_property_details(self, property_id: str) -> Optional[Property]:
        """
        Get detailed information for a specific property.
        
        Args:
            property_id: Redfin property ID
            
        Returns:
            Property object or None if not found
        """
        try:
            session = self.session_manager.get_session()
            url = f"{self.base_url}/property/{property_id}"
            
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            return self._parse_property_details(response.text, property_id)
            
        except Exception as e:
            print(f"Error fetching property details: {e}")
            return None
    
    def _parse_search_results(self, html: str) -> List[Property]:
        """Parse search results from Redfin HTML."""
        properties = []
        
        # Look for property data in script tags
        script_pattern = r'<script[^>]*>window\.__REDFIN__DATA\s*=\s*(\{.*?\});</script>'
        matches = re.findall(script_pattern, html, re.DOTALL)
        
        for match in matches:
            try:
                import json
                data = json.loads(match)
                listings = data.get("listings", [])
                
                for listing in listings:
                    property = self._parse_listing_data(listing)
                    if property:
                        properties.append(property)
                        
            except json.JSONDecodeError:
                continue
        
        # Fallback to HTML parsing
        if not properties:
            properties = self._parse_html_results(html)
        
        return properties
    
    def _parse_listing_data(self, listing: dict) -> Optional[Property]:
        """Parse a single listing from Redfin data."""
        try:
            address = listing.get("streetAddress", "")
            city = listing.get("city", "")
            state = listing.get("state", "")
            zip_code = listing.get("zip", "")
            
            price = listing.get("listPrice", 0)
            if isinstance(price, str):
                price = self._parse_price(price)
            
            beds = listing.get("beds")
            baths = listing.get("baths")
            sqft = listing.get("sqft")
            
            property_type = self._get_property_type(str(listing.get("propertyType", "")))
            
            listing_url = listing.get("url", "")
            if listing_url and not listing_url.startswith("http"):
                listing_url = f"{self.base_url}{listing_url}"
            
            listing_date = self._parse_listing_date(str(listing.get("listingDate", "")))
            
            # Use propertyId or mlsId as zpid
            zpid = listing.get("propertyId") or listing.get("mlsId") or listing.get("id", "")
            
            return Property(
                zpid=str(zpid),
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                price=price,
                beds=beds,
                baths=baths,
                sqft=sqft,
                property_type=property_type,
                listing_status=ListingStatus.FOR_SALE,
                listing_url=listing_url,
                listing_date=listing_date,
                source="redfin"
            )
            
        except Exception as e:
            print(f"Error parsing listing: {e}")
            return None
    
    def _parse_html_results(self, html: str) -> List[Property]:
        """Parse search results from HTML."""
        properties = []
        
        # Find property cards
        card_pattern = r'<div[^>]*class="[^"]*property-card[^"]*"[^>]*>(.*?)</div>'
        cards = re.findall(card_pattern, html, re.DOTALL)
        
        for card in cards:
            try:
                property = self._parse_property_card(card)
                if property:
                    properties.append(property)
            except Exception:
                continue
        
        return properties
    
    def _parse_property_card(self, card_html: str) -> Optional[Property]:
        """Parse a single property card."""
        try:
            # Extract price
            price_match = re.search(r'<span[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</span>', card_html, re.DOTALL)
            price = 0
            if price_match:
                price = self._parse_price(price_match.group(1))
            
            # Extract address
            address_match = re.search(r'<div[^>]*class="[^"]*address[^"]*"[^>]*>(.*?)</div>', card_html, re.DOTALL)
            address = ""
            if address_match:
                address = re.sub(r'<[^>]+>', '', address_match.group(1)).strip()
            
            # Extract beds/baths
            beds, baths = self._parse_beds_baths(card_html)
            
            # Extract sqft
            sqft = self._parse_sqft(card_html)
            
            # Extract URL
            url_match = re.search(r'<a[^>]*href="([^"]*redfin[^"]*)"[^>]*>', card_html)
            listing_url = ""
            if url_match:
                listing_url = url_match.group(1)
                if not listing_url.startswith("http"):
                    listing_url = f"{self.base_url}{listing_url}"
            
            # Extract ID
            id_match = re.search(r'"id":(\d+)', card_html)
            zpid = ""
            if id_match:
                zpid = id_match.group(1)
            
            # Extract city, state, zip from address or separate fields
            city, state, zip_code = self._parse_location(card_html)
            
            # Extract property type from text
            property_type = self._get_property_type(card_html)
            
            return Property(
                zpid=zpid,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                price=price,
                beds=beds,
                baths=baths,
                sqft=sqft,
                property_type=property_type,
                listing_status=ListingStatus.FOR_SALE,
                listing_url=listing_url,
                listing_date=datetime.now(),
                source="redfin"
            )
            
        except Exception as e:
            print(f"Error parsing property card: {e}")
            return None
    
    def _parse_location(self, text: str) -> tuple:
        """Extract city, state, zip from property text."""
        city = ""
        state = ""
        zip_code = ""
        
        # Look for city, state, zip pattern
        match = re.search(r'([\w\s]+),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)', text)
        if match:
            city = match.group(1).strip()
            state = match.group(2)
            zip_code = match.group(3)
        
        return city, state, zip_code
    
    def _parse_property_details(self, html: str, property_id: str) -> Optional[Property]:
        """Parse detailed property information."""
        try:
            # Extract comprehensive property data
            address_match = re.search(r'<h1[^>]*class="[^"]*address[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
            address = ""
            if address_match:
                address = re.sub(r'<[^>]+>', '', address_match.group(1)).strip()
            
            price_match = re.search(r'<span[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</span>', html, re.DOTALL)
            price = 0
            if price_match:
                price = self._parse_price(price_match.group(1))
            
            beds, baths = self._parse_beds_baths(html)
            sqft = self._parse_sqft(html)
            
            # Extract city, state, zip
            city, state, zip_code = self._parse_location(html)
            
            # Extract property type and listing status from text content
            property_type = self._get_property_type(html)
            listing_status = self._get_listing_status(html)
            
            listing_url = f"{self.base_url}/property/{property_id}"
            
            # Extract listing date from date string
            listing_date = self._parse_listing_date(html)
            
            # Extract features
            features = self._extract_features(html)
            
            return Property(
                zpid=str(property_id),
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                price=price,
                beds=beds,
                baths=baths,
                sqft=sqft,
                property_type=property_type,
                listing_status=listing_status,
                listing_url=listing_url,
                listing_date=listing_date,
                source="redfin",
                features=features
            )
            
        except Exception as e:
            print(f"Error parsing property details: {e}")
            return None
    
    def _parse_sqft(self, text: str) -> Optional[int]:
        """Parse square footage from listing text."""
        if not text:
            return None
        
        # Look for square footage patterns
        patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*s?q?f?t?',  # 1,234 sqft or 1234 sqft
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*s?q?f?t?\s*sq',  # 1,234 sq ft
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sq\.?ft\.?',  # 1,234 sq. ft.
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Remove commas and convert to int
                    cleaned = match.group(1).replace(',', '')
                    return int(float(cleaned))
                except ValueError:
                    continue
        
        return None
    
    def _parse_listing_date(self, text: str) -> datetime:
        """Parse listing date from text."""
        if not text:
            return datetime.now()
        
        # Try to parse as ISO date first
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            pass
        
        # Try common date formats
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(text.strip(), fmt)
            except ValueError:
                continue
        
        # Return current date if parsing fails
        return datetime.now()
    
    def _extract_features(self, html: str) -> list:
        """Extract property features from HTML."""
        features = []
        
        # Look for feature lists
        feature_patterns = [
            r'<li[^>]*>([^<]+)</li>',
            r'<span[^>]*class="[^"]*feature[^"]*"[^>]*>([^<]+)</span>',
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, html)
            features.extend(matches)
        
        # Limit to top 10 features
        return features[:10]
    
    def close(self):
        """Close the scraper session."""
        self.session_manager.close()
