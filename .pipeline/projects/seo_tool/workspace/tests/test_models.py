"""Tests for seo_tool.models."""

from __future__ import annotations

import pytest

from seo_tool.models import (
    ImageInfo,
    LinkInfo,
    MetaTag,
    OpenGraphTag,
    SEOReport,
)


# -- SEOReport --

class TestSEOReport:
    def test_default_values(self):
        report = SEOReport()
        assert report.url is None
        assert report.title is None
        assert report.meta_description is None
        assert report.meta_keywords is None
        assert report.canonical_link is None
        assert report.fetch_error is None
        assert report.http_status is None
        assert report.word_count == 0
        assert report.link_count == 0
        assert report.headings == []
        assert report.images == []
        assert report.meta_tags == []
        assert report.og_tags == []
        assert report.internal_links == []
        assert report.external_links == []

    def test_url_set(self):
        report = SEOReport(url="https://example.com")
        assert report.url == "https://example.com"

    def test_http_status_set(self):
        report = SEOReport()
        report.http_status = 404
        assert report.http_status == 404

    def test_fetch_error_set(self):
        report = SEOReport()
        report.fetch_error = "DNS failed"
        assert report.fetch_error == "DNS failed"

    def test_append_meta_tag(self):
        report = SEOReport()
        report.meta_tags.append(MetaTag(name="description", content="Desc"))
        assert len(report.meta_tags) == 1
        assert report.meta_tags[0].name == "description"

    def test_append_image(self):
        report = SEOReport()
        report.images.append(ImageInfo(src="a.jpg", alt="Alt"))
        assert len(report.images) == 1
        assert report.images[0].src == "a.jpg"

    def test_append_heading(self):
        report = SEOReport()
        report.headings.append((1, "H1"))
        assert len(report.headings) == 1
        assert report.headings[0] == (1, "H1")

    def test_append_og_tag(self):
        report = SEOReport()
        report.og_tags.append(OpenGraphTag(property="og:title", content="T"))
        assert len(report.og_tags) == 1
        assert report.og_tags[0].property == "og:title"

    def test_append_link(self):
        report = SEOReport()
        report.internal_links.append(LinkInfo(href="/a", text="A", is_internal=True))
        assert len(report.internal_links) == 1
        assert report.internal_links[0].href == "/a"

    def test_word_count_set(self):
        report = SEOReport()
        report.word_count = 42
        assert report.word_count == 42

    def test_link_count_set(self):
        report = SEOReport()
        report.link_count = 10
        assert report.link_count == 10


# -- MetaTag --

class TestMetaTag:
    def test_creation(self):
        tag = MetaTag(name="description", content="Desc")
        assert tag.name == "description"
        assert tag.content == "Desc"

    def test_default_content(self):
        tag = MetaTag(name="description")
        assert tag.content is None


# -- OpenGraphTag --

class TestOpenGraphTag:
    def test_creation(self):
        tag = OpenGraphTag(property="og:title", content="T")
        assert tag.property == "og:title"
        assert tag.content == "T"

    def test_default_content(self):
        tag = OpenGraphTag(property="og:title")
        assert tag.content is None


# -- ImageInfo --

class TestImageInfo:
    def test_creation(self):
        img = ImageInfo(src="a.jpg", alt="Alt")
        assert img.src == "a.jpg"
        assert img.alt == "Alt"

    def test_default_alt(self):
        img = ImageInfo(src="a.jpg")
        assert img.alt is None


# -- LinkInfo --

class TestLinkInfo:
    def test_creation(self):
        link = LinkInfo(href="/a", text="A", is_internal=True)
        assert link.href == "/a"
        assert link.text == "A"
        assert link.is_internal is True

    def test_default_is_internal(self):
        link = LinkInfo(href="/a", text="A")
        assert link.is_internal is False
