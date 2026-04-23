# Phase 1 Tasks - Transcript Extractor

## Phase 1: Core Audio Extraction & Transcription

### Description
Build the foundation - extract audio from video files and transcribe using Whisper/Faster Whisper.

### Deliverable
- CLI tool `transcript-extractor input.mp4 output.txt` that:
  - Accepts video/audio files (MP4, MOV, MKV, MP3, WAV, etc.)
  - Extracts audio stream
  - Transcribes using Faster Whisper (medium model by default)
  - Outputs plain text transcript

### Dependencies
- FFmpeg (system dependency)
- faster-whisper (pip install)
- pydub or moviepy for audio extraction

### Tasks

- [ ] Create project directory structure (`transcript_extractor/src/`, `transcript_extractor/tests/`, `transcript_extractor/config/`)
- [ ] Implement `audio_extractor.py` with `extract_audio()` function using FFmpeg/pydub
- [ ] Implement `transcriber.py` with `transcribe_audio()` function using faster-whisper
- [ ] Implement `cli.py` with argparse CLI interface (`transcript-extractor input output` command)
- [ ] Create `config/default_config.yaml` with Whisper model settings (model size, language, device)
- [ ] Implement error handling for: unsupported file formats, corrupted files, missing FFmpeg, transcription failures
- [ ] Write unit tests for `audio_extractor.py` (mock FFmpeg calls, test file format detection)
- [ ] Write unit tests for `transcriber.py` (test transcription with mock Whisper, test model loading)
- [ ] Write integration test: process a sample MP4 file and verify transcript output
- [ ] Create sample test files (sample.mp4, sample.mp3, sample.wav) for testing
- [ ] Create `requirements.txt` with dependencies (faster-whisper, pydub, ffmpeg-python, pytest)
- [ ] Create `README.md` with usage instructions and installation guide
- [ ] Run all tests and verify they pass
- [ ] Test CLI with actual video/audio files (verify transcription accuracy)

### Acceptance Criteria

#### Core Functionality
- [ ] CLI accepts input file path and output file path as arguments
- [ ] CLI accepts video formats: MP4, MOV, MKV, AVI, WebM
- [ ] CLI accepts audio formats: MP3, WAV, FLAC, OGG
- [ ] Audio extraction works correctly (verified by checking output audio duration matches input)
- [ ] Transcription produces readable text output
- [ ] Transcription accuracy >90% on clear audio samples

#### Error Handling
- [ ] Clear error message when FFmpeg is not installed
- [ ] Clear error message for unsupported file formats
- [ ] Graceful handling of corrupted files (error message, not crash)
- [ ] Clear error message for Whisper model download failures
- [ ] Proper exit codes: 0 for success, 1 for errors

#### Configuration
- [ ] Default configuration uses Whisper medium model
- [ ] Configuration file is YAML format
- [ ] User can override model size via CLI flag (`--model tiny|base|small|medium|large-v2|large-v3`)
- [ ] User can specify language via CLI flag (`--language en|fr|de|es|...`)
- [ ] User can specify device via CLI flag (`--device cpu|gpu`)

#### Performance
- [ ] Processing time <5x real-time on CPU (medium model)
- [ ] Memory usage <2GB for 1-hour audio file
- [ ] Progress indicator during transcription (progress bar or percentage)

### Success Criteria
- [ ] Can process MP4 video files end-to-end (extract + transcribe)
- [ ] Can process MP3 audio files end-to-end
- [ ] CLI is intuitive and well-documented
- [ ] All unit tests pass
- [ ] Integration test passes with sample files
- [ ] Error messages are clear and helpful

### Estimated Effort
2-3 days (16-24 hours)
