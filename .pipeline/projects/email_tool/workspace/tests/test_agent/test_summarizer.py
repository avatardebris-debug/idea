"""Tests for the inbox summarizer module."""

import pytest

from email_tool.agent.summarizer import InboxSummarizer
from email_tool.agent.base import AgentResult


class TestInboxSummarizer:
    """Test cases for InboxSummarizer."""
    
    def test_init(self):
        """Test initialization."""
        summarizer = InboxSummarizer()
        
        assert summarizer is not None
    
    def test_summarize_inbox_empty_emails(self):
        """Test summarization with empty email list."""
        summarizer = InboxSummarizer()
        
        result = summarizer.summarize_inbox(
            emails=[],
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert result.data == "No emails in inbox."
        assert result.metadata["total_emails"] == 0
    
    def test_summarize_inbox_with_emails(self):
        """Test summarization with emails."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender1@example.com",
                "subject": "Invoice #1",
                "date": "2024-01-01",
                "category": "invoices"
            },
            {
                "id": "2",
                "from": "sender2@example.com",
                "subject": "Meeting",
                "date": "2024-01-02",
                "category": "work"
            }
        ]
        
        rules = [
            {
                "name": "invoice_rule",
                "type": "subject_contains",
                "pattern": "invoice",
                "priority": 80,
                "category": "invoices"
            }
        ]
        
        matches = [
            {
                "email_id": "1",
                "rule_name": "invoice_rule",
                "confidence": 0.95
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=rules,
            matches=matches
        )
        
        assert result.success is True
        assert "2 emails" in result.data
        assert "2 categorized" in result.data
        assert "0 uncategorized" in result.data
    
    def test_summarize_inbox_with_rules(self):
        """Test summarization with rules."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        rules = [
            {
                "name": "work_rule",
                "type": "subject_contains",
                "pattern": "work",
                "priority": 80,
                "category": "work"
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=rules,
            matches=[]
        )
        
        assert result.success is True
        assert "1 active rule" in result.data
    
    def test_summarize_inbox_with_matches(self):
        """Test summarization with matches."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        matches = [
            {
                "email_id": "1",
                "rule_name": "work_rule",
                "confidence": 0.95
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=matches
        )
        
        assert result.success is True
        assert "1 matched" in result.data
    
    def test_summarize_inbox_with_all_data(self):
        """Test summarization with all data types."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender1@example.com",
                "subject": "Invoice #1",
                "date": "2024-01-01",
                "category": "invoices"
            },
            {
                "id": "2",
                "from": "sender2@example.com",
                "subject": "Meeting",
                "date": "2024-01-02",
                "category": "work"
            },
            {
                "id": "3",
                "from": "sender3@example.com",
                "subject": "Newsletter",
                "date": "2024-01-03",
                "category": "uncategorized"
            }
        ]
        
        rules = [
            {
                "name": "invoice_rule",
                "type": "subject_contains",
                "pattern": "invoice",
                "priority": 80,
                "category": "invoices"
            },
            {
                "name": "work_rule",
                "type": "subject_contains",
                "pattern": "meeting",
                "priority": 70,
                "category": "work"
            }
        ]
        
        matches = [
            {
                "email_id": "1",
                "rule_name": "invoice_rule",
                "confidence": 0.95
            },
            {
                "email_id": "2",
                "rule_name": "work_rule",
                "confidence": 0.9
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=rules,
            matches=matches
        )
        
        assert result.success is True
        assert "3 emails" in result.data
        assert "2 active rules" in result.data
        assert "2 matched" in result.data
        assert "2 categorized" in result.data
        assert "1 uncategorized" in result.data
    
    def test_summarize_inbox_with_large_email_count(self):
        """Test summarization with large email count."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": str(i),
                "from": f"sender{i}@example.com",
                "subject": f"Test {i}",
                "date": "2024-01-01",
                "category": "work"
            }
            for i in range(100)
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "100 emails" in result.data
    
    def test_summarize_inbox_with_no_categories(self):
        """Test summarization with no categories."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": None
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "1 uncategorized" in result.data
    
    def test_summarize_inbox_with_mixed_categories(self):
        """Test summarization with mixed categories."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender1@example.com",
                "subject": "Invoice",
                "date": "2024-01-01",
                "category": "invoices"
            },
            {
                "id": "2",
                "from": "sender2@example.com",
                "subject": "Meeting",
                "date": "2024-01-02",
                "category": "work"
            },
            {
                "id": "3",
                "from": "sender3@example.com",
                "subject": "Newsletter",
                "date": "2024-01-03",
                "category": "uncategorized"
            },
            {
                "id": "4",
                "from": "sender4@example.com",
                "subject": "Personal",
                "date": "2024-01-04",
                "category": "personal"
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "1 invoices" in result.data
        assert "1 work" in result.data
        assert "1 personal" in result.data
        assert "1 uncategorized" in result.data
    
    def test_summarize_inbox_with_empty_rules(self):
        """Test summarization with empty rules list."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "0 active rules" in result.data
    
    def test_summarize_inbox_with_empty_matches(self):
        """Test summarization with empty matches list."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "0 matched" in result.data
    
    def test_summarize_inbox_with_special_characters(self):
        """Test summarization with special characters in data."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test with special chars: @#$%",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "1 emails" in result.data
    
    def test_summarize_inbox_with_unicode_characters(self):
        """Test summarization with unicode characters."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test with unicode: 你好 🌍",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "1 emails" in result.data
    
    def test_summarize_inbox_with_long_subjects(self):
        """Test summarization with long subjects."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "This is a very long subject line that contains a lot of information and might be too long for a summary",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "1 emails" in result.data
    
    def test_summarize_inbox_with_duplicate_emails(self):
        """Test summarization with duplicate emails."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            },
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "2 emails" in result.data
    
    def test_summarize_inbox_with_none_values(self):
        """Test summarization with None values."""
        summarizer = InboxSummarizer()
        
        emails = [
            {
                "id": None,
                "from": None,
                "subject": None,
                "date": None,
                "category": None
            }
        ]
        
        result = summarizer.summarize_inbox(
            emails=emails,
            rules=[],
            matches=[]
        )
        
        assert result.success is True
        assert "1 emails" in result.data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
