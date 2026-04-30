"""Email notification handler for property alerts."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from src.models import Property, Alert, AlertConfig


class EmailNotifier:
    """Handles sending email notifications for property alerts."""
    
    def __init__(self, config: AlertConfig):
        """
        Initialize the email notifier.
        
        Args:
            config: Alert configuration with SMTP settings
        """
        self.config = config
        self.smtp_server = config.email_smtp_server
        self.smtp_port = config.email_smtp_port
        self.username = config.email_username
        self.password = config.email_password
        self.recipients = config.email_recipients
    
    def send_property_alert(self, alert: Alert, property: Property) -> bool:
        """
        Send an email notification for a property alert.
        
        Args:
            alert: The alert configuration
            property: The property that triggered the alert
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.config.email_enabled:
            return False
        
        if not self.recipients:
            return False
        
        try:
            msg = self._create_message(alert, property)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            return False
    
    def _create_message(self, alert: Alert, property: Property) -> MIMEMultipart:
        """Create an email message for the alert."""
        property_data = property
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🏠 New Property Alert: {property_data.address}"
        msg["From"] = self.username or "property-alerts@example.com"
        msg["To"] = ", ".join(self.recipients)
        
        # Create HTML body
        html_body = self._create_html_body(alert, property)
        msg.attach(MIMEText(html_body, "html"))
        
        # Create plain text body
        text_body = self._create_text_body(alert, property)
        msg.attach(MIMEText(text_body, "plain"))
        
        return msg
    
    def _create_html_body(self, alert: Alert, property: Property) -> str:
        """Create HTML email body."""
        property_data = property
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 15px; text-align: center; }}
                .property-info {{ background-color: #f9f9f9; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .price {{ font-size: 24px; color: #4CAF50; font-weight: bold; }}
                .details {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
                .detail-item {{ background-color: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }}
                .detail-label {{ font-weight: bold; color: #555; }}
                .detail-value {{ color: #333; }}
                .cta-button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 15px 0; }}
                .footer {{ font-size: 12px; color: #777; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 New Property Alert</h1>
                </div>
                
                <p>Hello,</p>
                
                <p>A new property matching your criteria has been found!</p>
                
                <div class="property-info">
                    <h2 style="margin-top: 0;">{property_data.address}</h2>
                    <p class="price">${property_data.price:,.0f}</p>
                    
                    <div class="details">
                        <div class="detail-item">
                            <div class="detail-label">🛏️ Bedrooms</div>
                            <div class="detail-value">{property_data.beds or 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">🚿 Bathrooms</div>
                            <div class="detail-value">{property_data.baths or 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">📐 Square Feet</div>
                            <div class="detail-value">{property_data.sqft or 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">🏡 Property Type</div>
                            <div class="detail-value">{property_data.property_type.value.title()}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">📅 Listed</div>
                            <div class="detail-value">{property_data.listing_date.strftime('%Y-%m-%d')}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">📍 Location</div>
                            <div class="detail-value">{property_data.city}, {property_data.state} {property_data.zip_code}</div>
                        </div>
                    </div>
                    
                    {self._create_features_section(property_data)}
                </div>
                
                <a href="{property_data.listing_url}" class="cta-button" target="_blank">View on {property_data.source.title()}</a>
                
                <div class="footer">
                    <p>You received this alert because it matches your saved criteria: <strong>{alert.criteria_name}</strong></p>
                    <p>Generated on {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _create_text_body(self, alert: Alert, property: Property) -> str:
        """Create plain text email body."""
        property_data = property
        
        text = f"""
🏠 NEW PROPERTY ALERT

{property_data.address}
{property_data.city}, {property_data.state} {property_data.zip_code}

💰 Price: ${property_data.price:,.0f}

📊 Details:
  • Bedrooms: {property_data.beds or 'N/A'}
  • Bathrooms: {property_data.baths or 'N/A'}
  • Square Feet: {property_data.sqft or 'N/A'}
  • Property Type: {property_data.property_type.value.title()}
  • Listed: {property_data.listing_date.strftime('%Y-%m-%d')}
  • Source: {property_data.source.title()}

🔗 View Listing: {property_data.listing_url}

---
This alert matches your criteria: {alert.criteria_name}
Generated on {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""
        return text
    
    def _create_features_section(self, property_data: Property) -> str:
        """Create features section for HTML body."""
        if not property_data.features:
            return ""
        
        features_html = "<h3>Features</h3><ul>"
        for feature in property_data.features:
            features_html += f"<li>{feature}</li>"
        features_html += "</ul>"
        return features_html
