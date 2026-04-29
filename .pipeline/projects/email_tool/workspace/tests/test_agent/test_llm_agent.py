"""Tests for the LLM agent module."""

import pytest
from unittest.mock import MagicMock, patch

from email_tool.agent.llm_agent import LLMAgent
from email_tool.agent.base import AgentResult, AgentContext
from email_tool.agent.prompt_templates import PromptTemplates


class TestLLMAgent:
    """Test cases for LLMAgent."""
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        agent = LLMAgent()
        
        assert agent.model == "gpt-4o-mini"
        assert agent.temperature == 0.7
        assert agent.max_tokens == 2000
        assert agent.enable_few_shot is True
        assert agent.api_key is None
    
    def test_init_custom_values(self):
        """Test initialization with custom values."""
        agent = LLMAgent(
            model="custom-model",
            temperature=0.5,
            max_tokens=1000,
            enable_few_shot=False,
            api_key="test-key"
        )
        
        assert agent.model == "custom-model"
        assert agent.temperature == 0.5
        assert agent.max_tokens == 1000
        assert agent.enable_few_shot is False
        assert agent.api_key == "test-key"
    
    def test_generate_rules_empty_description(self):
        """Test rule generation with empty description."""
        agent = LLMAgent()
        
        result = agent.generate_rules(
            description="",
            sample_emails=[],
            context=None,
            few_shot=True,
            custom_prompt=None
        )
        
        assert result.success is False
        assert "description" in result.error_message.lower()
    
    def test_generate_rules_with_sample_emails(self):
        """Test rule generation with sample emails."""
        agent = LLMAgent()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Invoice #12345",
                "date": "2024-01-01",
                "body": "Please find attached invoice"
            }
        ]
        
        with patch.object(agent, '_get_rule_generation_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value='{"rules": [{"name": "invoice_rule", "type": "subject_contains", "pattern": "invoice", "priority": 80, "category": "invoices"}]}'):
                result = agent.generate_rules(
                    description="Create rules for invoices",
                    sample_emails=sample_emails,
                    context=None,
                    few_shot=True,
                    custom_prompt=None
                )
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["name"] == "invoice_rule"
    
    def test_generate_rules_llm_error(self):
        """Test rule generation when LLM fails."""
        agent = LLMAgent()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(agent, '_get_rule_generation_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', side_effect=Exception("LLM error")):
                result = agent.generate_rules(
                    description="Create rules",
                    sample_emails=sample_emails,
                    context=None,
                    few_shot=True,
                    custom_prompt=None
                )
        
        assert result.success is False
        assert "LLM error" in result.error_message
    
    def test_generate_rules_invalid_json(self):
        """Test rule generation with invalid JSON response."""
        agent = LLMAgent()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(agent, '_get_rule_generation_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value="Invalid JSON"):
                result = agent.generate_rules(
                    description="Create rules",
                    sample_emails=sample_emails,
                    context=None,
                    few_shot=True,
                    custom_prompt=None
                )
        
        assert result.success is False
        assert "Invalid JSON" in result.error_message
    
    def test_generate_rules_with_context(self):
        """Test rule generation with context."""
        agent = LLMAgent()
        
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
        
        with patch.object(agent, '_get_rule_generation_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value='{"rules": []}'):
                result = agent.generate_rules(
                    description="Create rules",
                    sample_emails=sample_emails,
                    context=context,
                    few_shot=True,
                    custom_prompt=None
                )
        
        assert result.success is True
        assert result.metadata["conversation_id"] == "test_conversation"
    
    def test_generate_rules_with_custom_prompt(self):
        """Test rule generation with custom prompt."""
        agent = LLMAgent()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        custom_prompt = "Custom prompt for rule generation"
        
        with patch.object(agent, '_get_rule_generation_prompt', return_value=custom_prompt):
            with patch.object(agent, '_call_llm', return_value='{"rules": []}'):
                result = agent.generate_rules(
                    description="Create rules",
                    sample_emails=sample_emails,
                    context=None,
                    few_shot=True,
                    custom_prompt=custom_prompt
                )
        
        assert result.success is True
    
    def test_generate_rules_with_few_shot(self):
        """Test rule generation with few-shot examples."""
        agent = LLMAgent()
        
        sample_emails = [
            {
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(agent, '_get_rule_generation_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value='{"rules": []}'):
                result = agent.generate_rules(
                    description="Create rules",
                    sample_emails=sample_emails,
                    context=None,
                    few_shot=True,
                    custom_prompt=None
                )
        
        assert result.success is True
    
    def test_generate_rules_with_empty_sample_emails(self):
        """Test rule generation with empty sample emails."""
        agent = LLMAgent()
        
        with patch.object(agent, '_get_rule_generation_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value='{"rules": []}'):
                result = agent.generate_rules(
                    description="Create rules",
                    sample_emails=[],
                    context=None,
                    few_shot=True,
                    custom_prompt=None
                )
        
        assert result.success is True
        assert len(result.data) == 0
    
    def test_categorize_emails_empty_emails(self):
        """Test categorization with empty email list."""
        agent = LLMAgent()
        
        result = agent.categorize_emails(
            emails=[],
            rules=[],
            context=None,
            prompt=None,
            few_shot=True,
            existing_categories=None
        )
        
        assert result.success is True
        assert result.data == []
        assert "No emails to categorize" in result.metadata.get("warnings", [])
    
    def test_categorize_emails_with_emails(self):
        """Test categorization with emails."""
        agent = LLMAgent()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(agent, '_get_categorization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value='{"categorizations": [{"id": "1", "category": "work", "matched_rule": null, "confidence": 0.9}]}'):
                result = agent.categorize_emails(
                    emails=emails,
                    rules=[],
                    context=None,
                    prompt=None,
                    few_shot=True,
                    existing_categories=None
                )
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["category"] == "work"
    
    def test_categorize_emails_llm_error(self):
        """Test categorization when LLM fails."""
        agent = LLMAgent()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(agent, '_get_categorization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', side_effect=Exception("LLM error")):
                result = agent.categorize_emails(
                    emails=emails,
                    rules=[],
                    context=None,
                    prompt=None,
                    few_shot=True,
                    existing_categories=None
                )
        
        assert result.success is False
        assert "LLM error" in result.error_message
    
    def test_categorize_emails_with_rules(self):
        """Test categorization with rules."""
        agent = LLMAgent()
        
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
            {
                "name": "invoice_rule",
                "rule_type": "subject_contains",
                "pattern": "invoice",
                "priority": 80,
                "category": "invoices"
            }
        ]
        
        with patch.object(agent, '_get_categorization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value='{"categorizations": [{"id": "1", "category": "invoices", "matched_rule": "invoice_rule", "confidence": 0.95}]}'):
                result = agent.categorize_emails(
                    emails=emails,
                    rules=rules,
                    context=None,
                    prompt=None,
                    few_shot=True,
                    existing_categories=None
                )
        
        assert result.success is True
        assert result.data[0]["category"] == "invoices"
        assert result.data[0]["matched_rule"] == "invoice_rule"
    
    def test_categorize_emails_with_context(self):
        """Test categorization with context."""
        agent = LLMAgent()
        
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
        
        with patch.object(agent, '_get_categorization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value='{"categorizations": []}'):
                result = agent.categorize_emails(
                    emails=emails,
                    rules=[],
                    context=context,
                    prompt=None,
                    few_shot=True,
                    existing_categories=None
                )
        
        assert result.success is True
        assert result.metadata["conversation_id"] == "test_conversation"
    
    def test_categorize_emails_with_custom_prompt(self):
        """Test categorization with custom prompt."""
        agent = LLMAgent()
        
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
        
        with patch.object(agent, '_get_categorization_prompt', return_value=custom_prompt):
            with patch.object(agent, '_call_llm', return_value='{"categorizations": []}'):
                result = agent.categorize_emails(
                    emails=emails,
                    rules=[],
                    context=None,
                    prompt=custom_prompt,
                    few_shot=True,
                    existing_categories=None
                )
        
        assert result.success is True
    
    def test_categorize_emails_with_existing_categories(self):
        """Test categorization with existing categories."""
        agent = LLMAgent()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "body": "Test body"
            }
        ]
        
        with patch.object(agent, '_get_categorization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value='{"categorizations": [{"id": "1", "category": "work", "matched_rule": null, "confidence": 0.9}]}'):
                result = agent.categorize_emails(
                    emails=emails,
                    rules=[],
                    context=None,
                    prompt=None,
                    few_shot=True,
                    existing_categories=["work", "personal"]
                )
        
        assert result.success is True
        assert result.data[0]["category"] == "work"
    
    def test_summarize_inbox_empty_emails(self):
        """Test summarization with empty email list."""
        agent = LLMAgent()
        
        result = agent.summarize_inbox(
            emails=[],
            rules=[],
            matches=[],
            context=None,
            prompt=None,
            few_shot=True
        )
        
        assert result.success is True
        assert result.data == "No emails in inbox."
        assert result.metadata["total_emails"] == 0
    
    def test_summarize_inbox_with_emails(self):
        """Test summarization with emails."""
        agent = LLMAgent()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        with patch.object(agent, '_get_summarization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value="Summary of inbox"):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=[],
                    matches=[],
                    context=None,
                    prompt=None,
                    few_shot=True
                )
        
        assert result.success is True
        assert result.data == "Summary of inbox"
    
    def test_summarize_inbox_llm_error(self):
        """Test summarization when LLM fails."""
        agent = LLMAgent()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        with patch.object(agent, '_get_summarization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', side_effect=Exception("LLM error")):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=[],
                    matches=[],
                    context=None,
                    prompt=None,
                    few_shot=True
                )
        
        assert result.success is False
        assert "LLM error" in result.error_message
    
    def test_summarize_inbox_with_context(self):
        """Test summarization with context."""
        agent = LLMAgent()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        context = AgentContext(
            conversation_id="test_conversation",
            turn=1
        )
        
        with patch.object(agent, '_get_summarization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value="Summary"):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=[],
                    matches=[],
                    context=context,
                    prompt=None,
                    few_shot=True
                )
        
        assert result.success is True
        assert result.metadata["conversation_id"] == "test_conversation"
    
    def test_summarize_inbox_with_custom_prompt(self):
        """Test summarization with custom prompt."""
        agent = LLMAgent()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        custom_prompt = "Custom prompt for summarization"
        
        with patch.object(agent, '_get_summarization_prompt', return_value=custom_prompt):
            with patch.object(agent, '_call_llm', return_value="Summary"):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=[],
                    matches=[],
                    context=None,
                    prompt=custom_prompt,
                    few_shot=True
                )
        
        assert result.success is True
    
    def test_summarize_inbox_with_rules(self):
        """Test summarization with rules."""
        agent = LLMAgent()
        
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
        
        with patch.object(agent, '_get_summarization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value="Summary"):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=rules,
                    matches=[],
                    context=None,
                    prompt=None,
                    few_shot=True
                )
        
        assert result.success is True
    
    def test_summarize_inbox_with_matches(self):
        """Test summarization with matches."""
        agent = LLMAgent()
        
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
        
        with patch.object(agent, '_get_summarization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value="Summary"):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=[],
                    matches=matches,
                    context=None,
                    prompt=None,
                    few_shot=True
                )
        
        assert result.success is True
    
    def test_summarize_inbox_with_all_data(self):
        """Test summarization with all data types."""
        agent = LLMAgent()
        
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
        
        matches = [
            {
                "email_id": "1",
                "rule_name": "work_rule",
                "confidence": 0.95
            }
        ]
        
        with patch.object(agent, '_get_summarization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value="Summary"):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=rules,
                    matches=matches,
                    context=None,
                    prompt=None,
                    few_shot=True
                )
        
        assert result.success is True
    
    def test_summarize_inbox_with_large_email_count(self):
        """Test summarization with large email count."""
        agent = LLMAgent()
        
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
        
        with patch.object(agent, '_get_summarization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value="Summary"):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=[],
                    matches=[],
                    context=None,
                    prompt=None,
                    few_shot=True
                )
        
        assert result.success is True
    
    def test_summarize_inbox_with_empty_rules(self):
        """Test summarization with empty rules list."""
        agent = LLMAgent()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        with patch.object(agent, '_get_summarization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value="Summary"):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=[],
                    matches=[],
                    context=None,
                    prompt=None,
                    few_shot=True
                )
        
        assert result.success is True
    
    def test_summarize_inbox_with_empty_matches(self):
        """Test summarization with empty matches list."""
        agent = LLMAgent()
        
        emails = [
            {
                "id": "1",
                "from": "sender@example.com",
                "subject": "Test",
                "date": "2024-01-01",
                "category": "work"
            }
        ]
        
        with patch.object(agent, '_get_summarization_prompt', return_value="Test prompt"):
            with patch.object(agent, '_call_llm', return_value="Summary"):
                result = agent.summarize_inbox(
                    emails=emails,
                    rules=[],
                    matches=[],
                    context=None,
                    prompt=None,
                    few_shot=True
                )
        
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
