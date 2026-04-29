"""
Phase 6 Email Processing Models

This module contains all data models for the email processing system including:
- Email and EmailMetadata for email representation
- Rule and RuleMatch for rule-based processing
- Action and ActionExecutionResult for actions
- RuleSet and ActionSet for collections
- ProcessingConfig for configuration
- ProcessingStats for statistics
- EmailMatch and EmailProcessingResult for processing results
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


# == Enums ==

class RuleType(Enum):
    """Types of rules that can be applied to emails."""
    SUBJECT_CONTAINS = "subject_contains"
    SUBJECT_EXACT = "subject_exact"
    FROM_CONTAINS = "from_contains"
    FROM_EXACT = "from_exact"
    TO_CONTAINS = "to_contains"
    TO_EXACT = "to_exact"
    BODY_CONTAINS = "body_contains"
    BODY_EXACT = "body_exact"
    HAS_ATTACHMENT = "has_attachment"
    SIZE_GREATER_THAN = "size_greater_than"
    SIZE_LESS_THAN = "size_less_than"
    DATE_AFTER = "date_after"
    DATE_BEFORE = "date_before"
    LABEL_EXISTS = "label_exists"
    LABEL_NOT_EXISTS = "label_not_exists"


class RuleMatchType(Enum):
    """Types of rule matching."""
    EXACT = "exact"
    CONTAINS = "contains"
    REGEX = "regex"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class Category(Enum):
    """Email categories."""
    INBOX = "inbox"
    SENT = "sent"
    DRAFTS = "drafts"
    ARCHIVE = "archive"
    SPAM = "spam"
    TRASH = "trash"
    CUSTOM = "custom"


class ActionType(Enum):
    """Types of actions that can be performed on emails."""
    ADD_LABEL = "add_label"
    REMOVE_LABEL = "remove_label"
    MOVE_TO_CATEGORY = "move_to_category"
    DELETE = "delete"
    MARK_READ = "mark_read"
    MARK_UNREAD = "mark_unread"
    FORWARD = "forward"
    REPLY = "reply"
    ARCHIVE = "archive"
    FLAG = "flag"
    UNFLAG = "unflag"
    SEND_NOTIFICATION = "send_notification"
    EXECUTE_SCRIPT = "execute_script"
    EXPORT = "export"
    RETAIN = "retain"


class ProcessingStatus(Enum):
    """Status of email processing."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


# == Core Models ==

