"""Tests for seo_tool.cli."""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from seo_tool.cli import cli


# -- CLI --

class TestCli:
    @patch("seo_tool.cli.Analyzer")
    @patch("seo_tool.cli.Scorer")
    def test_json_output(self, mock_scorer_cls, mock_analyzer_cls):
        mock_report = MagicMock()
        mock_report.url = "https://example.com"
        mock_report.fetch_error = None
        mock_report.http_status = 200
        mock_report.word_count = 100
        mock_report.link_count = 5
        mock_report.internal_links = [MagicMock()]
        mock_report.external_links = [MagicMock()]
        mock_report.images = [MagicMock()]
        mock_report.headings = [(1, "H1")]
        mock_report.og_tags = []

        mock_analyzer = MagicMock()
        mock_analyzer.fetch_and_parse.return_value = mock_report
        mock_analyzer_cls.return_value = mock_analyzer

        mock_score_result = {"total_score": 50, "category_scores": {}}
        mock_scorer = MagicMock()
        mock_scorer.score.return_value = mock_score_result
        mock_scorer_cls.return_value = mock_scorer

        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com", "--json"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["url"] == "https://example.com"
        assert output["total_score"] == 50

    @patch("seo_tool.cli.Analyzer")
    @patch("seo_tool.cli.Scorer")
    def test_text_output(self, mock_scorer_cls, mock_analyzer_cls):
        mock_report = MagicMock()
        mock_report.url = "https://example.com"
        mock_report.fetch_error = None
        mock_report.http_status = 200
        mock_report.word_count = 100
        mock_report.link_count = 5
        mock_report.internal_links = [MagicMock()]
        mock_report.external_links = [MagicMock()]
        mock_report.images = [MagicMock()]
        mock_report.headings = [(1, "H1")]
        mock_report.og_tags = []

        mock_analyzer = MagicMock()
        mock_analyzer.fetch_and_parse.return_value = mock_report
        mock_analyzer_cls.return_value = mock_analyzer

        mock_score_result = {"total_score": 50, "category_scores": {}}
        mock_scorer = MagicMock()
        mock_scorer.score.return_value = mock_score_result
        mock_scorer_cls.return_value = mock_scorer

        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com"])

        assert result.exit_code == 0
        assert "SEO Analysis Report" in result.output
        assert "https://example.com" in result.output

    @patch("seo_tool.cli.Analyzer")
    def test_fetch_error_exits(self, mock_analyzer_cls):
        mock_analyzer = MagicMock()
        mock_analyzer.fetch_and_parse.side_effect = Exception("Network error")
        mock_analyzer_cls.return_value = mock_analyzer

        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com"])

        assert result.exit_code == 1
        assert "Error:" in result.output

    @patch("seo_tool.cli.Analyzer")
    @patch("seo_tool.cli.Scorer")
    def test_output_file(self, mock_scorer_cls, mock_analyzer_cls, tmp_path):
        mock_report = MagicMock()
        mock_report.url = "https://example.com"
        mock_report.fetch_error = None
        mock_report.http_status = 200
        mock_report.word_count = 100
        mock_report.link_count = 5
        mock_report.internal_links = [MagicMock()]
        mock_report.external_links = [MagicMock()]
        mock_report.images = [MagicMock()]
        mock_report.headings = [(1, "H1")]
        mock_report.og_tags = []

        mock_analyzer = MagicMock()
        mock_analyzer.fetch_and_parse.return_value = mock_report
        mock_analyzer_cls.return_value = mock_analyzer

        mock_score_result = {"total_score": 50, "category_scores": {}}
        mock_scorer = MagicMock()
        mock_scorer.score.return_value = mock_score_result
        mock_scorer_cls.return_value = mock_scorer

        output_file = tmp_path / "report.txt"
        runner = CliRunner()
        result = runner.invoke(cli, ["https://example.com", "-o", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Report written to" in result.output
