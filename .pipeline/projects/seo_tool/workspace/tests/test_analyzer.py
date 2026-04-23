"""Tests for seo_tool.analyzer."""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pytest
import requests

from seo_tool.analyzer import Analyzer, AnalyzerError
from seo_tool.models import SEOReport


# -- Fixtures --

GOOD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>My Page Title - Perfect Length</title>
    <meta name="description" content="This is a well-written meta description that is just the right length for SEO purposes.">
    <meta name="keywords" content="seo, test, example">
    <link rel="canonical" href="https://example.com/page">
    <meta property="og:title" content="OG Title">
    <meta property="og:description" content="OG Description">
    <meta property="og:image" content="https://example.com/image.jpg">
</head>
<body>
    <h1>Main Heading</h1>
    <h2>Sub Heading</h2>
    <h3>Sub Sub Heading</h3>
    <p>This is some paragraph text with enough words to pass the content length check. We need at least 300 words for a good score so here are more words to pad things out. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
    <img src="photo.jpg" alt="A descriptive alt text">
    <img src="no-alt.jpg">
    <a href="/internal-page">Internal Link</a>
    <a href="https://external.com/page">External Link</a>
    <a href="https://example.com/same-domain">Same Domain</a>
    <a href="/another-internal">Another Internal</a>
</body>
</html>
"""

MINIMAL_HTML = """
<html><head><title>Short</title></head><body><p>Hi</p></body></html>
"""

EMPTY_HTML = "<html><head></head><body></body></html>"


# -- fetch_and_parse --

class TestFetchAndParse:
    @patch("seo_tool.analyzer.requests.get")
    def test_successful_fetch(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = GOOD_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        report = Analyzer().fetch_and_parse("https://example.com")

        assert report.url == "https://example.com"
        assert report.http_status == 200
        assert report.fetch_error is None

    @patch("seo_tool.analyzer.requests.get")
    def test_http_error_raises(self, mock_get):
        mock_get.side_effect = requests.HTTPError("404 Not Found")
        mock_get.side_effect.response = MagicMock(status_code=404)

        with pytest.raises(AnalyzerError, match="Failed to fetch"):
            Analyzer().fetch_and_parse("https://example.com")

    @patch("seo_tool.analyzer.requests.get")
    def test_connection_error_raises(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("DNS failed")

        with pytest.raises(AnalyzerError, match="Failed to fetch"):
            Analyzer().fetch_and_parse("https://example.com")


# -- Title --

class TestTitle:
    @patch("seo_tool.analyzer.requests.get")
    def test_title_extracted(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            text='<html><head><title>My Title</title></head><body></body></html>',
        )
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.title == "My Title"

    @patch("seo_tool.analyzer.requests.get")
    def test_missing_title(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            text=EMPTY_HTML,
        )
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.title is None


# -- Meta description --

class TestMetaDescription:
    @patch("seo_tool.analyzer.requests.get")
    def test_meta_description_extracted(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            text='<html><head><meta name="description" content="A description"></head><body></body></html>',
        )
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.meta_description == "A description"

    @patch("seo_tool.analyzer.requests.get")
    def test_missing_meta_description(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            text=EMPTY_HTML,
        )
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.meta_description is None


# -- Meta keywords --

class TestMetaKeywords:
    @patch("seo_tool.analyzer.requests.get")
    def test_meta_keywords_extracted(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            text='<html><head><meta name="keywords" content="a, b, c"></head><body></body></html>',
        )
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.meta_keywords == "a, b, c"


# -- Headings --

class TestHeadings:
    @patch("seo_tool.analyzer.requests.get")
    def test_headings_extracted(self, mock_get):
        html = '<html><body><h1>H1</h1><h2>H2</h2><h6>H6</h6></body></html>'
        mock_get.return_value = MagicMock(status_code=200, text=html)
        report = Analyzer().fetch_and_parse("https://example.com")
        levels_texts = [(h[0], h[1]) for h in report.headings]
        assert (1, "H1") in levels_texts
        assert (2, "H2") in levels_texts
        assert (6, "H6") in levels_texts

    @patch("seo_tool.analyzer.requests.get")
    def test_no_headings(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, text=EMPTY_HTML)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.headings == []


# -- Images --

class TestImages:
    @patch("seo_tool.analyzer.requests.get")
    def test_images_with_alt(self, mock_get):
        html = '<html><body><img src="a.jpg" alt="Alt A"><img src="b.jpg"></body></html>'
        mock_get.return_value = MagicMock(status_code=200, text=html)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert len(report.images) == 2
        assert report.images[0].alt == "Alt A"
        assert report.images[1].alt is None

    @patch("seo_tool.analyzer.requests.get")
    def test_no_images(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, text=EMPTY_HTML)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.images == []


# -- Canonical --

class TestCanonical:
    @patch("seo_tool.analyzer.requests.get")
    def test_canonical_extracted(self, mock_get):
        html = '<html><head><link rel="canonical" href="https://example.com/canonical"></head><body></body></html>'
        mock_get.return_value = MagicMock(status_code=200, text=html)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.canonical_link == "https://example.com/canonical"

    @patch("seo_tool.analyzer.requests.get")
    def test_no_canonical(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, text=EMPTY_HTML)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.canonical_link is None


# -- OG tags --

class TestOgTags:
    @patch("seo_tool.analyzer.requests.get")
    def test_og_tags_extracted(self, mock_get):
        html = (
            '<html><head>'
            '<meta property="og:title" content="OG Title">'
            '<meta property="og:image" content="https://example.com/img.jpg">'
            '</head><body></body></html>'
        )
        mock_get.return_value = MagicMock(status_code=200, text=html)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert len(report.og_tags) == 2
        props = {t.property for t in report.og_tags}
        assert "og:title" in props
        assert "og:image" in props

    @patch("seo_tool.analyzer.requests.get")
    def test_no_og_tags(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, text=EMPTY_HTML)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.og_tags == []


# -- Links --

class TestLinks:
    @patch("seo_tool.analyzer.requests.get")
    def test_internal_external_links(self, mock_get):
        html = (
            '<html><body>'
            '<a href="/internal">Int</a>'
            '<a href="https://other.com/ext">Ext</a>'
            '<a href="https://example.com/same">Same</a>'
            '</body></html>'
        )
        mock_get.return_value = MagicMock(status_code=200, text=html)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert len(report.internal_links) == 2
        assert len(report.external_links) == 1
        assert report.link_count == 3

    @patch("seo_tool.analyzer.requests.get")
    def test_no_links(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, text=EMPTY_HTML)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.link_count == 0


# -- Word count --

class TestWordCount:
    @patch("seo_tool.analyzer.requests.get")
    def test_word_count(self, mock_get):
        html = '<html><body><p>Hello world this is a test</p></body></html>'
        mock_get.return_value = MagicMock(status_code=200, text=html)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.word_count == 6

    @patch("seo_tool.analyzer.requests.get")
    def test_empty_word_count(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, text=EMPTY_HTML)
        report = Analyzer().fetch_and_parse("https://example.com")
        assert report.word_count == 0


# -- SEOReport model --

class TestSEOReport:
    def test_default_values(self):
        report = SEOReport()
        assert report.title is None
        assert report.meta_description is None
        assert report.headings == []
        assert report.images == []
        assert report.link_count == 0

    def test_url_set(self):
        report = SEOReport(url="https://example.com")
        assert report.url == "https://example.com"
