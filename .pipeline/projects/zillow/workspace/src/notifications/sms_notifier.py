"""SMS notification handler for property alerts."""

from typing import List, Optional

from src.models import Property, Alert, AlertConfig


class SMSNotifier:
    """Handles sending SMS notifications for property alerts."""
    
    def __init__(self, config: AlertConfig):
        """
        Initialize the SMS notifier.
        
        Args:
            config: Alert configuration with SMS settings
        """
        self.config = config
        self.provider = config.sms_provider or "twilio"
        self.recipients = config.sms_recipients or []
        self.account_sid = config.sms_account_sid
        self.auth_token = config.sms_auth_token
        self.from_number = config.sms_from_number
        
        # Initialize Twilio client if needed
        if self.provider == "twilio":
            try:
                from twilio.rest import Client
                self.twilio_client = Client(self.account_sid, self.auth_token)
            except ImportError:
                print("Twilio library not installed. Install with: pip install twilio")
                self.twilio_client = None
        else:
            self.twilio_client = None
    
    def send_property_alert(self, alert: Alert, property: Property) -> bool:
        """
        Send an SMS notification for a property alert.
        
        Args:
            alert: The alert configuration
            property: The property that triggered the alert
            
        Returns:
            True if SMS was sent successfully, False otherwise
        """
        if not self.config.sms_enabled:
            return False
        
        if not self.recipients:
            return False
        
        if not self.from_number:
            print("SMS from number not configured")
            return False
        
        try:
            message_body = self._create_message(alert, property)
            
            if self.provider == "twilio" and self.twilio_client:
                for recipient in self.recipients:
                    self.twilio_client.messages.create(
                        body=message_body,
                        from_=self.from_number,
                        to=recipient
                    )
            else:
                # Fallback: log the message for manual sending
                print(f"SMS notification (provider: {self.provider}): {message_body}")
                print(f"Recipients: {self.recipients}")
            
            return True
            
        except Exception as e:
            print(f"Failed to send SMS notification: {e}")
            return False
    
    def _create_message(self, alert: Alert, property: Property) -> str:
        """Create an SMS message for the alert."""
        property_data = property
        
        # SMS has character limits, so keep it concise
        message = (
            f"🏠 Property Alert: ${property_data.price:,.0f}\n"
            f"{property_data.address}\n"
            f"{property_data.city}, {property_data.state}\n"
            f"{property_data.beds or '?'} bed, {property_data.baths or '?'} bath\n"
            f"{property_data.sqft or '?'} sqft\n"
            f"View: {property_data.listing_url[:50]}..."
        )
        
        # Truncate to 160 characters (standard SMS length)
        if len(message) > 160:
            message = message[:157] + "..."
        
        return message
