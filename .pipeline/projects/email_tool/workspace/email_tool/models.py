"""Data models for the email tool."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class RuleType(Enum):
    """Types of rules that can be evaluated against emails."""
    FROM_EXACT = "from_exact"
    FROM_PATTERN = "from_pattern"
    SUBJECT_EXACT = "subject_exact"
    SUBJECT_CONTAINS = "subject_contains"
    SUBJECT_PATTERN = "subject_pattern"
    BODY_CONTAINS_EXACT = "body_contains_exact"
    BODY_CONTAINS_CONTAINS = "body_contains_contains"
    BODY_CONTAINS_PATTERN = "body_contains_pattern"
    HAS_ATTACHMENT = "has_attachment"


class RuleMatchType(Enum):
    """Types of rule matches."""
    EXACT = "exact"
    CONTAINS = "contains"
    PATTERN = "pattern"


class RuleMatchStrategy(Enum):
    """Strategy for matching multiple rules to an email."""
    FIRST_MATCH = "first_match"  # Return the first matching rule
    BEST_MATCH = "best_match"    # Return the highest priority matching rule
    ALL_MATCH = "all_match"      # Return all matching rules


class Category(Enum):
    """Categories for email classification."""
    SPAM = "spam"
    PROMOTIONAL = "promotional"
    NEWSLETTER = "newsletter"
    PERSONAL = "personal"
    WORK = "work"
    URGENT = "urgent"
    GENERAL = "general"


@dataclass
class Email:
    """Represents an email message."""
    from_addr: str
    to_addrs: List[str]
    subject: str
    date: Optional[datetime] = None
    body_plain: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    raw_headers: dict = field(default_factory=dict)
    labels: List[str] = field(default_factory=list)
    source_path: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Ensure to_addrs is always a list."""
        if isinstance(self.to_addrs, str):
            self.to_addrs = [self.to_addrs]
        if self.attachments is None:
            self.attachments = []
        if self.raw_headers is None:
            self.raw_headers = {}
        if self.labels is None:
            self.labels = []
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_eml(self) -> str:
        """Convert email to EML format string."""
        from email.message import EmailMessage
        from email.utils import formatdate, make_msgid
        
        # Create an EmailMessage object for proper formatting
        msg = EmailMessage()
        
        # Set standard headers
        msg['From'] = self.from_addr
        msg['To'] = ', '.join(self.to_addrs) if self.to_addrs else ''
        msg['Subject'] = self.subject
        
        # Set Date header if available
        if self.date:
            msg['Date'] = formatdate(self.date.timestamp(), usegmt=True)
        
        # Set Message-ID
        msg['Message-ID'] = make_msgid()
        
        # Set MIME version
        msg['MIME-Version'] = '1.0'
        
        # Set body content
        if self.body_html and self.body_plain:
            # Multi-part email with both plain and HTML
            msg.set_content(self.body_plain)
            msg.add_alternative(self.body_html, subtype='html')
        elif self.body_html:
            # HTML only
            msg.set_content(self.body_html, subtype='html')
        elif self.body_plain:
            # Plain text only
            msg.set_content(self.body_plain)
        else:
            # Empty body
            msg.set_content('')
        
        # Add custom headers from raw_headers
        for header_name, header_value in self.raw_headers.items():
            if header_name not in ['From', 'To', 'Subject', 'Date', 'Message-ID', 'MIME-Version']:
                msg[header_name] = header_value
        
        # Serialize to string
        return msg.as_string()


@dataclass
class Rule:
    """Represents a rule that can be evaluated against emails."""
    name: str
    rule_type: RuleType
    pattern: Optional[str] = None
    value: Optional[str] = None
    priority: int = 50
    category: str = "general"
    description: str = ""
    labels: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate rule configuration."""
        if self.priority < 0 or self.priority > 100:
            raise ValueError("Priority must be between 0 and 100")
        if self.labels is None:
            self.labels = []
        if self.rule_type in [RuleType.FROM_EXACT, RuleType.FROM_PATTERN,
                             RuleType.SUBJECT_EXACT, RuleType.SUBJECT_CONTAINS,
                             RuleType.SUBJECT_PATTERN, RuleType.BODY_CONTAINS_EXACT,
                             RuleType.BODY_CONTAINS_CONTAINS, RuleType.BODY_CONTAINS_PATTERN]:
            if self.pattern is None:
                raise ValueError(f"Rule type {self.rule_type} requires a pattern")


@dataclass
class RuleMatch:
    """Represents a rule match result."""
    rule: Rule
    match_type: str
    matched_value: Optional[str] = None
    confidence: float = 1.0

    def __post_init__(self):
        """Ensure labels is always a list."""
        if self.matched_value is None:
            self.matched_value = None

    @property
    def rule_name(self) -> str:
        """Get the rule name."""
        return self.rule.name

    @property
    def rule_type(self) -> RuleType:
        """Get the rule type."""
        return self.rule.rule_type

    @property
    def priority(self) -> int:
        """Get the rule priority."""
        return self.rule.priority

    @property
    def category(self) -> str:
        """Get the rule category."""
        return self.rule.category

    @property
    def labels(self) -> List[str]:
        """Get the rule labels."""
        return self.rule.labels if hasattr(self.rule, 'labels') else []


class ActionType(Enum):
    """Types of actions that can be executed on emails."""
    MOVE = "MOVE"
    FILE = "FILE"
    LABEL = "LABEL"
    NOTIFY = "NOTIFY"
    DELETE = "DELETE"
    FORWARD = "FORWARD"


@dataclass
class ActionExecutionResult:
    """Represents the result of an action execution."""
    action_type: ActionType
    success: bool
    message: str
    details: dict = field(default_factory=dict)

    def __post_init__(self):
        """Ensure details is always a dict."""
        if self.details is None:
            self.details = {}
