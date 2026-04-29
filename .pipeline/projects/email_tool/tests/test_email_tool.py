"""Test suite for Email Tool.

This test suite covers all major components of the Email Tool application,
including configuration, email processing, organization, and dashboard functionality.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add the workspace to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "workspace"))

from email_tool.config import EmailToolConfig, load_config, save_config
from email_tool.logging_config import get_logger, setup_logging
from email_tool.processor import EmailProcessor
from email_tool.organizer import EmailOrganizer
from email_tool.rules import RuleEngine, Rule
from email_tool.dashboard.app import Dashboard, create_app


class TestEmailToolConfig:
    """Tests for EmailToolConfig class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = EmailToolConfig()
        
        assert config.email_dir == "Mail/inbox"
        assert config.organized_dir == "Mail/organized"
        assert config.rules_file == "Mail/rules.yaml"
        assert config.log_level == "INFO"
        assert config.log_file == "logs/email_tool.log"
        assert config.dashboard_port == 8000
        assert config.dashboard_host == "127.0.0.1"
        assert config.sync_interval == 300
        assert config.max_emails_per_batch == 100
    
    def test_from_dict(self):
        """Test configuration from dictionary."""
        data = {
            "email_dir": "/custom/inbox",
            "organized_dir": "/custom/organized",
            "log_level": "DEBUG"
        }
        
        config = EmailToolConfig.from_dict(data)
        
        assert config.email_dir == "/custom/inbox"
        assert config.organized_dir == "/custom/organized"
        assert config.log_level == "DEBUG"
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        config = EmailToolConfig()
        config.log_level = "DEBUG"
        
        data = config.to_dict()
        
        assert "email_tool" in data
        assert data["email_tool"]["log_level"] == "DEBUG"
    
    def test_get_base_path(self):
        """Test base path resolution."""
        config = EmailToolConfig()
        config.email_dir = "~/test_inbox"
        
        base_path = config.get_base_path()
        
        assert base_path.exists()
        assert "test_inbox" in str(base_path)


class TestEmailProcessor:
    """Tests for EmailProcessor class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_scan_emails(self, temp_dir):
        """Test email scanning functionality."""
        # Create test email files
        inbox_dir = temp_dir / "inbox"
        inbox_dir.mkdir()
        
        email1 = inbox_dir / "email1.eml"
        email1.write_text("From: test@example.com\nSubject: Test\n\nTest body")
        
        email2 = inbox_dir / "email2.eml"
        email2.write_text("From: spam@example.com\nSubject: Spam\n\nSpam body")
        
        processor = EmailProcessor(str(inbox_dir))
        emails = processor.scan_emails()
        
        assert len(emails) == 2
        assert emails[0]["filename"] == "email1.eml"
        assert emails[0]["sender"] == "test@example.com"
        assert emails[0]["subject"] == "Test"
    
    def test_parse_email(self, temp_dir):
        """Test email parsing functionality."""
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test Subject
Date: Mon, 1 Jan 2024 12:00:00 +0000

This is the email body."""
        
        processor = EmailProcessor(str(temp_dir))
        email = processor.parse_email(email_content)
        
        assert email["sender"] == "sender@example.com"
        assert email["recipient"] == "recipient@example.com"
        assert email["subject"] == "Test Subject"
        assert email["date"] == "Mon, 1 Jan 2024 12:00:00 +0000"
        assert email["body"] == "This is the email body."
    
    def test_get_email_stats(self, temp_dir):
        """Test email statistics calculation."""
        inbox_dir = temp_dir / "inbox"
        inbox_dir.mkdir()
        
        # Create test emails
        for i in range(10):
            email = inbox_dir / f"email{i}.eml"
            email.write_text(f"From: test{i}@example.com\nSubject: Test {i}\n\nBody {i}")
        
        processor = EmailProcessor(str(inbox_dir))
        stats = processor.get_stats()
        
        assert stats["total_emails"] == 10
        assert stats["unread_emails"] == 10
        assert stats["oldest_email"] is not None
        assert stats["newest_email"] is not None


