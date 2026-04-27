"""Tests for comparative report generator."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from seo_tool.models import SEOReport, MetaTag
from seo_tool.reports.comparative import ComparativeReport


class TestComparativeReport:
    """Test comparative report generation."""

    @pytest.fixture
    def sample_report_1(self):
        """Create first sample SEO report for testing."""
        return SEOReport(
            url="https://example1.com",
            word_count=1500,
            link_count=25,
            internal_links=15,
            external_links=10,
            images=8,
            headings=12,
            meta_tags=[
                MetaTag(name="title", content="Example Page Title 1"),
                MetaTag(name="description", content="This is an example page 1"),
            ],
            og_tags=[],
            generated_at=datetime.now(),
        )

    @pytest.fixture
    def sample_report_2(self):
        """Create second sample SEO report for testing."""
        return SEOReport(
            url="https://example2.com",
            word_count=1200,
            link_count=20,
            internal_links=12,
            external_links=8,
            images=6,
            headings=10,
            meta_tags=[
                MetaTag(name="title", content="Example Page Title 2"),
                MetaTag(name="description", content="This is an example page 2"),
            ],
            og_tags=[],
            generated_at=datetime.now(),
        )

    @pytest.fixture
    def sample_score_result_1(self):
        """Create first sample score result for testing."""
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

    @pytest.fixture
    def sample_score_result_2(self):
        """Create second sample score result for testing."""
        return {
            "total_score": 65,
            "max_total_score": 100,
            "category_scores": {
                "content": {"score": 70, "max": 100, "reason": "Moderate content"},
                "structure": {"score": 60, "max": 100, "reason": "Needs more headings"},
                "links": {"score": 50, "max": 100, "reason": "Fewer links"},
                "images": {"score": 80, "max": 100, "reason": "Good image usage"},
                "meta_tags": {"score": 75, "max": 100, "reason": "Good meta tags"},
            },
        }

    def test_initialization(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test comparative report initialization."""
        report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
            title="Test Report",
            company_name="Test Company",
        )

        assert len(report.reports) == 2
        assert len(report.score_results) == 2
        assert report.title == "Test Report"
        assert report.company_name == "Test Company"

    def test_generate_comparative_report(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test comparative report generation."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        report_text = comp_report.generate()

        # Check for expected content
        assert "COMPARATIVE SEO ANALYSIS" in report_text
        assert "https://example1.com" in report_text
        assert "https://example2.com" in report_text
        assert "75/100" in report_text
        assert "65/100" in report_text
        assert "Comparison" in report_text
        assert "Recommendations" in report_text

    def test_save_comparative_report(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test saving comparative report to file."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "comparison.txt"

            comp_report = ComparativeReport(
                reports=[sample_report_1, sample_report_2],
                score_results=[sample_score_result_1, sample_score_result_2],
                generated_at=datetime.now(),
            )

            saved_path = comp_report.save(output_path)

            assert saved_path.exists()
            assert saved_path == output_path

            content = saved_path.read_text()
            assert "COMPARATIVE SEO ANALYSIS" in content
            assert "75/100" in content
            assert "65/100" in content

    def test_to_bytes(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test converting report to bytes."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        report_bytes = comp_report.to_bytes()

        assert isinstance(report_bytes, bytes)
        assert len(report_bytes) > 0
        assert b"COMPARATIVE SEO ANALYSIS" in report_bytes

    def test_to_stream(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test converting report to stream."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        stream = comp_report.to_stream()

        assert stream is not None
        content = stream.read()
        assert isinstance(content, bytes)
        assert len(content) > 0

    def test_custom_title(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test custom title in report."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
            title="Custom Comparison",
        )

        report_text = comp_report.generate()
        assert "Custom Comparison" in report_text

    def test_custom_company_name(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test custom company name in report."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
            company_name="Custom Company",
        )

        report_text = comp_report.generate()
        assert "Custom Company" in report_text

    def test_single_report_comparison(self, sample_report_1, sample_score_result_1):
        """Test comparison with single report."""
        comp_report = ComparativeReport(
            reports=[sample_report_1],
            score_results=[sample_score_result_1],
            generated_at=datetime.now(),
        )

        report_text = comp_report.generate()
        assert "COMPARATIVE SEO ANALYSIS" in report_text
        assert "https://example1.com" in report_text

    def test_multiple_reports_comparison(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test comparison with multiple reports."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        report_text = comp_report.generate()
        assert "COMPARATIVE SEO ANALYSIS" in report_text
        assert "https://example1.com" in report_text
        assert "https://example2.com" in report_text

    def test_comparison_metrics(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test comparison metrics are generated correctly."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        report_text = comp_report.generate()

        # Check for comparison metrics
        assert "Comparison" in report_text
        assert "Words" in report_text
        assert "Links" in report_text
        assert "Images" in report_text
        assert "Headings" in report_text

    def test_category_breakdown(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test category breakdown is generated correctly."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        report_text = comp_report.generate()

        # Check for category breakdown
        assert "Category Breakdown" in report_text
        assert "Content Score" in report_text
        assert "Structure Score" in report_text

    def test_recommendations_generation(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test recommendations are generated correctly."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        report_text = comp_report.generate()

        # Check for recommendations
        assert "RECOMMENDATIONS" in report_text
        assert "High" in report_text or "Medium" in report_text
        assert "Low" in report_text

    def test_empty_reports(self, sample_score_result_1, sample_score_result_2):
        """Test comparative report with empty SEO data."""
        empty_report_1 = SEOReport(
            url="https://empty1.com",
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

        empty_report_2 = SEOReport(
            url="https://empty2.com",
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

        comp_report = ComparativeReport(
            reports=[empty_report_1, empty_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        report_text = comp_report.generate()
        assert "COMPARATIVE SEO ANALYSIS" in report_text
        assert "0/100" in report_text

    def test_fetch_errors(self, sample_score_result_1, sample_score_result_2):
        """Test comparative report with fetch errors."""
        error_report_1 = SEOReport(
            url="https://error1.com",
            word_count=0,
            link_count=0,
            internal_links=0,
            external_links=0,
            images=0,
            headings=0,
            meta_tags=[],
            og_tags=[],
            fetch_error="Failed to fetch URL 1",
            http_status=404,
            generated_at=datetime.now(),
        )

        error_report_2 = SEOReport(
            url="https://error2.com",
            word_count=0,
            link_count=0,
            internal_links=0,
            external_links=0,
            images=0,
            headings=0,
            meta_tags=[],
            og_tags=[],
            fetch_error="Failed to fetch URL 2",
            http_status=500,
            generated_at=datetime.now(),
        )

        comp_report = ComparativeReport(
            reports=[error_report_1, error_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        report_text = comp_report.generate()
        assert "COMPARATIVE SEO ANALYSIS" in report_text
        assert "Failed to fetch URL 1" in report_text
        assert "Failed to fetch URL 2" in report_text

    def test_directory_creation(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test that comparative report creates directories if they don't exist."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "comparison.txt"

            comp_report = ComparativeReport(
                reports=[sample_report_1, sample_report_2],
                score_results=[sample_score_result_1, sample_score_result_2],
                generated_at=datetime.now(),
            )

            saved_path = comp_report.save(output_path)

            assert saved_path.exists()
            assert saved_path.parent.exists()

    def test_score_differences(self, sample_report_1, sample_report_2, sample_score_result_1, sample_score_result_2):
        """Test score differences are highlighted correctly."""
        comp_report = ComparativeReport(
            reports=[sample_report_1, sample_report_2],
            score_results=[sample_score_result_1, sample_score_result_2],
            generated_at=datetime.now(),
        )

        report_text = comp_report.generate()

        # Check for score differences
        assert "75/100" in report_text
        assert "65/100" in report_text
        # Should show which one is better
        assert "example1.com" in report_text
        assert "example2.com" in report_text
