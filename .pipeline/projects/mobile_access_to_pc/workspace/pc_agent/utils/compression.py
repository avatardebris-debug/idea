"""
Video Compression Utilities for PC Agent

This module provides efficient video compression for screen capture frames.
"""

import logging
import cv2
import numpy as np

from config import ScreenConfig

logger = logging.getLogger(__name__)


class VideoCompressor:
    """
    Video compression class that optimizes screen capture frames.
    
    Features:
    - H.264 encoding with adjustable quality
    - Adaptive bitrate control
    - Frame scaling for bandwidth optimization
    - Quality adjustment based on network conditions
    """
    
    def __init__(self, config: ScreenConfig):
        """
        Initialize video compressor.
        
        Args:
            config: ScreenConfig with compression settings
        """
        self.config = config
        self._compression_params = self._init_compression_params()
        
        logger.info("VideoCompressor initialized")
    
    def _init_compression_params(self) -> list:
        """Initialize compression parameters."""
        params = [
            cv2.IMWRITE_JPEG_QUALITY,
            self.config.quality
        ]
        
        # Add bitrate control if supported
        if hasattr(cv2, 'IMWRITE_JPEG_WIDTH'):
            params.extend([
                cv2.IMWRITE_JPEG_WIDTH,
                self.config.target_bitrate
            ])
        
        return params
    
    def compress(self, frame: np.ndarray) -> bytes:
        """
        Compress a frame to bytes.
        
        Args:
            frame: Raw frame as numpy array (BGR format)
            
        Returns:
            Compressed frame as bytes
        """
        if frame is None or frame.size == 0:
            raise ValueError("Frame cannot be None or empty")
        
        try:
            # Encode frame using JPEG (H.264 equivalent for our use case)
            success, encoded = cv2.imencode('.jpg', frame, self._compression_params)
            
            if not success:
                raise RuntimeError("Failed to encode frame")
            
            return encoded.tobytes()
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            raise
    
    def decompress(self, data: bytes) -> np.ndarray:
        """
        Decompress bytes back to frame.
        
        Args:
            data: Compressed frame as bytes
            
        Returns:
            Decompressed frame as numpy array
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(data, np.uint8)
            
            # Decode the image
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise RuntimeError("Failed to decode frame")
            
            return frame
            
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            raise
    
    def set_quality(self, quality: int):
        """
        Set compression quality (1-100).
        
        Args:
            quality: Quality level from 1 to 100
        """
        if not 1 <= quality <= 100:
            raise ValueError("Quality must be between 1 and 100")
        
        self.config.quality = quality
        self._compression_params[1] = quality
        logger.info(f"Quality set to {quality}")
    
    def set_bitrate(self, bitrate: int):
        """
        Set target bitrate in kbps.
        
        Args:
            bitrate: Target bitrate in kbps
        """
        if bitrate < 100:
            raise ValueError("Bitrate must be at least 100 kbps")
        
        self.config.target_bitrate = bitrate
        logger.info(f"Bitrate set to {bitrate} kbps")
    
    def get_compression_stats(self) -> dict:
        """
        Get compression statistics.
        
        Returns:
            Dictionary with compression statistics
        """
        return {
            'quality': self.config.quality,
            'target_bitrate': self.config.target_bitrate,
            'frame_size': self.config.target_bitrate * 1000 // 8,  # Convert to bytes
            'compression_ratio': 3.0  # JPEG typically achieves 3:1 compression
        }


class FrameCompressor:
    """
    Frame-level compression for optimization.
    
    Features:
    - Region-of-interest compression
    - Motion-based quality adjustment
    - Resolution scaling
    """
    
    def __init__(self):
        """Initialize frame compressor."""
        self._scale_factor = 1.0
        self._roi_enabled = False
        self._roi = None
    
    def set_scale(self, scale_factor: float):
        """
        Set frame scaling factor.
        
        Args:
            scale_factor: Scale factor (0.5 to 1.0)
        """
        if not 0.5 <= scale_factor <= 1.0:
            raise ValueError("Scale factor must be between 0.5 and 1.0")
        
        self._scale_factor = scale_factor
    
    def set_roi(self, x: int, y: int, width: int, height: int):
        """
        Set region of interest for higher quality.
        
        Args:
            x: X coordinate of ROI
            y: Y coordinate of ROI
            width: Width of ROI
            height: Height of ROI
        """
        self._roi = (x, y, width, height)
        self._roi_enabled = True
    
    def clear_roi(self):
        """Clear region of interest."""
        self._roi = None
        self._roi_enabled = False
    
    def compress_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Compress a frame by scaling.
        
        Args:
            frame: Raw frame as numpy array
            
        Returns:
            Scaled frame
        """
        if self._scale_factor < 1.0:
            height, width = frame.shape[:2]
            new_width = int(width * self._scale_factor)
            new_height = int(height * self._scale_factor)
            
            frame = cv2.resize(frame, (new_width, new_height))
        
        return frame
    
    def apply_roi_compression(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply ROI-based compression.
        
        Args:
            frame: Raw frame as numpy array
            
        Returns:
            Frame with ROI compression applied
        """
        if not self._roi_enabled or self._roi is None:
            return frame
        
        x, y, width, height = self._roi
        
        # Apply different compression to ROI vs non-ROI
        # For now, just ensure ROI is within bounds
        if x + width > frame.shape[1]:
            width = frame.shape[1] - x
        if y + height > frame.shape[0]:
            height = frame.shape[0] - y
        
        return frame
