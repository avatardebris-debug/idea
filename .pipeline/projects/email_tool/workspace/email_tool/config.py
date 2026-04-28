"""Configuration loader for loading rules from YAML files."""

import re
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
from email_tool.models import Rule, RuleType


class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails."""
    def __init__(self, message: str, file: Optional[str] = None, line: Optional[int] = None):
        super().__init__(message)
        self.file = file
        self.line = line
        self.message = message
    
    def __str__(self):
        parts = [self.message]
        if self.file:
            parts.append(f"file: {self.file}")
        if self.line:
            parts.append(f"line {self.line}")
        return " | ".join(parts)


def validate_rule_config(rule_data: Dict[str, Any], rule_name: str) -> List[str]:
    """
    Validate a single rule configuration.

    Args:
        rule_data: The rule configuration dictionary.
        rule_name: The name of the rule (for error messages).

    Returns:
        List of error messages (empty if valid).
    """
    errors = []

    # Check required fields
    if 'name' not in rule_data:
        errors.append(f"Rule '{rule_name}': missing required field 'name'")
    elif not rule_data.get('name'):
        errors.append(f"Rule '{rule_name}': name cannot be empty")

    if 'type' not in rule_data:
        errors.append(f"Rule '{rule_name}': missing required field 'type'")
    else:
        try:
            RuleType(rule_data['type'])
        except ValueError:
            errors.append(f"Rule '{rule_name}': invalid rule type '{rule_data['type']}'")

    # Check pattern/value based on rule type
    if 'type' in rule_data:
        rule_type = rule_data['type']
        has_pattern = 'pattern' in rule_data
        has_value = 'value' in rule_data

        if rule_type in [RuleType.FROM_EXACT.value, RuleType.FROM_PATTERN.value,
                         RuleType.SUBJECT_EXACT.value, RuleType.SUBJECT_CONTAINS.value,
                         RuleType.SUBJECT_PATTERN.value, RuleType.BODY_CONTAINS_EXACT.value,
                         RuleType.BODY_CONTAINS_CONTAINS.value, RuleType.BODY_CONTAINS_PATTERN.value]:
            if not has_pattern and not has_value:
                errors.append(f"Rule '{rule_name}': missing required field 'pattern'")
            elif has_pattern:
                # Validate regex pattern
                try:
                    re.compile(rule_data['pattern'])
                except re.error:
                    errors.append(f"Rule '{rule_name}': invalid regex pattern '{rule_data['pattern']}'")

        if rule_type == RuleType.HAS_ATTACHMENT.value:
            if has_pattern:
                errors.append(f"Rule '{rule_name}': has_attachment type should not have 'pattern'")

    # Check priority if provided
    if 'priority' in rule_data:
        priority_value = rule_data['priority']
        if not isinstance(priority_value, int) or isinstance(priority_value, bool):
            errors.append(f"Rule '{rule_name}': priority must be an integer")
        else:
            priority = int(priority_value)
            if priority < 0 or priority > 100:
                errors.append(f"Rule '{rule_name}': priority must be between 0 and 100")

    return errors


def _parse_rule_type(type_str: str) -> RuleType:
    """Parse a rule type string into RuleType enum."""
    try:
        return RuleType(type_str)
    except ValueError:
        raise ValueError(f"Invalid rule type: {type_str}")


def _parse_rule(rule_data: Dict[str, Any], rule_name: str = 'unknown') -> Rule:
    """
    Parse a rule configuration dictionary into a Rule object.

    Args:
        rule_data: The rule configuration dictionary.
        rule_name: The name of the rule (for error messages).

    Returns:
        Rule object.

    Raises:
        ConfigValidationError: If the rule configuration is invalid.
    """
    errors = validate_rule_config(rule_data, rule_name)
    if errors:
        raise ConfigValidationError(f"Invalid rule configuration: {'; '.join(errors)}")

    rule_type = _parse_rule_type(rule_data['type'])
    pattern = rule_data.get('pattern')
    value = rule_data.get('value')

    # Use pattern if available, otherwise use value
    if pattern is None and value is None:
        # For types that require pattern or value, this should have been caught by validation
        # But handle gracefully anyway
        pattern = ""

    return Rule(
        name=rule_data['name'],
        rule_type=rule_type,
        pattern=pattern,
        value=value,
        priority=int(rule_data.get('priority', 50)),
        category=rule_data.get('category', 'general'),
        description=rule_data.get('description', '')
    )


def load_rules_from_yaml(filepath: str | Path) -> List[Rule]:
    """
    Load rules from a YAML configuration file.

    Args:
        filepath: Path to the YAML file containing rule definitions.

    Returns:
        List of Rule objects.
    """
    try:
        filepath = Path(filepath)
        
        if not filepath.exists():
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError:
        return []

    if config is None:
        return []

    if not isinstance(config, dict):
        return []

    if 'rules' not in config:
        return []

    rules_data = config['rules']
    if not isinstance(rules_data, list):
        return []

    rules: List[Rule] = []
    for i, rule_data in enumerate(rules_data):
        if not isinstance(rule_data, dict):
            continue

        rule_name = rule_data.get('name', f'rule_{i}')
        try:
            rule = _parse_rule(rule_data, rule_name)
            rules.append(rule)
        except ConfigValidationError:
            # Skip invalid rules
            continue

    return rules


def validate_rule_config_file(filepath: str | Path) -> List[str]:
    """
    Validate a rules configuration file without loading it.

    Args:
        filepath: Path to the YAML file.

    Returns:
        List of validation error messages (empty if valid).
    """
    filepath = Path(filepath)
    errors = []

    if not filepath.exists():
        errors.append(f"File not found: {filepath}")
        return errors

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {e}")
        return errors

    if not isinstance(config, dict):
        errors.append("Configuration must be a YAML dictionary")
        return errors

    if 'rules' not in config:
        errors.append("Configuration must contain 'rules' key")
        return errors

    rules_data = config['rules']
    if not isinstance(rules_data, list):
        errors.append("'rules' must be a list")
        return errors

    for i, rule_data in enumerate(rules_data):
        if not isinstance(rule_data, dict):
            errors.append(f"Rule at index {i} must be a dictionary")
            continue

        rule_name = rule_data.get('name', f'rule_{i}')
        rule_errors = validate_rule_config(rule_data, rule_name)
        errors.extend(rule_errors)

    return errors


def load_rules_from_dict(rules_data: Dict[str, Any]) -> List[Rule]:
    """
    Load rules from a dictionary containing a 'rules' key.

    Args:
        rules_data: Dictionary containing 'rules' key with list of rule configurations.

    Returns:
        List of Rule objects.
    """
    rules: List[Rule] = []
    
    if not isinstance(rules_data, dict):
        return rules
    
    rules_list = rules_data.get('rules', [])
    if not isinstance(rules_list, list):
        return rules

    for i, rule_data in enumerate(rules_list):
        if not isinstance(rule_data, dict):
            continue

        rule_name = rule_data.get('name', f'rule_{i}')
        try:
            rule = _parse_rule(rule_data, rule_name)
            rules.append(rule)
        except ConfigValidationError:
            # Skip invalid rules
            continue

    return rules
