"""Tests for HTML report generator."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from seo_tool.models import SEOReport, MetaTag, ImageInfo, OpenGraphTag
from seo_tool.reports.html import HTMLReport


class TestHTMLReport:
    """Test HTML report generation."""

    @pytest.fixture
    def sample_report(self):
        """Create a sample SEO report for testing."""
        return SEOReport(
            url="https://example.com",
            word_count=1500,
            link_count=25,
            internal_links=[type("Link", (), {"href": "/a"})() for _ in range(15)],
            external_links=[type("Link", (), {"href": "https://other.com"})() for _ in range(10)],
            images=[ImageInfo(src=f"img{i}.jpg", alt=f"Image {i}") for i in range(8)],
            headings=[(1, "H1"), (2, "H2"), (3, "H3") for _ in range(4)],
            meta_tags=[
                MetaTag(name="title", content="Example Page Title"),
                MetaTag(name="description", content="This is an example page"),
                MetaTag(name="keywords", content="example, test, seo"),
            ],
            og_tags=[
                OpenGraphTag(property="og:title", content="Example OG Title"),
                OpenGraphTag(property="og:description", content="Example OG Description"),
            ],
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
        """Test HTML report initialization."""
        report = HTMLReport(
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

    def test_generate_html(self, sample_report, sample_score_result):
        """Test HTML generation."""
        html_report = HTMLReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        html_content = html_report.generate()

        # Check for expected content
        assert "SEO Report" in html_content
        assert "https://example.com" in html_content
        assert "75/100" in html_content
        assert "Content Score" in html_content
        assert "Structure Score" in html_content
        assert "Example Page Title" in html_content
        assert "Example OG Title" in html_content

    def test_save_html(self, sample_report, sample_score_result):
        """Test saving HTML report to file."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.html"

            html_report = HTMLReport(
                report=sample_report,
                score_result=sample_score_result,
                generated_at=datetime.now(),
            )

            saved_path = html_report.save(output_path)

            assert saved_path.exists()
            assert saved_path == output_path

            content = saved_path.read_text()
            assert "SEO Report" in content
            assert "<html" in content.lower()
            assert "<head" in content.lower()
            assert "<body" in content.lower()

    def test_to_bytes(self, sample_report, sample_score_result):
        """Test converting report to bytes."""
        html_report = HTMLReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        html_bytes = html_report.to_bytes()

        assert isinstance(html_bytes, bytes)
        assert len(html_bytes) > 0
        assert b"SEO Report" in html_bytes

    def test_to_stream(self, sample_report, sample_score_result):
        """Test converting report to stream."""
        html_report = HTMLReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        stream = html_report.to_stream()

        assert stream is not None
        content = stream.read()
        assert isinstance(content, bytes)
        assert len(content) > 0

    def test_custom_title(self, sample_report, sample_score_result):
        """Test custom title in report."""
        html_report = HTMLReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
            title="Custom Title",
        )

        html_content = html_report.generate()
        assert "Custom Title" in html_content

    def test_custom_company_name(self, sample_report, sample_score_result):
        """Test custom company name in report."""
        html_report = HTMLReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
            company_name="Custom Company",
        )

        html_content = html_report.generate()
        assert "Custom Company" in html_content

    def test_empty_report(self, sample_score_result):
        """Test report with empty SEO data."""
        empty_report = SEOReport(
            url="https://empty.com",
            word_count=0,
            link_count=0,
            internal_links=[],
            external_links=[],
            images=[],
            headings=[],
            meta_tags=[],
            og_tags=[],
            generated_at=datetime.now(),
        )

        html_report = HTMLReport(
            report=empty_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        html_content = html_report.generate()
        assert "SEO Report" in html_content
        assert "0/100" in html_content

    def test_fetch_error(self, sample_score_result):
        """Test report with fetch error."""
        error_report = SEOReport(
            url="https://error.com",
            word_count=0,
            link_count=0,
            internal_links=[],
            external_links=[],
            images=[],
            headings=[],
            meta_tags=[],
            og_tags=[],
            fetch_error="Failed to fetch URL",
            http_status=404,
            generated_at=datetime.now(),
        )

        html_report = HTMLReport(
            report=error_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        html_content = html_report.generate()
        assert "Analysis Failed" in html_content
        assert "Failed to fetch URL" in html_content
        assert "404" in html_content

    def test_score_coloring(self, sample_report, sample_score_result):
        """Test score-based coloring in report."""
        html_report = HTMLReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        html_content = html_report.generate()

        # Check for score classes
        assert "score-excellent" in html_content or "score-good" in html_content or "score-poor" in html_content

    def test_css_included(self, sample_report, sample_score_result):
        """Test that CSS is included in report."""
        html_report = HTMLReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        html_content = html_report.generate()

        assert "<style" in html_content.lower()
        assert "color" in html_content.lower()
        assert "font" in html_content.lower()
        assert "margin" in html_content.lower()

    def test_unicode_handling(self, sample_report, sample_score_result):
        """Test handling of unicode characters."""
        unicode_report = SEOReport(
            url="https://example.com",
            word_count=1500,
            link_count=25,
            internal_links=[type("Link", (), {"href": "/a"})() for _ in range(15)],
            external_links=[type("Link", (), {"href": "https://other.com"})() for _ in range(10)],
            images=[ImageInfo(src=f"img{i}.jpg", alt=f"Image {i}") for i in range(8)],
            headings=[(1, "H1"), (2, "H2"), (3, "H3") for _ in range(4)],
            meta_tags=[
                MetaTag(name="title", content="Example Page with Unicode: 你好 🌍"),
                MetaTag(name="description", content="Description with emojis: 🚀✨"),
            ],
            og_tags=[],
            generated_at=datetime.now(),
        )

        html_report = HTMLReport(
            report=unicode_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        html_content = html_report.generate()
        assert "你好" in html_content
        assert "🌍" in html_content
        assert "🚀" in html_content
        assert "✨" in html_content
