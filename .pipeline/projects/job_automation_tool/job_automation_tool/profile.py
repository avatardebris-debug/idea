"""Job profile data model."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Profile:
    """Represents a job profile with structured fields."""

    title: str = ""
    company: str = ""
    description: str = ""
    skills: list[str] = field(default_factory=list)
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: Optional[str] = None
    source_url: Optional[str] = None
    parsed_at: str = ""

    def __post_init__(self) -> None:
        if not self.parsed_at:
            self.parsed_at = datetime.now().isoformat()
        # Normalize skills to lowercase for consistent matching
        self.skills = [s.lower().strip() for s in self.skills]

    @classmethod
    def from_dict(cls, data: dict) -> Profile:
        """Create a Profile from a dictionary."""
        # Filter out any keys not in the dataclass fields
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    def to_dict(self) -> dict:
        """Convert the Profile to a dictionary."""
        return asdict(self)

    def validate(self) -> list[str]:
        """Validate required fields. Returns list of error messages (empty if valid)."""
        errors: list[str] = []
        if not self.title.strip():
            errors.append("title is required")
        if not self.company.strip():
            errors.append("company is required")
        if not self.description.strip():
            errors.append("description is required")
        return errors

    def validate_or_raise(self) -> None:
        """Validate and raise ValueError on failure."""
        errors = self.validate()
        if errors:
            raise ValueError("; ".join(errors))

    def skill_similarity(self, other_skills: list[str]) -> float:
        """Compute Jaccard similarity between this profile's skills and another set."""
        my_skills = set(self.skills)
        other_set = set(s.lower().strip() for s in other_skills)
        if not my_skills and not other_set:
            return 1.0
        if not my_skills or not other_set:
            return 0.0
        intersection = my_skills & other_set
        union = my_skills | other_set
        return len(intersection) / len(union) if union else 0.0
