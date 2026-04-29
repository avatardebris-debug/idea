"""Configuration settings for the Fiverr Job Automation Tool."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""
    
    # API Configuration
    FIVERR_API_KEY = os.getenv("FIVERR_API_KEY", "")
    FIVERR_API_SECRET = os.getenv("FIVERR_API_SECRET", "")
    FIVERR_BASE_URL = os.getenv("FIVERR_BASE_URL", "https://api.fiverr.com/v1")
    
    # Authentication
    AUTH_TOKEN = os.getenv("FIVERR_AUTH_TOKEN", "")
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/automation.log")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Automation Settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))
    TIMEOUT = int(os.getenv("TIMEOUT", 30))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 10))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))


class DevelopmentConfig(Config):
    """Development configuration."""
    LOG_LEVEL = "DEBUG"
    LOG_FILE = "logs/dev_automation.log"


class ProductionConfig(Config):
    """Production configuration."""
    LOG_LEVEL = "INFO"
    LOG_FILE = "/var/log/fiverr_automation/automation.log"


def get_config(env: str = "development") -> type:
    """Get the appropriate configuration class based on environment."""
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    return configs.get(env, DevelopmentConfig)
