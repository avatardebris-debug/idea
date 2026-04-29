"""Tests for the rule validator module."""

import pytest

from email_tool.agent.rule_validator import RuleValidator
from email_tool.agent.base import AgentResult
from email_tool.models import Rule, RuleType


class TestRuleValidator:
    """Test cases for RuleValidator."""
    
    def test_validate_empty_rules(self):
        """Test validation of empty rules list."""
        validator = RuleValidator()
        result = validator.validate_rules([])
        
        assert result.success is True
        assert result.data == []
        assert "No rules provided" in result.metadata.get("warnings", [])
    
    def test_validate_invalid_type(self):
        """Test validation with non-list input."""
        validator = RuleValidator()
        result = validator.validate_rules("not a list")
        
        assert result.success is False
        assert "Rules must be a list" in result.error_message
    
    def test_validate_missing_name(self):
        """Test validation with missing rule name."""
        validator = RuleValidator()
        rules = [{"type": "from_exact", "pattern": "test@example.com"}]
        result = validator.validate_rules(rules)
        
        assert result.success is False
        assert "name" in result.metadata.get("errors", [{}])[0]
    
    def test_validate_missing_type(self):
        """Test validation with missing rule type."""
        validator = RuleValidator()
        rules = [{"name": "test_rule", "pattern": "test@example.com"}]
        result = validator.validate_rules(rules)
        
        assert result.success is False
        assert "type" in result.metadata.get("errors", [{}])[0]
    
    def test_validate_invalid_rule_type(self):
        """Test validation with invalid rule type."""
        validator = RuleValidator()
        rules = [{"name": "test_rule", "type": "invalid_type", "pattern": "test@example.com"}]
        result = validator.validate_rules(rules)
        
        assert result.success is False
        assert "invalid_type" in result.metadata.get("errors", [{}])[0]
    
    def test_validate_valid_rule(self):
        """Test validation of a valid rule."""
        validator = RuleValidator()
        rules = [{
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "test@example.com",
            "priority": 80,
            "category": "test"
        }]
        result = validator.validate_rules(rules)
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["name"] == "test_rule"
    
    def test_validate_duplicate_names(self):
        """Test validation with duplicate rule names."""
        validator = RuleValidator()
        rules = [
            {"name": "test_rule", "type": "from_exact", "pattern": "test@example.com", "category": "test"},
            {"name": "test_rule", "type": "from_pattern", "pattern": "test.*@example.com", "category": "test"}
        ]
        result = validator.validate_rules(rules)
        
        assert result.success is False
        assert "duplicate" in result.metadata.get("errors", [{}])[0].lower()
    
    def test_validate_priority_range(self):
        """Test validation of priority values."""
        validator = RuleValidator()
        
        # Valid priority
        rules = [{"name": "test", "type": "from_exact", "pattern": "test@example.com", "priority": 50, "category": "test"}]
        result = validator.validate_rules(rules)
        assert result.success is True
        
        # Invalid priority (too high)
        rules = [{"name": "test", "type": "from_exact", "pattern": "test@example.com", "priority": 150, "category": "test"}]
        result = validator.validate_rules(rules)
        assert result.success is False
        
        # Invalid priority (too low)
        rules = [{"name": "test", "type": "from_exact", "pattern": "test@example.com", "priority": -10, "category": "test"}]
        result = validator.validate_rules(rules)
        assert result.success is False
    
    def test_validate_category_required(self):
        """Test that category is required."""
        validator = RuleValidator()
        rules = [{"name": "test", "type": "from_exact", "pattern": "test@example.com"}]
        result = validator.validate_rules(rules)
        
        assert result.success is False
        assert "category" in result.metadata.get("errors", [{}])[0]
    
    def test_validate_pattern_required(self):
        """Test that pattern is required."""
        validator = RuleValidator()
        rules = [{"name": "test", "type": "from_exact", "category": "test"}]
        result = validator.validate_rules(rules)
        
        assert result.success is False
        assert "pattern" in result.metadata.get("errors", [{}])[0]
    
    def test_validate_has_attachment_rule(self):
        """Test validation of has_attachment rule type."""
        validator = RuleValidator()
        rules = [{
            "name": "has_attachments",
            "type": "has_attachment",
            "priority": 70,
            "category": "attachments"
        }]
        result = validator.validate_rules(rules)
        
        assert result.success is True
        assert len(result.data) == 1
    
    def test_validate_all_rule_types(self):
        """Test validation of all rule types."""
        validator = RuleValidator()
        
        rule_types = [
            ("from_exact", "test@example.com"),
            ("from_pattern", ".*@example.com"),
            ("subject_exact", "Meeting"),
            ("subject_contains", "meeting"),
            ("subject_pattern", ".*meeting.*"),
            ("body_contains_exact", "urgent"),
            ("body_contains_contains", "urgent"),
            ("body_contains_pattern", ".*urgent.*"),
            ("has_attachment", None)
        ]
        
        for rule_type, pattern in rule_types:
            rule = {
                "name": f"test_{rule_type}",
                "type": rule_type,
                "priority": 50,
                "category": "test"
            }
            if pattern:
                rule["pattern"] = pattern
            
            result = validator.validate_rules([rule])
            assert result.success is True, f"Failed for rule type: {rule_type}"
    
    def test_validate_with_description(self):
        """Test validation with description field."""
        validator = RuleValidator()
        rules = [{
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "test@example.com",
            "priority": 80,
            "category": "test",
            "description": "Test rule description"
        }]
        result = validator.validate_rules(rules)
        
        assert result.success is True
        assert result.data[0]["description"] == "Test rule description"
    
    def test_validate_returns_validated_rules(self):
        """Test that validated rules are returned correctly."""
        validator = RuleValidator()
        rules = [{
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "test@example.com",
            "priority": 80,
            "category": "test"
        }]
        result = validator.validate_rules(rules)
        
        assert result.success is True
        assert isinstance(result.data, list)
        assert len(result.data) == 1
        assert result.data[0]["name"] == "test_rule"
        assert result.data[0]["type"] == "from_exact"
        assert result.data[0]["pattern"] == "test@example.com"
        assert result.data[0]["priority"] == 80
        assert result.data[0]["category"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
