"""
Transcript Extractor package configuration.
"""

from setuptools import setup, find_packages

setup(
    name="transcript-extractor",
    version="1.0.0",
    author="Transcript Extractor Team",
    description="Extract transcripts from video/audio files using Whisper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/transcript-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "faster-whisper>=1.0.0",
        "ffmpeg-python>=0.2.0",
        "click>=8.1.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "transcript-extractor=transcript_extractor.cli:main",
        ],
    },
)
