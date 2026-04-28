"""
Orchestration Module - Phase 6
Coordinates multi-phase workflows and manages project state across all phases.
"""

from .state_manager import StateManager
from .workflow_manager import WorkflowManager
from .interface import Interface

__all__ = ['StateManager', 'WorkflowManager', 'Interface']
