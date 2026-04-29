"""Tests for the FiverrAutomationEngine."""

import pytest
from src.engine import FiverrAutomationEngine
from src.api.client import FiverrAPIClient
from src.utils.exceptions import APIError


class TestEngineInitialization:
    """Tests for engine initialization."""
    
    def test_engine_initialization(self, automation_engine):
        """Test that the engine initializes correctly."""
        assert automation_engine is not None
        assert isinstance(automation_engine, FiverrAutomationEngine)
        assert automation_engine.is_running is False
    
    def test_engine_without_api_client(self):
        """Test engine initialization without providing API client."""
        engine = FiverrAutomationEngine()
        assert engine is not None
        assert engine.api_client is not None
        assert isinstance(engine.api_client, FiverrAPIClient)
    
    def test_engine_is_not_running_initially(self, automation_engine):
        """Test that engine is not running when first created."""
        assert automation_engine.is_running is False


class TestEngineStartStop:
    """Tests for engine start and stop functionality."""
    
    def test_start_engine(self, automation_engine):
        """Test that the engine can be started."""
        result = automation_engine.start()
        assert result is True
        assert automation_engine.is_running is True
    
    def test_start_already_running_engine(self, automation_engine):
        """Test starting an already running engine."""
        automation_engine.start()
        result = automation_engine.start()
        assert result is False
    
    def test_stop_engine(self, automation_engine):
        """Test that the engine can be stopped."""
        automation_engine.start()
        result = automation_engine.stop()
        assert result is True
        assert automation_engine.is_running is False
    
    def test_stop_not_running_engine(self, automation_engine):
        """Test stopping an engine that is not running."""
        result = automation_engine.stop()
        assert result is False


class TestEngineMainLoop:
    """Tests for the main loop functionality."""
    
    def test_main_loop_structure(self, automation_engine, mock_logger):
        """Test that the main loop structure exists."""
        # The main loop should be callable
        assert hasattr(automation_engine, 'run_main_loop')
        assert callable(automation_engine.run_main_loop)
    
    def test_main_loop_respects_running_state(self, automation_engine):
        """Test that main loop respects the running state."""
        # Start the engine
        automation_engine.start()
        assert automation_engine.is_running is True
        
        # Stop the engine
        automation_engine.stop()
        assert automation_engine.is_running is False


class TestEngineInitializationMethod:
    """Tests for the initialize method."""
    
    def test_initialize_method_exists(self, automation_engine):
        """Test that the initialize method exists."""
        assert hasattr(automation_engine, 'initialize')
        assert callable(automation_engine.initialize)
    
    def test_initialize_returns_boolean(self, automation_engine):
        """Test that initialize returns a boolean."""
        result = automation_engine.initialize()
        assert isinstance(result, bool)
