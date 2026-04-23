# YouTube Studio 🎬

A comprehensive Python tool for YouTube content creators that provides SEO-friendly title generation, thumbnail planning, keyword suggestions, and transcript management.

## 🚀 Features

- **SEO-Optimized Title Generation** - Create compelling titles that rank well
- **Thumbnail Planning** - Generate metadata for eye-catching thumbnails
- **Keyword Suggestions** - Smart keyword generation with relevance scoring
- **Transcript Management** - Create and export transcripts in multiple formats (SRT, VTT, TXT)
- **Template System** - Customizable templates for consistent metadata
- **Video Format Support** - Handle MP4, AVI, and MOV formats
- **Batch Processing** - Generate metadata for multiple videos at once
- **SEO Scoring** - Get instant feedback on your metadata quality

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-studio.git
cd youtube-studio

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Run the CLI
python -m youtube_studio.cli
```

## 🎯 Usage

### Command Line Interface

```bash
# Generate metadata for a single video
python -m youtube_studio.cli generate --title "Python Tutorial" --description "Learn Python" --content "Python programming"

# Generate metadata for multiple videos (batch)
python -m youtube_studio.cli batch --input-file videos.json --output-file results.json

# Create a transcript
python -m youtube_studio.cli transcript --input sections.json --format srt --output transcript.srt

# Validate configuration
python -m youtube_studio.cli validate-config --config config.json

# Show all available templates
python -m youtube_studio.cli templates list
```

### Python API

```python
from youtube_studio import StudioOrchestrator

# Initialize the orchestrator
orchestrator = StudioOrchestrator()

# Generate metadata for a video
metadata = orchestrator.generate_video_metadata({
    'title': 'Python Programming Tutorial',
    'description': 'Learn Python from scratch',
    'content': 'Python programming basics',
    'category': 'education',
    'author': 'John Doe'
})

# Access generated components
print(f"Title: {metadata['title']}")
print(f"SEO Score: {metadata['seo_score']}")
print(f"Keywords: {metadata['keywords']}")

# Generate a transcript
sections = [
    {'text': 'Welcome to the tutorial', 'start_time': 0, 'end_time': 5},
    {'text': 'In this video we cover Python', 'start_time': 5, 'end_time': 15}
]
transcript = orchestrator.create_transcript(sections, 'srt')

# Render a custom template
template_data = {
    'title': 'Python Basics',
    'author': 'John Doe',
    'tags': ['python', 'tutorial'],
    'category': 'education'
}
rendered = orchestrator.render_template('default_template', template_data)
```

### Configuration

Create a `config.json` file:

```json
{
    "seo": {
        "max_title_length": 60,
        "max_keywords": 15
    },
    "thumbnail": {
        "default_style": "bold",
        "default_size": "large"
    },
    "transcript": {
        "default_format": "srt"
    },
    "templates": {
        "template_directory": "./templates"
    },
    "log_level": "INFO"
}
```

Load custom configuration:

```python
from youtube_studio import YouTubeStudioConfig

config = YouTubeStudioConfig.from_dict(config_dict)
orchestrator = StudioOrchestrator(config)
```

## 📁 Project Structure

```
youtube_studio/
├── config.py              # Configuration management
├── constants.py           # Project constants
├── video_formats.py       # Video format handling
├── title_generator.py     # Title generation logic
├── thumbnail_generator.py # Thumbnail planning
├── keyword_generator.py   # Keyword suggestions
├── keyword_database.py    # Keyword persistence
├── transcript_builder.py  # Transcript generation
├── template_manager.py    # Template management
├── template_engine.py     # Template rendering
├── studio_orchestrator.py # Main coordinator
├── cli.py                 # Command-line interface
├── __init__.py           # Package initialization
├── tests/
│   ├── test_video_formats.py
│   ├── test_generators.py
│   ├── test_transcript.py
│   ├── test_templates.py
│   └── test_integration.py
├── templates/
│   └── default_template.json
└── README.md             # This file
```

## 🔧 Components

### StudioOrchestrator

The central coordinator that ties all components together:

- `generate_video_metadata(input_data)` - Generate complete metadata
- `generate_title(input_text, keywords, style)` - Generate optimized titles
- `generate_thumbnail_metadata(title, style, size)` - Plan thumbnails
- `generate_keywords(content, category, count)` - Suggest keywords
- `create_transcript(sections, output_format)` - Create transcripts
- `render_template(template_name, data)` - Render templates
- `generate_batch(inputs)` - Batch processing

### Template Engine

Supports Jinja2-style syntax with:

- **Variable substitution**: `{{variable}}`
- **Filters**: `{{title|upper}}`, `{{tags|join(", ")}}`
- **Conditionals**: `{% if show_greeting %}Welcome!{% endif %}`
- **Loops**: `{% for tag in tags %}{{tag}}{% endfor %}`

### Video Format Handlers

- **MP4Handler** - MP4 video files
- **AVIHandler** - AVI video files
- **MOVHandler** - MOV video files

Each handler provides:
- Format validation
- Metadata extraction
- File integrity checking

## 🧪 Testing

Run all tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Run specific test file:

```bash
python -m unittest tests.test_video_formats
```

Run with coverage:

```bash
pip install coverage
coverage run -m unittest discover
coverage report
```

## 🐳 Docker Support

Build and run the container:

```bash
# Build the Docker image
docker build -t youtube-studio .

# Run the container
docker run -it youtube-studio -- --help
```

## 📊 SEO Scoring

The system calculates an SEO score (0.0 to 1.0) based on:

- **Title length** (30-80 characters optimal)
- **Keyword count** (5-15 keywords recommended)
- **Keyword diversity** (unique starting characters)
- **Keyword matches** (keywords in title)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Support

For support, email support@example.com or create an issue on GitHub.

## 🙏 Acknowledgments

- YouTube for the platform
- Python community for excellent libraries
- All contributors to this project
