"""Criteria matching engine for property alerts."""

from datetime import datetime, timedelta
from typing import List, Optional

from src.models import Property, SearchCriteria, PropertyType, ListingStatus


class CriteriaEngine:
    """Engine to match properties against search criteria."""
    
    def __init__(self):
        """Initialize the criteria engine."""
        pass
    
    def evaluate(self, property: Property, criteria: SearchCriteria) -> bool:
        """
        Evaluate if a property matches the search criteria.
        
        Args:
            property: The property to evaluate
            criteria: The search criteria to match against
            
        Returns:
            True if the property matches all criteria, False otherwise
        """
        # Check location (basic substring match for now)
        if not self._matches_location(property, criteria):
            return False
        
        # Check price range
        if not self._matches_price(property, criteria):
            return False
        
        # Check bedrooms
        if not self._matches_beds(property, criteria):
            return False
        
        # Check bathrooms
        if not self._matches_baths(property, criteria):
            return False
        
        # Check square footage
        if not self._matches_sqft(property, criteria):
            return False
        
        # Check property types
        if not self._matches_property_type(property, criteria):
            return False
        
        # Check listing status
        if not self._matches_listing_status(property, criteria):
            return False
        
        # Check lot size
        if not self._matches_lot_size(property, criteria):
            return False
        
        # Check keywords
        if not self._matches_keywords(property, criteria):
            return False
        
        # Check days on market
        if not self._matches_days_on_market(property, criteria):
            return False
        
        # Check special flags
        if not self._matches_special_flags(property, criteria):
            return False
        
        return True
    
    def _matches_location(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property location matches criteria."""
        if not criteria.location:
            return True
        
        location_lower = criteria.location.lower()
        full_address = property.full_address.lower()
        city_state = f"{property.city}, {property.state}".lower()
        zip_code = property.zip_code.lower()
        
        return (location_lower in full_address or 
                location_lower in city_state or 
                location_lower in zip_code)
    
    def _matches_price(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property price matches criteria."""
        if criteria.min_price and property.price < criteria.min_price:
            return False
        if criteria.max_price and property.price > criteria.max_price:
            return False
        return True
    
    def _matches_beds(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property bedrooms match criteria."""
        if property.beds is None:
            return True
        
        if criteria.min_beds and property.beds < criteria.min_beds:
            return False
        if criteria.max_beds and property.beds > criteria.max_beds:
            return False
        return True
    
    def _matches_baths(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property bathrooms match criteria."""
        if property.baths is None:
            return True
        
        if criteria.min_baths and property.baths < criteria.min_baths:
            return False
        if criteria.max_baths and property.baths > criteria.max_baths:
            return False
        return True
    
    def _matches_sqft(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property square footage matches criteria."""
        if property.sqft is None:
            return True
        
        if criteria.min_sqft and property.sqft < criteria.min_sqft:
            return False
        if criteria.max_sqft and property.sqft > criteria.max_sqft:
            return False
        return True
    
    def _matches_property_type(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property type matches criteria."""
        if not criteria.property_type and not criteria.property_types:
            return True
        
        # Check single property type
        if criteria.property_type:
            return property.property_type == criteria.property_type
        
        # Check multiple property types
        if criteria.property_types:
            return property.property_type in criteria.property_types
        
        return True
    
    def _matches_listing_status(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if listing status matches criteria."""
        if not criteria.listing_statuses:
            return True
        
        return property.listing_status in criteria.listing_statuses
    
    def _matches_lot_size(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if lot size matches criteria."""
        if property.lot_size is None:
            return True
        
        if criteria.min_lot_size and property.lot_size < criteria.min_lot_size:
            return False
        if criteria.max_lot_size and property.lot_size > criteria.max_lot_size:
            return False
        return True
    
    def _matches_keywords(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property matches keyword filters."""
        # Check for required keywords
        if criteria.keywords:
            search_text = f"{property.description} {property.address}".lower()
            for keyword in criteria.keywords:
                if keyword.lower() not in search_text:
                    return False
        
        # Check for excluded keywords
        if criteria.exclude_keywords:
            search_text = f"{property.description} {property.address}".lower()
            for keyword in criteria.exclude_keywords:
                if keyword.lower() in search_text:
                    return False
        
        return True
    
    def _matches_days_on_market(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property days on market matches criteria."""
        if criteria.max_days_on_market is None:
            return True
        
        days_on_market = (datetime.now() - property.listing_date).days
        return days_on_market <= criteria.max_days_on_market
    
    def _matches_special_flags(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check special listing flags."""
        # Check new construction
        if not criteria.include_new_construction:
            if property.listing_status == ListingStatus.NEW_CONSTRUCTION:
                return False
        
        # Check foreclosures
        if not criteria.include_foreclosures:
            if property.listing_status == ListingStatus.FORECLOSURE:
                return False
        
        # Check auctions
        if not criteria.include_auctions:
            if property.listing_status == ListingStatus.AUCTION:
                return False
        
        return True
    
    def matches_criteria(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property matches criteria (alias for evaluate)."""
        return self.evaluate(property, criteria)
    
    def get_match_details(self, property: Property, criteria: SearchCriteria) -> dict:
        """
        Get detailed match information for debugging.
        
        Returns:
            Dictionary with match details for each criterion
        """
        details = {
            "location_match": self._matches_location(property, criteria),
            "price_match": self._matches_price(property, criteria),
            "beds_match": self._matches_beds(property, criteria),
            "baths_match": self._matches_baths(property, criteria),
            "sqft_match": self._matches_sqft(property, criteria),
            "property_type_match": self._matches_property_type(property, criteria),
            "listing_status_match": self._matches_listing_status(property, criteria),
            "lot_size_match": self._matches_lot_size(property, criteria),
            "keywords_match": self._matches_keywords(property, criteria),
            "days_on_market_match": self._matches_days_on_market(property, criteria),
            "special_flags_match": self._matches_special_flags(property, criteria),
            "overall_match": self.evaluate(property, criteria),
        }
        return details
