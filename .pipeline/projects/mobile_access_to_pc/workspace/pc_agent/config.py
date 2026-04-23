"""
Configuration module for PC Agent
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ServerConfig:
    """Server configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8765
    max_connections: int = 5
    heartbeat_interval: int = 30
    connection_timeout: int = 300


@dataclass
class ScreenConfig:
    """Screen capture configuration settings."""
    capture_fps: int = 15
    quality: int = 75
    target_bitrate: int = 2000
    scale_factor: float = 1.0
    monitor: int = 0
    auto_adjust_quality: bool = True


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    enable_tls: bool = False
    tls_cert_path: Optional[str] = None
    tls_key_path: Optional[str] = None
    require_auth: bool = True
    auth_token: Optional[str] = None


@dataclass
class InputConfig:
    """Input handling configuration settings."""
    mouse_sensitivity: float = 1.0
    keyboard_delay: float = 0.05
    log_input_events: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    log_file: str = "pc_agent.log"
    max_log_size: int = 10485760
    backup_count: int = 5


@dataclass
class DeviceConfig:
    """Device identification settings."""
    device_name: str = "PC-localhost"
    device_id: Optional[str] = None


@dataclass
class Config:
    """Main configuration class."""
    server_config: ServerConfig = field(default_factory=ServerConfig)
    screen_config: ScreenConfig = field(default_factory=ScreenConfig)
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
    input_config: InputConfig = field(default_factory=InputConfig)
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    device_config: DeviceConfig = field(default_factory=DeviceConfig)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.screen_config.capture_fps < 1:
            raise ValueError("capture_fps must be at least 1")
        if self.screen_config.capture_fps > 60:
            raise ValueError("capture_fps should not exceed 60")
        if self.screen_config.quality < 1 or self.screen_config.quality > 100:
            raise ValueError("quality must be between 1 and 100")
        if self.screen_config.scale_factor < 0.5 or self.screen_config.scale_factor > 1.0:
            raise ValueError("scale_factor must be between 0.5 and 1.0")
        if self.input_config.mouse_sensitivity < 0.1 or self.input_config.mouse_sensitivity > 5.0:
            raise ValueError("mouse_sensitivity must be between 0.1 and 5.0")
        if self.input_config.keyboard_delay < 0:
            raise ValueError("keyboard_delay must be non-negative")


class ConfigLoader:
    """Load configuration from JSON file."""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = None
    
    def load(self) -> Config:
        """Load configuration from JSON file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            data = json.load(f)
        
        return self._parse_config(data)
    
    def _parse_config(self, data: dict) -> Config:
        """Parse configuration dictionary into Config object."""
        return Config(
            server_config=ServerConfig(
                host=data.get('server', {}).get('host', '0.0.0.0'),
                port=data.get('server', {}).get('port', 8765),
                max_connections=data.get('server', {}).get('max_connections', 5),
                heartbeat_interval=data.get('server', {}).get('heartbeat_interval', 30),
                connection_timeout=data.get('server', {}).get('connection_timeout', 300)
            ),
            screen_config=ScreenConfig(
                capture_fps=data.get('screen', {}).get('capture_fps', 15),
                quality=data.get('screen', {}).get('quality', 75),
                target_bitrate=data.get('screen', {}).get('target_bitrate', 2000),
                scale_factor=data.get('screen', {}).get('scale_factor', 1.0),
                monitor=data.get('screen', {}).get('monitor', 0),
                auto_adjust_quality=data.get('screen', {}).get('auto_adjust_quality', True)
            ),
            security_config=SecurityConfig(
                enable_tls=data.get('security', {}).get('enable_tls', False),
                tls_cert_path=data.get('security', {}).get('tls_cert_path'),
                tls_key_path=data.get('security', {}).get('tls_key_path'),
                require_auth=data.get('security', {}).get('require_auth', True),
                auth_token=data.get('security', {}).get('auth_token')
            ),
            input_config=InputConfig(
                mouse_sensitivity=data.get('input', {}).get('mouse_sensitivity', 1.0),
                keyboard_delay=data.get('input', {}).get('keyboard_delay', 0.05),
                log_input_events=data.get('input', {}).get('log_input_events', True)
            ),
            logging_config=LoggingConfig(
                level=data.get('logging', {}).get('level', 'INFO'),
                log_file=data.get('logging', {}).get('log_file', 'pc_agent.log'),
                max_log_size=data.get('logging', {}).get('max_log_size', 10485760),
                backup_count=data.get('logging', {}).get('backup_count', 5)
            ),
            device_config=DeviceConfig(
                device_name=data.get('device', {}).get('device_name', 'PC-localhost'),
                device_id=data.get('device', {}).get('device_id')
            )
        )


def get_config(config_path: str = 'config.json') -> Config:
    """Load and return configuration."""
    loader = ConfigLoader(config_path)
    return loader.load()
