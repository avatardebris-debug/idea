"""Data models for the Zillow/Redfin alert tool."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class PropertyType(Enum):
    """Types of properties."""
    HOUSE = "house"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    MULTI_FAMILY = "multi_family"
    LAND = "land"
    MANUFACTURED = "manufactured"
    MOBILE = "mobile"


class ListingStatus(Enum):
    """Status of a property listing."""
    FOR_SALE = "for_sale"
    PENDING = "pending"
    NEW_CONSTRUCTION = "new_construction"
    FORECLOSURE = "foreclosure"
    AUCTION = "auction"


@dataclass
class Property:
    """Represents a property listing."""
    zpid: str
    address: str
    city: str
    state: str
    zip_code: str = ""
    price: int = 0
    beds: Optional[int] = None
    baths: Optional[int] = None
    sqft: Optional[int] = None
    lot_size: Optional[int] = None
    property_type: PropertyType = PropertyType.HOUSE
    listing_status: ListingStatus = ListingStatus.FOR_SALE
    listing_url: str = ""
    listing_date: datetime = field(default_factory=datetime.now)
    source: str = "zillow"
    description: str = ""
    images: list = field(default_factory=list)
    features: list = field(default_factory=list)
    
    @property
    def full_address(self) -> str:
        """Return full address string."""
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
    
    @property
    def price_per_sqft(self) -> Optional[float]:
        """Calculate price per square foot."""
        if self.sqft and self.sqft > 0:
            return round(self.price / self.sqft, 2)
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "zpid": self.zpid,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "price": self.price,
            "beds": self.beds,
            "baths": self.baths,
            "sqft": self.sqft,
            "lot_size": self.lot_size,
            "property_type": self.property_type.name,
            "listing_status": self.listing_status.name,
            "listing_url": self.listing_url,
            "listing_date": self.listing_date.isoformat(),
            "source": self.source,
            "description": self.description,
            "images": self.images,
            "features": self.features,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Property":
        """Create from dictionary."""
        # Handle both uppercase and lowercase enum values
        property_type_value = data["property_type"]
        if isinstance(property_type_value, str):
            property_type_value = property_type_value.lower()
        listing_status_value = data["listing_status"]
        if isinstance(listing_status_value, str):
            listing_status_value = listing_status_value.lower()
        
        return cls(
            zpid=data["zpid"],
            address=data["address"],
            city=data["city"],
            state=data["state"],
            zip_code=data["zip_code"],
            price=data["price"],
            beds=data.get("beds"),
            baths=data.get("baths"),
            sqft=data.get("sqft"),
            lot_size=data.get("lot_size"),
            property_type=PropertyType(property_type_value),
            listing_status=ListingStatus(listing_status_value),
            listing_url=data["listing_url"],
            listing_date=datetime.fromisoformat(data["listing_date"]),
            source=data["source"],
            description=data.get("description", ""),
            images=data.get("images", []),
            features=data.get("features", []),
        )


@dataclass
class SearchCriteria:
    """User-defined search criteria for property alerts."""
    location: str  # City, state, or ZIP code
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_beds: Optional[int] = None
    max_beds: Optional[int] = None
    min_baths: Optional[int] = None
    max_baths: Optional[int] = None
    min_sqft: Optional[int] = None
    max_sqft: Optional[int] = None
    property_type: Optional[PropertyType] = None
    property_types: list = field(default_factory=list)
    listing_status: Optional[ListingStatus] = None
    listing_statuses: list = field(default_factory=list)
    min_lot_size: Optional[int] = None
    max_lot_size: Optional[int] = None
    keywords: list = field(default_factory=list)
    exclude_keywords: list = field(default_factory=list)
    max_days_on_market: Optional[int] = None
    include_new_construction: bool = True
    include_foreclosures: bool = False
    include_auctions: bool = False
    description: str = ""
    id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "location": self.location,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "min_beds": self.min_beds,
            "max_beds": self.max_beds,
            "min_baths": self.min_baths,
            "max_baths": self.max_baths,
            "min_sqft": self.min_sqft,
            "max_sqft": self.max_sqft,
            "property_type": self.property_type.name if self.property_type else None,
            "property_types": [pt.name for pt in self.property_types],
            "listing_status": self.listing_status.name if self.listing_status else None,
            "listing_statuses": [ls.name for ls in self.listing_statuses],
            "min_lot_size": self.min_lot_size,
            "max_lot_size": self.max_lot_size,
            "keywords": self.keywords,
            "exclude_keywords": self.exclude_keywords,
            "max_days_on_market": self.max_days_on_market,
            "include_new_construction": self.include_new_construction,
            "include_foreclosures": self.include_foreclosures,
            "include_auctions": self.include_auctions,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SearchCriteria":
        """Create from dictionary."""
        # Handle both uppercase and lowercase enum values
        property_type_value = data.get("property_type")
        if isinstance(property_type_value, str):
            property_type_value = PropertyType(property_type_value.lower())
        
        listing_status_value = data.get("listing_status")
        if isinstance(listing_status_value, str):
            listing_status_value = ListingStatus(listing_status_value.lower())
        
        return cls(
            id=data.get("id"),
            location=data["location"],
            min_price=data.get("min_price"),
            max_price=data.get("max_price"),
            min_beds=data.get("min_beds"),
            max_beds=data.get("max_beds"),
            min_baths=data.get("min_baths"),
            max_baths=data.get("max_baths"),
            min_sqft=data.get("min_sqft"),
            max_sqft=data.get("max_sqft"),
            property_type=property_type_value,
            property_types=[PropertyType(pt.lower()) if isinstance(pt, str) else pt for pt in data.get("property_types", [])],
            listing_status=listing_status_value,
            listing_statuses=[ListingStatus(ls.lower()) if isinstance(ls, str) else ls for ls in data.get("listing_statuses", [])],
            min_lot_size=data.get("min_lot_size"),
            max_lot_size=data.get("max_lot_size"),
            keywords=data.get("keywords", []),
            exclude_keywords=data.get("exclude_keywords", []),
            max_days_on_market=data.get("max_days_on_market"),
            include_new_construction=data.get("include_new_construction", True),
            include_foreclosures=data.get("include_foreclosures", False),
            include_auctions=data.get("include_auctions", False),
            description=data.get("description", ""),
        )


@dataclass
class Alert:
    """Represents an alert configuration."""
    id: str = ""
    criteria_id: str = ""
    criteria_name: str = ""
    email_enabled: bool = True
    sms_enabled: bool = False
    trigger_interval_hours: int = 24
    trigger_interval_seconds: int = 86400
    is_active: bool = True
    last_triggered: Optional[str] = None
    description: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "criteria_id": self.criteria_id,
            "criteria_name": self.criteria_name,
            "email_enabled": self.email_enabled,
            "sms_enabled": self.sms_enabled,
            "trigger_interval_hours": self.trigger_interval_hours,
            "trigger_interval_seconds": self.trigger_interval_seconds,
            "is_active": self.is_active,
            "last_triggered": self.last_triggered,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Alert":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            criteria_id=data.get("criteria_id", ""),
            criteria_name=data.get("criteria_name", ""),
            email_enabled=data.get("email_enabled", True),
            sms_enabled=data.get("sms_enabled", False),
            trigger_interval_hours=data.get("trigger_interval_hours", 24),
            trigger_interval_seconds=data.get("trigger_interval_seconds", 86400),
            is_active=data.get("is_active", True),
            last_triggered=data.get("last_triggered"),
            description=data.get("description", ""),
        )


@dataclass
class AlertConfig:
    """Configuration for alert notifications."""
    email_enabled: bool = True
    email_address: str = ""
    sms_enabled: bool = False
    sms_number: str = ""
    sms_provider: str = "twilio"
    sms_recipients: list = field(default_factory=list)
    sms_account_sid: str = ""
    sms_auth_token: str = ""
    sms_from_number: str = ""
    email_smtp_server: str = ""
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_recipients: list = field(default_factory=list)
    id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "email_enabled": self.email_enabled,
            "email_address": self.email_address,
            "sms_enabled": self.sms_enabled,
            "sms_number": self.sms_number,
            "sms_provider": self.sms_provider,
            "sms_recipients": self.sms_recipients,
            "sms_account_sid": self.sms_account_sid,
            "sms_auth_token": self.sms_auth_token,
            "sms_from_number": self.sms_from_number,
            "email_smtp_server": self.email_smtp_server,
            "email_smtp_port": self.email_smtp_port,
            "email_username": self.email_username,
            "email_password": self.email_password,
            "email_recipients": self.email_recipients,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AlertConfig":
        """Create from dictionary."""
        return cls(
            id=data.get("id"),
            email_enabled=data.get("email_enabled", True),
            email_address=data.get("email_address", ""),
            sms_enabled=data.get("sms_enabled", False),
            sms_number=data.get("sms_number", ""),
            email_smtp_server=data.get("email_smtp_server", ""),
            email_smtp_port=data.get("email_smtp_port", 587),
            email_username=data.get("email_username", ""),
            email_password=data.get("email_password", ""),
            email_recipients=data.get("email_recipients", []),
        )
