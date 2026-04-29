"""Tests for the rule generator module."""

import pytest
from unittest.mock import MagicMock, patch

from email_tool.agent.rule_generator import RuleGenerator
from email_tool.agent.base import AgentResult, AgentContext
from email_tool.agent.llm_agent import LLMAgent


class TestRuleGenerator:
    """Test cases for RuleGenerator."""
    
    def test_init_default_llm_agent(self):
        """Test initialization with default LLM agent."""
        generator = RuleGenerator()
        
        assert isinstance(generator.llm_agent, LLMAgent)
    
    def test_init_custom_llm_agent(self):
        """Test initialization with custom LLM agent."""
        custom_agent = MagicMock(spec=LLMAgent)
        generator = RuleGenerator(llm_agent=custom_agent)
        
        assert generator.llm_agent == custom_agent
    
    def test_generate_rules_empty_description(self):
        """Test rule generation with empty description."""
        generator = RuleGenerator()
        
        result = generator.generate_rules(
            description="",
            sample_emails=[]
        )
        
        assert result.success is False
        assert "description" in result.error_message.lower()
    
    def test_generate_rules_no_sample_emails(self):
        """Test rule generation without sample emails."""
        generator = RuleGenerator()
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=True,
            data=[],
            metadata={}
        )):
            result = generator.generate_rules(
                description="Create rules for invoices",
                sample_emails=[]
            )
        
        # Should still succeed but with warning
        assert result.success is True
        assert "No sample emails provided" in result.metadata.get("warnings", [])
    
    def test_generate_rules_valid_request(self):
        """Test rule generation with valid request."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Invoice #12345",
                "date": "2024-01-01",
                "body": "Please find attached invoice"
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=True,
            data=[
                {
                    "name": "invoice_rule",
                    "type": "subject_contains",
                    "pattern": "invoice",
                    "priority": 80,
                    "category": "invoices"
                }
            ],
            metadata={}
        )):
            result = generator.generate_rules(
                description="Create rules for invoices",
                sample_emails=sample_emails
            )
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["name"] == "invoice_rule"
    
    def test_generate_rules_llm_failure(self):
        """Test rule generation when LLM fails."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=False,
            data=None,
            error_message="LLM generation failed"
        )):
            result = generator.generate_rules(
                description="Create rules",
                sample_emails=sample_emails
            )
        
        assert result.success is False
        assert "LLM generation failed" in result.error_message
    
    def test_generate_rules_with_context(self):
        """Test rule generation with context."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
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
        
        with patch.object(generator.llm_agent, 'generate_rules') as mock_generate:
            generator.generate_rules(
                description="Create rules",
                sample_emails=sample_emails,
                context=context
            )
            
            # Verify context was passed to LLM
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            assert call_args[1].get("context") == context
    
    def test_generate_rules_metadata_includes_counts(self):
        """Test that metadata includes rule counts."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=True,
            data=[
                {"name": "rule1", "type": "from_exact", "pattern": "test@example.com", "priority": 50, "category": "test"},
                {"name": "rule2", "type": "subject_contains", "pattern": "test", "priority": 60, "category": "test"}
            ],
            metadata={}
        )):
            result = generator.generate_rules(
                description="Create rules",
                sample_emails=sample_emails
            )
        
        assert result.metadata["generated_count"] == 2
        assert result.metadata["description"] == "Create rules"
    
    def test_generate_rules_with_priority_adjustment(self):
        """Test rule generation with priority adjustment."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Urgent Invoice",
                "date": "2024-01-01",
                "body": "Urgent invoice"
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=True,
            data=[
                {
                    "name": "urgent_invoice",
                    "type": "subject_contains",
                    "pattern": "urgent",
                    "priority": 90,
                    "category": "urgent"
                }
            ],
            metadata={}
        )):
            result = generator.generate_rules(
                description="Create rules for urgent invoices",
                sample_emails=sample_emails
            )
        
        assert result.success is True
        assert result.data[0]["priority"] == 90
    
    def test_generate_rules_with_description_in_metadata(self):
        """Test that description is included in metadata."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=True,
            data=[],
            metadata={}
        )):
            result = generator.generate_rules(
                description="Custom description for testing",
                sample_emails=sample_emails
            )
        
        assert result.metadata["description"] == "Custom description for testing"
    
    def test_generate_rules_with_few_shot_examples(self):
        """Test rule generation with few-shot examples enabled."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Invoice #12345",
                "date": "2024-01-01",
                "body": "Please find attached invoice"
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules') as mock_generate:
            generator.generate_rules(
                description="Create rules for invoices",
                sample_emails=sample_emails
            )
            
            # Verify few-shot examples are included
            call_args = mock_generate.call_args
            assert "few_shot" in call_args[1]
            assert call_args[1]["few_shot"] is True
    
    def test_generate_rules_with_custom_prompt(self):
        """Test rule generation with custom prompt."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        custom_prompt = "Custom prompt for rule generation"
        
        with patch.object(generator.llm_agent, 'generate_rules') as mock_generate:
            generator.generate_rules(
                description="Create rules",
                sample_emails=sample_emails,
                custom_prompt=custom_prompt
            )
            
            # Verify custom prompt was used
            call_args = mock_generate.call_args
            assert call_args[1].get("custom_prompt") == custom_prompt
    
    def test_generate_rules_with_invalid_email_format(self):
        """Test rule generation with invalid email format."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "invalid_email",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=True,
            data=[],
            metadata={}
        )):
            result = generator.generate_rules(
                description="Create rules",
                sample_emails=sample_emails
            )
        
        # Should still succeed, validation happens at LLM level
        assert result.success is True
    
    def test_generate_rules_with_empty_subject(self):
        """Test rule generation with empty subject."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=True,
            data=[],
            metadata={}
        )):
            result = generator.generate_rules(
                description="Create rules",
                sample_emails=sample_emails
            )
        
        assert result.success is True
    
    def test_generate_rules_with_empty_body(self):
        """Test rule generation with empty body."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Test Subject",
                "date": "2024-01-01",
                "body": ""
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=True,
            data=[],
            metadata={}
        )):
            result = generator.generate_rules(
                description="Create rules",
                sample_emails=sample_emails
            )
        
        assert result.success is True
    
    def test_generate_rules_with_multiple_emails(self):
        """Test rule generation with multiple sample emails."""
        generator = RuleGenerator()
        
        sample_emails = [
            {
                "from": "sender1@example.com",
                "subject": "Invoice #1",
                "date": "2024-01-01",
                "body": "Invoice 1"
            },
            {
                "from": "sender2@example.com",
                "subject": "Invoice #2",
                "date": "2024-01-02",
                "body": "Invoice 2"
            },
            {
                "from": "sender3@example.com",
                "subject": "Invoice #3",
                "date": "2024-01-03",
                "body": "Invoice 3"
            }
        ]
        
        with patch.object(generator.llm_agent, 'generate_rules', return_value=AgentResult(
            success=True,
            data=[
                {
                    "name": "invoice_rule",
                    "type": "subject_contains",
                    "pattern": "invoice",
                    "priority": 80,
                    "category": "invoices"
                }
            ],
            metadata={}
        )):
            result = generator.generate_rules(
                description="Create rules for invoices",
                sample_emails=sample_emails
            )
        
        assert result.success is True
        assert len(result.data) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
