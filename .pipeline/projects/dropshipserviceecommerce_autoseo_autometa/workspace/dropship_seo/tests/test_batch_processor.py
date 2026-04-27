"""Tests for batch processing functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dropship_seo.batch_processor import BatchProcessor, BatchResult, BatchStats
from dropship_seo.cache import CacheManager
from dropship_seo.models import Product, SEOReport, SEOMetrics, Issue, IssueSeverity
from dropship_seo.seo_analyzer import SEOAnalyzer
from dropship_seo.config import SEOConfig, BatchConfig, AppConfig, ConfigManager


class TestBatchResult:
    """Tests for BatchResult class."""

    def test_batch_result_creation(self):
        """Test creating a batch result."""
        report = SEOReport(
            product_name="Test Product",
            overall_score=85,
            seo_metrics=SEOMetrics(
                title_score=90,
                meta_description_score=80,
                image_alt_score=85,
                content_length_score=85,
                keyword_density_score=85,
            ),
            issues=[],
            meta_tags=[],
            analysis_date=None,
            processing_time_ms=100,
        )

        result = BatchResult(
            product_name="Test Product",
            success=True,
            report=report,
            processing_time_ms=100,
            cache_hit=False,
            error_message=None,
        )

        assert result.success is True
        assert result.product_name == "Test Product"
        assert result.processing_time_ms == 100
        assert result.cache_hit is False
        assert result.error_message is None

    def test_batch_result_to_dict(self):
        """Test converting batch result to dictionary."""
        report = SEOReport(
            product_name="Test Product",
            overall_score=85,
            seo_metrics=SEOMetrics(
                title_score=90,
                meta_description_score=80,
                image_alt_score=85,
                content_length_score=85,
                keyword_density_score=85,
            ),
            issues=[],
            meta_tags=[],
            analysis_date=None,
            processing_time_ms=100,
        )

        result = BatchResult(
            product_name="Test Product",
            success=True,
            report=report,
            processing_time_ms=100,
            cache_hit=False,
            error_message=None,
        )

        data = result.to_dict()

        assert data["product_name"] == "Test Product"
        assert data["success"] is True
        assert data["processing_time_ms"] == 100
        assert data["cache_hit"] is False
        assert data["error_message"] is None
        assert "report" in data

    def test_batch_result_from_dict(self):
        """Test creating batch result from dictionary."""
        data = {
            "product_name": "Test Product",
            "success": True,
            "report": {
                "product_name": "Test Product",
                "overall_score": 85,
                "seo_metrics": {
                    "title_score": 90,
                    "meta_description_score": 80,
                    "image_alt_score": 85,
                    "content_length_score": 85,
                    "keyword_density_score": 85,
                },
                "issues": [],
                "meta_tags": [],
                "analysis_date": "2024-01-01T00:00:00",
                "processing_time_ms": 100,
            },
            "processing_time_ms": 100,
            "cache_hit": False,
            "error_message": None,
        }

        result = BatchResult.from_dict(data)

        assert result.product_name == "Test Product"
        assert result.success is True
        assert result.processing_time_ms == 100
        assert result.cache_hit is False
        assert result.error_message is None
        assert result.report is not None
        assert result.report.overall_score == 85

    def test_batch_result_failure(self):
        """Test creating a failed batch result."""
        result = BatchResult(
            product_name="Test Product",
            success=False,
            report=None,
            processing_time_ms=0,
            cache_hit=False,
            error_message="Test error",
        )

        assert result.success is False
        assert result.report is None
        assert result.error_message == "Test error"


class TestBatchStats:
    """Tests for BatchStats class."""

    def test_batch_stats_creation(self):
        """Test creating batch statistics."""
        stats = BatchStats(
            total_products=10,
            successful=8,
            failed=2,
            cache_hits=3,
            total_processing_time_ms=1000,
        )

        assert stats.total_products == 10
        assert stats.successful == 8
        assert stats.failed == 2
        assert stats.cache_hits == 3
        assert stats.success_rate == 80.0
        assert stats.avg_processing_time_ms == 125.0

    def test_batch_stats_to_dict(self):
        """Test converting batch stats to dictionary."""
        stats = BatchStats(
            total_products=10,
            successful=8,
            failed=2,
            cache_hits=3,
            total_processing_time_ms=1000,
        )

        data = stats.to_dict()

        assert data["total_products"] == 10
        assert data["successful"] == 8
        assert data["failed"] == 2
        assert data["cache_hits"] == 3
        assert data["success_rate"] == 80.0
        assert data["avg_processing_time_ms"] == 125.0

    def test_batch_stats_from_dict(self):
        """Test creating batch stats from dictionary."""
        data = {
            "total_products": 10,
            "successful": 8,
            "failed": 2,
            "cache_hits": 3,
            "total_processing_time_ms": 1000,
        }

        stats = BatchStats.from_dict(data)

        assert stats.total_products == 10
        assert stats.successful == 8
        assert stats.failed == 2
        assert stats.cache_hits == 3
        assert stats.success_rate == 80.0
        assert stats.avg_processing_time_ms == 125.0


class TestBatchProcessor:
    """Tests for BatchProcessor class."""

    @pytest.fixture
    def mock_analyzer(self):
        """Create a mock SEO analyzer."""
        analyzer = MagicMock(spec=SEOAnalyzer)
        analyzer.analyze_product = MagicMock(return_value=SEOReport(
            product_name="Test",
            overall_score=85,
            seo_metrics=SEOMetrics(
                title_score=90,
                meta_description_score=80,
                image_alt_score=85,
                content_length_score=85,
                keyword_density_score=85,
            ),
            issues=[],
            meta_tags=[],
            analysis_date=None,
            processing_time_ms=100,
        ))
        return analyzer

    @pytest.fixture
    def mock_cache(self):
        """Create a mock cache manager."""
        cache = MagicMock(spec=CacheManager)
        cache.get = MagicMock(return_value=None)
        cache.set = MagicMock(return_value=None)
        return cache

    def test_process_single_product(self, mock_analyzer, mock_cache):
        """Test processing a single product."""
        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        product = Product(name="Test Product", description="Test")
        results, stats = processor.process_single(product)

        assert len(results) == 1
        assert results[0].success is True
        assert results[0].product_name == "Test Product"
        assert stats.total_products == 1
        assert stats.successful == 1
        assert stats.failed == 0

    def test_process_single_product_with_cache_hit(self, mock_analyzer, mock_cache):
        """Test processing with cache hit."""
        mock_cache.get = MagicMock(return_value={
            "report": {
                "product_name": "Cached Product",
                "overall_score": 90,
                "seo_metrics": {
                    "title_score": 95,
                    "meta_description_score": 85,
                    "image_alt_score": 90,
                    "content_length_score": 90,
                    "keyword_density_score": 90,
                },
                "issues": [],
                "meta_tags": [],
                "analysis_date": "2024-01-01T00:00:00",
                "processing_time_ms": 50,
            },
            "processing_time_ms": 50,
        })

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        product = Product(name="Cached Product", description="Test")
        results, stats = processor.process_single(product)

        assert results[0].success is True
        assert results[0].cache_hit is True
        assert results[0].report.overall_score == 90
        assert stats.cache_hits == 1

    def test_process_single_product_failure(self, mock_analyzer, mock_cache):
        """Test processing with failure."""
        mock_analyzer.analyze_product = MagicMock(side_effect=Exception("Test error"))

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        product = Product(name="Error Product", description="Test")
        results, stats = processor.process_single(product)

        assert results[0].success is False
        assert results[0].error_message == "Test error"
        assert stats.failed == 1

    def test_process_batch(self, mock_analyzer, mock_cache):
        """Test processing multiple products."""
        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        products = [
            Product(name=f"Product {i}", description="Test")
            for i in range(5)
        ]

        results, stats = processor.process_batch(products)

        assert len(results) == 5
        assert stats.total_products == 5
        assert stats.successful == 5
        assert stats.failed == 0

    def test_process_batch_with_mixed_results(self, mock_analyzer, mock_cache):
        """Test processing with mixed success/failure."""
        call_count = [0]

        def analyze_side_effect(product):
            call_count[0] += 1
            if call_count[0] % 2 == 0:
                raise Exception("Error")
            return SEOReport(
                product_name=product.name,
                overall_score=85,
                seo_metrics=SEOMetrics(
                    title_score=90,
                    meta_description_score=80,
                    image_alt_score=85,
                    content_length_score=85,
                    keyword_density_score=85,
                ),
                issues=[],
                meta_tags=[],
                analysis_date=None,
                processing_time_ms=100,
            )

        mock_analyzer.analyze_product = MagicMock(side_effect=analyze_side_effect)

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        products = [
            Product(name=f"Product {i}", description="Test")
            for i in range(4)
        ]

        results, stats = processor.process_batch(products)

        assert len(results) == 4
        assert stats.successful == 2
        assert stats.failed == 2

    def test_process_from_json_file(self, mock_analyzer, mock_cache, tmp_path):
        """Test processing from JSON file."""
        # Create test input file
        input_file = tmp_path / "input.json"
        products = [
            {"name": "Product 1", "description": "Test"},
            {"name": "Product 2", "description": "Test"},
        ]
        input_file.write_text(json.dumps(products))

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        output_dir = tmp_path / "output"
        results, stats = processor.process_from_file(
            input_file=str(input_file),
            output_dir=str(output_dir),
            format="json",
        )

        assert len(results) == 2
        assert stats.total_products == 2
        assert stats.successful == 2
        assert output_dir.exists()

    def test_process_from_csv_file(self, mock_analyzer, mock_cache, tmp_path):
        """Test processing from CSV file."""
        import csv

        # Create test input file
        input_file = tmp_path / "input.csv"
        with open(input_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "description"])
            writer.writerow(["Product 1", "Test"])
            writer.writerow(["Product 2", "Test"])

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        output_dir = tmp_path / "output"
        results, stats = processor.process_from_file(
            input_file=str(input_file),
            output_dir=str(output_dir),
            format="csv",
        )

        assert len(results) == 2
        assert stats.total_products == 2

    def test_process_from_file_invalid_format(self, mock_analyzer, mock_cache, tmp_path):
        """Test processing with invalid file format."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("test")

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        with pytest.raises(ValueError, match="Unsupported file format"):
            processor.process_from_file(
                input_file=str(input_file),
                output_dir=str(tmp_path / "output"),
                format="txt",
            )

    def test_process_with_workers(self, mock_analyzer, mock_cache, tmp_path):
        """Test processing with multiple workers."""
        # Create test input file
        input_file = tmp_path / "input.json"
        products = [
            {"name": f"Product {i}", "description": "Test"}
            for i in range(10)
        ]
        input_file.write_text(json.dumps(products))

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
            max_workers=2,
        )

        output_dir = tmp_path / "output"
        results, stats = processor.process_from_file(
            input_file=str(input_file),
            output_dir=str(output_dir),
            format="json",
        )

        assert len(results) == 10
        assert stats.total_products == 10

    def test_process_with_cache_disabled(self, mock_analyzer, mock_cache, tmp_path):
        """Test processing with cache disabled."""
        # Create test input file
        input_file = tmp_path / "input.json"
        products = [
            {"name": "Product 1", "description": "Test"},
            {"name": "Product 1", "description": "Test"},  # Duplicate
        ]
        input_file.write_text(json.dumps(products))

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
            cache_enabled=False,
        )

        output_dir = tmp_path / "output"
        results, stats = processor.process_from_file(
            input_file=str(input_file),
            output_dir=str(output_dir),
            format="json",
        )

        # Should process both even though they're the same
        assert len(results) == 2
        assert stats.cache_hits == 0

    def test_process_from_file_with_output(self, mock_analyzer, mock_cache, tmp_path):
        """Test processing with output file generation."""
        # Create test input file
        input_file = tmp_path / "input.json"
        products = [
            {"name": "Product 1", "description": "Test"},
        ]
        input_file.write_text(json.dumps(products))

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        output_dir = tmp_path / "output"
        results, stats = processor.process_from_file(
            input_file=str(input_file),
            output_dir=str(output_dir),
            format="json",
        )

        # Check output files exist
        assert (output_dir / "results.json").exists()
        assert (output_dir / "stats.json").exists()

    def test_process_from_file_with_csv_output(self, mock_analyzer, mock_cache, tmp_path):
        """Test processing with CSV output."""
        # Create test input file
        input_file = tmp_path / "input.json"
        products = [
            {"name": "Product 1", "description": "Test"},
        ]
        input_file.write_text(json.dumps(products))

        processor = BatchProcessor(
            analyzer=mock_analyzer,
            cache=mock_cache,
        )

        output_dir = tmp_path / "output"
        results, stats = processor.process_from_file(
            input_file=str(input_file),
            output_dir=str(output_dir),
            format="json",
            output_format="csv",
        )

        # Check CSV output exists
        assert (output_dir / "results.csv").exists()
