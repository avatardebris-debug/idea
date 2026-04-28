"""Pytest fixtures for email_tool tests."""

import pytest
from datetime import datetime
from email_tool.models import Email, Rule, RuleType, RuleMatch, ActionType


@pytest.fixture
def sample_email():
    """Create a sample email for testing."""
    return Email(
        id="test_email_001",
        from_addr="sender@example.com",
        to_addrs=["recipient@test.com"],
        subject="Test Email Subject",
        date=datetime(2024, 3, 15, 10, 30, 0),
        body_plain="This is the plain text body of the test email.",
        body_html="<html><body>This is the HTML body of the test email.</body></html>",
        attachments=[],
        raw_headers={"Message-ID": "<test@example.com>"},
        labels=["inbox"],
        source_path="/tmp/test_email.eml"
    )


@pytest.fixture
def sample_rule_match():
    """Create a sample rule match for testing."""
    rule = Rule(
        id="test_rule_001",
        name="test_rule",
        rule_type=RuleType.SUBJECT_EXACT,
        pattern="Test Email",
        priority=50,
        category="general",
        labels=["test"]
    )
    
    return RuleMatch(
        rule=rule,
        match_type=RuleType.SUBJECT_EXACT,
        matched_value="Test Email",
        confidence=0.95
    )