class TestEmailOrganizer:
    """Tests for EmailOrganizer class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_organize_emails(self, temp_dir):
        """Test email organization functionality."""
        # Setup directories
        inbox_dir = temp_dir / "inbox"
        organized_dir = temp_dir / "organized"
        inbox_dir.mkdir()
        organized_dir.mkdir()
        
        # Create test email
        email_file = inbox_dir / "test.eml"
        email_file.write_text("From: work@example.com\nSubject: Work Meeting\n\nMeeting body")
        
        # Create rules
        rules = [
            {
                "name": "work",
                "patterns": ["work", "meeting"],
                "priority": 1
            }
        ]
        
        organizer = EmailOrganizer(
            email_dir=str(inbox_dir),
            organized_dir=str(organized_dir),
            rules=rules
        )
        
        # Organize emails
        organizer.organize()
        
        # Verify organization
        work_dir = organized_dir / "work"
        assert work_dir.exists()
        assert len(list(work_dir.glob("*.eml"))) == 1
    
    def test_move_email(self, temp_dir):
        """Test email moving functionality."""
        inbox_dir = temp_dir / "inbox"
        organized_dir = temp_dir / "organized"
        inbox_dir.mkdir()
        organized_dir.mkdir()
        
        email_file = inbox_dir / "test.eml"
        email_file.write_text("Test email")
        
        organizer = EmailOrganizer(
            email_dir=str(inbox_dir),
            organized_dir=str(organized_dir)
        )
        
        # Move email
        organizer.move_email("test.eml", "work")
        
        # Verify move
        assert not email_file.exists()
        assert (organized_dir / "work" / "test.eml").exists()
    
    def test_get_organizer_stats(self, temp_dir):
        """Test organizer statistics."""
        inbox_dir = temp_dir / "inbox"
        organized_dir = temp_dir / "organized"
        inbox_dir.mkdir()
        organized_dir.mkdir()
        
        # Create test emails
        for i in range(5):
            email = inbox_dir / f"email{i}.eml"
            email.write_text(f"Test {i}")
        
        organizer = EmailOrganizer(
            email_dir=str(inbox_dir),
            organized_dir=str(organized_dir)
        )
        
        stats = organizer.get_stats()
        
        assert stats["total_emails"] == 5
        assert stats["organized_emails"] == 0
        assert stats["categories"] == {}


class TestRuleEngine:
    """Tests for RuleEngine class."""
    
    def test_match_patterns(self):
        """Test pattern matching functionality."""
        rules = [
            {
                "name": "work",
                "patterns": ["work", "meeting", "business"],
                "priority": 1
            }
        ]
        
        engine = RuleEngine(rules)
        
        # Test subject matching
        assert engine.match_patterns("work meeting", ["work", "meeting"])
        assert engine.match_patterns("business call", ["work", "meeting"])
        assert not engine.match_patterns("personal email", ["work", "meeting"])
        
        # Test sender matching
        assert engine.match_patterns("work@example.com", ["work", "meeting"])
        assert not engine.match_patterns("personal@example.com", ["work", "meeting"])
    
    def test_get_category(self):
        """Test category determination."""
        rules = [
            {
                "name": "work",
                "patterns": ["work", "meeting"],
                "priority": 1
            },
            {
                "name": "personal",
                "patterns": ["personal", "family"],
                "priority": 2
            }
        ]
        
        engine = RuleEngine(rules)
        
        assert engine.get_category("work meeting", "work@example.com") == "work"
        assert engine.get_category("family call", "personal@example.com") == "personal"
        assert engine.get_category("unknown", "unknown@example.com") is None
    
    def test_priority_ordering(self):
        """Test that higher priority rules are matched first."""
        rules = [
            {
                "name": "low",
                "patterns": ["test"],
                "priority": 1
            },
            {
                "name": "high",
                "patterns": ["test"],
                "priority": 2
            }
        ]
        
        engine = RuleEngine(rules)
        
        # Both rules match, but high priority should win
        category = engine.get_category("test", "test@example.com")
        assert category == "high"


class TestDashboard:
    """Tests for Dashboard application."""
    
    @pytest.fixture
    def app(self):
        """Create test application."""
        return create_app()
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_stats_endpoint(self, client):
        """Test statistics endpoint."""
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_emails" in data
        assert "categories" in data
    
    def test_categories_endpoint(self, client):
        """Test categories endpoint."""
        response = client.get("/api/categories")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_activity_endpoint(self, client):
        """Test activity endpoint."""
        response = client.get("/api/activity")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert "checks" in data


class TestLogging:
    """Tests for logging configuration."""
    
    def test_setup_logging(self):
        """Test logging setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            
            setup_logging(
                log_level="DEBUG",
                log_file=str(log_file)
            )
            
            logger = get_logger()
            logger.info("Test message")
            
            assert log_file.exists()
            assert log_file.stat().st_size > 0
    
    def test_logger_format(self):
        """Test logger format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            
            setup_logging(
                log_level="DEBUG",
                log_file=str(log_file)
            )
            
            logger = get_logger()
            logger.info("Test message")
            
            with open(log_file) as f:
                log_content = f.read()
            
            assert "Test message" in log_content
            assert "INFO" in log_content


class TestIntegration:
    """Integration tests for complete workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_full_workflow(self, temp_dir):
        """Test complete email organization workflow."""
        # Setup directories
        inbox_dir = temp_dir / "inbox"
        organized_dir = temp_dir / "organized"
        inbox_dir.mkdir()
        organized_dir.mkdir()
        
        # Create test emails
        for i in range(5):
            email = inbox_dir / f"email{i}.eml"
            email.write_text(f"From: work{i}@example.com\nSubject: Work Meeting {i}\n\nBody {i}")
        
        # Create rules
        rules = [
            {
                "name": "work",
                "patterns": ["work", "meeting"],
                "priority": 1
            }
        ]
        
        # Initialize components
        config = EmailToolConfig(
            email_dir=str(inbox_dir),
            organized_dir=str(organized_dir)
        )
        
        processor = EmailProcessor(str(inbox_dir))
        organizer = EmailOrganizer(
            email_dir=str(inbox_dir),
            organized_dir=str(organized_dir),
            rules=rules
        )
        
        # Process and organize
        emails = processor.scan_emails()
        assert len(emails) == 5
        
        organizer.organize()
        
        # Verify results
        work_dir = organized_dir / "work"
        assert work_dir.exists()
        assert len(list(work_dir.glob("*.eml"))) == 5
        
        # Verify inbox is empty
        assert len(list(inbox_dir.glob("*.eml"))) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
