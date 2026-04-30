# Summarizer Tool

A CLI tool for summarizing various content sources including PDFs, YouTube videos, and web pages.

## Features

- **PDF Summarization**: Extract text from PDF files and generate summaries
- **YouTube Summarization**: Fetch transcripts from YouTube videos and summarize them
- **Web Summarization**: Scrape web content and generate summaries

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd summarizer_tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file in the root directory:
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

### Summarize a PDF
```bash
python -m summarizer_tool.main --source-type pdf --source path/to/document.pdf
```

### Summarize a YouTube Video
```bash
python -m summarizer_tool.main --source-type youtube --source https://www.youtube.com/watch?v=VIDEO_ID
```

### Summarize a Web Page
```bash
python -m summarizer_tool.main --source-type web --source https://example.com/article
```

### Save Summary to File
```bash
python -m summarizer_tool.main --source-type pdf --source document.pdf --output summary.txt
```

## Command Line Arguments

- `--source-type`: Type of source to summarize (pdf, youtube, web) - **Required**
- `--source`: Path to PDF file or URL for YouTube/web content - **Required**
- `--output`: Output file path (optional, prints to stdout if not specified)

## Requirements

- Python 3.8+
- pypdf
- youtube-transcript-api
- requests
- beautifulsoup4
- openai
- python-dotenv

## License

MIT License
