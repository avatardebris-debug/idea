"""
Integration Tests - Phase 6
End-to-end tests for the complete AI Author Suite workflow.
"""

import pytest
import json
import os
from pathlib import Path
from orchestration.state_manager import StateManager
from orchestration.workflow_manager import WorkflowManager
from orchestration.interface import Interface


class TestStateManager:
    """Tests for the StateManager class."""

    def test_save_and_load_state(self, tmp_path):
        """Test saving and loading state."""
        state_manager = StateManager(state_dir=str(tmp_path))
        
        test_data = {'topic': 'test book', 'keywords': ['test', 'keywords']}
        success = state_manager.save_state('research', test_data)
        
        assert success is True
        loaded = state_manager.load_state('research')
        assert loaded is not None
        assert loaded['topic'] == 'test book'

    def test_validate_research_data(self, tmp_path):
        """Test research data validation."""
        state_manager = StateManager(state_dir=str(tmp_path))
        
        valid_data = {
            'topic': 'test',
            'niche_analysis': {},
            'keywords': [],
            'market_analysis': {}
        }
        is_valid, errors = state_manager.validate_state('research', valid_data)
        assert is_valid is True
        assert len(errors) == 0

        invalid_data = {'topic': 'test'}
        is_valid, errors = state_manager.validate_state('research', invalid_data)
        assert is_valid is False
        assert len(errors) > 0

    def test_get_phase_progress(self, tmp_path):
        """Test phase progress tracking."""
        state_manager = StateManager(state_dir=str(tmp_path))
        
        progress = state_manager.get_phase_progress()
        assert 'research' in progress
        assert 'outlining' in progress
        assert 'development' in progress
        assert 'editor' in progress
        assert 'design' in progress


class TestWorkflowManager:
    """Tests for the WorkflowManager class."""

    def test_initialization(self):
        """Test workflow manager initialization."""
        workflow_manager = WorkflowManager()
        assert workflow_manager.current_phase == ""
        assert workflow_manager.phase_status == {}

    def test_get_progress(self):
        """Test progress tracking."""
        workflow_manager = WorkflowManager()
        progress = workflow_manager.get_progress()
        
        assert 'current_phase' in progress
        assert 'phase_status' in progress
        assert 'progress_log' in progress
        assert 'completed_phases' in progress
        assert 'total_phases' in progress


class TestIntegration:
    """End-to-end integration tests."""

    def test_full_workflow_structure(self, tmp_path):
        """Test that all workflow components are properly structured."""
        state_manager = StateManager(state_dir=str(tmp_path))
        workflow_manager = WorkflowManager(state_manager=state_manager)
        interface = Interface(workflow_manager=workflow_manager)

        assert workflow_manager.state_manager is state_manager
        assert interface.workflow_manager is workflow_manager

    def test_state_persistence_across_phases(self, tmp_path):
        """Test that state persists correctly across phase transitions."""
        state_manager = StateManager(state_dir=str(tmp_path))
        workflow_manager = WorkflowManager(state_manager=state_manager)

        # Simulate state being saved for multiple phases
        workflow_manager.state_manager.save_state('research', {'topic': 'test'})
        workflow_manager.state_manager.save_state('outlining', {'chapters': []})

        state = workflow_manager.get_state()
        assert 'research' in state
        assert 'outlining' in state
        assert state['research']['topic'] == 'test'

    def test_error_handling_invalid_input(self, tmp_path):
        """Test error handling for invalid inputs."""
        state_manager = StateManager(state_dir=str(tmp_path))
        workflow_manager = WorkflowManager(state_manager=state_manager)

        # Test with empty topic
        progress = workflow_manager.get_progress()
        assert progress['completed_phases'] == 0

    def test_module_interoperability(self, tmp_path):
        """Test that all modules can work together."""
        state_manager = StateManager(state_dir=str(tmp_path))
        workflow_manager = WorkflowManager(state_manager=state_manager)
        interface = Interface(workflow_manager=workflow_manager)

        # Verify all components can access shared state
        state = workflow_manager.get_state()
        assert isinstance(state, dict)

        # Verify interface can access workflow manager
        progress = interface.workflow_manager.get_progress()
        assert 'current_phase' in progress


class TestErrorHandling:
    """Tests for error handling and recovery."""

    def test_invalid_phase_data(self, tmp_path):
        """Test handling of invalid phase data."""
        state_manager = StateManager(state_dir=str(tmp_path))

        # Test with missing required fields
        is_valid, errors = state_manager.validate_state('research', {})
        assert is_valid is False
        assert len(errors) > 0

    def test_state_clear(self, tmp_path):
        """Test state clearing functionality."""
        state_manager = StateManager(state_dir=str(tmp_path))
        state_manager.save_state('research', {'topic': 'test'})

        state_manager.clear_state()
        state = state_manager.get_full_state()
        assert state == {}

    def test_resume_workflow_logic(self, tmp_path):
        """Test workflow resume logic."""
        state_manager = StateManager(state_dir=str(tmp_path))
        workflow_manager = WorkflowManager(state_manager=state_manager)

        # Simulate partial completion
        workflow_manager.phase_status['research'] = 'completed'
        workflow_manager.phase_status['outlining'] = 'completed'

        progress = workflow_manager.get_progress()
        assert progress['completed_phases'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
