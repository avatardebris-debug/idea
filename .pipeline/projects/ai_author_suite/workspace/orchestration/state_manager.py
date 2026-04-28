"""
State Manager - Phase 6
Manages project state across all phases with persistence and validation.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class StateManager:
    """
    Manages project state across all phases of the AI Author Suite.
    Persists state to disk and validates data integrity.
    """

    def __init__(self, state_dir: str = "state"):
        """
        Initialize the state manager.

        Args:
            state_dir: Directory to store state files. Defaults to 'state'.
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "project_state.json"
        self.current_state: Dict[str, Any] = {}

    def save_state(self, phase: str, data: Dict[str, Any]) -> bool:
        """
        Save state for a specific phase.

        Args:
            phase: The phase name (e.g., 'research', 'outlining', 'development').
            data: The state data to save.

        Returns:
            True if save was successful, False otherwise.
        """
        try:
            self.current_state[phase] = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            self._persist_state()
            return True
        except Exception as e:
            print(f"Error saving state for phase {phase}: {e}")
            return False

    def load_state(self, phase: str) -> Optional[Dict[str, Any]]:
        """
        Load state for a specific phase.

        Args:
            phase: The phase name to load.

        Returns:
            The state data if found, None otherwise.
        """
        try:
            self._load_state()
            if phase in self.current_state:
                return self.current_state[phase].get('data')
            return None
        except Exception as e:
            print(f"Error loading state for phase {phase}: {e}")
            return None

    def get_full_state(self) -> Dict[str, Any]:
        """
        Get the complete project state.

        Returns:
            Dictionary containing all phase states.
        """
        self._load_state()
        return {
            phase: data.get('data', {})
            for phase, data in self.current_state.items()
        }

    def validate_state(self, phase: str, data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate state data for a phase.

        Args:
            phase: The phase name.
            data: The data to validate.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        if phase == 'research':
            errors.extend(self._validate_research_data(data))
        elif phase == 'outlining':
            errors.extend(self._validate_outlining_data(data))
        elif phase == 'development':
            errors.extend(self._validate_development_data(data))
        elif phase == 'editor':
            errors.extend(self._validate_editor_data(data))
        elif phase == 'design':
            errors.extend(self._validate_design_data(data))

        return len(errors) == 0, errors

    def _validate_research_data(self, data: Dict[str, Any]) -> list[str]:
        """Validate research phase data."""
        errors = []
        required_fields = ['topic', 'niche_analysis', 'keywords', 'market_analysis']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        return errors

    def _validate_outlining_data(self, data: Dict[str, Any]) -> list[str]:
        """Validate outlining phase data."""
        errors = []
        required_fields = ['book_title', 'outline', 'chapters']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        return errors

    def _validate_development_data(self, data: Dict[str, Any]) -> list[str]:
        """Validate development phase data."""
        errors = []
        required_fields = ['chapters', 'content']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        return errors

    def _validate_editor_data(self, data: Dict[str, Any]) -> list[str]:
        """Validate editor phase data."""
        errors = []
        required_fields = ['edited_content', 'suggestions']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        return errors

    def _validate_design_data(self, data: Dict[str, Any]) -> list[str]:
        """Validate design phase data."""
        errors = []
        required_fields = ['cover_design', 'design_elements']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        return errors

    def _persist_state(self) -> None:
        """Persist current state to disk."""
        with open(self.state_file, 'w') as f:
            json.dump(self.current_state, f, indent=2)

    def _load_state(self) -> None:
        """Load state from disk."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.current_state = json.load(f)
        else:
            self.current_state = {}

    def clear_state(self) -> None:
        """Clear all saved state."""
        self.current_state = {}
        if self.state_file.exists():
            self.state_file.unlink()

    def get_phase_progress(self) -> Dict[str, bool]:
        """
        Get progress status for each phase.

        Returns:
            Dictionary mapping phase names to completion status.
        """
        self._load_state()
        return {
            phase: phase in self.current_state
            for phase in ['research', 'outlining', 'development', 'editor', 'design']
        }