@dataclass
class Email:
    """Represents an email message."""
    id: Optional[str] = None
    from_addr: str = ""
    to_addrs: List[str] = field(default_factory=list)
    subject: str = ""
    date: Optional[datetime] = None
    body_plain: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    raw_headers: Dict[str, str] = field(default_factory=dict)
    labels: List[str] = field(default_factory=list)
    source_path: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize created_at and id if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert email to dictionary."""
        return {
            "id": self.id,
            "from_addr": self.from_addr,
            "to_addrs": self.to_addrs,
            "subject": self.subject,
            "date": self.date.isoformat() if self.date else None,
            "body_plain": self.body_plain,
            "body_html": self.body_html,
            "attachments": self.attachments,
            "raw_headers": self.raw_headers,
            "labels": self.labels,
            "source_path": self.source_path,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Email':
        """Create email from dictionary."""
        return cls(
            id=data.get("id"),
            from_addr=data.get("from_addr", ""),
            to_addrs=data.get("to_addrs", []),
            subject=data.get("subject", ""),
            date=datetime.fromisoformat(data["date"]) if data.get("date") else None,
            body_plain=data.get("body_plain"),
            body_html=data.get("body_html"),
            attachments=data.get("attachments", []),
            raw_headers=data.get("raw_headers", {}),
            labels=data.get("labels", []),
            source_path=data.get("source_path"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )
    
    def to_eml(self) -> str:
        """Convert email to EML format string."""
        lines = [
            f"From: {self.from_addr}",
            f"To: {', '.join(self.to_addrs)}",
            f"Subject: {self.subject}",
            f"Date: {self.date.isoformat() if self.date else 'N/A'}"
        ]
        
        if self.body_plain:
            lines.append("")
            lines.append(self.body_plain)
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"Email(id='{self.id}', from='{self.from_addr}', subject='{self.subject}')"


@dataclass
class EmailMetadata:
    """Metadata about an email for processing."""
    subject: str = ""
    from_email: str = ""
    from_name: str = ""
    to_emails: List[str] = field(default_factory=list)
    cc_emails: List[str] = field(default_factory=list)
    bcc_emails: List[str] = field(default_factory=list)
    date: Optional[datetime] = None
    message_id: Optional[str] = None
    size_bytes: int = 0
    has_attachments: bool = False
    attachment_names: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "subject": self.subject,
            "from_email": self.from_email,
            "from_name": self.from_name,
            "to_emails": self.to_emails,
            "cc_emails": self.cc_emails,
            "bcc_emails": self.bcc_emails,
            "date": self.date.isoformat() if self.date else None,
            "message_id": self.message_id,
            "size_bytes": self.size_bytes,
            "has_attachments": self.has_attachments,
            "attachment_names": self.attachment_names,
            "labels": self.labels,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "headers": self.headers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailMetadata':
        """Create metadata from dictionary."""
        return cls(
            subject=data.get("subject", ""),
            from_email=data.get("from_email", ""),
            from_name=data.get("from_name", ""),
            to_emails=data.get("to_emails", []),
            cc_emails=data.get("cc_emails", []),
            bcc_emails=data.get("bcc_emails", []),
            date=datetime.fromisoformat(data["date"]) if data.get("date") else None,
            message_id=data.get("message_id"),
            size_bytes=data.get("size_bytes", 0),
            has_attachments=data.get("has_attachments", False),
            attachment_names=data.get("attachment_names", []),
            labels=data.get("labels", []),
            body_text=data.get("body_text"),
            body_html=data.get("body_html"),
            headers=data.get("headers", {})
        )


@dataclass
class Rule:
    """Represents a rule for email processing."""
    name: str
    rule_type: RuleType
    pattern: str
    priority: int = 50
    category: str = "general"
    labels: List[str] = field(default_factory=list)
    description: str = ""
    enabled: bool = True
    
    def __post_init__(self):
        """Validate priority range."""
        if not (0 <= self.priority <= 100):
            raise ValueError(f"Priority must be between 0 and 100, got {self.priority}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            "name": self.name,
            "rule_type": self.rule_type.value,
            "pattern": self.pattern,
            "priority": self.priority,
            "category": self.category,
            "labels": self.labels,
            "description": self.description,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rule':
        """Create rule from dictionary."""
        return cls(
            name=data["name"],
            rule_type=RuleType(data["rule_type"]),
            pattern=data["pattern"],
            priority=data.get("priority", 50),
            category=data.get("category", "general"),
            labels=data.get("labels", []),
            description=data.get("description", ""),
            enabled=data.get("enabled", True)
        )


@dataclass
class RuleMatch:
    """Represents a match between an email and a rule."""
    rule: Rule
    match_type: RuleMatchType
    matched_value: str
    confidence: float = 1.0
    rule_name: str = ""
    
    def __post_init__(self):
        """Set rule_name from rule if not provided."""
        if not self.rule_name and self.rule:
            self.rule_name = self.rule.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match to dictionary."""
        return {
            "rule_name": self.rule_name,
            "rule_type": self.rule.rule_type.value if self.rule else None,
            "match_type": self.match_type.value,
            "matched_value": self.matched_value,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], rule: Optional[Rule] = None) -> 'RuleMatch':
        """Create match from dictionary."""
        return cls(
            rule=rule,
            match_type=RuleMatchType(data["match_type"]),
            matched_value=data["matched_value"],
            confidence=data.get("confidence", 1.0),
            rule_name=data.get("rule_name", "")
        )
    
    def __repr__(self) -> str:
        return f"RuleMatch(rule='{self.rule_name}', type={self.match_type.value}, value='{self.matched_value}')"


@dataclass
class ActionExecutionResult:
    """Result of an action execution."""
    action_type: ActionType
    success: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "action_type": self.action_type.value,
            "success": self.success,
            "message": self.message,
            "details": self.details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionExecutionResult':
        """Create result from dictionary."""
        return cls(
            action_type=ActionType(data["action_type"]),
            success=data["success"],
            message=data["message"],
            details=data.get("details", {})
        )
    
    def __repr__(self) -> str:
        return f"ActionExecutionResult(action_type={self.action_type}, success={self.success}, message='{self.message}')"


# == Collection Models ==

