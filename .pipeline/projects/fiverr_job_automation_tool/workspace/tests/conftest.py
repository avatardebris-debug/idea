"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add the workspace directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'workspace'))


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    with patch('src.utils.logger.logging.getLogger') as mock_get_logger:
        mock_logger_instance = MagicMock()
        mock_get_logger.return_value = mock_logger_instance
        yield mock_logger_instance


@pytest.fixture
def mock_requests_session():
    """Provide a mock requests session for testing API client."""
    with patch('src.api.client.requests.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        yield mock_session


@pytest.fixture
def api_client(mock_requests_session):
    """Provide a configured API client for testing."""
    from src.api.client import FiverrAPIClient
    
    client = FiverrAPIClient(
        api_key="test_api_key",
        api_secret="test_api_secret",
        auth_token="test_token"
    )
    client._session = mock_requests_session
    return client


@pytest.fixture
def automation_engine(api_client):
    """Provide a configured automation engine for testing."""
    from src.engine import FiverrAutomationEngine
    
    engine = FiverrAutomationEngine(api_client=api_client)
    return engine


@pytest.fixture
def mock_config():
    """Provide mocked configuration values."""
    with patch('src.config.Config') as mock_config_class:
        mock_config = MagicMock()
        mock_config.FIVERR_API_KEY = "test_key"
        mock_config.FIVERR_API_SECRET = "test_secret"
        mock_config.FIVERR_BASE_URL = "https://test.api.fiverr.com/v1"
        mock_config.AUTH_TOKEN = "test_token"
        mock_config.LOG_LEVEL = "DEBUG"
        mock_config.LOG_FILE = "test.log"
        mock_config.LOG_FORMAT = "%(message)s"
        mock_config.MAX_RETRIES = 3
        mock_config.RETRY_DELAY = 5
        mock_config.TIMEOUT = 30
        mock_config.RATE_LIMIT_REQUESTS = 10
        mock_config.RATE_LIMIT_WINDOW = 60
        
        mock_config_class.return_value = mock_config
        yield mock_config
