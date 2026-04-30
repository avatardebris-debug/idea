"""Tests for the property alert system."""

import pytest
import os
import tempfile
from datetime import datetime

from src.models import Property, SearchCriteria, Alert, AlertConfig, PropertyType, ListingStatus
from src.matching.criteria_engine import CriteriaEngine
from src.storage.data_store import DataStore
from src.orchestrator import PropertyAlertOrchestrator


class TestProperty:
    """Tests for Property model."""
    
    def test_property_creation(self):
        """Test property creation."""
        property = Property(
            zpid="12345",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            zip_code="94102",
            price=800000,
            beds=3,
            baths=2,
            sqft=1500,
            property_type=PropertyType.HOUSE,
            listing_status=ListingStatus.FOR_SALE,
            listing_url="https://zillow.com/homedetails/12345",
            listing_date=datetime.now(),
            source="zillow"
        )
        
        assert property.zpid == "12345"
        assert property.price == 800000
        assert property.beds == 3
        assert property.property_type == PropertyType.HOUSE
    
    def test_property_from_dict(self):
        """Test property from dictionary."""
        data = {
            "zpid": "12345",
            "address": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94102",
            "price": 800000,
            "beds": 3,
            "baths": 2,
            "sqft": 1500,
            "property_type": "HOUSE",
            "listing_status": "FOR_SALE",
            "listing_url": "https://zillow.com/homedetails/12345",
            "listing_date": datetime.now().isoformat(),
            "source": "zillow"
        }
        
        property = Property.from_dict(data)
        
        assert property.zpid == "12345"
        assert property.price == 800000
        assert property.property_type == PropertyType.HOUSE
    
    def test_property_to_dict(self):
        """Test property to dictionary."""
        property = Property(
            zpid="12345",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            zip_code="94102",
            price=800000,
            beds=3,
            baths=2,
            sqft=1500,
            property_type=PropertyType.HOUSE,
            listing_status=ListingStatus.FOR_SALE,
            listing_url="https://zillow.com/homedetails/12345",
            listing_date=datetime.now(),
            source="zillow"
        )
        
        data = property.to_dict()
        
        assert data["zpid"] == "12345"
        assert data["price"] == 800000
        assert data["property_type"] == "HOUSE"


class TestSearchCriteria:
    """Tests for SearchCriteria model."""
    
    def test_search_criteria_creation(self):
        """Test search criteria creation."""
        criteria = SearchCriteria(
            location="San Francisco, CA",
            min_price=500000,
            max_price=1000000,
            min_beds=2,
            min_baths=1,
            min_sqft=1000,
            property_type=PropertyType.HOUSE,
            listing_status=ListingStatus.FOR_SALE,
            description="Test search"
        )
        
        assert criteria.location == "San Francisco, CA"
        assert criteria.min_price == 500000
        assert criteria.max_price == 1000000
        assert criteria.property_type == PropertyType.HOUSE
    
    def test_search_criteria_from_dict(self):
        """Test search criteria from dictionary."""
        data = {
            "location": "San Francisco, CA",
            "min_price": 500000,
            "max_price": 1000000,
            "min_beds": 2,
            "min_baths": 1,
            "min_sqft": 1000,
            "property_type": "HOUSE",
            "listing_status": "FOR_SALE",
            "description": "Test search"
        }
        
        criteria = SearchCriteria.from_dict(data)
        
        assert criteria.location == "San Francisco, CA"
        assert criteria.min_price == 500000
        assert criteria.property_type == PropertyType.HOUSE


class TestAlert:
    """Tests for Alert model."""
    
    def test_alert_creation(self):
        """Test alert creation."""
        alert = Alert(
            criteria_id="criteria-123",
            email_enabled=True,
            sms_enabled=False,
            trigger_interval_hours=24,
            description="Test alert"
        )
        
        assert alert.criteria_id == "criteria-123"
        assert alert.email_enabled is True
        assert alert.sms_enabled is False
        assert alert.trigger_interval_hours == 24
    
    def test_alert_from_dict(self):
        """Test alert from dictionary."""
        data = {
            "criteria_id": "criteria-123",
            "email_enabled": True,
            "sms_enabled": False,
            "trigger_interval_hours": 24,
            "description": "Test alert"
        }
        
        alert = Alert.from_dict(data)
        
        assert alert.criteria_id == "criteria-123"
        assert alert.email_enabled is True


class TestAlertConfig:
    """Tests for AlertConfig model."""
    
    def test_alert_config_creation(self):
        """Test alert config creation."""
        config = AlertConfig(
            email_enabled=True,
            sms_enabled=False,
            email_address="test@example.com",
            sms_number="+1234567890"
        )
        
        assert config.email_enabled is True
        assert config.sms_enabled is False
        assert config.email_address == "test@example.com"
    
    def test_alert_config_from_dict(self):
        """Test alert config from dictionary."""
        data = {
            "email_enabled": True,
            "sms_enabled": False,
            "email_address": "test@example.com",
            "sms_number": "+1234567890"
        }
        
        config = AlertConfig.from_dict(data)
        
        assert config.email_enabled is True
        assert config.email_address == "test@example.com"


