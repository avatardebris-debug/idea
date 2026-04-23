from transcript_extractor import (
    TranscriptionPipeline,
    Config,
    TranscriptionOutput,
    SUPPORTED_FORMATS,
    MODEL_SIZES,
    OUTPUT_FORMATS,
    AudioExtractor,
    WhisperTranscriber,
    TranscriptParser,
    TranscriptFormatter,
    SummaryGenerator,
)

def test_import_all():
    """Test that all public APIs can be imported."""
    assert Config is not None
    assert SUPPORTED_FORMATS is not None
    assert OUTPUT_FORMATS is not None
    assert MODEL_SIZES is not None
    assert AudioExtractor is not None
    assert WhisperTranscriber is not None
    assert TranscriptParser is not None
    assert TranscriptFormatter is not None
    assert SummaryGenerator is not None
    assert TranscriptionPipeline is not None
    assert TranscriptionOutput is not None

def test_supported_formats():
    """Test that supported formats are correctly defined."""
    expected = ['mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'flac', 'aac', 'm4a']
    assert SUPPORTED_FORMATS == expected

def test_output_formats():
    """Test that output formats are correctly defined."""
    expected = ['txt', 'srt', 'vtt', 'json']
    assert OUTPUT_FORMATS == expected

def test_model_sizes():
    """Test that model sizes are correctly defined."""
    expected = ['tiny', 'small', 'medium', 'large', 'large-v2', 'large-v3']
    assert MODEL_SIZES == expected
