"""Accountability Manager - Implements accountability mechanisms for the DESS framework."""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum

import yaml


class AccountabilityType(Enum):
    """Types of accountability mechanisms."""
    PUBLIC_COMMITMENT = "public_commitment"
    FINANCIAL_PENALTY = "financial_penalty"
    PROGRESS_TRACKING = "progress_tracking"
    ACCOUNTABILITY_PARTNER = "accountability_partner"
    SOCIAL_CONTRACT = "social_contract"


class StakesLevel(Enum):
    """Levels of stakes intensity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class PublicCommitment:
    """Represents a public commitment to a learning goal."""
    commitment_id: str
    goal_description: str
    commitment_date: datetime
    deadline: datetime
    public_platform: str  # e.g., "social_media", "blog", "community"
    audience_size: int
    status: str  # "active", "completed", "expired"
    progress_percentage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "commitment_id": self.commitment_id,
            "goal_description": self.goal_description,
            "commitment_date": self.commitment_date.isoformat(),
            "deadline": self.deadline.isoformat(),
            "public_platform": self.public_platform,
            "audience_size": self.audience_size,
            "status": self.status,
            "progress_percentage": self.progress_percentage
        }


@dataclass
class FinancialPenalty:
    """Represents a financial penalty mechanism."""
    penalty_id: str
    amount: float
    currency: str
    trigger_condition: str
    payout_recipient: str
    status: str  # "active", "triggered", "paid", "waived"
    created_date: datetime
    triggered_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "penalty_id": self.penalty_id,
            "amount": self.amount,
            "currency": self.currency,
            "trigger_condition": self.trigger_condition,
            "payout_recipient": self.payout_recipient,
            "status": self.status,
            "created_date": self.created_date.isoformat(),
            "triggered_date": self.triggered_date.isoformat() if self.triggered_date else None
        }


@dataclass
class AccountabilityPartner:
    """Represents an accountability partner relationship."""
    partner_id: str
    partner_name: str
    partner_email: str
    relationship_type: str  # "peer", "mentor", "coach"
    check_in_frequency: str  # "daily", "weekly", "biweekly"
    next_check_in: datetime
    status: str  # "active", "inactive"
    shared_goals: List[str]
    communication_method: str  # "email", "video_call", "chat"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "partner_id": self.partner_id,
            "partner_name": self.partner_name,
            "partner_email": self.partner_email,
            "relationship_type": self.relationship_type,
            "check_in_frequency": self.check_in_frequency,
            "next_check_in": self.next_check_in.isoformat(),
            "status": self.status,
            "shared_goals": self.shared_goals,
            "communication_method": self.communication_method
        }


@dataclass
class AccountabilityRecord:
    """Records accountability activities and outcomes."""
    record_id: str
    timestamp: datetime
    accountability_type: str
    action_taken: str
    outcome: str
    effectiveness_score: float  # 0-10
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp.isoformat(),
            "accountability_type": self.accountability_type,
            "action_taken": self.action_taken,
            "outcome": self.outcome,
            "effectiveness_score": self.effectiveness_score,
            "notes": self.notes
        }


class AccountabilityManager:
    """
    Manages accountability mechanisms for learning goals.
    
    Implements various accountability types from the DESS framework:
    - Public commitments
    - Financial penalties
    - Progress tracking
    - Accountability partners
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the accountability manager.
        
        Args:
            config_path: Path to accountability configuration file.
        """
        self.config = self._load_config(config_path)
        self.commitments: List[PublicCommitment] = []
        self.penalties: List[FinancialPenalty] = []
        self.partners: List[AccountabilityPartner] = []
        self.records: List[AccountabilityRecord] = []
        self.data_dir = Path("data/accountability")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_data()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load accountability configuration."""
        default_config = {
            "accountability_level": "medium",
            "stakes_types": [
                "public_commitment",
                "financial_penalty",
                "progress_tracking"
            ],
            "progress_threshold": 70,
            "check_in_frequency": "weekly",
            "notification_enabled": True
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    default_config.update(loaded_config)
        
        return default_config
    
    def _load_data(self):
        """Load existing accountability data from files."""
        # Load commitments
        commitments_file = self.data_dir / "commitments.json"
        if commitments_file.exists():
            with open(commitments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.commitments = [
                    PublicCommitment(**item) for item in data.get("commitments", [])
                ]
        
        # Load penalties
        penalties_file = self.data_dir / "penalties.json"
        if penalties_file.exists():
            with open(penalties_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.penalties = [
                    FinancialPenalty(**item) for item in data.get("penalties", [])
                ]
        
        # Load partners
        partners_file = self.data_dir / "partners.json"
        if partners_file.exists():
            with open(partners_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.partners = [
                    AccountabilityPartner(**item) for item in data.get("partners", [])
                ]
        
        # Load records
        records_file = self.data_dir / "records.json"
        if records_file.exists():
            with open(records_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.records = [
                    AccountabilityRecord(**item) for item in data.get("records", [])
                ]
    
    def save_data(self):
        """Save all accountability data to files."""
        # Save commitments
        with open(self.data_dir / "commitments.json", 'w', encoding='utf-8') as f:
            json.dump({
                "commitments": [c.to_dict() for c in self.commitments]
            }, f, indent=2)
        
        # Save penalties
        with open(self.data_dir / "penalties.json", 'w', encoding='utf-8') as f:
            json.dump({
                "penalties": [p.to_dict() for p in self.penalties]
            }, f, indent=2)
        
        # Save partners
        with open(self.data_dir / "partners.json", 'w', encoding='utf-8') as f:
            json.dump({
                "partners": [p.to_dict() for p in self.partners]
            }, f, indent=2)
        
        # Save records
        with open(self.data_dir / "records.json", 'w', encoding='utf-8') as f:
            json.dump({
                "records": [r.to_dict() for r in self.records]
            }, f, indent=2)
    
    def create_public_commitment(
        self,
        goal_description: str,
        deadline: datetime,
        public_platform: str = "social_media",
        audience_size: int = 100,
        notes: str = ""
    ) -> PublicCommitment:
        """
        Create a new public commitment.
        
        Args:
            goal_description: Description of the learning goal.
            deadline: Deadline for achieving the goal.
            public_platform: Platform for public commitment.
            audience_size: Estimated audience size.
            notes: Additional notes.
        
        Returns:
            Created PublicCommitment object.
        """
        commitment = PublicCommitment(
            commitment_id=str(uuid.uuid4()),
            goal_description=goal_description,
            commitment_date=datetime.now(),
            deadline=deadline,
            public_platform=public_platform,
            audience_size=audience_size,
            status="active",
            progress_percentage=0.0
        )
        
        self.commitments.append(commitment)
        self._create_record(
            accountability_type=AccountabilityType.PUBLIC_COMMITMENT.value,
            action_taken=f"Created public commitment for {goal_description}",
            outcome="Commitment created successfully",
            effectiveness_score=8.0,
            notes=notes
        )
        
        self.save_data()
        return commitment
    
    def update_commitment_progress(
        self,
        commitment_id: str,
        progress_percentage: float,
        notes: str = ""
    ) -> Optional[PublicCommitment]:
        """
        Update the progress of a public commitment.
        
        Args:
            commitment_id: ID of the commitment to update.
            progress_percentage: New progress percentage (0-100).
            notes: Notes about the progress update.
        
        Returns:
            Updated PublicCommitment or None if not found.
        """
        for commitment in self.commitments:
            if commitment.commitment_id == commitment_id:
                commitment.progress_percentage = progress_percentage
                
                # Check if deadline is reached
                if datetime.now() >= commitment.deadline:
                    commitment.status = "completed" if progress_percentage >= 100 else "expired"
                
                self._create_record(
                    accountability_type=AccountabilityType.PUBLIC_COMMITMENT.value,
                    action_taken=f"Updated progress to {progress_percentage}%",
                    outcome=f"Progress updated for commitment {commitment_id}",
                    effectiveness_score=7.0,
                    notes=notes
                )
                
                self.save_data()
                return commitment
        
        return None
    
    def create_financial_penalty(
        self,
        amount: float,
        currency: str = "USD",
        trigger_condition: str = "Not completing learning goal by deadline",
        payout_recipient: str = "charity",
        deadline: Optional[datetime] = None,
        notes: str = ""
    ) -> FinancialPenalty:
        """
        Create a new financial penalty mechanism.
        
        Args:
            amount: Penalty amount.
            currency: Currency code.
            trigger_condition: Condition that triggers the penalty.
            payout_recipient: Recipient of the penalty payment.
            deadline: Deadline for the learning goal.
            notes: Additional notes.
        
        Returns:
            Created FinancialPenalty object.
        """
        penalty = FinancialPenalty(
            penalty_id=str(uuid.uuid4()),
            amount=amount,
            currency=currency,
            trigger_condition=trigger_condition,
            payout_recipient=payout_recipient,
            status="active",
            created_date=datetime.now(),
            triggered_date=None
        )
        
        self.penalties.append(penalty)
        self._create_record(
            accountability_type=AccountabilityType.FINANCIAL_PENALTY.value,
            action_taken=f"Created financial penalty of {amount} {currency}",
            outcome="Penalty created successfully",
            effectiveness_score=9.0,
            notes=notes
        )
        
        self.save_data()
        return penalty
    
    def add_accountability_partner(
        self,
        partner_name: str,
        partner_email: str,
        relationship_type: str = "peer",
        check_in_frequency: str = "weekly",
        shared_goals: Optional[List[str]] = None,
        communication_method: str = "email",
        notes: str = ""
    ) -> AccountabilityPartner:
        """
        Add a new accountability partner.
        
        Args:
            partner_name: Name of the partner.
            partner_email: Email address of the partner.
            relationship_type: Type of relationship.
            check_in_frequency: Frequency of check-ins.
            shared_goals: List of shared learning goals.
            communication_method: Preferred communication method.
            notes: Additional notes.
        
        Returns:
            Created AccountabilityPartner object.
        """
        partner = AccountabilityPartner(
            partner_id=str(uuid.uuid4()),
            partner_name=partner_name,
            partner_email=partner_email,
            relationship_type=relationship_type,
            check_in_frequency=check_in_frequency,
            next_check_in=datetime.now() + timedelta(days=7),
            status="active",
            shared_goals=shared_goals or [],
            communication_method=communication_method
        )
        
        self.partners.append(partner)
        self._create_record(
            accountability_type=AccountabilityType.ACCOUNTABILITY_PARTNER.value,
            action_taken=f"Added accountability partner {partner_name}",
            outcome="Partner added successfully",
            effectiveness_score=8.5,
            notes=notes
        )
        
        self.save_data()
        return partner
    
    def schedule_check_in(self, partner_id: str, new_date: datetime) -> bool:
        """
        Schedule a check-in with an accountability partner.
        
        Args:
            partner_id: ID of the partner.
            new_date: New check-in date.
        
        Returns:
            True if successful, False if partner not found.
        """
        for partner in self.partners:
            if partner.partner_id == partner_id:
                partner.next_check_in = new_date
                self._create_record(
                    accountability_type=AccountabilityType.ACCOUNTABILITY_PARTNER.value,
                    action_taken=f"Scheduled check-in for {new_date}",
                    outcome="Check-in scheduled",
                    effectiveness_score=7.0,
                    notes=""
                )
                self.save_data()
                return True
        return False
    
    def _create_record(
        self,
        accountability_type: str,
        action_taken: str,
        outcome: str,
        effectiveness_score: float,
        notes: str
    ):
        """Create an accountability record."""
        record = AccountabilityRecord(
            record_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            accountability_type=accountability_type,
            action_taken=action_taken,
            outcome=outcome,
            effectiveness_score=effectiveness_score,
            notes=notes
        )
        self.records.append(record)
    
    def get_active_commitments(self) -> List[PublicCommitment]:
        """Get all active public commitments."""
        return [c for c in self.commitments if c.status == "active"]
    
    def get_active_penalties(self) -> List[FinancialPenalty]:
        """Get all active financial penalties."""
        return [p for p in self.penalties if p.status == "active"]
    
    def get_active_partners(self) -> List[AccountabilityPartner]:
        """Get all active accountability partners."""
        return [p for p in self.partners if p.status == "active"]
    
    def get_accountability_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all accountability mechanisms.
        
        Returns:
            Dictionary with accountability summary statistics.
        """
        return {
            "total_commitments": len(self.commitments),
            "active_commitments": len(self.get_active_commitments()),
            "total_penalties": len(self.penalties),
            "active_penalties": len(self.get_active_penalties()),
            "total_partners": len(self.partners),
            "active_partners": len(self.get_active_partners()),
            "total_records": len(self.records),
            "average_effectiveness": (
                sum(r.effectiveness_score for r in self.records) / len(self.records)
                if self.records else 0
            ),
            "last_updated": datetime.now().isoformat()
        }
    
    def remove_commitment(self, commitment_id: str) -> bool:
        """Remove a public commitment."""
        for i, commitment in enumerate(self.commitments):
            if commitment.commitment_id == commitment_id:
                self.commitments.pop(i)
                self.save_data()
                return True
        return False
    
    def remove_penalty(self, penalty_id: str) -> bool:
        """Remove a financial penalty."""
        for i, penalty in enumerate(self.penalties):
            if penalty.penalty_id == penalty_id:
                self.penalties.pop(i)
                self.save_data()
                return True
        return False
    
    def remove_partner(self, partner_id: str) -> bool:
        """Remove an accountability partner."""
        for i, partner in enumerate(self.partners):
            if partner.partner_id == partner_id:
                self.partners.pop(i)
                self.save_data()
                return True
        return False