class TestCriteriaEngine:
    """Tests for CriteriaEngine."""
    
    def test_matches_criteria_price(self):
        """Test criteria matching with price."""
        engine = CriteriaEngine()
        
        criteria = SearchCriteria(
            location="San Francisco, CA",
            min_price=500000,
            max_price=1000000
        )
        
        # Should match
        property1 = Property(
            zpid="1",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            price=750000
        )
        assert engine.matches_criteria(property1, criteria) is True
        
        # Below min price
        property2 = Property(
            zpid="2",
            address="456 Main St",
            city="San Francisco",
            state="CA",
            price=400000
        )
        assert engine.matches_criteria(property2, criteria) is False
        
        # Above max price
        property3 = Property(
            zpid="3",
            address="789 Main St",
            city="San Francisco",
            state="CA",
            price=1200000
        )
        assert engine.matches_criteria(property3, criteria) is False
    
    def test_matches_criteria_beds(self):
        """Test criteria matching with beds."""
        engine = CriteriaEngine()
        
        criteria = SearchCriteria(
            location="San Francisco, CA",
            min_beds=3
        )
        
        # Should match
        property1 = Property(
            zpid="1",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            beds=3
        )
        assert engine.matches_criteria(property1, criteria) is True
        
        # Below min beds
        property2 = Property(
            zpid="2",
            address="456 Main St",
            city="San Francisco",
            state="CA",
            beds=2
        )
        assert engine.matches_criteria(property2, criteria) is False
    
    def test_matches_criteria_property_type(self):
        """Test criteria matching with property type."""
        engine = CriteriaEngine()
        
        criteria = SearchCriteria(
            location="San Francisco, CA",
            property_type=PropertyType.HOUSE
        )
        
        # Should match
        property1 = Property(
            zpid="1",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            property_type=PropertyType.HOUSE
        )
        assert engine.matches_criteria(property1, criteria) is True
        
        # Different property type
        property2 = Property(
            zpid="2",
            address="456 Main St",
            city="San Francisco",
            state="CA",
            property_type=PropertyType.CONDO
        )
        assert engine.matches_criteria(property2, criteria) is False


class TestDataStore:
    """Tests for DataStore."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            store = DataStore(db_path)
            yield store
            store.close()
    
    def test_add_and_get_property(self, temp_db):
        """Test adding and getting a property."""
        property = Property(
            zpid="12345",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            price=800000
        )
        
        temp_db.add_property(property)
        retrieved = temp_db.get_property("12345")
        
        assert retrieved is not None
        assert retrieved.zpid == "12345"
        assert retrieved.price == 800000
    
    def test_add_and_get_search_criteria(self, temp_db):
        """Test adding and getting search criteria."""
        criteria = SearchCriteria(
            location="San Francisco, CA",
            min_price=500000
        )
        
        criteria_id = temp_db.add_search_criteria(criteria)
        retrieved = temp_db.get_search_criteria(criteria_id)
        
        assert retrieved is not None
        assert retrieved.location == "San Francisco, CA"
    
    def test_add_and_get_alert(self, temp_db):
        """Test adding and getting an alert."""
        alert = Alert(
            criteria_id="criteria-123",
            email_enabled=True
        )
        
        alert_id = temp_db.add_alert(alert)
        retrieved = temp_db.get_alert(alert_id)
        
        assert retrieved is not None
        assert retrieved.criteria_id == "criteria-123"
    
    def test_list_all(self, temp_db):
        """Test listing all items."""
        # Add properties
        for i in range(3):
            property = Property(
                zpid=f"{i}",
                address=f"{i} Main St",
                city="San Francisco",
                state="CA",
                price=800000 + i * 100000
            )
            temp_db.add_property(property)
        
        properties = temp_db.list_properties()
        assert len(properties) == 3
    
    def test_delete_property(self, temp_db):
        """Test deleting a property."""
        property = Property(
            zpid="12345",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            price=800000
        )
        
        temp_db.add_property(property)
        temp_db.delete_property("12345")
        
        retrieved = temp_db.get_property("12345")
        assert retrieved is None


class TestPropertyAlertOrchestrator:
    """Tests for PropertyAlertOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator with a temporary database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            orchestrator = PropertyAlertOrchestrator(db_path)
            yield orchestrator
            orchestrator.close()
    
    def test_run_cycle(self, orchestrator):
        """Test running an alert cycle."""
        # Add search criteria
        criteria = SearchCriteria(
            location="San Francisco, CA",
            min_price=500000,
            max_price=1000000,
            min_beds=2
        )
        criteria_id = orchestrator.add_search_criteria(criteria)
        
        # Add alert
        alert = Alert(
            criteria_id=criteria_id,
            email_enabled=False,
            sms_enabled=False
        )
        alert_id = orchestrator.add_alert(alert)
        
        # Add a matching property
        property = Property(
            zpid="12345",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            price=750000,
            beds=3,
            baths=2,
            sqft=1500
        )
        orchestrator.data_store.add_property(property)
        
        # Run cycle
        stats = orchestrator.run_cycle()
        
        assert stats["criteria_processed"] == 1
        assert stats["properties_scraped"] == 1
        assert stats["alerts_triggered"] == 1
    
    def test_no_alert_triggered(self, orchestrator):
        """Test when no alert should be triggered."""
        # Add search criteria
        criteria = SearchCriteria(
            location="San Francisco, CA",
            min_price=500000,
            max_price=1000000
        )
        criteria_id = orchestrator.add_search_criteria(criteria)
        
        # Add alert with short interval
        alert = Alert(
            criteria_id=criteria_id,
            email_enabled=False,
            sms_enabled=False,
            trigger_interval_hours=1
        )
        alert_id = orchestrator.add_alert(alert)
        
        # Manually set last triggered time to be recent
        alert.last_triggered = datetime.now().isoformat()
        orchestrator.data_store.update_alert(alert)
        
        # Add a matching property
        property = Property(
            zpid="12345",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            price=750000
        )
        orchestrator.data_store.add_property(property)
        
        # Run cycle
        stats = orchestrator.run_cycle()
        
        # Alert should not be triggered again
        assert stats["alerts_triggered"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
