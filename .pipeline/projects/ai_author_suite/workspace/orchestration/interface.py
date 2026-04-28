"""
Interface - Phase 6
CLI-based user interaction for the AI Author Suite workflow.
"""

from typing import Optional
from .workflow_manager import WorkflowManager
from .state_manager import StateManager


class Interface:
    """
    Provides CLI-based user interaction for the complete book creation process.
    Guides users through each phase and displays progress.
    """

    def __init__(self, workflow_manager: Optional[WorkflowManager] = None):
        """
        Initialize the interface.

        Args:
            workflow_manager: WorkflowManager instance. If None, a new one will be created.
        """
        self.workflow_manager = workflow_manager or WorkflowManager()
        self.state_manager = self.workflow_manager.state_manager

    def start_book_creation(self) -> bool:
        """
        Start the book creation workflow with user interaction.

        Returns:
            True if workflow completed successfully.
        """
        print("=" * 60)
        print("AI Author Suite - Book Creation Workflow")
        print("=" * 60)

        # Get topic from user
        topic = self._get_user_input("Enter your book topic: ")
        if not topic:
            print("Error: Topic cannot be empty")
            return False

        print(f"\nStarting workflow for topic: '{topic}'")
        print("This may take a few moments...\n")

        # Execute workflow
        success = self.workflow_manager.execute_workflow(topic)

        if success:
            self._display_completion_message()
        else:
            self._display_error_message()

        return success

    def _get_user_input(self, prompt: str) -> str:
        """
        Get input from the user.

        Args:
            prompt: The prompt to display.

        Returns:
            User input as a string.
        """
        try:
            return input(prompt).strip()
        except EOFError:
            return ""
        except KeyboardInterrupt:
            print("\n\nWorkflow cancelled by user")
            return ""

    def _display_progress(self, progress: dict) -> None:
        """
        Display current workflow progress.

        Args:
            progress: Progress dictionary from workflow manager.
        """
        print("\n" + "-" * 40)
        print("Current Progress:")
        print(f"  Current Phase: {progress['current_phase']}")
        print(f"  Completed: {progress['completed_phases']}/{progress['total_phases']}")
        print("-" * 40)

        for phase, status in progress['phase_status'].items():
            status_icon = "✓" if status == 'completed' else "○"
            print(f"  {status_icon} {phase}: {status}")

    def _display_completion_message(self) -> None:
        """Display completion message."""
        print("\n" + "=" * 60)
        print("✓ Book creation workflow completed successfully!")
        print("=" * 60)
        print("\nYour book has been processed through all phases:")
        print("  - Research: Topic analysis and keyword research")
        print("  - Outlining: Book structure and chapter planning")
        print("  - Development: Chapter content generation")
        print("  - Editor: Content refinement and optimization")
        print("  - Design: Cover design and visual elements")
        print("\nState has been saved for future reference.")

    def _display_error_message(self) -> None:
        """Display error message."""
        print("\n" + "=" * 60)
        print("✗ Book creation workflow failed")
        print("=" * 60)
        print("\nAn error occurred during the workflow.")
        print("Please check the error messages above and try again.")

    def resume_workflow(self) -> bool:
        """
        Resume a previously interrupted workflow.

        Returns:
            True if workflow resumed and completed successfully.
        """
        print("\n" + "=" * 60)
        print("Resuming Previous Workflow")
        print("=" * 60)

        progress = self.workflow_manager.get_progress()
        if progress['completed_phases'] == 0:
            print("No previous workflow found. Starting fresh.")
            return self.start_book_creation()

        print(f"Found {progress['completed_phases']} completed phases.")
        print("Resuming from the next phase...\n")

        # Get topic from saved state or user
        state = self.workflow_manager.get_state()
        topic = state.get('research', {}).get('data', {}).get('topic', '')

        if not topic:
            topic = self._get_user_input("Enter your book topic: ")
            if not topic:
                print("Error: Topic cannot be empty")
                return False

        success = self.workflow_manager.resume_workflow(topic)

        if success:
            self._display_completion_message()
        else:
            self._display_error_message()

        return success

    def show_status(self) -> None:
        """Display current workflow status."""
        progress = self.workflow_manager.get_progress()
        self._display_progress(progress)

        state = self.workflow_manager.get_state()
        if state:
            print("\nSaved State:")
            for phase, data in state.items():
                if data:
                    print(f"  {phase}: ✓ saved")
                else:
                    print(f"  {phase}: empty")

    def clear_state(self) -> None:
        """Clear all saved state."""
        self.state_manager.clear_state()
        print("All saved state has been cleared.")
