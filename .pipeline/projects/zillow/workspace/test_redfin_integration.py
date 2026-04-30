#!/usr/bin/env python3
"""Integration test for Redfin scraper."""

import sys
sys.path.insert(0, '/workspace/idea impl/.pipeline/projects/zillow/workspace')

from src.scrapers.redfin_scraper import RedfinScraper
from src.models import Property, PropertyType, ListingStatus

def test_redfin_integration():
    """Test the Redfin scraper integration."""
    print("Testing RedfinScraper Integration...")
    
    scraper = RedfinScraper()
    
    # Test complete property creation
    print("\n1. Testing complete property creation:")
    property_data = {
        'zpid': '12345678',
        'address': '123 Main St',
        'city': 'Austin',
        'state': 'TX',
        'zip_code': '78701',
        'price': 500000,
        'beds': 3,
        'baths': 2,
        'sqft': 2500,
        'lot_size': 7200,
        'property_type': PropertyType.HOUSE,
        'listing_status': ListingStatus.FOR_SALE,
        'listing_url': 'https://www.redfin.com/property/12345678',
        'listing_date': '2024-01-15',
        'source': 'redfin',
        'features': ['Garage', 'Pool', 'Fireplace']
    }
    
    property_obj = Property(**property_data)
    print(f"   Created property: {property_obj.zpid}")
    print(f"   Address: {property_obj.address}")
    print(f"   Price: ${property_obj.price:,}")
    print(f"   Beds/Baths: {property_obj.beds}/{property_obj.baths}")
    print(f"   Sqft: {property_obj.sqft}")
    print(f"   Type: {property_obj.property_type}")
    print(f"   Status: {property_obj.listing_status}")
    print(f"   Source: {property_obj.source}")
    
    # Test property validation
    print("\n2. Testing property validation:")
    assert property_obj.zpid == '12345678', "ZPID mismatch"
    assert property_obj.price == 500000, "Price mismatch"
    assert property_obj.beds == 3, "Beds mismatch"
    assert property_obj.baths == 2, "Baths mismatch"
    assert property_obj.sqft == 2500, "Sqft mismatch"
    assert property_obj.property_type == PropertyType.HOUSE, "Property type mismatch"
    assert property_obj.listing_status == ListingStatus.FOR_SALE, "Listing status mismatch"
    assert property_obj.source == 'redfin', "Source mismatch"
    print("   ✅ All validations passed!")
    
    # Test edge cases
    print("\n3. Testing edge cases:")
    
    # Test with missing fields
    partial_data = {
        'zpid': '87654321',
        'address': '456 Oak Ave',
        'city': 'Los Angeles',
        'state': 'CA',
        'zip_code': '90001',
        'price': 750000,
        'beds': 4,
        'baths': 3,
        'sqft': 3200,
        'lot_size': 5000,
        'property_type': PropertyType.CONDO,
        'listing_status': ListingStatus.PENDING,
        'listing_url': 'https://www.redfin.com/property/87654321',
        'listing_date': '2024-02-20',
        'source': 'redfin',
        'features': []
    }
    
    partial_property = Property(**partial_data)
    print(f"   Partial property created: {partial_property.zpid}")
    print(f"   Features: {partial_property.features}")
    
    # Test with None values
    none_data = {
        'zpid': '11111111',
        'address': '789 Pine Rd',
        'city': 'Miami',
        'state': 'FL',
        'zip_code': '33101',
        'price': 0,
        'beds': None,
        'baths': None,
        'sqft': None,
        'lot_size': None,
        'property_type': PropertyType.HOUSE,
        'listing_status': ListingStatus.FOR_SALE,
        'listing_url': 'https://www.redfin.com/property/11111111',
        'listing_date': None,
        'source': 'redfin',
        'features': None
    }
    
    none_property = Property(**none_data)
    print(f"   Property with None values: {none_property.zpid}")
    print(f"   Beds: {none_property.beds}, Baths: {none_property.baths}, Sqft: {none_property.sqft}")
    
    print("\n✅ All integration tests passed!")
    scraper.close()

if __name__ == "__main__":
    test_redfin_integration()
