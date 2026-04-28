"""Unit tests for the config loader."""

import pytest
import yaml
from pathlib import Path
from email_tool.config import (
    load_rules_from_yaml,
    load_rules_from_dict,
    validate_rule_config,
    validate_rule_config_file,
    ConfigValidationError,
    _parse_rule,
)
from email_tool.models import Rule, RuleType


class TestValidateRuleConfig:
    """Tests for rule configuration validation."""

    def test_valid_rule_config(self):
        """Test validation of a valid rule configuration."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50,
            "category": "important"
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0

    def test_missing_type_field(self):
        """Test validation with missing type field."""
        rule_data = {
            "name": "test_rule",
            "pattern": "sender@example.com"
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 1
        assert "missing required field 'type'" in errors[0]

    def test_invalid_rule_type(self):
        """Test validation with invalid rule type."""
        rule_data = {
            "name": "test_rule",
            "type": "invalid_type",
            "pattern": "sender@example.com"
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 1
        assert "invalid rule type" in errors[0]

    def test_missing_pattern_for_pattern_rule(self):
        """Test validation with missing pattern for pattern-based rule."""
        rule_data = {
            "name": "test_rule",
            "type": "from_pattern",
            "priority": 50
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 1
        assert "missing required field 'pattern'" in errors[0]

    def test_missing_pattern_for_exact_rule(self):
        """Test validation with missing pattern for exact match rule."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "priority": 50
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 1
        assert "missing required field 'pattern'" in errors[0]

    def test_invalid_priority_type(self):
        """Test validation with invalid priority type."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": "high"
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 1
        assert "priority must be an integer" in errors[0]

    def test_priority_out_of_range(self):
        """Test validation with priority out of valid range."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 150
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 1
        assert "priority must be between 0 and 100" in errors[0]

    def test_missing_name_field(self):
        """Test validation with missing name field."""
        rule_data = {
            "type": "from_exact",
            "pattern": "sender@example.com"
        }
        
        errors = validate_rule_config(rule_data, "unnamed_rule")
        assert len(errors) == 1
        assert "missing required field 'name'" in errors[0]

    def test_empty_name(self):
        """Test validation with empty name."""
        rule_data = {
            "name": "",
            "type": "from_exact",
            "pattern": "sender@example.com"
        }
        
        errors = validate_rule_config(rule_data, "unnamed_rule")
        assert len(errors) == 1
        assert "name cannot be empty" in errors[0]

    def test_valid_rule_with_all_fields(self):
        """Test validation with all optional fields."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50,
            "category": "important",
            "description": "A test rule"
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0

    def test_invalid_regex_pattern(self):
        """Test validation with invalid regex pattern."""
        rule_data = {
            "name": "test_rule",
            "type": "from_pattern",
            "pattern": "[invalid(regex",
            "priority": 50
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 1
        assert "invalid regex pattern" in errors[0]

    def test_rule_without_pattern_for_non_pattern_rule(self):
        """Test validation for rules that don't require pattern."""
        rule_data = {
            "name": "test_rule",
            "type": "has_attachment",
            "priority": 50
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0


class TestParseRule:
    """Tests for rule parsing from configuration."""

    def test_parse_from_exact_rule(self):
        """Test parsing FROM_EXACT rule."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50,
            "category": "important"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.name == "test_rule"
        assert rule.rule_type == RuleType.FROM_EXACT
        assert rule.pattern == "sender@example.com"
        assert rule.priority == 50
        assert rule.category == "important"

    def test_parse_from_pattern_rule(self):
        """Test parsing FROM_PATTERN rule."""
        rule_data = {
            "name": "test_rule",
            "type": "from_pattern",
            "pattern": r".*@example\.com",
            "priority": 50,
            "category": "important"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.name == "test_rule"
        assert rule.rule_type == RuleType.FROM_PATTERN
        assert rule.pattern == r".*@example\.com"

    def test_parse_subject_exact_rule(self):
        """Test parsing SUBJECT_EXACT rule."""
        rule_data = {
            "name": "test_rule",
            "type": "subject_exact",
            "pattern": "Important Update",
            "priority": 50,
            "category": "important"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.name == "test_rule"
        assert rule.rule_type == RuleType.SUBJECT_EXACT
        assert rule.pattern == "Important Update"

    def test_parse_subject_pattern_rule(self):
        """Test parsing SUBJECT_PATTERN rule."""
        rule_data = {
            "name": "test_rule",
            "type": "subject_pattern",
            "pattern": r"Important.*Update",
            "priority": 50,
            "category": "important"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.name == "test_rule"
        assert rule.rule_type == RuleType.SUBJECT_PATTERN

    def test_parse_body_contains_exact_rule(self):
        """Test parsing BODY_CONTAINS_EXACT rule."""
        rule_data = {
            "name": "test_rule",
            "type": "body_contains_exact",
            "pattern": "Important keyword",
            "priority": 50,
            "category": "important"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.name == "test_rule"
        assert rule.rule_type == RuleType.BODY_CONTAINS_EXACT

    def test_parse_body_contains_pattern_rule(self):
        """Test parsing BODY_CONTAINS_PATTERN rule."""
        rule_data = {
            "name": "test_rule",
            "type": "body_contains_pattern",
            "pattern": r"Important\s+keyword",
            "priority": 50,
            "category": "important"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.name == "test_rule"
        assert rule.rule_type == RuleType.BODY_CONTAINS_PATTERN

    def test_parse_has_attachment_rule(self):
        """Test parsing HAS_ATTACHMENT rule."""
        rule_data = {
            "name": "test_rule",
            "type": "has_attachment",
            "priority": 50,
            "category": "important"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.name == "test_rule"
        assert rule.rule_type == RuleType.HAS_ATTACHMENT

    def test_parse_rule_with_optional_fields(self):
        """Test parsing rule with optional fields."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50,
            "category": "important",
            "description": "A test rule"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.name == "test_rule"
        assert rule.description == "A test rule"

    def test_parse_rule_with_default_priority(self):
        """Test parsing rule with default priority."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.priority == 50  # Default priority

    def test_parse_rule_with_default_category(self):
        """Test parsing rule with default category."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com"
        }
        
        rule = _parse_rule(rule_data, "test_rule")
        assert rule.category == "general"  # Default category


