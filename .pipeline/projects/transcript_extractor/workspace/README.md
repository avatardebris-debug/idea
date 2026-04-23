# Transcript Extractor

A comprehensive tool for extracting transcripts from video and audio files using Whisper-based models, with basic summary functionality.

## Features

- **Multi-format Support**: Extract audio from MP4, AVI, MOV, MKV, MP3, WAV, FLAC, AAC, M4A files
- **Multiple Output Formats**: TXT, SRT (SubRip), VTT (WebVTT), JSON
- **Whisper Integration**: Use OpenAI's Whisper models (tiny, small, medium, large, large-v2, large-v3)
- **Automatic Summarization**: Generate summaries and extract key points
- **Command-Line Interface**: Easy-to-use CLI for single and batch processing
- **Language Detection**: Auto-detect or specify input language

## Installation

### Prerequisites

- Python 3.8+
- ffmpeg (for audio extraction)
- Git (for cloning)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Package (Optional)

```bash
pip install -e .
```

## Usage

### Basic Transcription

```bash
# Transcribe a single file
transcript-extractor transcribe video.mp4

# Specify model size
transcript-extractor transcribe video.mp4 --model small

# Specify output language
transcript-extractor transcribe video.mp4 --language en

# Output to SRT format
transcript-extractor transcribe video.mp4 --output-format srt

# Generate a short summary
transcript-extractor transcribe video.mp4 --summary-length short

# Enable verbose output
transcript-extractor transcribe video.mp4 --verbose
```

### Batch Processing

```bash
# Process multiple files
transcript-extractor batch video1.mp4 video2.mp4 video3.mp4

# With options
transcript-extractor batch *.mp4 --model small --output-format json
```

### System Information

```bash
# View supported formats and models
transcript-extractor info

# View version
transcript-extractor version
```

## Command-Line Options

### `transcribe` Command

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--model` | `-m` | `small` | Whisper model size (tiny, small, medium, large, large-v2, large-v3) |
| `--language` | `-l` | `en` | Language code (e.g., en, es, fr) |
| `--output-format` | `-o` | `txt` | Output format (txt, srt, vtt, json) |
| `--summary-length` | `-s` | `medium` | Summary length (short, medium, long) |
| `--summary-strategy` | | `extractive` | Summarization strategy (extractive, abstractive, simple) |
| `--output-dir` | `-d` | | Output directory for files |
| `--no-timestamps` | | | Exclude timestamps from transcript |
| `--verbose` | `-v` | | Enable verbose output |

### `batch` Command

Same options as `transcribe`, plus accepts multiple input files as arguments.

## Configuration

Environment variables can be used to configure the application:

| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSCRIPT_EXTRACTOR_MODEL_PATH` | Path to Whisper model cache | Auto-detected |
| `TRANSCRIPT_EXTRACTOR_OUTPUT_DIR` | Default output directory | Current directory |
| `TRANSCRIPT_EXTRACTOR_TEMP_DIR` | Temporary file directory | System temp |

## Programmatic Usage

```python
from transcript_extractor import TranscriptionPipeline, Config

# Create configuration
config = Config(
    model_size='small',
    language='en',
    output_format='txt'
)

# Create pipeline
pipeline = TranscriptionPipeline(
    model_size='small',
    language='en',
    output_format='txt',
    summary_length='medium',
    summary_strategy='extractive'
)

# Process a file
output = pipeline.process('video.mp4', output_dir='./output')

if output.success:
    print(f"Transcript: {output.transcript}")
    print(f"Summary: {output.summary}")
    print(f"Duration: {output.duration:.2f} seconds")
else:
    print(f"Error: {output.error_message}")
```

## Supported Formats

### Input Formats
- MP4 (MPEG-4)
- AVI (Audio Video Interleave)
- MOV (QuickTime)
- MKV (Matroska)
- MP3 (MPEG Audio Layer 3)
- WAV (Waveform Audio)
- FLAC (Free Lossless Audio Codec)
- AAC (Advanced Audio Coding)
- M4A (MPEG-4 Audio)

### Output Formats
- **TXT**: Plain text transcript
- **SRT**: SubRip subtitle format with timestamps
- **VTT**: WebVTT format for web video
- **JSON**: Structured JSON with metadata and segments

## Whisper Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 75 MB | Fastest | Lower |
| small | 244 MB | Fast | Good |
| medium | 769 MB | Moderate | Better |
| large | 1550 MB | Slow | Best |
| large-v2 | 1550 MB | Slow | Best (improved) |
| large-v3 | 1550 MB | Slow | Best (multilingual) |

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=transcript_extractor --cov-report=html
```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### Common Issues

**Issue**: ffmpeg not found
- **Solution**: Install ffmpeg from https://ffmpeg.org/download.html

**Issue**: Model download fails
- **Solution**: Check internet connection and ensure sufficient disk space

**Issue**: Audio extraction fails
- **Solution**: Ensure input file is not corrupted and format is supported

**Issue**: Transcription is slow
- **Solution**: Use a smaller model (e.g., 'tiny' or 'small')

## Changelog

### 1.0.0 (2025-01-16)
- Initial release
- Core transcription functionality
- CLI interface
- Multiple output formats
- Summary generation
