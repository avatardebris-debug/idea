#!/usr/bin/env python3
"""Test script for Redfin scraper."""

import sys
sys.path.insert(0, '/workspace/idea impl/.pipeline/projects/zillow/workspace')

from src.scrapers.redfin_scraper import RedfinScraper
from src.models import PropertyType, ListingStatus

def test_redfin_scraper():
    """Test the Redfin scraper."""
    print("Testing RedfinScraper...")
    
    scraper = RedfinScraper()
    
    # Test _parse_price
    print("\n1. Testing _parse_price:")
    test_prices = [
        "$500,000",
        "$1,234,567",
        "from $300,000",
        "$450K",
        "500000",
    ]
    for price_str in test_prices:
        result = scraper._parse_price(price_str)
        print(f"   '{price_str}' -> ${result:,}")
    
    # Test _parse_beds_baths
    print("\n2. Testing _parse_beds_baths:")
    test_texts = [
        "3 bed, 2 bath",
        "4bd/3ba",
        "2 bed, 1.5 bath",
        "5 bed, 4 bath",
    ]
    for text in test_texts:
        beds, baths = scraper._parse_beds_baths(text)
        print(f"   '{text}' -> beds={beds}, baths={baths}")
    
    # Test _parse_sqft
    print("\n3. Testing _parse_sqft:")
    test_texts = [
        "2,500 sqft",
        "1,800 sqft",
        "3,200 sqft",
    ]
    for text in test_texts:
        result = scraper._parse_sqft(text)
        print(f"   '{text}' -> {result} sqft")
    
    # Test _get_property_type
    print("\n4. Testing _get_property_type:")
    test_texts = [
        "Single Family Home",
        "Condo",
        "Townhouse",
        "Multi-family",
        "Land",
    ]
    for text in test_texts:
        result = scraper._get_property_type(text)
        print(f"   '{text}' -> {result}")
    
    # Test _get_listing_status
    print("\n5. Testing _get_listing_status:")
    test_texts = [
        "For Sale",
        "Pending",
        "New Construction",
        "Foreclosure",
        "Auction",
    ]
    for text in test_texts:
        result = scraper._get_listing_status(text)
        print(f"   '{text}' -> {result}")
    
    # Test _parse_location
    print("\n6. Testing _parse_location:")
    test_texts = [
        "123 Main St, Austin, TX 78701",
        "456 Oak Ave, Los Angeles, CA 90001",
        "789 Pine Rd, Miami, FL 33101",
    ]
    for text in test_texts:
        city, state, zip_code = scraper._parse_location(text)
        print(f"   '{text}' -> city='{city}', state='{state}', zip='{zip_code}'")
    
    # Test _parse_listing_date
    print("\n7. Testing _parse_listing_date:")
    test_dates = [
        "2024-01-15",
        "2024-02-20",
        "2024-03-10",
        "",
    ]
    for date_str in test_dates:
        result = scraper._parse_listing_date(date_str)
        print(f"   '{date_str}' -> {result}")
    
    print("\n✅ All tests completed!")
    scraper.close()

if __name__ == "__main__":
    test_redfin_scraper()
