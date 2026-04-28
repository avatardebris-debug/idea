"""Email Tool - A rule-based email filtering and organization system."""

from email_tool.models import Email, Rule, Category, RuleMatch
from email_tool.parser import parse_email_file, parse_email_content
from email_tool.rules import RuleEngine, RuleType, RuleMatchStrategy
from email_tool.config import (
    load_rules_from_yaml,
    load_rules_from_dict,
    validate_rule_config,
    validate_rule_config_file,
    ConfigValidationError,
)
from email_tool.organizer import EmailOrganizer, OrganizerBuilder, create_organizer
from email_tool.path_builder import PathBuilder
from email_tool.formatter import Formatter
from email_tool.dispatcher import Dispatcher, ActionBuilder, ActionExecutor
from email_tool.processor import EmailProcessor, PipelineBuilder, PipelineExecutor, PipelineMonitor, PipelineConfig

__all__ = [
    # Models
    "Email",
    "Rule",
    "Category",
    "RuleMatch",
    # Parser
    "parse_email_file",
    "parse_email_content",
    # Rules
    "RuleEngine",
    "RuleType",
    "RuleMatchStrategy",
    # Config
    "load_rules_from_yaml",
    "load_rules_from_dict",
    "validate_rule_config",
    "validate_rule_config_file",
    "ConfigValidationError",
    # Organizer
    "EmailOrganizer",
    "OrganizerBuilder",
    "create_organizer",
    # Path Builder
    "PathBuilder",
    # Formatter
    "Formatter",
    # Dispatcher
    "Dispatcher",
    "ActionBuilder",
    "ActionExecutor",
    # Processor
    "EmailProcessor",
    "PipelineBuilder",
    "PipelineExecutor",
    "PipelineMonitor",
    "PipelineConfig",
]

__version__ = "0.1.0"
