# Transcript Extractor API Documentation

## Overview

This documentation covers the Transcript Extractor API, a comprehensive tool for extracting transcripts from video and audio files using Whisper-based models.

## Modules

### transcript_extractor

Core package containing all main classes and functions.

#### Classes

- [`Config`](#config) - Configuration management
- [`AudioExtractor`](#audioextractor) - Audio/video extraction
- [`WhisperTranscriber`](#whispertranscriber) - Whisper-based transcription
- [`TranscriptParser`](#transcriptparser) - Transcript parsing
- [`TranscriptFormatter`](#transcriptformatter) - Output formatting
- [`SummaryGenerator`](#summarygenerator) - Summary generation
- [`TranscriptionPipeline`](#transcriptionpipeline) - End-to-end processing

#### Data Classes

- [`TranscriptionSegment`](#transcriptionsegment) - Transcript segment
- [`TranscriptionResultData`](#transcriptionresultdata) - Transcription result

#### Constants

- [`SUPPORTED_FORMATS`](#supported_formats) - Supported input formats
- [`OUTPUT_FORMATS`](#output_formats) - Supported output formats
- [`MODEL_SIZES`](#model_sizes) - Available Whisper models

---

## Config

Configuration class for managing application settings.

### Constructor

```python
Config(
    model_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    temp_dir: Optional[str] = None,
    api_endpoint: Optional[str] = None
)
```

### Attributes

- `model_path` (str): Path to Whisper model cache
- `output_dir` (str): Default output directory
- `temp_dir` (str): Temporary file directory
- `api_endpoint` (str): API endpoint for remote processing

### Methods

#### `create_directories()`

Creates all necessary directories if they don't exist.

**Returns**: `bool` - True if successful

---

## AudioExtractor

Handles audio extraction from video files.

### Constructor

```python
AudioExtractor(
    sample_rate: int = 16000,
    bitrate: str = '128k',
    temp_dir: Optional[str] = None
)
```

### Attributes

- `sample_rate` (int): Output sample rate in Hz
- `bitrate` (str): Output audio bitrate
- `temp_dir` (str): Temporary directory for extracted audio

### Methods

#### `is_supported_format(file_path: str) -> bool`

Checks if the file format is supported.

**Parameters**:
- `file_path` (str): Path to the file

**Returns**: `bool` - True if format is supported

#### `extract_audio(video_path: str, output_path: str) -> bool`

Extracts audio from a video file.

**Parameters**:
- `video_path` (str): Path to input video file
- `output_path` (str): Path for output audio file

**Returns**: `bool` - True if extraction successful

#### `cleanup_temp_files()`

Removes temporary files.

**Returns**: `bool` - True if cleanup successful

---

## WhisperTranscriber

Handles Whisper-based transcription.

### Constructor

```python
WhisperTranscriber(
    model_size: str = 'small',
    language: str = 'en',
    device: str = 'auto',
    compute_type: str = 'float32'
)
```

### Attributes

- `model_size` (str): Whisper model size
- `language` (str): Input language
- `device` (str): Device to use ('cpu' or 'cuda')
- `compute_type` (str): Compute type for inference

### Methods

#### `transcribe(audio_path: str, language: Optional[str] = None) -> TranscriptionResultData`

Transcribes audio using Whisper.

**Parameters**:
- `audio_path` (str): Path to audio file
- `language` (str, optional): Language override

**Returns**: `TranscriptionResultData` - Transcription result

---

## TranscriptParser

Parses and validates transcription results.

### Constructor

```python
TranscriptParser()
```

### Methods

#### `parse_text(text: str) -> TranscriptionResultData`

Parses plain text as a transcription result.

**Parameters**:
- `text` (str): Text to parse

**Returns**: `TranscriptionResultData` - Parsed result

#### `parse_segments(segments: list) -> TranscriptionResultData`

Parses segment data into a transcription result.

**Parameters**:
- `segments` (list): List of segment data

**Returns**: `TranscriptionResultData` - Parsed result

#### `validate_result(result: TranscriptionResultData) -> bool`

Validates a transcription result.

**Parameters**:
- `result` (TranscriptionResultData): Result to validate

**Returns**: `bool` - True if valid

---

## TranscriptFormatter

Formats transcription results to various output formats.

### Constructor

```python
TranscriptFormatter()
```

### Methods

#### `format_to_txt(result: TranscriptionResultData, include_timestamps: bool = False) -> str`

Formats result as plain text.

**Parameters**:
- `result` (TranscriptionResultData): Transcription result
- `include_timestamps` (bool): Include timestamps

**Returns**: `str` - Formatted text

#### `format_to_srt(result: TranscriptionResultData) -> str`

Formats result as SRT subtitle file.

**Parameters**:
- `result` (TranscriptionResultData): Transcription result

**Returns**: `str` - SRT formatted text

#### `format_to_vtt(result: TranscriptionResultData) -> str`

Formats result as VTT subtitle file.

**Parameters**:
- `result` (TranscriptionResultData): Transcription result

**Returns**: `str` - VTT formatted text

#### `format_to_json(result: TranscriptionResultData) -> str`

Formats result as JSON.

**Parameters**:
- `result` (TranscriptionResultData): Transcription result

**Returns**: `str` - JSON string

#### `split_into_sections(result: TranscriptionResultData, section_length: int = 300) -> list`

Splits transcript into sections.

**Parameters**:
- `result` (TranscriptionResultData): Transcription result
- `section_length` (int): Maximum characters per section

**Returns**: `list` - List of section texts

---

## SummaryGenerator

Generates summaries and key points from transcripts.

### Constructor

```python
SummaryGenerator(
    strategy: str = 'extractive',
    length: str = 'medium'
)
```

### Attributes

- `strategy` (str): Summarization strategy
- `length` (str): Summary length

### Methods

#### `generate(result: TranscriptionResultData) -> str`

Generates a summary.

**Parameters**:
- `result` (TranscriptionResultData): Transcription result

**Returns**: `str` - Generated summary

#### `get_key_points(result: TranscriptionResultData, max_points: int = 5) -> list`

Extracts key points.

**Parameters**:
- `result` (TranscriptionResultData): Transcription result
- `max_points` (int): Maximum number of points

**Returns**: `list` - List of key points

#### `update_strategy(strategy: str)`

Updates the summarization strategy.

**Parameters**:
- `strategy` (str): New strategy

#### `update_length(length: str)`

Updates the summary length.

**Parameters**:
- `length` (str): New length

---

## TranscriptionPipeline

End-to-end transcription pipeline.

### Constructor

```python
TranscriptionPipeline(
    model_size: str = 'small',
    language: str = 'en',
    output_format: str = 'txt',
    summary_length: str = 'medium',
    summary_strategy: str = 'extractive'
)
```

### Methods

#### `process(input_file: str, output_dir: Optional[str] = None, include_timestamps: bool = True) -> TranscriptionOutput`

Processes a single file.

**Parameters**:
- `input_file` (str): Path to input file
- `output_dir` (str, optional): Output directory
- `include_timestamps` (bool): Include timestamps

**Returns**: `TranscriptionOutput` - Processing result

#### `process_batch(input_files: list, output_dir: Optional[str] = None) -> list`

Processes multiple files.

**Parameters**:
- `input_files` (list): List of file paths
- `output_dir` (str, optional): Output directory

**Returns**: `list` - List of TranscriptionOutput results

---

## Data Classes

### TranscriptionSegment

Represents a segment of a transcript.

```python
@dataclass
class TranscriptionSegment:
    text: str
    start: float
    end: float
    confidence: Optional[float] = None
```

### TranscriptionResultData

Complete transcription result.

```python
@dataclass
class TranscriptionResultData:
    text: str
    language: str
    duration: float
    word_count: int
    segments: list
    success: bool
    error_message: Optional[str] = None
```

### TranscriptionOutput

Pipeline processing output.

```python
@dataclass
class TranscriptionOutput:
    input_file: str
    transcript: str
    summary: str
    language: str
    duration: float
    word_count: int
    segments_count: int
    success: bool
    error_message: Optional[str] = None
```

---

## Constants

### SUPPORTED_FORMATS

List of supported input formats.

```python
SUPPORTED_FORMATS = [
    'mp4', 'avi', 'mov', 'mkv',
    'mp3', 'wav', 'flac', 'aac', 'm4a'
]
```

### OUTPUT_FORMATS

List of supported output formats.

```python
OUTPUT_FORMATS = ['txt', 'srt', 'vtt', 'json']
```

### MODEL_SIZES

Available Whisper model sizes.

```python
MODEL_SIZES = [
    'tiny', 'small', 'medium',
    'large', 'large-v2', 'large-v3'
]
```

---

## Examples

### Basic Usage

```python
from transcript_extractor import TranscriptionPipeline

# Create pipeline
pipeline = TranscriptionPipeline(
    model_size='small',
    language='en'
)

# Process file
output = pipeline.process('video.mp4')

if output.success:
    print(output.transcript)
    print(output.summary)
```

### Multiple Output Formats

```python
from transcript_extractor import TranscriptFormatter

formatter = TranscriptFormatter()

# Format as SRT
srt = formatter.format_to_srt(result)

# Format as VTT
vtt = formatter.format_to_vtt(result)

# Format as JSON
json_output = formatter.format_to_json(result)
```

### Custom Summary

```python
from transcript_extractor import SummaryGenerator

generator = SummaryGenerator(
    strategy='abstractive',
    length='short'
)

summary = generator.generate(result)
key_points = generator.get_key_points(result, max_points=3)
```