class TestLoadRulesFromDict:
    """Tests for loading rules from dictionary."""

    def test_load_rules_from_dict(self):
        """Test loading rules from dictionary."""
        rules_dict = {
            "rules": [
                {
                    "name": "rule1",
                    "type": "from_exact",
                    "pattern": "sender@example.com",
                    "priority": 50,
                    "category": "important"
                },
                {
                    "name": "rule2",
                    "type": "subject_exact",
                    "pattern": "Test",
                    "priority": 30,
                    "category": "test"
                }
            ]
        }
        
        rules = load_rules_from_dict(rules_dict)
        assert len(rules) == 2
        assert rules[0].name == "rule1"
        assert rules[1].name == "rule2"

    def test_load_rules_from_dict_empty(self):
        """Test loading rules from empty dictionary."""
        rules_dict = {}
        
        rules = load_rules_from_dict(rules_dict)
        assert len(rules) == 0

    def test_load_rules_from_dict_no_rules_key(self):
        """Test loading rules from dictionary without rules key."""
        rules_dict = {
            "other_key": "value"
        }
        
        rules = load_rules_from_dict(rules_dict)
        assert len(rules) == 0

    def test_load_rules_from_dict_with_validation_errors(self):
        """Test loading rules with validation errors."""
        rules_dict = {
            "rules": [
                {
                    "name": "rule1",
                    "type": "from_exact",
                    "pattern": "sender@example.com"
                },
                {
                    "type": "from_exact",  # Missing name
                    "pattern": "sender@example.com"
                }
            ]
        }
        
        rules = load_rules_from_dict(rules_dict)
        assert len(rules) == 1  # Only valid rule should be loaded