@dataclass
class RuleSet:
    """A collection of rules."""
    name: str
    rules: List[Rule] = field(default_factory=list)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_rule(self, rule: Rule):
        """Add a rule to the set."""
        self.rules.append(rule)
        self.updated_at = datetime.now()
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name."""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_rule(self, rule_name: str) -> Optional[Rule]:
        """Get a rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def get_enabled_rules(self) -> List[Rule]:
        """Get all enabled rules, sorted by priority."""
        return sorted(
            [r for r in self.rules if r.enabled],
            key=lambda r: r.priority,
            reverse=True
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule set to dictionary."""
        return {
            "name": self.name,
            "rules": [r.to_dict() for r in self.rules],
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuleSet':
        """Create rule set from dictionary."""
        rules = [Rule.from_dict(r) for r in data.get("rules", [])]
        return cls(
            name=data["name"],
            rules=rules,
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        )


@dataclass
class ActionSet:
    """A collection of actions."""
    name: str
    actions: List[ActionType] = field(default_factory=list)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_action(self, action: ActionType):
        """Add an action to the set."""
        self.actions.append(action)
        self.updated_at = datetime.now()
    
    def remove_action(self, action_type: ActionType) -> bool:
        """Remove an action by type."""
        for i, action in enumerate(self.actions):
            if action == action_type:
                self.actions.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_action(self, action_type: ActionType) -> Optional[ActionType]:
        """Get an action by type."""
        for action in self.actions:
            if action == action_type:
                return action
        return None
    
    def get_enabled_actions(self) -> List[ActionType]:
        """Get all enabled actions."""
        return [a for a in self.actions]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action set to dictionary."""
        return {
            "name": self.name,
            "actions": [a.value for a in self.actions],
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionSet':
        """Create action set from dictionary."""
        actions = [ActionType(a) for a in data.get("actions", [])]
        return cls(
            name=data["name"],
            actions=actions,
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        )


# == Configuration and Statistics ==

@dataclass
class ProcessingConfig:
    """Configuration for email processing."""
    max_processing_time_ms: int = 30000
    max_actions_per_email: int = 10
    enable_attachments: bool = True
    enable_llm: bool = False
    enable_monitoring: bool = True
    rule_sets: List[RuleSet] = field(default_factory=list)
    action_sets: List[ActionSet] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "max_processing_time_ms": self.max_processing_time_ms,
            "max_actions_per_email": self.max_actions_per_email,
            "enable_attachments": self.enable_attachments,
            "enable_llm": self.enable_llm,
            "enable_monitoring": self.enable_monitoring,
            "rule_sets": [rs.to_dict() for rs in self.rule_sets],
            "action_sets": [as_.to_dict() for as_ in self.action_sets]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingConfig':
        """Create config from dictionary."""
        rule_sets = [RuleSet.from_dict(rs) for rs in data.get("rule_sets", [])]
        action_sets = [ActionSet.from_dict(as_) for as_ in data.get("action_sets", [])]
        return cls(
            max_processing_time_ms=data.get("max_processing_time_ms", 30000),
            max_actions_per_email=data.get("max_actions_per_email", 10),
            enable_attachments=data.get("enable_attachments", True),
            enable_llm=data.get("enable_llm", False),
            enable_monitoring=data.get("enable_monitoring", True),
            rule_sets=rule_sets,
            action_sets=action_sets
        )


@dataclass
class ProcessingStats:
    """Statistics for email processing."""
    total_emails: int = 0
    processed_emails: int = 0
    successful_emails: int = 0
    failed_emails: int = 0
    matched_emails: int = 0
    total_rules: int = 0
    total_actions: int = 0
    total_processing_time_ms: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    def add_error(self, error_type: str):
        """Add an error to the stats."""
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.processed_emails == 0:
            return 0.0
        return self.successful_emails / self.processed_emails
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_emails": self.total_emails,
            "processed_emails": self.processed_emails,
            "successful_emails": self.successful_emails,
            "failed_emails": self.failed_emails,
            "matched_emails": self.matched_emails,
            "total_rules": self.total_rules,
            "total_actions": self.total_actions,
            "success_rate": self.success_rate,
            "total_processing_time_ms": self.total_processing_time_ms,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "errors_by_type": self.errors_by_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingStats':
        """Create stats from dictionary."""
        return cls(
            total_emails=data.get("total_emails", 0),
            processed_emails=data.get("processed_emails", 0),
            successful_emails=data.get("successful_emails", 0),
            failed_emails=data.get("failed_emails", 0),
            matched_emails=data.get("matched_emails", 0),
            total_rules=data.get("total_rules", 0),
            total_actions=data.get("total_actions", 0),
            total_processing_time_ms=data.get("total_processing_time_ms", 0.0),
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            errors_by_type=data.get("errors_by_type", {})
        )


# == Processing Results ==

@dataclass
class EmailMatch:
    """Represents a match between an email and a rule."""
    email_id: str
    rule_name: str
    match_type: RuleMatchType
    matched_value: str
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match to dictionary."""
        return {
            "email_id": self.email_id,
            "rule_name": self.rule_name,
            "match_type": self.match_type.value,
            "matched_value": self.matched_value,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailMatch':
        """Create match from dictionary."""
        return cls(
            email_id=data["email_id"],
            rule_name=data["rule_name"],
            match_type=RuleMatchType(data["match_type"]),
            matched_value=data["matched_value"],
            confidence=data.get("confidence", 1.0)
        )


@dataclass
class EmailProcessingResult:
    """Result of processing an email."""
    email_id: str
    status: ProcessingStatus
    processing_time_ms: float
    rules_matched: int
    actions_executed: int
    errors: List[str] = field(default_factory=list)
    matched_rules: List[str] = field(default_factory=list)
    executed_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "email_id": self.email_id,
            "status": self.status.value,
            "processing_time_ms": self.processing_time_ms,
            "rules_matched": self.rules_matched,
            "actions_executed": self.actions_executed,
            "errors": self.errors,
            "matched_rules": self.matched_rules,
            "executed_actions": self.executed_actions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailProcessingResult':
        """Create result from dictionary."""
        return cls(
            email_id=data["email_id"],
            status=ProcessingStatus(data["status"]),
            processing_time_ms=data.get("processing_time_ms", 0.0),
            rules_matched=data.get("rules_matched", 0),
            actions_executed=data.get("actions_executed", 0),
            errors=data.get("errors", []),
            matched_rules=data.get("matched_rules", []),
            executed_actions=data.get("executed_actions", [])
        )
