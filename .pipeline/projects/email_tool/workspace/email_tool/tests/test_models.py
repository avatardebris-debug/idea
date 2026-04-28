"""Tests for the Email model and to_eml method."""

import pytest
from datetime import datetime
from email_tool.models import Email, Rule, RuleMatch, RuleType, ActionType


class TestEmailToEML:
    """Tests for Email.to_eml() method."""
    
    def test_to_eml_minimal(self):
        """Test to_eml with minimal email data."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test Subject"
        )
        
        eml_str = email.to_eml()
        
        assert "From: sender@example.com" in eml_str
        assert "To: recipient@example.com" in eml_str
        assert "Subject: Test Subject" in eml_str
        assert "MIME-Version: 1.0" in eml_str
        assert "Message-ID:" in eml_str
    
    def test_to_eml_with_date(self):
        """Test to_eml with date header."""
        test_date = datetime(2024, 1, 15, 10, 30, 0)
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test Subject",
            date=test_date
        )
        
        eml_str = email.to_eml()
        
        assert "Date:" in eml_str
        assert "2024" in eml_str
        assert "Jan" in eml_str or "Jan" in eml_str
    
    def test_to_eml_with_plain_body(self):
        """Test to_eml with plain text body."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test Subject",
            body_plain="This is the plain text body."
        )
        
        eml_str = email.to_eml()
        
        assert "This is the plain text body." in eml_str
        assert "text/plain" in eml_str
    
    def test_to_eml_with_html_body(self):
        """Test to_eml with HTML body."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test Subject",
            body_html="<p>This is the HTML body.</p>"
        )
        
        eml_str = email.to_eml()
        
        assert "<p>This is the HTML body.</p>" in eml_str
        assert "text/html" in eml_str
    
    def test_to_eml_with_both_bodies(self):
        """Test to_eml with both plain and HTML bodies."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test Subject",
            body_plain="Plain text body",
            body_html="<p>HTML body</p>"
        )
        
        eml_str = email.to_eml()
        
        assert "Plain text body" in eml_str
        assert "<p>HTML body</p>" in eml_str
        assert "multipart/alternative" in eml_str
    
    def test_to_eml_with_multiple_recipients(self):
        """Test to_eml with multiple recipients."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient1@example.com", "recipient2@example.com"],
            subject="Test Subject"
        )
        
        eml_str = email.to_eml()
        
        assert "recipient1@example.com" in eml_str
        assert "recipient2@example.com" in eml_str
    
    def test_to_eml_with_raw_headers(self):
        """Test to_eml with custom headers."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test Subject",
            raw_headers={
                "X-Priority": "1",
                "Importance": "high"
            }
        )
        
        eml_str = email.to_eml()
        
        assert "X-Priority: 1" in eml_str
        assert "Importance: high" in eml_str
    
    def test_to_eml_empty_body(self):
        """Test to_eml with empty body."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test Subject",
            body_plain=""
        )
        
        eml_str = email.to_eml()
        
        # Should still be valid EML even with empty body
        assert "From: sender@example.com" in eml_str
        assert "Subject: Test Subject" in eml_str
    
    def test_to_eml_roundtrip(self):
        """Test that to_eml produces valid EML that can be parsed."""
        from email_tool.parser import EmailParser
        
        original_email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test Subject",
            body_plain="Test body",
            date=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        # Convert to EML
        eml_str = original_email.to_eml()
        
        # Parse it back
        parser = EmailParser()
        parsed_email = parser.parse_content(eml_str)
        
        # Verify key fields match
        assert parsed_email is not None
        assert parsed_email.from_addr == original_email.from_addr
        assert parsed_email.subject == original_email.subject
        assert parsed_email.body_plain == original_email.body_plain


class TestEmailModel:
    """Tests for Email model initialization and validation."""
    
    def test_email_creation(self):
        """Test basic email creation."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test"
        )
        
        assert email.from_addr == "sender@example.com"
        assert email.to_addrs == ["recipient@example.com"]
        assert email.subject == "Test"
        assert email.id is not None
        assert email.created_at is not None
    
    def test_email_to_addrs_string(self):
        """Test that to_addrs string is converted to list."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs="recipient@example.com",
            subject="Test"
        )
        
        assert isinstance(email.to_addrs, list)
        assert email.to_addrs == ["recipient@example.com"]
    
    def test_email_labels_default(self):
        """Test that labels defaults to empty list."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test"
        )
        
        assert email.labels == []
    
    def test_email_attachments_default(self):
        """Test that attachments defaults to empty list."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test"
        )
        
        assert email.attachments == []
    
    def test_email_raw_headers_default(self):
        """Test that raw_headers defaults to empty dict."""
        email = Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@example.com"],
            subject="Test"
        )
        
        assert email.raw_headers == {}


class TestRuleModel:
    """Tests for Rule model."""
    
    def test_rule_creation(self):
        """Test basic rule creation."""
        rule = Rule(
            name="Test Rule",
            rule_type=RuleType.FROM_EXACT,
            pattern="sender@example.com",
            priority=75
        )
        
        assert rule.name == "Test Rule"
        assert rule.rule_type == RuleType.FROM_EXACT
        assert rule.pattern == "sender@example.com"
        assert rule.priority == 75
    
    def test_rule_invalid_priority(self):
        """Test that invalid priority raises error."""
        with pytest.raises(ValueError):
            Rule(
                name="Test Rule",
                rule_type=RuleType.FROM_EXACT,
                pattern="sender@example.com",
                priority=150
            )
    
    def test_rule_missing_pattern(self):
        """Test that missing pattern raises error."""
        with pytest.raises(ValueError):
            Rule(
                name="Test Rule",
                rule_type=RuleType.FROM_EXACT,
                pattern=None
            )


class TestRuleMatchModel:
    """Tests for RuleMatch model."""
    
    def test_rule_match_properties(self):
        """Test RuleMatch properties."""
        rule = Rule(
            name="Test Rule",
            rule_type=RuleType.FROM_EXACT,
            pattern="sender@example.com"
        )
        
        match = RuleMatch(
            rule=rule,
            match_type="exact",
            matched_value="sender@example.com"
        )
        
        assert match.rule_name == "Test Rule"
        assert match.rule_type == RuleType.FROM_EXACT
        assert match.priority == 50
        assert match.category == "general"
        assert match.labels == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
