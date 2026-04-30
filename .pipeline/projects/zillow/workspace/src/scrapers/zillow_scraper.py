"""Zillow property scraper implementation."""

import re
from datetime import datetime
from typing import List, Optional

from src.models import Property, PropertyType, ListingStatus
from src.scrapers.base_scraper import BaseScraper, ScraperSession


class ZillowScraper(BaseScraper):
    """Scraper for Zillow property listings."""
    
    def __init__(self):
        """Initialize the Zillow scraper."""
        super().__init__("https://www.zillow.com")
        self.session_manager = ScraperSession()
    
    def search(self, location: str, **kwargs) -> List[Property]:
        """
        Search for properties on Zillow.
        
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
            search_url = f"{self.base_url}/homes/{location.replace(' ', '-')}/rc"
            
            # Add search parameters
            params = {
                "searchQueryState": self._build_search_query(kwargs),
            }
            
            response = session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse the response
            properties = self._parse_search_results(response.text)
            
        except Exception as e:
            print(f"Error searching Zillow: {e}")
        
        return properties
    
    def get_property_details(self, property_id: str) -> Optional[Property]:
        """
        Get detailed information for a specific property.
        
        Args:
            property_id: Zillow property ID (zpid)
            
        Returns:
            Property object or None if not found
        """
        try:
            session = self.session_manager.get_session()
            url = f"{self.base_url}/homedetails/{property_id}_zpid/"
            
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            return self._parse_property_details(response.text, property_id)
            
        except Exception as e:
            print(f"Error fetching property details: {e}")
            return None
    
    def _build_search_query(self, kwargs: dict) -> str:
        """Build the search query parameter for Zillow."""
        # This is a simplified version - in production would need proper encoding
        return "eyJwYWdlIjoxLCJzZWFyY2hRdWVyeSI6eyJpc0xvY2F0aW9uQ29tcGxldGlvblJlc3VsdCI6ZmFsc2V9fQ=="
    
    def _parse_search_results(self, html: str) -> List[Property]:
        """Parse search results from Zillow HTML."""
        properties = []
        
        # Extract property data from the page
        # Zillow uses JSON data embedded in the page
        import json
        
        # Look for Zillow data objects
        data_matches = re.findall(r'Zillow\.Listings\.setResults\((\{.*?\})\)', html, re.DOTALL)
        
        if not data_matches:
            # Try alternative parsing
            data_matches = re.findall(r'window\.zillowData\s*=\s*(\{.*?\});', html, re.DOTALL)
        
        for data_str in data_matches:
            try:
                data = json.loads(data_str)
                listings = data.get("listings", [])
                
                for listing in listings:
                    property = self._parse_listing_data(listing)
                    if property:
                        properties.append(property)
                        
            except json.JSONDecodeError:
                continue
        
        # If no JSON data found, try basic HTML parsing
        if not properties:
            properties = self._parse_html_results(html)
        
        return properties
    
    def _parse_listing_data(self, listing: dict) -> Optional[Property]:
        """Parse a single listing from Zillow data."""
        try:
            address = listing.get("address", "")
            city = listing.get("city", "")
            state = listing.get("state", "")
            zip_code = listing.get("zipcode", "")
            
            price = listing.get("price", 0)
            if isinstance(price, str):
                price = self._parse_price(price)
            
            beds = listing.get("beds")
            baths = listing.get("baths")
            sqft = listing.get("livingArea")
            
            property_type = self._get_property_type(listing.get("propertyType", ""))
            
            listing_url = listing.get("hdpUrl", "")
            if listing_url and not listing_url.startswith("http"):
                listing_url = f"{self.base_url}{listing_url}"
            
            listing_date = self._parse_listing_date(str(listing.get("date")))
            
            return Property(
                zpid=str(listing.get("zpid", "")),
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
                source="zillow"
            )
            
        except Exception as e:
            print(f"Error parsing listing: {e}")
            return None
    
    def _parse_html_results(self, html: str) -> List[Property]:
        """Parse search results from HTML."""
        properties = []
        
        # Find property cards
        card_pattern = r'<div[^>]*class="[^"]*result-card[^"]*"[^>]*>(.*?)</div>'
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
            url_match = re.search(r'<a[^>]*href="([^"]*zillow[^"]*)"[^>]*>', card_html)
            listing_url = ""
            if url_match:
                listing_url = url_match.group(1)
                if not listing_url.startswith("http"):
                    listing_url = f"{self.base_url}{listing_url}"
            
            # Extract ZPID
            zpid_match = re.search(r'"zpid":(\d+)', card_html)
            zpid = ""
            if zpid_match:
                zpid = zpid_match.group(1)
            
            return Property(
                zpid=zpid,
                address=address,
                city="",
                state="",
                zip_code="",
                price=price,
                beds=beds,
                baths=baths,
                sqft=sqft,
                property_type=PropertyType.HOUSE,
                listing_status=ListingStatus.FOR_SALE,
                listing_url=listing_url,
                listing_date=datetime.now(),
                source="zillow"
            )
            
        except Exception as e:
            print(f"Error parsing property card: {e}")
            return None
    
    def _parse_property_details(self, html: str, zpid: str) -> Optional[Property]:
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
            
            property_type = self._get_property_type(html)
            listing_status = self._get_listing_status(html)
            
            listing_url = f"{self.base_url}/homedetails/{zpid}_zpid/"
            
            listing_date = self._parse_listing_date(html)
            
            # Extract features
            features = self._extract_features(html)
            
            return Property(
                zpid=zpid,
                address=address,
                city="",
                state="",
                zip_code="",
                price=price,
                beds=beds,
                baths=baths,
                sqft=sqft,
                property_type=property_type,
                listing_status=listing_status,
                listing_url=listing_url,
                listing_date=listing_date,
                source="zillow",
                features=features
            )
            
        except Exception as e:
            print(f"Error parsing property details: {e}")
            return None
    
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
