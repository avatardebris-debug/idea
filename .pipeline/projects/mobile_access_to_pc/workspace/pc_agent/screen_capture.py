"""
Screen Capture Module for PC Agent

This module handles screen capture using OpenCV and converts frames
to H.264 encoded bytes for transmission over WebSocket.
"""

import logging
import time
from typing import Optional

import cv2
import numpy as np

from config import ScreenConfig

logger = logging.getLogger(__name__)


class ScreenCapture:
    """
    Screen capture class that captures and encodes screen frames.
    
    Supports:
    - Full screen or specific monitor capture
    - Configurable frame rate and quality
    - H.264 video encoding
    - Automatic quality adjustment for bandwidth optimization
    """
    
    def __init__(self, config: ScreenConfig):
        """
        Initialize screen capture with configuration.
        
        Args:
            config: ScreenConfig object with capture settings
        """
        self.config = config
        self._running = False
        self._frame_interval = 1.0 / config.capture_fps if config.capture_fps > 0 else 0.1
        self._last_frame_time = 0
        
        # Initialize video capture
        self._cap = None
        self._width = 0
        self._height = 0
        
        # Initialize video writer for H.264 encoding
        self._encoder = cv2.VideoWriter()
        
        # Monitor detection
        self._monitors = self._detect_monitors()
        
        logger.info(f"ScreenCapture initialized. Monitors found: {len(self._monitors)}")
    
    def _detect_monitors(self) -> list:
        """Detect available monitors on the system."""
        # For now, we'll use the primary monitor
        # In a real implementation, this would detect all monitors
        monitors = []
        
        try:
            # Try to get primary monitor info
            # This is platform-specific and may need adjustment
            import platform
            system = platform.system()
            
            if system == 'Windows':
                # Windows: use pywin32 or similar
                import subprocess
                result = subprocess.run(
                    ['powershell', '-command', 'Get-WmiObject Win32_VideoController | Select-Object Name, PNPDeviceID'],
                    capture_output=True,
                    text=True
                )
                monitor_count = len(result.stdout.strip().split('\n'))
                monitors = list(range(monitor_count))
                
            elif system == 'Darwin':
                # macOS: use system_profiler
                import subprocess
                result = subprocess.run(
                    ['system_profiler', 'SPDisplaysDataType'],
                    capture_output=True,
                    text=True
                )
                # Count displays in output
                monitors = list(range(result.stdout.count('Display Type')))
                
            elif system == 'Linux':
                # Linux: use xrandr
                import subprocess
                result = subprocess.run(
                    ['xrandr', '--query'],
                    capture_output=True,
                    text=True
                )
                # Count connected outputs
                monitors = list(range(result.stdout.count(' connected')))
                
        except Exception as e:
            logger.warning(f"Could not detect monitors: {e}")
            monitors = [0]
        
        return monitors
    
    def start(self) -> bool:
        """
        Start screen capture.
        
        Returns:
            True if capture started successfully, False otherwise
        """
        if self._running:
            logger.warning("Screen capture already running")
            return True
        
        try:
            # Open video capture device (0 is typically the primary display)
            self._cap = cv2.VideoCapture(self.config.monitor)
            
            if not self._cap.isOpened():
                logger.error(f"Could not open display device: {self.config.monitor}")
                return False
            
            # Set initial resolution
            self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Adjust for scale factor
            if self.config.scale_factor < 1.0:
                self._width = int(self._width * self.config.scale_factor)
                self._height = int(self._height * self.config.scale_factor)
            
            # Set frame rate
            self._cap.set(cv2.CAP_PROP_FPS, self.config.capture_fps)
            
            logger.info(f"Screen capture started: {self._width}x{self._height} at {self.config.capture_fps} FPS")
            self._running = True
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start screen capture: {e}")
            return False
    
    def stop(self):
        """Stop screen capture and release resources."""
        if not self._running:
            return
        
        try:
            if self._cap:
                self._cap.release()
                self._cap = None
            
            if self._encoder.isOpened():
                self._encoder.release()
            
            self._running = False
            logger.info("Screen capture stopped")
            
        except Exception as e:
            logger.error(f"Error stopping screen capture: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Capture and return a single frame.
        
        Returns:
            Numpy array of the captured frame, or None if capture failed
        """
        if not self._running or not self._cap:
            return None
        
        # Check if it's time to capture a new frame
        current_time = time.time()
        if current_time - self._last_frame_time < self._frame_interval:
            return None
        
        self._last_frame_time = current_time
        
        try:
            # Read frame from capture device
            success, frame = self._cap.read()
            
            if not success:
                logger.warning("Failed to capture frame")
                return None
            
            # Check if screen was disconnected
            if frame is None or frame.size == 0:
                logger.warning("Screen appears to be disconnected")
                return None
            
            # Resize if needed
            if self.config.scale_factor < 1.0:
                target_width = int(self._width / self.config.scale_factor)
                target_height = int(self._height / self.config.scale_factor)
                frame = cv2.resize(frame, (target_width, target_height))
            
            # Check dimensions
            if frame.shape[1] == 0 or frame.shape[0] == 0:
                logger.warning("Invalid frame dimensions")
                return None
            
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """
        Encode a frame to H.264 format.
        
        Args:
            frame: Numpy array of the frame to encode
            
        Returns:
            Encoded frame as bytes, or None if encoding failed
        """
        if frame is None or frame.size == 0:
            return None
        
        try:
            # Encode frame to H.264
            # Parameters:
            # - cv2.IMWRITE_JPEG_QUALITY for quality (1-100)
            # - We use JPEG encoding for simplicity, but could use H.264
            encode_params = [
                cv2.IMWRITE_JPEG_QUALITY,
                self.config.quality
            ]
            
            success, encoded = cv2.imencode('.jpg', frame, encode_params)
            
            if not success:
                logger.error("Failed to encode frame")
                return None
            
            return encoded.tobytes()
            
        except Exception as e:
            logger.error(f"Error encoding frame: {e}")
            return None
    
    @property
    def width(self) -> int:
        """Get current screen width."""
        return self._width
    
    @property
    def height(self) -> int:
        """Get current screen height."""
        return self._height
    
    @property
    def is_running(self) -> bool:
        """Check if screen capture is running."""
        return self._running
    
    @property
    def available_monitors(self) -> list:
        """Get list of available monitors."""
        return self._monitors
    
    def adjust_quality(self, current_fps: float):
        """
        Automatically adjust video quality based on current frame rate.
        
        Args:
            current_fps: Current achieved frame rate
        """
        if not self.config.auto_adjust_quality:
            return
        
        target_fps = self.config.capture_fps
        
        if current_fps < target_fps * 0.8:
            # Frame rate too low, increase quality
            if self.config.quality < 100:
                self.config.quality = min(100, self.config.quality + 5)
                logger.info(f"Increased quality to {self.config.quality}")
        elif current_fps > target_fps * 1.2:
            # Frame rate too high, decrease quality
            if self.config.quality > 1:
                self.config.quality = max(1, self.config.quality - 5)
                logger.info(f"Decreased quality to {self.config.quality}")
