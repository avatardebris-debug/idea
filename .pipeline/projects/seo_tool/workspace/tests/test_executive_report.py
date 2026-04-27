"""Tests for executive summary report generator."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from seo_tool.models import SEOReport, MetaTag
from seo_tool.reports.executive import ExecutiveSummaryReport


class TestExecutiveSummaryReport:
    """Test executive summary report generation."""

    @pytest.fixture
    def sample_report(self):
        """Create a sample SEO report for testing."""
        return SEOReport(
            url="https://example.com",
            word_count=1500,
            link_count=25,
            internal_links=15,
            external_links=10,
            images=8,
            headings=12,
            meta_tags=[
                MetaTag(name="title", content="Example Page Title"),
                MetaTag(name="description", content="This is an example page"),
            ],
            og_tags=[],
            generated_at=datetime.now(),
        )

    @pytest.fixture
    def sample_score_result(self):
        """Create a sample score result for testing."""
        return {
            "total_score": 75,
            "max_total_score": 100,
            "category_scores": {
                "content": {"score": 80, "max": 100, "reason": "Good content length"},
                "structure": {"score": 70, "max": 100, "reason": "Needs more headings"},
                "links": {"score": 60, "max": 100, "reason": "Limited links"},
                "images": {"score": 90, "max": 100, "reason": "Good image usage"},
                "meta_tags": {"score": 85, "max": 100, "reason": "Good meta tags"},
            },
        }

    def test_initialization(self, sample_report, sample_score_result):
        """Test executive summary report initialization."""
        report = ExecutiveSummaryReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
            title="Test Report",
            company_name="Test Company",
        )

        assert report.report == sample_report
        assert report.score_result == sample_score_result
        assert report.title == "Test Report"
        assert report.company_name == "Test Company"

    def test_generate_executive_summary(self, sample_report, sample_score_result):
        """Test executive summary generation."""
        exec_report = ExecutiveSummaryReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        summary_text = exec_report.generate()

        # Check for expected content
        assert "EXECUTIVE SUMMARY" in summary_text
        assert "https://example.com" in summary_text
        assert "75/100" in summary_text
        assert "Action Items" in summary_text
        assert "Recommendations" in summary_text
        assert "Category Breakdown" in summary_text

    def test_save_executive_summary(self, sample_report, sample_score_result):
        """Test saving executive summary to file."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "summary.txt"

            exec_report = ExecutiveSummaryReport(
                report=sample_report,
                score_result=sample_score_result,
                generated_at=datetime.now(),
            )

            saved_path = exec_report.save(output_path)

            assert saved_path.exists()
            assert saved_path == output_path

            content = saved_path.read_text()
            assert "EXECUTIVE SUMMARY" in content
            assert "75/100" in content

    def test_to_bytes(self, sample_report, sample_score_result):
        """Test converting report to bytes."""
        exec_report = ExecutiveSummaryReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        summary_bytes = exec_report.to_bytes()

        assert isinstance(summary_bytes, bytes)
        assert len(summary_bytes) > 0
        assert b"EXECUTIVE SUMMARY" in summary_bytes

    def test_to_stream(self, sample_report, sample_score_result):
        """Test converting report to stream."""
        exec_report = ExecutiveSummaryReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        stream = exec_report.to_stream()

        assert stream is not None
        content = stream.read()
        assert isinstance(content, bytes)
        assert len(content) > 0

    def test_custom_title(self, sample_report, sample_score_result):
        """Test custom title in report."""
        exec_report = ExecutiveSummaryReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
            title="Custom Executive Summary",
        )

        summary_text = exec_report.generate()
        assert "Custom Executive Summary" in summary_text

    def test_custom_company_name(self, sample_report, sample_score_result):
        """Test custom company name in report."""
        exec_report = ExecutiveSummaryReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
            company_name="Custom Company",
        )

        summary_text = exec_report.generate()
        assert "Custom Company" in summary_text

    def test_low_score_summary(self, sample_score_result):
        """Test executive summary for low score."""
        low_score_result = {
            "total_score": 25,
            "max_total_score": 100,
            "category_scores": {
                "content": {"score": 20, "max": 100, "reason": "Low content"},
                "structure": {"score": 30, "max": 100, "reason": "Poor structure"},
            },
        }

        exec_report = ExecutiveSummaryReport(
            report=SEOReport(
                url="https://example.com",
                word_count=100,
                link_count=0,
                internal_links=0,
                external_links=0,
                images=0,
                headings=0,
                meta_tags=[],
                og_tags=[],
                generated_at=datetime.now(),
            ),
            score_result=low_score_result,
            generated_at=datetime.now(),
        )

        summary_text = exec_report.generate()
        assert "requires significant SEO improvements" in summary_text.lower()

    def test_excellent_score_summary(self, sample_score_result):
        """Test executive summary for excellent score."""
        excellent_score_result = {
            "total_score": 95,
            "max_total_score": 100,
            "category_scores": {
                "content": {"score": 100, "max": 100, "reason": "Excellent content"},
                "structure": {"score": 90, "max": 100, "reason": "Good structure"},
            },
        }

        exec_report = ExecutiveSummaryReport(
            report=SEOReport(
                url="https://example.com",
                word_count=2500,
                link_count=50,
                internal_links=30,
                external_links=20,
                images=20,
                headings=20,
                meta_tags=[],
                og_tags=[],
                generated_at=datetime.now(),
            ),
            score_result=excellent_score_result,
            generated_at=datetime.now(),
        )

        summary_text = exec_report.generate()
        assert "strong SEO foundation" in summary_text.lower()

    def test_action_items_generation(self, sample_report, sample_score_result):
        """Test action items are generated correctly."""
        exec_report = ExecutiveSummaryReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        summary_text = exec_report.generate()

        # Check for action items
        assert "ACTION ITEMS" in summary_text
        assert "High" in summary_text or "Medium" in summary_text
        assert "Low" in summary_text

    def test_recommendations_generation(self, sample_report, sample_score_result):
        """Test recommendations are generated correctly."""
        exec_report = ExecutiveSummaryReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        summary_text = exec_report.generate()

        # Check for recommendations
        assert "RECOMMENDATIONS" in summary_text

    def test_key_findings_generation(self, sample_report, sample_score_result):
        """Test key findings are generated correctly."""
        exec_report = ExecutiveSummaryReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        summary_text = exec_report.generate()

        # Check for key findings
        assert "KEY FINDINGS" in summary_text
        assert "✅" in summary_text or "⚠️" in summary_text or "❌" in summary_text

    def test_empty_report(self, sample_score_result):
        """Test executive summary with empty SEO data."""
        empty_report = SEOReport(
            url="https://empty.com",
            word_count=0,
            link_count=0,
            internal_links=0,
            external_links=0,
            images=0,
            headings=0,
            meta_tags=[],
            og_tags=[],
            generated_at=datetime.now(),
        )

        exec_report = ExecutiveSummaryReport(
            report=empty_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        summary_text = exec_report.generate()
        assert "EXECUTIVE SUMMARY" in summary_text
        assert "0/100" in summary_text

    def test_fetch_error(self, sample_score_result):
        """Test executive summary with fetch error."""
        error_report = SEOReport(
            url="https://error.com",
            word_count=0,
            link_count=0,
            internal_links=0,
            external_links=0,
            images=0,
            headings=0,
            meta_tags=[],
            og_tags=[],
            fetch_error="Failed to fetch URL",
            http_status=404,
            generated_at=datetime.now(),
        )

        exec_report = ExecutiveSummaryReport(
            report=error_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        summary_text = exec_report.generate()
        assert "EXECUTIVE SUMMARY" in summary_text
        assert "Failed to fetch URL" in summary_text

    def test_directory_creation(self, sample_report, sample_score_result):
        """Test that executive summary creates directories if they don't exist."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "summary.txt"

            exec_report = ExecutiveSummaryReport(
                report=sample_report,
                score_result=sample_score_result,
                generated_at=datetime.now(),
            )

            saved_path = exec_report.save(output_path)

            assert saved_path.exists()
            assert saved_path.parent.exists()
