"""Property alert orchestrator implementation."""

import logging
from datetime import datetime
from typing import List, Optional

from src.models import Property, SearchCriteria, Alert, AlertConfig
from src.storage.data_store import DataStore
from src.matching.criteria_engine import CriteriaEngine
from src.notifications.email_notifier import EmailNotifier
from src.notifications.sms_notifier import SMSNotifier
from src.scrapers.zillow_scraper import ZillowScraper
from src.scrapers.redfin_scraper import RedfinScraper

logger = logging.getLogger(__name__)


class PropertyAlertOrchestrator:
    """Orchestrates property alerts and notifications."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the orchestrator.
        
        Args:
            data_dir: Directory for data storage
        """
        self.data_store = DataStore(data_dir)
        self.criteria_engine = CriteriaEngine()
        self.email_notifier = None
        self.sms_notifier = None
        self.zillow_scraper = ZillowScraper()
        self.redfin_scraper = RedfinScraper()
        self._running = False
        
        # Initialize notification handlers
        self._init_notifications()
    
    def _init_notifications(self):
        """Initialize notification handlers."""
        config = self.data_store.get_alert_config()
        
        if config.email_enabled:
            self.email_notifier = EmailNotifier(config)
        
        if config.sms_enabled:
            self.sms_notifier = SMSNotifier(config)
    
    def run_cycle(self) -> dict:
        """
        Run a single alert cycle.
        
        Returns:
            Dictionary with cycle statistics
        """
        stats = {
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "criteria_processed": 0,
            "properties_scraped": 0,
            "alerts_triggered": 0,
            "notifications_sent": 0,
            "errors": []
        }
        
        try:
            # Get all active search criteria
            criteria_list = self.data_store.list_search_criteria()
            
            for criteria in criteria_list:
                try:
                    stats["criteria_processed"] += 1
                    
                    # Get matching alerts
                    alerts = self.data_store.get_alerts_by_criteria_id(criteria.id)
                    
                    # Search for properties (scrape or check existing)
                    properties = self._search_properties(criteria)
                    stats["properties_scraped"] += len(properties)
                    
                    # Check each property against all alerts
                    for property in properties:
                        for alert in alerts:
                            try:
                                # Check if alert should be triggered
                                if self._should_trigger_alert(alert, property):
                                    # Trigger alert
                                    self._trigger_alert(alert, property)
                                    stats["alerts_triggered"] += 1
                                    stats["notifications_sent"] += self._send_notifications(alert, property)
                                    
                            except Exception as e:
                                stats["errors"].append(f"Error processing alert {alert.id}: {str(e)}")
                    
                except Exception as e:
                    stats["errors"].append(f"Error processing criteria {criteria.id}: {str(e)}")
            
            stats["end_time"] = datetime.now().isoformat()
            
        except Exception as e:
            stats["errors"].append(f"Error in alert cycle: {str(e)}")
            stats["end_time"] = datetime.now().isoformat()
        
        return stats
    
    def _search_properties(self, criteria: SearchCriteria) -> List[Property]:
        """Search for properties matching criteria."""
        all_properties = []
        
        # First, check existing properties in data store that match criteria
        existing_properties = self.data_store.list_properties()
        for property in existing_properties:
            if self.criteria_engine.matches_criteria(property, criteria):
                all_properties.append(property)
        
        # Then try to scrape for new properties
        try:
            zillow_properties = self.zillow_scraper.search(criteria.location)
            all_properties.extend(zillow_properties)
        except Exception as e:
            print(f"Error searching Zillow: {e}")
        
        try:
            redfin_properties = self.redfin_scraper.search(criteria.location)
            all_properties.extend(redfin_properties)
        except Exception as e:
            print(f"Error searching Redfin: {e}")
        
        # Store new properties
        for property in all_properties:
            self.data_store.add_property(property)
        
        return all_properties
    
    def _is_new_property(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property is new for this criteria."""
        # Check if property already exists
        existing = self.data_store.get_property(property.zpid)
        if existing:
            return False
        
        # Check if property matches criteria
        if not self.criteria_engine.matches_criteria(property, criteria):
            return False
        
        return True
    
    def _should_trigger_alert(self, alert: Alert, property: Property) -> bool:
        """Check if alert should be triggered."""
        # Check if alert is active
        if not alert.is_active:
            return False
        
        # Check if alert has been triggered recently
        if alert.last_triggered:
            last_triggered = datetime.fromisoformat(alert.last_triggered)
            now = datetime.now()
            time_since = (now - last_triggered).total_seconds()
            
            if time_since < alert.trigger_interval_seconds:
                return False
        
        return True
    
    def _matches_property_type(self, property: Property, criteria: SearchCriteria) -> bool:
        """Check if property type matches criteria."""
        # If no property type specified in criteria, any type matches
        if not criteria.property_type and not criteria.property_types:
            return True
        
        # Check single property type
        if criteria.property_type:
            if property.property_type == criteria.property_type:
                return True
        
        # Check multiple property types
        if criteria.property_types:
            if property.property_type in criteria.property_types:
                return True
        
        return False
    
    def _trigger_alert(self, alert: Alert, property: Property):
        """Trigger an alert."""
        # Update last triggered time
        alert.last_triggered = datetime.now().isoformat()
        self.data_store.update_alert(alert)
    
    def _send_notifications(self, alert: Alert, property: Property) -> int:
        """Send notifications for an alert."""
        count = 0
        
        # Send email
        if self.email_notifier and alert.email_enabled:
            try:
                self.email_notifier.send_property_alert(alert, property)
                count += 1
            except Exception as e:
                print(f"Error sending email: {e}")
        
        # Send SMS
        if self.sms_notifier and alert.sms_enabled:
            try:
                self.sms_notifier.send_property_alert(alert, property)
                count += 1
            except Exception as e:
                print(f"Error sending SMS: {e}")
        
        return count
    
    def add_search_criteria(self, criteria: SearchCriteria) -> str:
        """Add a new search criteria."""
        return self.data_store.add_search_criteria(criteria)
    
    def get_search_criteria(self, criteria_id: str) -> Optional[SearchCriteria]:
        """Get search criteria by ID."""
        return self.data_store.get_search_criteria(criteria_id)
    
    def update_search_criteria(self, criteria: SearchCriteria) -> bool:
        """Update search criteria."""
        return self.data_store.update_search_criteria(criteria)
    
    def delete_search_criteria(self, criteria_id: str) -> bool:
        """Delete search criteria."""
        return self.data_store.delete_search_criteria(criteria_id)
    
    def list_search_criteria(self) -> List[SearchCriteria]:
        """List all search criteria."""
        return self.data_store.list_search_criteria()
    
    def add_alert(self, alert: Alert) -> str:
        """Add a new alert."""
        return self.data_store.add_alert(alert)
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID."""
        return self.data_store.get_alert(alert_id)
    
    def update_alert(self, alert: Alert) -> bool:
        """Update alert."""
        return self.data_store.update_alert(alert)
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete alert."""
        return self.data_store.delete_alert(alert_id)
    
    def list_alerts(self) -> List[Alert]:
        """List all alerts."""
        return self.data_store.list_alerts()
    
    def get_alert_config(self) -> AlertConfig:
        """Get alert configuration."""
        return self.data_store.get_alert_config()
    
    def update_alert_config(self, config: AlertConfig) -> bool:
        """Update alert configuration."""
        return self.data_store.update_alert_config(config)
    
    def list_properties(self) -> List[Property]:
        """List all properties."""
        return self.data_store.list_properties()
    
    def close(self):
        """Close the orchestrator."""
        self.zillow_scraper.close()
        self.redfin_scraper.close()
