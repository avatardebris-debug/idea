"""Tests for transcript builder in YouTube Studio.

This module provides comprehensive tests for transcript building and
export functionality in multiple formats.
"""

import os
import tempfile
import unittest
from transcript_builder import TranscriptBuilder, TranscriptFormats


class TestTranscriptBuilder(unittest.TestCase):
    """Test cases for TranscriptBuilder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.builder = TranscriptBuilder()
    
    def test_add_section(self):
        """Test adding a section to transcript."""
        self.builder.add_section("Welcome to the tutorial", 0, 5)
        sections = self.builder.get_sections()
        
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]['text'], "Welcome to the tutorial")
        self.assertEqual(sections[0]['start_time'], 0)
        self.assertEqual(sections[0]['end_time'], 5)
    
    def test_add_section_auto_time(self):
        """Test adding section with auto-calculated times."""
        self.builder.add_section("This is a test sentence", 0)
        sections = self.builder.get_sections()
        
        self.assertEqual(len(sections), 1)
        self.assertGreater(sections[0]['end_time'], 0)
    
    def test_add_text_to_current_section(self):
        """Test adding text to current section."""
        self.builder.add_section("Welcome", 0, 5)
        self.builder.add_text(" to the tutorial")
        
        sections = self.builder.get_sections()
        self.assertEqual(sections[0]['text'], "Welcome to the tutorial")
    
    def test_clear_sections(self):
        """Test clearing all sections."""
        self.builder.add_section("Section 1", 0, 5)
        self.builder.add_section("Section 2", 5, 10)
        self.builder.clear()
        
        sections = self.builder.get_sections()
        self.assertEqual(len(sections), 0)
    
    def test_get_statistics_empty(self):
        """Test getting statistics for empty transcript."""
        stats = self.builder.get_statistics()
        
        self.assertEqual(stats['total_sections'], 0)
        self.assertEqual(stats['total_duration'], 0)
        self.assertEqual(stats['total_words'], 0)
    
    def test_get_statistics_with_sections(self):
        """Test getting statistics with sections."""
        self.builder.add_section("Hello world", 0, 5)
        self.builder.add_section("This is a longer section with more words", 5, 10)
        
        stats = self.builder.get_statistics()
        
        self.assertEqual(stats['total_sections'], 2)
        self.assertEqual(stats['total_duration_seconds'], 10)
        self.assertGreater(stats['total_words'], 0)


class TestTranscriptExport(unittest.TestCase):
    """Test cases for transcript export functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.builder = TranscriptBuilder()
        self.builder.add_section("Welcome to the tutorial", 0, 5)
        self.builder.add_section("In this video, we'll learn about Python", 5, 12)
    
    def test_export_srt_format(self):
        """Test SRT format export."""
        srt = self.builder.export_srt()
        
        # SRT format checks
        self.assertIn('00:00:00,000 --> 00:00:05,000', srt)
        self.assertIn('00:00:05,000 --> 00:00:12,000', srt)
        self.assertIn('Welcome to the tutorial', srt)
        self.assertIn('Python', srt)
    
    def test_export_vtt_format(self):
        """Test VTT format export."""
        vtt = self.builder.export_vtt()
        
        # VTT format checks
        self.assertIn('WEBVTT', vtt)
        self.assertIn('00:00:00.000 --> 00:00:05.000', vtt)
        self.assertIn('Welcome to the tutorial', vtt)
        self.assertIn('Python', vtt)
    
    def test_export_txt_format(self):
        """Test plain text format export."""
        txt = self.builder.export_txt()
        
        # TXT format checks
        self.assertIn('[00:00:00,000]', txt)
        self.assertIn('[00:00:05,000]', txt)
        self.assertIn('Welcome to the tutorial', txt)
    
    def test_export_srt_timestamps(self):
        """Test SRT timestamp format."""
        srt = self.builder.export_srt()
        
        # Check timestamp format (HH:MM:SS,mmm)
        self.assertRegex(srt, r'\d{2}:\d{2}:\d{2},\d{3}')
    
    def test_export_vtt_timestamps(self):
        """Test VTT timestamp format."""
        vtt = self.builder.export_vtt()
        
        # Check timestamp format (HH:MM:SS.mmm)
        self.assertRegex(vtt, r'\d{2}:\d{2}:\d{2}\.\d{3}')


class TestTranscriptFormats(unittest.TestCase):
    """Test cases for TranscriptFormats utility class."""
    
    def test_get_format_extension(self):
        """Test getting file extension for format."""
        self.assertEqual(TranscriptFormats.get_format_extension('srt'), '.srt')
        self.assertEqual(TranscriptFormats.get_format_extension('vtt'), '.vtt')
        self.assertEqual(TranscriptFormats.get_format_extension('txt'), '.txt')
        self.assertEqual(TranscriptFormats.get_format_extension('invalid'), '.txt')
    
    def test_is_valid_format(self):
        """Test format validation."""
        self.assertTrue(TranscriptFormats.is_valid_format('srt'))
        self.assertTrue(TranscriptFormats.is_valid_format('vtt'))
        self.assertTrue(TranscriptFormats.is_valid_format('txt'))
        self.assertFalse(TranscriptFormats.is_valid_format('invalid'))


class TestTranscriptSave(unittest.TestCase):
    """Test cases for transcript file saving."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.builder = TranscriptBuilder()
        self.builder.add_section("Test transcript content", 0, 5)
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_save_srt_file(self):
        """Test saving SRT file."""
        filepath = os.path.join(self.test_dir, 'test.srt')
        success = self.builder.save(filepath, 'srt')
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(filepath))
        
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('Test transcript content', content)
    
    def test_save_vtt_file(self):
        """Test saving VTT file."""
        filepath = os.path.join(self.test_dir, 'test.vtt')
        success = self.builder.save(filepath, 'vtt')
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(filepath))
    
    def test_save_txt_file(self):
        """Test saving TXT file."""
        filepath = os.path.join(self.test_dir, 'test.txt')
        success = self.builder.save(filepath, 'txt')
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(filepath))
    
    def test_save_invalid_format(self):
        """Test saving with invalid format."""
        filepath = os.path.join(self.test_dir, 'test.xyz')
        success = self.builder.save(filepath, 'xyz')
        
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()