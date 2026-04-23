"""CLI entry point for dropship-seo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from dropship_seo.analyzer import Analyzer
from dropship_seo.config import default_config
from dropship_seo.meta_generator import MetaGenerator
from dropship_seo.models import Product


# ── Helpers ────────────────────────────────────────────────────────────────

def _load_product_from_json(ctx: click.Context, param: click.Option, value: str | None) -> Product:
    """Parse --json argument into a Product."""
    if value is None:
        ctx.fail("--json is required. Provide a JSON string with product data.")
    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        ctx.fail(f"Invalid JSON: {exc}")
    try:
        return Product.from_dict(data)
    except (ValueError, TypeError) as exc:
        ctx.fail(f"Product validation error: {exc}")


def _write_output(data: str, output_file: str | None) -> None:
    """Write output to file or stdout."""
    if output_file:
        Path(output_file).write_text(data, encoding="utf-8")
        click.echo(f"Output written to {output_file}")
    else:
        click.echo(data)


# ── CLI group ────────────────────────────────────────────────────────────────

@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """dropship-seo — Auto-generate SEO metadata for dropshipping products."""
    pass


# ── analyze subcommand ───────────────────────────────────────────────────────

@cli.command()
@click.option("--json", "product_json", required=True, help="Product data as JSON string.")
@click.option("--output-file", "output_file", default=None, help="Write output to file instead of stdout.")
def analyze(product_json: str, output_file: str | None) -> None:
    """Analyze a product's SEO readiness and return a scored report."""
    product = _load_product_from_json(click.get_current_context(), None, product_json)
    analyzer = Analyzer(default_config())
    report = analyzer.analyze(product)
    output = report.to_json()
    _write_output(output, output_file)


# ── generate subcommand ──────────────────────────────────────────────────────

@cli.command()
@click.option("--json", "product_json", required=True, help="Product data as JSON string.")
@click.option("--output-file", "output_file", default=None, help="Write output to file instead of stdout.")
def generate(product_json: str, output_file: str | None) -> None:
    """Generate SEO metadata from product data."""
    product = _load_product_from_json(click.get_current_context(), None, product_json)
    generator = MetaGenerator(default_config())
    metadata = generator.generate(product)
    # Convert MetaTag objects to dicts for JSON serialization
    serializable_metadata = {
        key: [tag.to_dict() for tag in value] if isinstance(value, list) else value
        for key, value in metadata.items()
    }
    output = json.dumps(serializable_metadata, indent=2, ensure_ascii=False)
    _write_output(output, output_file)


# ── list-templates subcommand ─────────────────────────────────────────────────

@cli.command(name="list-templates")
@click.option("--output-file", "output_file", default=None, help="Write output to file instead of stdout.")
def list_templates(output_file: str | None) -> None:
    """List available title and description templates."""
    generator = MetaGenerator(default_config())
    templates = generator.list_templates()
    output = json.dumps(templates, indent=2, ensure_ascii=False)
    _write_output(output, output_file)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