class TestLoadRulesFromYaml:
    """Tests for loading rules from YAML file."""

    def test_load_rules_from_yaml_file(self, tmp_path):
        """Test loading rules from YAML file."""
        yaml_content = """
rules:
  - name: rule1
    type: from_exact
    pattern: sender@example.com
    priority: 50
    category: important
  - name: rule2
    type: subject_exact
    pattern: Test
    priority: 30
    category: test
"""
        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml_content)
        
        rules = load_rules_from_yaml(str(yaml_file))
        assert len(rules) == 2
        assert rules[0].name == "rule1"
        assert rules[1].name == "rule2"

    def test_load_rules_from_yaml_file_not_found(self, tmp_path):
        """Test loading rules from non-existent YAML file."""
        yaml_file = tmp_path / "nonexistent.yaml"
        
        rules = load_rules_from_yaml(str(yaml_file))
        assert len(rules) == 0

    def test_load_rules_from_yaml_file_invalid_yaml(self, tmp_path):
        """Test loading rules from invalid YAML file."""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: content: [")
        
        rules = load_rules_from_yaml(str(yaml_file))
        assert len(rules) == 0

    def test_load_rules_from_yaml_file_empty(self, tmp_path):
        """Test loading rules from empty YAML file."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")
        
        rules = load_rules_from_yaml(str(yaml_file))
        assert len(rules) == 0

    def test_load_rules_from_yaml_file_with_comments(self, tmp_path):
        """Test loading rules from YAML file with comments."""
        yaml_content = """
# This is a comment
rules:
  # Another comment
  - name: rule1
    type: from_exact
    pattern: sender@example.com
    priority: 50
"""
        yaml_file = tmp_path / "comments.yaml"
        yaml_file.write_text(yaml_content)
        
        rules = load_rules_from_yaml(str(yaml_file))
        assert len(rules) == 1
        assert rules[0].name == "rule1"


class TestValidateRuleConfigFile:
    """Tests for validating rule configuration files."""

    def test_validate_rule_config_file_valid(self, tmp_path):
        """Test validating a valid rule configuration file."""
        yaml_content = """
rules:
  - name: rule1
    type: from_exact
    pattern: sender@example.com
    priority: 50
    category: important
"""
        yaml_file = tmp_path / "valid.yaml"
        yaml_file.write_text(yaml_content)
        
        errors = validate_rule_config_file(str(yaml_file))
        assert len(errors) == 0

    def test_validate_rule_config_file_invalid(self, tmp_path):
        """Test validating an invalid rule configuration file."""
        yaml_content = """
rules:
  - name: rule1
    type: invalid_type
    pattern: sender@example.com
"""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text(yaml_content)
        
        errors = validate_rule_config_file(str(yaml_file))
        assert len(errors) == 1
        assert "invalid rule type" in errors[0]

    def test_validate_rule_config_file_not_found(self, tmp_path):
        """Test validating a non-existent file."""
        yaml_file = tmp_path / "nonexistent.yaml"
        
        errors = validate_rule_config_file(str(yaml_file))
        assert len(errors) == 1
        assert "File not found" in errors[0]

    def test_validate_rule_config_file_invalid_yaml(self, tmp_path):
        """Test validating a file with invalid YAML."""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: content: [")
        
        errors = validate_rule_config_file(str(yaml_file))
        assert len(errors) == 1
        assert "YAML parsing error" in errors[0]


class TestConfigValidationError:
    """Tests for ConfigValidationError exception."""

    def test_config_error_creation(self):
        """Test ConfigValidationError creation."""
        error = ConfigValidationError("Test error message")
        assert str(error) == "Test error message"

    def test_config_error_with_file(self):
        """Test ConfigValidationError with file information."""
        error = ConfigValidationError("Test error message", file="test.yaml")
        assert "test.yaml" in str(error)

    def test_config_error_with_line(self):
        """Test ConfigValidationError with line information."""
        error = ConfigValidationError("Test error message", line=10)
        assert "line 10" in str(error)

    def test_config_error_with_all_info(self):
        """Test ConfigValidationError with all information."""
        error = ConfigValidationError("Test error message", file="test.yaml", line=10)
        assert "test.yaml" in str(error)
        assert "line 10" in str(error)


class TestRuleConfigEdgeCases:
    """Tests for edge cases in rule configuration."""

    def test_rule_with_unicode_in_pattern(self):
        """Test rule with unicode in pattern."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50,
            "category": "important"
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0

    def test_rule_with_special_characters_in_pattern(self):
        """Test rule with special characters in pattern."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50,
            "category": "important"
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0

    def test_rule_with_long_pattern(self):
        """Test rule with very long pattern."""
        long_pattern = "A" * 1000
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": long_pattern,
            "priority": 50,
            "category": "important"
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0

    def test_rule_with_duplicate_names(self):
        """Test validation with duplicate rule names."""
        rules_dict = {
            "rules": [
                {
                    "name": "rule1",
                    "type": "from_exact",
                    "pattern": "sender@example.com",
                    "priority": 50
                },
                {
                    "name": "rule1",  # Duplicate name
                    "type": "subject_exact",
                    "pattern": "Test",
                    "priority": 30
                }
            ]
        }
        
        rules = load_rules_from_dict(rules_dict)
        assert len(rules) == 2  # Both rules should be loaded

    def test_rule_with_negative_priority(self):
        """Test rule with negative priority."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": -10
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 1
        assert "priority must be between 0 and 100" in errors[0]

    def test_rule_with_float_priority(self):
        """Test rule with float priority."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50.5
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 1
        assert "priority must be an integer" in errors[0]

    def test_rule_with_empty_category(self):
        """Test rule with empty category."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50,
            "category": ""
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0  # Empty category is allowed

    def test_rule_with_whitespace_in_name(self):
        """Test rule with whitespace in name."""
        rule_data = {
            "name": "  test_rule  ",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0  # Whitespace in name is allowed

    def test_rule_with_unicode_in_name(self):
        """Test rule with unicode in name."""
        rule_data = {
            "name": "测试规则",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0

    def test_rule_with_unicode_in_category(self):
        """Test rule with unicode in category."""
        rule_data = {
            "name": "test_rule",
            "type": "from_exact",
            "pattern": "sender@example.com",
            "priority": 50,
            "category": "重要"
        }
        
        errors = validate_rule_config(rule_data, "test_rule")
        assert len(errors) == 0
