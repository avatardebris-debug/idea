"""Tests for video format handling in YouTube Studio.

This module provides comprehensive tests for the video format handler,
including format detection, validation, and conversion functionality.
"""

import os
import tempfile
import unittest
from pathlib import Path

from video_formats import (
    VideoFormatHandler,
    FormatFactory,
    create_handler,
    detect_video_format
)
from formats.mp4_handler import MP4Handler
from formats.avi_handler import AVIHandler
from formats.mov_handler import MOVHandler


class TestVideoFormatDetection(unittest.TestCase):
    """Test cases for video format detection."""
    
    def test_detect_mp4_format(self):
        """Test detection of MP4 format."""
        format_name = detect_video_format('/path/to/video.mp4')
        self.assertEqual(format_name, 'mp4')
    
    def test_detect_aviformat(self):
        """Test detection of AVI format."""
        format_name = detect_video_format('/path/to/video.avi')
        self.assertEqual(format_name, 'avi')
    
    def test_detect_movformat(self):
        """Test detection of MOV format."""
        format_name = detect_video_format('/path/to/video.mov')
        self.assertEqual(format_name, 'mov')
    
    def test_detect_unknown_format(self):
        """Test detection of unsupported format."""
        format_name = detect_video_format('/path/to/video.xyz')
        self.assertIsNone(format_name)
    
    def test_detect_case_insensitive(self):
        """Test case-insensitive format detection."""
        self.assertEqual(detect_video_format('/path/TO/VIDEO.MP4'), 'mp4')
        self.assertEqual(detect_video_format('/path/to/video.Mp4'), 'mp4')


class TestFormatFactory(unittest.TestCase):
    """Test cases for the FormatFactory class."""
    
    def test_get_handler_mp4(self):
        """Test getting MP4 handler."""
        handler = create_handler('/path/to/video.mp4')
        self.assertIsInstance(handler, MP4Handler)
        self.assertEqual(handler.format, 'mp4')
    
    def test_get_handler_avi(self):
        """Test getting AVI handler."""
        handler = create_handler('/path/to/video.avi')
        self.assertIsInstance(handler, AVIHandler)
        self.assertEqual(handler.format, 'avi')
    
    def test_get_handler_mov(self):
        """Test getting MOV handler."""
        handler = create_handler('/path/to/video.mov')
        self.assertIsInstance(handler, MOVHandler)
        self.assertEqual(handler.format, 'mov')
    
    def test_get_handler_unsupported(self):
        """Test getting handler for unsupported format."""
        handler = create_handler('/path/to/video.xyz')
        self.assertIsNone(handler)


class TestVideoFormatHandler(unittest.TestCase):
    """Test cases for the base VideoFormatHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def test_format_property(self):
        """Test format property is set correctly."""
        handler = create_handler('/path/to/video.mp4')
        self.assertIsNotNone(handler)
        self.assertEqual(handler.format, 'mp4')
    
    def test_file_path_property(self):
        """Test file_path property returns correct path."""
        handler = create_handler('/path/to/video.mp4')
        self.assertEqual(handler.file_path, '/path/to/video.mp4')


class TestMP4Handler(unittest.TestCase):
    """Test cases for MP4 format handler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.mp4')
        # Create a minimal valid MP4-like file
        with open(self.test_file, 'w') as f:
            f.write('fake mp4 content')
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_mp4_handler_creation(self):
        """Test MP4 handler creation."""
        handler = MP4Handler(self.test_file)
        self.assertIsNotNone(handler)
        self.assertEqual(handler.format, 'mp4')
    
    def test_mp4_metadata(self):
        """Test MP4 metadata extraction."""
        handler = MP4Handler(self.test_file)
        metadata = handler.get_metadata()
        
        self.assertEqual(metadata['format'], 'mp4')
        self.assertEqual(metadata['codec'], 'H.264')
        self.assertEqual(metadata['mime_type'], 'video/mp4')
        self.assertIn('file_size_bytes', metadata)
    
    def test_mp4_validation(self):
        """Test MP4 file validation."""
        handler = MP4Handler(self.test_file)
        is_valid, message = handler.validate_integrity()
        
        self.assertTrue(is_valid)
        self.assertIn('validated', message.lower())
    
    def test_mp4_invalid_extension(self):
        """Test MP4 handler rejects wrong extension."""
        wrong_file = os.path.join(self.test_dir, 'test.avi')
        with open(wrong_file, 'w') as f:
            f.write('fake avi content')
        
        with self.assertRaises(ValueError):
            MP4Handler(wrong_file)


class TestAVIHandler(unittest.TestCase):
    """Test cases for AVI format handler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.avi')
        with open(self.test_file, 'w') as f:
            f.write('fake avi content')
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_avi_handler_creation(self):
        """Test AVI handler creation."""
        handler = AVIHandler(self.test_file)
        self.assertIsNotNone(handler)
        self.assertEqual(handler.format, 'avi')
    
    def test_avi_metadata(self):
        """Test AVI metadata extraction."""
        handler = AVIHandler(self.test_file)
        metadata = handler.get_metadata()
        
        self.assertEqual(metadata['format'], 'avi')
        self.assertEqual(metadata['codec'], 'Xvid')
        self.assertEqual(metadata['mime_type'], 'video/x-msvideo')
    
    def test_avi_validation(self):
        """Test AVI file validation."""
        handler = AVIHandler(self.test_file)
        is_valid, message = handler.validate_integrity()
        
        self.assertTrue(is_valid)
        self.assertIn('validated', message.lower())


class TestMOVHandler(unittest.TestCase):
    """Test cases for MOV format handler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.mov')
        with open(self.test_file, 'w') as f:
            f.write('fake mov content')
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_mov_handler_creation(self):
        """Test MOV handler creation."""
        handler = MOVHandler(self.test_file)
        self.assertIsNotNone(handler)
        self.assertEqual(handler.format, 'mov')
    
    def test_mov_metadata(self):
        """Test MOV metadata extraction."""
        handler = MOVHandler(self.test_file)
        metadata = handler.get_metadata()
        
        self.assertEqual(metadata['format'], 'mov')
        self.assertEqual(metadata['codec'], 'H.264')
        self.assertEqual(metadata['mime_type'], 'video/quicktime')
    
    def test_mov_validation(self):
        """Test MOV file validation."""
        handler = MOVHandler(self.test_file)
        is_valid, message = handler.validate_integrity()
        
        self.assertTrue(is_valid)
        self.assertIn('validated', message.lower())


class TestConversion(unittest.TestCase):
    """Test cases for video conversion functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.mp4')
        with open(self.test_file, 'w') as f:
            f.write('fake mp4 content')
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_mp4_conversion(self):
        """Test MP4 file conversion."""
        handler = MP4Handler(self.test_file)
        output_file = os.path.join(self.test_dir, 'output.mp4')
        
        success = handler.convert(output_file, codec='H.264')
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
    
    def test_mp4_unsupported_codec(self):
        """Test MP4 conversion with unsupported codec."""
        handler = MP4Handler(self.test_file)
        output_file = os.path.join(self.test_dir, 'output.mp4')
        
        with self.assertRaises(ValueError):
            handler.convert(output_file, codec='INVALID_CODEC')


if __name__ == '__main__':
    unittest.main()
