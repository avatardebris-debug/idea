"""
Workflow Manager - Phase 6
Coordinates multi-phase workflows for the AI Author Suite.
"""

from typing import Any, Dict, Optional, Callable
from .state_manager import StateManager


class WorkflowManager:
    """
    Manages the complete book creation workflow from research through design.
    Orchestrates phase execution and handles transitions.
    """

    def __init__(self, state_manager: Optional[StateManager] = None):
        """
        Initialize the workflow manager.

        Args:
            state_manager: StateManager instance for persisting state.
                          If None, a new one will be created.
        """
        self.state_manager = state_manager or StateManager()
        self.current_phase: str = ""
        self.phase_status: Dict[str, str] = {}
        self.progress_log: list[Dict[str, Any]] = []

    def execute_workflow(self, topic: str) -> bool:
        """
        Execute the complete workflow from research to design.

        Args:
            topic: The book topic to process.

        Returns:
            True if workflow completed successfully, False otherwise.
        """
        try:
            phases = ['research', 'outlining', 'development', 'editor', 'design']
            self.progress_log = []

            for phase in phases:
                self.current_phase = phase
                success = self._execute_phase(phase, topic)
                if not success:
                    print(f"Workflow failed at phase: {phase}")
                    return False

            return True
        except Exception as e:
            print(f"Workflow error: {e}")
            return False

    def _execute_phase(self, phase: str, topic: str) -> bool:
        """
        Execute a single phase of the workflow.

        Args:
            phase: The phase name to execute.
            topic: The book topic.

        Returns:
            True if phase completed successfully.
        """
        try:
            # Import phase modules dynamically
            phase_module = self._import_phase_module(phase)
            if phase_module is None:
                print(f"Could not import phase module: {phase}")
                return False

            # Execute phase
            result = phase_module.execute(topic)

            # Validate and save state
            is_valid, errors = self.state_manager.validate_state(phase, result)
            if not is_valid:
                print(f"Phase {phase} validation failed: {errors}")
                return False

            self.state_manager.save_state(phase, result)
            self.phase_status[phase] = 'completed'
            self.progress_log.append({
                'phase': phase,
                'status': 'completed',
                'timestamp': str(self._get_timestamp())
            })

            print(f"Phase {phase} completed successfully")
            return True

        except ImportError as e:
            print(f"Import error for phase {phase}: {e}")
            self._record_failure(phase, f"Import error: {e}")
            return False
        except Exception as e:
            print(f"Error executing phase {phase}: {e}")
            self._record_failure(phase, str(e))
            return False

    def _import_phase_module(self, phase: str) -> Optional[Any]:
        """
        Import a phase module dynamically.

        Args:
            phase: The phase name.

        Returns:
            The imported module or None if import fails.
        """
        try:
            module_path = f"workspace.{phase}"
            if phase == 'research':
                from workspace.research.report_generator import ReportGenerator
                return ReportGenerator
            elif phase == 'outlining':
                from workspace.outlining.book_outliner import BookOutliner
                return BookOutliner
            elif phase == 'development':
                from workspace.development.chapter_developer import ChapterDeveloper
                return ChapterDeveloper
            elif phase == 'editor':
                from workspace.editor.deep_editor import DeepEditor
                return DeepEditor
            elif phase == 'design':
                from workspace.design.cover_designer import CoverDesigner
                return CoverDesigner
            return None
        except ImportError:
            return None

    def _record_failure(self, phase: str, error: str) -> None:
        """Record a phase failure."""
        self.phase_status[phase] = 'failed'
        self.progress_log.append({
            'phase': phase,
            'status': 'failed',
            'error': error,
            'timestamp': str(self._get_timestamp())
        })

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_progress(self) -> Dict[str, Any]:
        """
        Get current workflow progress.

        Returns:
            Dictionary containing progress information.
        """
        return {
            'current_phase': self.current_phase,
            'phase_status': self.phase_status,
            'progress_log': self.progress_log,
            'completed_phases': sum(1 for s in self.phase_status.values() if s == 'completed'),
            'total_phases': len(self.phase_status)
        }

    def resume_workflow(self, topic: str) -> bool:
        """
        Resume a workflow from the last completed phase.

        Args:
            topic: The book topic.

        Returns:
            True if workflow resumed and completed successfully.
        """
        completed_phases = [
            phase for phase, status in self.phase_status.items()
            if status == 'completed'
        ]

        if not completed_phases:
            print("No completed phases to resume from")
            return self.execute_workflow(topic)

        # Start from the next phase after the last completed one
        phases = ['research', 'outlining', 'development', 'editor', 'design']
        start_index = len(completed_phases)

        if start_index >= len(phases):
            print("All phases already completed")
            return True

        for phase in phases[start_index:]:
            if not self._execute_phase(phase, topic):
                return False

        return True

    def get_state(self) -> Dict[str, Any]:
        """
        Get the current project state.

        Returns:
            Dictionary containing all saved state data.
        """
        return self.state_manager.get_full_state()
