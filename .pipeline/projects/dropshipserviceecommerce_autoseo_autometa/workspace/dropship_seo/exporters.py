"""Export functionality for SEO analysis results."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
from datetime import datetime

from dropship_seo.models import Product, SEOReport, Issue, MetaTag, MetaTagType
from dropship_seo.batch_processor import BatchResult, BatchStats


class Exporter:
    """Export SEO analysis results to various formats."""

    @staticmethod
    def to_json(data: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
        """Convert data to JSON string.

        Args:
            data: Data to serialize.
            indent: Indentation level.
            ensure_ascii: Whether to escape non-ASCII characters.

        Returns:
            JSON string.
        """
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)

    @staticmethod
    def from_json(json_str: str) -> Any:
        """Parse JSON string to Python object.

        Args:
            json_str: JSON string to parse.

        Returns:
            Parsed Python object.
        """
        return json.loads(json_str)

    @staticmethod
    def export_report_to_json(report: SEOReport, indent: int = 2) -> str:
        """Export a single SEO report to JSON.

        Args:
            report: SEO report to export.
            indent: Indentation level.

        Returns:
            JSON string.
        """
        return json.dumps(report.to_dict(), indent=indent, ensure_ascii=False)

    @staticmethod
    def export_reports_to_json(reports: list[SEOReport], indent: int = 2) -> str:
        """Export multiple SEO reports to JSON.

        Args:
            reports: List of SEO reports to export.
            indent: Indentation level.

        Returns:
            JSON string.
        """
        return json.dumps(
            [report.to_dict() for report in reports],
            indent=indent,
            ensure_ascii=False,
        )

    @staticmethod
    def export_batch_results_to_json(results: list[BatchResult], indent: int = 2) -> str:
        """Export batch results to JSON.

        Args:
            results: List of batch results to export.
            indent: Indentation level.

        Returns:
            JSON string.
        """
        return json.dumps(
            [result.to_dict() for result in results],
            indent=indent,
            ensure_ascii=False,
        )

    @staticmethod
    def export_batch_stats_to_json(stats: BatchStats, indent: int = 2) -> str:
        """Export batch statistics to JSON.

        Args:
            stats: Batch statistics to export.
            indent: Indentation level.

        Returns:
            JSON string.
        """
        return json.dumps(stats.to_dict(), indent=indent, ensure_ascii=False)

    @staticmethod
    def export_report_to_csv(report: SEOReport, output_file: str | Path) -> None:
        """Export a single SEO report to CSV.

        Args:
            report: SEO report to export.
            output_file: Path to output CSV file.
        """
        output_path = Path(output_file)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Field", "Value"])

            # Basic info
            writer.writerow(["Product Name", report.product_name])
            writer.writerow(["Overall Score", report.overall_score])
            writer.writerow(["Analysis Date", report.analysis_date.isoformat()])
            writer.writerow(["Processing Time (ms)", report.processing_time_ms])

            # SEO metrics
            writer.writerow(["--- SEO Metrics ---"])
            writer.writerow(["Title Score", report.seo_metrics.title_score])
            writer.writerow(["Meta Description Score", report.seo_metrics.meta_description_score])
            writer.writerow(["Image Alt Score", report.seo_metrics.image_alt_score])
            writer.writerow(["Content Length Score", report.seo_metrics.content_length_score])
            writer.writerow(["Keyword Density Score", report.seo_metrics.keyword_density_score])

            # Issues
            writer.writerow(["--- Issues ---"])
            for issue in report.issues:
                writer.writerow([
                    f"Issue: {issue.category}",
                    f"{issue.severity}: {issue.message}",
                ])

            # Meta tags
            writer.writerow(["--- Meta Tags ---"])
            for tag in report.meta_tags:
                writer.writerow([
                    f"Tag: {tag.name}",
                    f"Type: {tag.tag_type.value}, Content: {tag.content}",
                ])

    @staticmethod
    def export_reports_to_csv(reports: list[SEOReport], output_file: str | Path) -> None:
        """Export multiple SEO reports to CSV.

        Args:
            reports: List of SEO reports to export.
            output_file: Path to output CSV file.
        """
        output_path = Path(output_file)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                "Product Name",
                "Overall Score",
                "Title Score",
                "Meta Description Score",
                "Image Alt Score",
                "Content Length Score",
                "Keyword Density Score",
                "Issue Count",
                "Meta Tag Count",
                "Analysis Date",
            ])

            for report in reports:
                writer.writerow([
                    report.product_name,
                    report.overall_score,
                    report.seo_metrics.title_score,
                    report.seo_metrics.meta_description_score,
                    report.seo_metrics.image_alt_score,
                    report.seo_metrics.content_length_score,
                    report.seo_metrics.keyword_density_score,
                    len(report.issues),
                    len(report.meta_tags),
                    report.analysis_date.isoformat(),
                ])

    @staticmethod
    def export_batch_results_to_csv(
        results: list[BatchResult],
        output_file: str | Path,
    ) -> None:
        """Export batch results to CSV.

        Args:
            results: List of batch results to export.
            output_file: Path to output CSV file.
        """
        output_path = Path(output_file)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                "Product Name",
                "Success",
                "Overall Score",
                "Processing Time (ms)",
                "Cache Hit",
                "Error Message",
            ])

            for result in results:
                writer.writerow([
                    result.product_name,
                    result.success,
                    result.report.overall_score if result.report else None,
                    result.processing_time_ms,
                    result.cache_hit,
                    result.error_message,
                ])

    @staticmethod
    def export_batch_stats_to_csv(stats: BatchStats, output_file: str | Path) -> None:
        """Export batch statistics to CSV.

        Args:
            stats: Batch statistics to export.
            output_file: Path to output CSV file.
        """
        output_path = Path(output_file)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Metric", "Value"])

            # Statistics
            writer.writerow(["Total Products", stats.total_products])
            writer.writerow(["Successful", stats.successful])
            writer.writerow(["Failed", stats.failed])
            writer.writerow(["Cache Hits", stats.cache_hits])
            writer.writerow(["Success Rate (%)", stats.success_rate])
            writer.writerow(["Total Processing Time (ms)", stats.total_processing_time_ms])
            writer.writerow(["Average Processing Time (ms)", stats.avg_processing_time_ms])

    @staticmethod
    def export_to_parquet(
        reports: list[SEOReport],
        output_file: str | Path,
    ) -> None:
        """Export reports to Parquet format.

        Args:
            reports: List of SEO reports to export.
            output_file: Path to output Parquet file.

        Note:
            Requires 'pyarrow' or 'fastparquet' package.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Parquet export requires pandas. Install with: pip install pandas"
            )

        # Convert reports to list of dictionaries
        data = [report.to_dict() for report in reports]

        # Create DataFrame
        df = pd.DataFrame(data)

        # Save to Parquet
        df.to_parquet(output_file, index=False)

    @staticmethod
    def export_to_html(
        reports: list[SEOReport],
        output_file: str | Path,
        title: str = "SEO Analysis Report",
    ) -> None:
        """Export reports to HTML report.

        Args:
            reports: List of SEO reports to export.
            output_file: Path to output HTML file.
            title: Report title.
        """
        output_path = Path(output_file)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .report {{
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .report-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .score {{
            font-size: 24px;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 4px;
            color: white;
        }}
        .score-excellent {{ background-color: #28a745; }}
        .score-good {{ background-color: #17a2b8; }}
        .score-fair {{ background-color: #ffc107; color: #333; }}
        .score-poor {{ background-color: #dc3545; }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 10px 0;
        }}
        .metric {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            text-align: center;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        .issues {{
            margin-top: 10px;
        }}
        .issue {{
            padding: 8px;
            margin: 5px 0;
            border-radius: 4px;
            border-left: 4px solid;
        }}
        .issue-critical {{ background-color: #f8d7da; border-color: #dc3545; }}
        .issue-warning {{ background-color: #fff3cd; border-color: #ffc107; }}
        .issue-info {{ background-color: #d1ecf1; border-color: #17a2b8; }}
        .meta-tags {{
            margin-top: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }}
        .meta-tag {{
            margin: 5px 0;
            padding: 5px;
            background-color: white;
            border-radius: 3px;
        }}
        .timestamp {{
            color: #666;
            font-size: 12px;
            margin-top: 20px;
            border-top: 1px solid #ddd;
            padding-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        {''.join([Exporter._render_report_html(report) for report in reports])}

        <div class="timestamp">
            Total reports: {len(reports)}
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    @staticmethod
    def _render_report_html(report: SEOReport) -> str:
        """Render a single report as HTML.

        Args:
            report: SEO report to render.

        Returns:
            HTML string.
        """
        # Determine score color
        if report.overall_score >= 80:
            score_class = "score-excellent"
        elif report.overall_score >= 60:
            score_class = "score-good"
        elif report.overall_score >= 40:
            score_class = "score-fair"
        else:
            score_class = "score-poor"

        # Render issues
        issues_html = ""
        for issue in report.issues:
            issue_class = f"issue-{issue.severity}"
            issues_html += f"""
            <div class="issue {issue_class}">
                <strong>{issue.severity.upper()}</strong>: {issue.message}
                <br><small>Suggestion: {issue.suggestion}</small>
            </div>"""

        # Render meta tags
        meta_tags_html = ""
        for tag in report.meta_tags:
            meta_tags_html += f"""
            <div class="meta-tag">
                <strong>{tag.name}</strong> ({tag.tag_type.value}): {tag.content}
            </div>"""

        return f"""
        <div class="report">
            <div class="report-header">
                <h2>{report.product_name}</h2>
                <div class="score {score_class}">{report.overall_score}</div>
            </div>

            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Title</div>
                    <div class="metric-value">{report.seo_metrics.title_score}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Meta Description</div>
                    <div class="metric-value">{report.seo_metrics.meta_description_score}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Image Alt</div>
                    <div class="metric-value">{report.seo_metrics.image_alt_score}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Content Length</div>
                    <div class="metric-value">{report.seo_metrics.content_length_score}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Keyword Density</div>
                    <div class="metric-value">{report.seo_metrics.keyword_density_score}</div>
                </div>
            </div>

            {'<div class="issues">' + issues_html + '</div>' if issues_html else ''}
            {'<div class="meta-tags">' + meta_tags_html + '</div>' if meta_tags_html else ''}
        </div>"""

    @staticmethod
    def export_to_yaml(reports: list[SEOReport], output_file: str | Path) -> None:
        """Export reports to YAML format.

        Args:
            reports: List of SEO reports to export.
            output_file: Path to output YAML file.

        Note:
            Requires 'pyyaml' package.
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "YAML export requires pyyaml. Install with: pip install pyyaml"
            )

        data = [report.to_dict() for report in reports]

        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
