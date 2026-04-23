"""Integration tests for the SEO tool — end-to-end flow."""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from seo_tool.analyzer import Analyzer
from seo_tool.cli import cli
from seo_tool.models import SEOReport
from seo_tool.scorer import Scorer


# -- Integration: Analyzer + Scorer + CLI --

class TestIntegration:
    @patch("seo_tool.analyzer.requests.get")
    def test_full_pipeline_json(self, mock_get):
        """Analyzer fetches → Scorer scores → CLI outputs JSON."""
        html = """
        <html>
        <head>
            <title>Perfect Title</title>
            <meta name="description" content="A perfect meta description that is exactly the right length for SEO purposes and should score full marks.">
            <link rel="canonical" href="https://example.com/page">
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Description">
            <meta property="og:image" content="https://example.com/img.jpg">
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Sub Heading</h2>
            <p>This is some paragraph text with enough words to pass the content length check. We need at least 300 words for a good score so here are more words to pad things out. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
            <img src="photo.jpg" alt="A descriptive alt text">
            <a href="/internal-page">Internal Link</a>
            <a href="https://external.com/page">External Link</a>
        </body>
        </html>
        """
        mock_get.return_value = MagicMock(status_code=200, text=html)

        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com", "--json"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["url"] == "https://example.com"
        assert output["total_score"] == 100
        assert output["category_scores"]["title"]["score"] == 10
        assert output["category_scores"]["meta_description"]["score"] == 10
        assert output["category_scores"]["h1_count"]["score"] == 15
        assert output["category_scores"]["canonical"]["score"] == 10
        assert output["category_scores"]["content_length"]["score"] == 30
        assert output["category_scores"]["og_tags"]["score"] == 10
        assert output["category_scores"]["images"]["score"] == 5
        assert output["category_scores"]["links"]["score"] == 5
        assert output["category_scores"]["headings"]["score"] == 5

    @patch("seo_tool.analyzer.requests.get")
    def test_full_pipeline_text(self, mock_get):
        """Analyzer fetches → Scorer scores → CLI outputs formatted text."""
        html = """
        <html>
        <head>
            <title>Short</title>
        </head>
        <body>
            <p>Hi</p>
        </body>
        </html>
        """
        mock_get.return_value = MagicMock(status_code=200, text=html)

        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com"])

        assert result.exit_code == 0
        assert "SEO Analysis Report" in result.output
        assert "https://example.com" in result.output
        assert "Total Score" in result.output
        assert "Category Scores" in result.output

    @patch("seo_tool.analyzer.requests.get")
    def test_full_pipeline_output_file(self, mock_get, tmp_path):
        """Analyzer fetches → Scorer scores → CLI writes to file."""
        html = """
        <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <p>Content</p>
        </body>
        </html>
        """
        mock_get.return_value = MagicMock(status_code=200, text=html)

        output_file = tmp_path / "report.txt"
        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com", "-o", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Report written to" in result.output
        content = output_file.read_text()
        assert "SEO Analysis Report" in content

    @patch("seo_tool.analyzer.requests.get")
    def test_analyzer_error_propagates(self, mock_get):
        """Analyzer error → CLI exits with code 1."""
        import requests

        mock_get.side_effect = requests.HTTPError("404 Not Found")
        mock_get.side_effect.response = MagicMock(status_code=404)

        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com"])

        assert result.exit_code == 1
        assert "Error:" in result.output

    @patch("seo_tool.analyzer.requests.get")
    def test_scorer_zero_score_for_empty_page(self, mock_get):
        """Empty page → Scorer returns 0 → CLI outputs 0."""
        mock_get.return_value = MagicMock(status_code=200, text="<html><head></head><body></body></html>")

        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com", "--json"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["total_score"] == 0

    @patch("seo_tool.analyzer.requests.get")
    def test_scorer_partial_score(self, mock_get):
        """Partial content → Scorer returns partial score."""
        html = """
        <html>
        <head>
            <title>Good Title Here</title>
            <meta name="description" content="A good meta description that is exactly the right length for SEO purposes and should score full marks.">
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>This is some paragraph text with enough words to pass the content length check. We need at least 300 words for a good score so here are more words to pad things out. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </body>
        </html>
        """
        mock_get.return_value = MagicMock(status_code=200, text=html)

        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com", "--json"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        # Should have some score but not 100 (missing canonical, og_tags, images, links)
        assert 0 < output["total_score"] < 100
