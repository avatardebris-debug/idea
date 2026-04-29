"""Tests for the email categorizer module."""

import pytest
from unittest.mock import MagicMock, patch

from email_tool.agent.categorizer import EmailCategorizer
from email_tool.agent.base import AgentResult, AgentContext
from email_tool.agent.llm_agent import LLMAgent
from email_tool.models import Rule


class TestEmailCategorizer:
    """Test cases for EmailCategorizer."""
    
    def test_init_default_llm_agent(self):
        """Test initialization with default LLM agent."""
        categorizer = EmailCategorizer()
        
        assert isinstance(categorizer.llm_agent, LLMAgent)
    
    def test_init_custom_llm_agent(self):
        """Test initialization with custom LLM agent."""
        custom_agent = MagicMock(spec=LLMAgent)
        categorizer = EmailCategorizer(llm_agent=custom_agent)
        
        assert categorizer.llm_agent == custom_agent
    
    def test_categorize_emails_empty_emails(self):
        """Test categorization with empty email list."""
        categorizer = EmailCategorizer()
        
        result = categorizer.categorize_emails(
            emails=[],
            rules=[]
        )
        
        assert result.success is True
        assert result.data == []
        assert "No emails to categorize" in result.metadata.get("warnings", [])
    
    def test_categorize_emails_empty_rules(self):
        """Test categorization with no rules."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        result = categorizer.categorize_emails(
            emails=emails,
            rules=[]
        )
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["category"] == "uncategorized"
    
    def test_categorize_emails_with_rules(self):
        """Test categorization with rules."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Invoice #12345",
                "date": "2024-01-01",
                "body": "Please find attached invoice"
            }
        ]
        
        rules = [
            Rule(
                name="invoice_rule",
                rule_type="subject_contains",
                pattern="invoice",
                priority=80,
                category="invoices"
            )
        ]
        
        with patch.object(categorizer.llm_agent, 'suggest_categories', return_value=AgentResult(
            success=True,
            data=[
                {
                    "email_id": "1",
                    "category": "invoices",
                    "confidence": 0.95
                }
            ],
            metadata={}
        )):
            result = categorizer.categorize_emails(
                emails=emails,
                rules=rules
            )
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["category"] == "invoices"
    
    def test_categorize_emails_llm_failure(self):
        """Test categorization when LLM fails."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(categorizer.llm_agent, 'suggest_categories', return_value=AgentResult(
            success=False,
            data=None,
            error_message="LLM categorization failed"
        )):
            result = categorizer.categorize_emails(
                emails=emails,
                rules=[]
            )
        
        assert result.success is False
        assert "LLM categorization failed" in result.error_message
    
    def test_categorize_emails_with_context(self):
        """Test categorization with context."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        context = AgentContext(
            conversation_id="test_conversation",
            turn=1
        )
        
        with patch.object(categorizer.llm_agent, 'suggest_categories') as mock_suggest:
            categorizer.categorize_emails(
                emails=emails,
                rules=[],
                context=context
            )
            
            # Verify context was passed to LLM
            mock_suggest.assert_called_once()
            call_args = mock_suggest.call_args
            assert call_args[1].get("context") == context
    
    def test_categorize_emails_metadata_includes_counts(self):
        """Test that metadata includes categorization counts."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(categorizer.llm_agent, 'suggest_categories', return_value=AgentResult(
            success=True,
            data=[
                {
                    "email_id": "1",
                    "category": "work",
                    "confidence": 0.9
                }
            ],
            metadata={}
        )):
            result = categorizer.categorize_emails(
                emails=emails,
                rules=[]
            )
        
        assert result.metadata["categorized_count"] == 1
        assert result.metadata["uncategorized_count"] == 0
        assert result.metadata["total_emails"] == 1
    
    def test_categorize_emails_with_multiple_emails(self):
        """Test categorization with multiple emails."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender1@example.com",
                "subject": "Invoice #1",
                "date": "2024-01-01",
                "body": "Invoice 1"
            },
            {
                "id": "2",
                "from": "sender2@example.com",
                "subject": "Meeting",
                "date": "2024-01-02",
                "body": "Meeting body"
            },
            {
                "id": "3",
                "from": "sender3@example.com",
                "subject": "Newsletter",
                "date": "2024-01-03",
                "body": "Newsletter body"
            }
        ]
        
        with patch.object(categorizer.llm_agent, 'suggest_categories', return_value=AgentResult(
            success=True,
            data=[
                {
                    "email_id": "1",
                    "category": "invoices",
                    "confidence": 0.95
                },
                {
                    "email_id": "2",
                    "category": "work",
                    "confidence": 0.9
                },
                {
                    "email_id": "3",
                    "category": "uncategorized",
                    "confidence": 0.5
                }
            ],
            metadata={}
        )):
            result = categorizer.categorize_emails(
                emails=emails,
                rules=[]
            )
        
        assert result.success is True
        assert len(result.data) == 3
        assert result.metadata["categorized_count"] == 2
        assert result.metadata["uncategorized_count"] == 1
    
    def test_categorize_emails_with_custom_prompt(self):
        """Test categorization with custom prompt."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        custom_prompt = "Custom prompt for categorization"
        
        with patch.object(categorizer.llm_agent, 'suggest_categories') as mock_suggest:
            categorizer.categorize_emails(
                emails=emails,
                rules=[],
                prompt=custom_prompt
            )
            
            # Verify custom prompt was used
            call_args = mock_suggest.call_args
            assert call_args[1].get("prompt") == custom_prompt
    
    def test_categorize_emails_with_existing_categories(self):
        """Test categorization with existing categories."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(categorizer.llm_agent, 'suggest_categories', return_value=AgentResult(
            success=True,
            data=[
                {
                    "email_id": "1",
                    "category": "work",
                    "confidence": 0.8
                }
            ],
            metadata={}
        )):
            result = categorizer.categorize_emails(
                emails=emails,
                rules=[],
                existing_categories=["work", "personal"]
            )
        
        assert result.success is True
        assert result.data[0]["category"] == "work"
    
    def test_categorize_emails_with_few_shot_examples(self):
        """Test categorization with few-shot examples enabled."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(categorizer.llm_agent, 'suggest_categories') as mock_suggest:
            categorizer.categorize_emails(
                emails=emails,
                rules=[]
            )
            
            # Verify few-shot examples are included
            call_args = mock_suggest.call_args
            assert "few_shot" in call_args[1]
            assert call_args[1]["few_shot"] is True
    
    def test_categorize_emails_with_low_confidence(self):
        """Test categorization with low confidence scores."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(categorizer.llm_agent, 'suggest_categories', return_value=AgentResult(
            success=True,
            data=[
                {
                    "id": "1",
                    "category": "uncategorized",
                    "matched_rule": None,
                    "confidence": 0.3
                }
            ],
            metadata={}
        )):
            result = categorizer.categorize_emails(
                emails=emails,
                rules=[]
            )
        
        assert result.success is True
        assert result.data[0]["confidence"] == 0.3
        assert result.data[0]["category"] == "uncategorized"
    
    def test_categorize_emails_with_rule_matching(self):
        """Test categorization with rule matching."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Invoice #12345",
                "date": "2024-01-01",
                "body": "Please find attached invoice"
            }
        ]
        
        rules = [
            Rule(
                name="invoice_rule",
                rule_type="subject_contains",
                pattern="invoice",
                priority=80,
                category="invoices"
            )
        ]
        
        with patch.object(categorizer.llm_agent, 'suggest_categories', return_value=AgentResult(
            success=True,
            data=[
                {
                    "id": "1",
                    "category": "invoices",
                    "matched_rule": "invoice_rule",
                    "confidence": 0.95
                }
            ],
            metadata={}
        )):
            result = categorizer.categorize_emails(
                emails=emails,
                rules=rules
            )
        
        assert result.success is True
        assert result.data[0]["matched_rule"] == "invoice_rule"
    
    def test_categorize_emails_with_empty_subject(self):
        """Test categorization with empty subject."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(categorizer.llm_agent, 'suggest_categories', return_value=AgentResult(
            success=True,
            data=[
                {
                    "id": "1",
                    "category": "uncategorized",
                    "matched_rule": None,
                    "confidence": 0.5
                }
            ],
            metadata={}
        )):
            result = categorizer.categorize_emails(
                emails=emails,
                rules=[]
            )
        
        assert result.success is True
    
    def test_categorize_emails_with_empty_body(self):
        """Test categorization with empty body."""
        categorizer = EmailCategorizer()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test Subject",
                "date": "2024-01-01",
                "body": ""
            }
        ]
        
        with patch.object(categorizer.llm_agent, 'categorize_emails', return_value=AgentResult(
            success=True,
            data=[
                {
                    "id": "1",
                    "category": "uncategorized",
                    "matched_rule": None,
                    "confidence": 0.5
                }
            ],
            metadata={}
        )):
            result = categorizer.categorize_emails(
                emails=emails,
                rules=[]
            )
        
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
