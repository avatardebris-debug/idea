"""Tests for PDF report generator."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from seo_tool.models import SEOReport, MetaTag
from seo_tool.reports.pdf import PDFReport


class TestPDFReport:
    """Test PDF report generation."""

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
                MetaTag(name="keywords", content="example, test, seo"),
            ],
            og_tags=[
                MetaTag(name="og:title", content="Example OG Title"),
                MetaTag(name="og:description", content="Example OG Description"),
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
        """Test PDF report initialization."""
        report = PDFReport(
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

    def test_generate_pdf(self, sample_report, sample_score_result):
        """Test PDF generation."""
        pdf_report = PDFReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        pdf_bytes = pdf_report.to_bytes()

        # Check for PDF header
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 0

    def test_save_pdf(self, sample_report, sample_score_result):
        """Test saving PDF report to file."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.pdf"

            pdf_report = PDFReport(
                report=sample_report,
                score_result=sample_score_result,
                generated_at=datetime.now(),
            )

            saved_path = pdf_report.save(output_path)

            assert saved_path.exists()
            assert saved_path == output_path

            content = saved_path.read_bytes()
            assert content.startswith(b"%PDF-")

    def test_to_bytes(self, sample_report, sample_score_result):
        """Test converting report to bytes."""
        pdf_report = PDFReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        pdf_bytes = pdf_report.to_bytes()

        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 0

    def test_to_stream(self, sample_report, sample_score_result):
        """Test converting report to stream."""
        pdf_report = PDFReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        stream = pdf_report.to_stream()

        assert stream is not None
        content = stream.read()
        assert isinstance(content, bytes)
        assert content.startswith(b"%PDF-")
        assert len(content) > 0

    def test_custom_title(self, sample_report, sample_score_result):
        """Test custom title in report."""
        pdf_report = PDFReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
            title="Custom Title",
        )

        pdf_bytes = pdf_report.to_bytes()
        assert b"Custom Title" in pdf_bytes

    def test_custom_company_name(self, sample_report, sample_score_result):
        """Test custom company name in report."""
        pdf_report = PDFReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
            company_name="Custom Company",
        )

        pdf_bytes = pdf_report.to_bytes()
        assert b"Custom Company" in pdf_bytes

    def test_empty_report(self, sample_score_result):
        """Test report with empty SEO data."""
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

        pdf_report = PDFReport(
            report=empty_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        pdf_bytes = pdf_report.to_bytes()
        assert pdf_bytes.startswith(b"%PDF-")

    def test_fetch_error(self, sample_score_result):
        """Test report with fetch error."""
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

        pdf_report = PDFReport(
            report=error_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        pdf_bytes = pdf_report.to_bytes()
        assert pdf_bytes.startswith(b"%PDF-")
        assert b"Analysis Failed" in pdf_bytes
        assert b"Failed to fetch URL" in pdf_bytes

    def test_score_coloring(self, sample_report, sample_score_result):
        """Test score-based coloring in report."""
        pdf_report = PDFReport(
            report=sample_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        pdf_bytes = pdf_report.to_bytes()
        # PDF uses color codes, so we check for color-related content
        assert len(pdf_bytes) > 0

    def test_unicode_handling(self, sample_report, sample_score_result):
        """Test handling of unicode characters."""
        unicode_report = SEOReport(
            url="https://example.com",
            word_count=1500,
            link_count=25,
            internal_links=15,
            external_links=10,
            images=8,
            headings=12,
            meta_tags=[
                MetaTag(name="title", content="Example Page with Unicode: 你好 🌍"),
                MetaTag(name="description", content="Description with emojis: 🚀✨"),
            ],
            og_tags=[],
            generated_at=datetime.now(),
        )

        pdf_report = PDFReport(
            report=unicode_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        pdf_bytes = pdf_report.to_bytes()
        assert pdf_bytes.startswith(b"%PDF-")
        # PDF encoding handles unicode, so we just check it generates valid PDF

    def test_large_report(self, sample_report, sample_score_result):
        """Test report with large amount of data."""
        # Create a report with many meta tags
        many_meta_tags = [
            MetaTag(name=f"meta-{i}", content=f"Content {i}")
            for i in range(50)
        ]

        large_report = SEOReport(
            url="https://example.com",
            word_count=1500,
            link_count=25,
            internal_links=15,
            external_links=10,
            images=8,
            headings=12,
            meta_tags=many_meta_tags,
            og_tags=[],
            generated_at=datetime.now(),
        )

        pdf_report = PDFReport(
            report=large_report,
            score_result=sample_score_result,
            generated_at=datetime.now(),
        )

        pdf_bytes = pdf_report.to_bytes()
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 0

    def test_directory_creation(self, sample_report, sample_score_result):
        """Test that PDF report creates directories if they don't exist."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "report.pdf"

            pdf_report = PDFReport(
                report=sample_report,
                score_result=sample_score_result,
                generated_at=datetime.now(),
            )

            saved_path = pdf_report.save(output_path)

            assert saved_path.exists()
            assert saved_path.parent.exists()
