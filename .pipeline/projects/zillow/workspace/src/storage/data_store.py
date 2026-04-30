"""Data storage layer for the property alert system."""

import json
import os
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from src.models import Property, SearchCriteria, Alert, AlertConfig


class DataStore:
    """Persistent data storage for the property alert system."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the data store.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        self.db_path = data_dir  # For test compatibility
        self._ensure_data_dir()
        
        # Initialize storage
        self._search_criteria = self._load_search_criteria()
        self._alerts = self._load_alerts()
        self._properties = self._load_properties()
        self._alert_config = self._load_alert_config()
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_search_criteria(self) -> dict:
        """Load search criteria from file."""
        file_path = os.path.join(self.data_dir, "search_criteria.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return {k: SearchCriteria.from_dict(v) for k, v in data.items()}
            except Exception as e:
                print(f"Error loading search criteria: {e}")
        return {}
    
    def _save_search_criteria(self):
        """Save search criteria to file."""
        file_path = os.path.join(self.data_dir, "search_criteria.json")
        try:
            with open(file_path, 'w') as f:
                json.dump({k: v.to_dict() for k, v in self._search_criteria.items()}, f, indent=2)
        except Exception as e:
            print(f"Error saving search criteria: {e}")
    
    def _load_alerts(self) -> dict:
        """Load alerts from file."""
        file_path = os.path.join(self.data_dir, "alerts.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return {k: Alert.from_dict(v) for k, v in data.items()}
            except Exception as e:
                print(f"Error loading alerts: {e}")
        return {}
    
    def _save_alerts(self):
        """Save alerts to file."""
        file_path = os.path.join(self.data_dir, "alerts.json")
        try:
            with open(file_path, 'w') as f:
                json.dump({k: v.to_dict() for k, v in self._alerts.items()}, f, indent=2)
        except Exception as e:
            print(f"Error saving alerts: {e}")
    
    def _load_properties(self) -> dict:
        """Load properties from file."""
        file_path = os.path.join(self.data_dir, "properties.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return {k: Property.from_dict(v) for k, v in data.items()}
            except Exception as e:
                print(f"Error loading properties: {e}")
        return {}
    
    def _save_properties(self):
        """Save properties to file."""
        file_path = os.path.join(self.data_dir, "properties.json")
        try:
            with open(file_path, 'w') as f:
                json.dump({k: v.to_dict() for k, v in self._properties.items()}, f, indent=2)
        except Exception as e:
            print(f"Error saving properties: {e}")
    
    def _load_alert_config(self) -> AlertConfig:
        """Load alert configuration from file."""
        file_path = os.path.join(self.data_dir, "alert_config.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return AlertConfig.from_dict(data)
            except Exception as e:
                print(f"Error loading alert config: {e}")
        return AlertConfig(id="default")
    
    def _save_alert_config(self):
        """Save alert configuration to file."""
        file_path = os.path.join(self.data_dir, "alert_config.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(self._alert_config.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving alert config: {e}")
    
    # Search Criteria Methods
    def add_search_criteria(self, criteria: SearchCriteria) -> str:
        """Add a new search criteria."""
        criteria_id = criteria.id or str(uuid4())
        criteria.id = criteria_id
        self._search_criteria[criteria_id] = criteria
        self._save_search_criteria()
        return criteria_id
    
    def get_search_criteria(self, criteria_id: str) -> Optional[SearchCriteria]:
        """Get search criteria by ID."""
        return self._search_criteria.get(criteria_id)
    
    def update_search_criteria(self, criteria: SearchCriteria) -> bool:
        """Update search criteria."""
        if criteria.id in self._search_criteria:
            self._search_criteria[criteria.id] = criteria
            self._save_search_criteria()
            return True
        return False
    
    def delete_search_criteria(self, criteria_id: str) -> bool:
        """Delete search criteria."""
        if criteria_id in self._search_criteria:
            del self._search_criteria[criteria_id]
            self._save_search_criteria()
            return True
        return False
    
    def list_search_criteria(self) -> List[SearchCriteria]:
        """List all search criteria."""
        return list(self._search_criteria.values())
    
    # Alert Methods
    def add_alert(self, alert: Alert) -> str:
        """Add a new alert."""
        alert_id = alert.id or str(uuid4())
        alert.id = alert_id
        self._alerts[alert_id] = alert
        self._save_alerts()
        return alert_id
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID."""
        return self._alerts.get(alert_id)
    
    def update_alert(self, alert: Alert) -> bool:
        """Update alert."""
        if alert.id in self._alerts:
            self._alerts[alert.id] = alert
            self._save_alerts()
            return True
        return False
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete alert."""
        if alert_id in self._alerts:
            del self._alerts[alert_id]
            self._save_alerts()
            return True
        return False
    
    def list_alerts(self) -> List[Alert]:
        """List all alerts."""
        return list(self._alerts.values())
    
    def get_alerts_by_criteria_id(self, criteria_id: str) -> List[Alert]:
        """Get all alerts for a specific search criteria."""
        return [alert for alert in self._alerts.values() if alert.criteria_id == criteria_id]
    
    # Property Methods
    def add_property(self, property: Property) -> str:
        """Add a new property."""
        property_id = property.zpid or str(uuid4())
        self._properties[property_id] = property
        self._save_properties()
        return property_id
    
    def get_property(self, property_id: str) -> Optional[Property]:
        """Get property by ID."""
        return self._properties.get(property_id)
    
    def update_property(self, property: Property) -> bool:
        """Update property."""
        if property.zpid in self._properties:
            self._properties[property.zpid] = property
            self._save_properties()
            return True
        return False
    
    def delete_property(self, property_id: str) -> bool:
        """Delete property."""
        if property_id in self._properties:
            del self._properties[property_id]
            self._save_properties()
            return True
        return False
    
    def list_properties(self) -> List[Property]:
        """List all properties."""
        return list(self._properties.values())
    
    def get_properties_by_criteria_id(self, criteria_id: str) -> List[Property]:
        """Get all properties matching a search criteria."""
        criteria = self.get_search_criteria(criteria_id)
        if not criteria:
            return []
        
        matching = []
        for property in self._properties.values():
            if self._matches_criteria(property, criteria):
                matching.append(property)
        
        return matching
    
    def _matches_criteria(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if a property matches search criteria."""
        # Check price
        if criteria.min_price and property.price < criteria.min_price:
            return False
        if criteria.max_price and property.price > criteria.max_price:
            return False
        
        # Check beds
        if criteria.min_beds and (property.beds is None or property.beds < criteria.min_beds):
            return False
        
        # Check baths
        if criteria.min_baths and (property.baths is None or property.baths < criteria.min_baths):
            return False
        
        # Check sqft
        if criteria.min_sqft and (property.sqft is None or property.sqft < criteria.min_sqft):
            return False
        
        # Check property type
        if criteria.property_type and property.property_type != criteria.property_type:
            return False
        
        # Check listing status
        if criteria.listing_status and property.listing_status != criteria.listing_status:
            return False
        
        # Check location
        if criteria.location:
            location_lower = criteria.location.lower()
            address_lower = f"{property.address} {property.city} {property.state}".lower()
            if location_lower not in address_lower:
                return False
        
        return True
    
    # Alert Configuration Methods
    def get_alert_config(self) -> AlertConfig:
        """Get alert configuration."""
        return self._alert_config
    
    def update_alert_config(self, config: AlertConfig) -> bool:
        """Update alert configuration."""
        self._alert_config = config
        self._save_alert_config()
        return True
    
    def close(self):
        """Close the data store."""
        self._save_search_criteria()
        self._save_alerts()
        self._save_properties()
        self._save_alert_config()
    
    # Utility Methods
    def clear_all(self):
        """Clear all data."""
        self._search_criteria.clear()
        self._alerts.clear()
        self._properties.clear()
        self._save_search_criteria()
        self._save_alerts()
        self._save_properties()
        self._save_alert_config()
