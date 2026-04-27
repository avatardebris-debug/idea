"""Batch processing for SEO analysis of multiple products."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator
from datetime import datetime

from tqdm import tqdm

from dropship_seo.analyzer import Analyzer
from dropship_seo.config import Config, default_config
from dropship_seo.caching import SEOCache, get_cache
from dropship_seo.models import Product, SEOReport


@dataclass
class BatchResult:
    """Result of a single product analysis in a batch."""

    product_name: str
    success: bool
    report: SEOReport | None = None
    error_message: str | None = None
    processing_time_ms: float | None = None
    cache_hit: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "product_name": self.product_name,
            "success": self.success,
            "report": self.report.to_dict() if self.report else None,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "cache_hit": self.cache_hit,
        }


@dataclass
class BatchStats:
    """Statistics for a batch processing run."""

    total_products: int = 0
    successful: int = 0
    failed: int = 0
    cache_hits: int = 0
    total_processing_time_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_products == 0:
            return 0.0
        return (self.successful / self.total_products) * 100

    @property
    def avg_processing_time_ms(self) -> float:
        """Calculate average processing time."""
        if self.successful == 0:
            return 0.0
        return self.total_processing_time_ms / self.successful

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_products": self.total_products,
            "successful": self.successful,
            "failed": self.failed,
            "cache_hits": self.cache_hits,
            "success_rate": round(self.success_rate, 2),
            "total_processing_time_ms": round(self.total_processing_time_ms, 2),
            "avg_processing_time_ms": round(self.avg_processing_time_ms, 2),
        }


@dataclass
class BatchConfig:
    """Configuration for batch processing."""

    max_workers: int = 4
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    progress_bar: bool = True
    progress_bar_desc: str = "Processing products"
    on_progress: Callable[[BatchResult, int, int], None] | None = None
    cache_dir: str | Path = ".seo_cache"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_workers": self.max_workers,
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "progress_bar": self.progress_bar,
            "progress_bar_desc": self.progress_bar_desc,
            "cache_dir": str(self.cache_dir),
        }


class BatchProcessor:
    """Process multiple products in batch with caching and progress tracking."""

    def __init__(
        self,
        config: Config | None = None,
        batch_config: BatchConfig | None = None,
    ):
        """Initialize the batch processor.

        Args:
            config: SEO analysis configuration.
            batch_config: Batch processing configuration.
        """
        self.config = config or default_config()
        self.batch_config = batch_config or BatchConfig()
        self.analyzer = Analyzer(self.config)

        if self.batch_config.cache_enabled:
            self.cache = get_cache(
                cache_dir=self.batch_config.cache_dir,
                default_ttl_seconds=self.batch_config.cache_ttl_seconds,
            )
        else:
            self.cache = None

    def _process_single_product(
        self,
        product: Product,
        use_cache: bool,
    ) -> BatchResult:
        """Process a single product.

        Args:
            product: The product to analyze.
            use_cache: Whether to use caching.

        Returns:
            BatchResult with the analysis result.
        """
        start_time = datetime.now()

        try:
            # Try to get from cache
            if use_cache and self.cache:
                cached_result = self.cache.get(product, operation="analyze")
                if cached_result is not None:
                    processing_time = (datetime.now() - start_time).total_seconds() * 1000
                    return BatchResult(
                        product_name=product.name,
                        success=True,
                        report=cached_result,
                        processing_time_ms=processing_time,
                        cache_hit=True,
                    )

            # Perform analysis
            report = self.analyzer.analyze_product(product)
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            # Cache the result
            if use_cache and self.cache:
                self.cache.set(product, report, operation="analyze")

            return BatchResult(
                product_name=product.name,
                success=True,
                report=report,
                processing_time_ms=processing_time,
                cache_hit=False,
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            return BatchResult(
                product_name=product.name,
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time,
            )

    def process_batch(
        self,
        products: list[Product],
        output_dir: str | Path | None = None,
    ) -> tuple[list[BatchResult], BatchStats]:
        """Process a batch of products.

        Args:
            products: List of products to analyze.
            output_dir: Directory to save results (optional).

        Returns:
            Tuple of (results list, statistics).
        """
        if not products:
            return [], BatchStats()

        results: list[BatchResult] = []
        stats = BatchStats(total_products=len(products))

        def process_product(product: Product) -> BatchResult:
            """Process a single product and update stats."""
            result = self._process_single_product(
                product,
                use_cache=self.batch_config.cache_enabled,
            )

            if result.success:
                stats.successful += 1
                stats.total_processing_time_ms += result.processing_time_ms or 0
                if result.cache_hit:
                    stats.cache_hits += 1
            else:
                stats.failed += 1

            return result

        # Process with progress bar
        if self.batch_config.progress_bar:
            with ThreadPoolExecutor(max_workers=self.batch_config.max_workers) as executor:
                futures = {
                    executor.submit(process_product, product): i
                    for i, product in enumerate(products)
                }

                with tqdm(
                    total=len(products),
                    desc=self.batch_config.progress_bar_desc,
                    unit="product",
                ) as pbar:
                    for future in as_completed(futures):
                        result = future.result()
                        results.append(result)
                        pbar.update(1)

                        # Call progress callback if provided
                        if self.batch_config.on_progress:
                            idx = futures[future]
                            self.batch_config.on_progress(result, idx + 1, len(products))

                        # Update progress bar with stats
                        pbar.set_postfix(
                            {
                                "success": stats.successful,
                                "failed": stats.failed,
                                "cache_hits": stats.cache_hits,
                            }
                        )
        else:
            with ThreadPoolExecutor(max_workers=self.batch_config.max_workers) as executor:
                futures = [
                    executor.submit(process_product, product)
                    for product in products
                ]

                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)

        # Save results if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Save individual results
            results_file = output_path / "batch_results.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(
                    [result.to_dict() for result in results],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Save statistics
            stats_file = output_path / "batch_stats.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats.to_dict(), f, indent=2, ensure_ascii=False)

        return results, stats

    def process_from_file(
        self,
        input_file: str | Path,
        output_dir: str | Path | None = None,
        format: str = "json",
    ) -> tuple[list[BatchResult], BatchStats]:
        """Process products from a file.

        Args:
            input_file: Path to input file (JSON or CSV).
            output_dir: Directory to save results.
            format: Input file format ("json" or "csv").

        Returns:
            Tuple of (results list, statistics).
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Load products from file
        if format == "json":
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                products = [Product(**item) if isinstance(item, dict) else item for item in data]
            elif isinstance(data, dict) and "products" in data:
                products = [Product(**item) if isinstance(item, dict) else item for item in data["products"]]
            else:
                raise ValueError("Invalid JSON format. Expected list of products or object with 'products' key.")

        elif format == "csv":
            import csv

            products = []
            with open(input_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string fields to appropriate types
                    product_data = {
                        "name": row.get("name", ""),
                        "description": row.get("description", ""),
                        "category": row.get("category", ""),
                        "price": float(row.get("price", 0)),
                        "target_keywords": row.get("target_keywords", "").split(",") if row.get("target_keywords") else [],
                        "images": row.get("images", "[]"),
                        "brand": row.get("brand", ""),
                        "sku": row.get("sku", ""),
                    }
                    # Parse images JSON
                    if product_data["images"]:
                        try:
                            product_data["images"] = json.loads(product_data["images"])
                        except json.JSONDecodeError:
                            product_data["images"] = []
                    products.append(Product(**product_data))
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'.")

        return self.process_batch(products, output_dir)

    def process_stream(
        self,
        products: Iterator[Product],
        output_dir: str | Path | None = None,
        batch_size: int = 10,
    ) -> tuple[list[BatchResult], BatchStats]:
        """Process products from a stream with batching.

        Args:
            products: Iterator of products to analyze.
            output_dir: Directory to save results.
            batch_size: Number of products to process at once.

        Returns:
            Tuple of (results list, statistics).
        """
        all_results: list[BatchResult] = []
        stats = BatchStats()

        batch: list[Product] = []

        for product in products:
            batch.append(product)

            if len(batch) >= batch_size:
                results, batch_stats = self.process_batch(batch, output_dir)
                all_results.extend(results)
                stats.successful += batch_stats.successful
                stats.failed += batch_stats.failed
                stats.cache_hits += batch_stats.cache_hits
                stats.total_processing_time_ms += batch_stats.total_processing_time_ms
                batch = []

        # Process remaining products
        if batch:
            results, batch_stats = self.process_batch(batch, output_dir)
            all_results.extend(results)
            stats.successful += batch_stats.successful
            stats.failed += batch_stats.failed
            stats.cache_hits += batch_stats.cache_hits
            stats.total_processing_time_ms += batch_stats.total_processing_time_ms

        stats.total_products = stats.successful + stats.failed

        return all_results, stats
