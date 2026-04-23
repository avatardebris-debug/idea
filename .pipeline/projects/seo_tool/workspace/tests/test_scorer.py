"""Tests for seo_tool.scorer."""

from __future__ import annotations

import pytest

from seo_tool.models import SEOReport
from seo_tool.scorer import Scorer


def _make_report(**kwargs) -> SEOReport:
    """Helper to create an SEOReport with overrides."""
    defaults = {
        "url": "https://example.com",
        "title": "Perfect Title Here",
        "meta_description": "A perfect meta description that is exactly the right length for SEO purposes and should score full marks.",
        "headings": [(1, "H1"), (2, "H2"), (3, "H3")],
        "images": [
            type("Img", (), {"src": "a.jpg", "alt": "Alt"})(),
            type("Img", (), {"src": "b.jpg", "alt": "Alt2"})(),
        ],
        "internal_links": [type("Link", (), {"href": "/a"})(), type("Link", (), {"href": "/b"})()],
        "external_links": [type("Link", (), {"href": "https://other.com"})()],
        "link_count": 3,
        "word_count": 500,
        "og_tags": [
            type("OG", (), {"property": "og:title", "content": "T"})(),
            type("OG", (), {"property": "og:description", "content": "D"})(),
            type("OG", (), {"property": "og:image", "content": "I"})(),
        ],
        "canonical_link": "https://example.com/canonical",
    }
    defaults.update(kwargs)
    return SEOReport(**defaults)


# -- Total score --

class TestTotalScore:
    def test_perfect_score(self):
        report = _make_report()
        result = Scorer().score(report)
        assert result["total_score"] == 100

    def test_zero_score(self):
        report = SEOReport(url="https://example.com")
        result = Scorer().score(report)
        assert result["total_score"] == 0

    def test_score_capped_at_100(self):
        report = _make_report()
        result = Scorer().score(report)
        assert result["total_score"] <= 100


# -- Title scoring --

class TestTitleScoring:
    def test_perfect_title(self):
        report = _make_report(title="A title that is between 30 and 60 characters long for sure")
        result = Scorer().score(report)
        assert result["category_scores"]["title"]["score"] == 10

    def test_short_title(self):
        report = _make_report(title="Hi")
        result = Scorer().score(report)
        assert result["category_scores"]["title"]["score"] == 5

    def test_long_title(self):
        report = _make_report(title="A" * 100)
        result = Scorer().score(report)
        assert result["category_scores"]["title"]["score"] == 5

    def test_missing_title(self):
        report = _make_report(title=None)
        result = Scorer().score(report)
        assert result["category_scores"]["title"]["score"] == 0


# -- Meta description scoring --

class TestMetaDescriptionScoring:
    def test_perfect_meta_description(self):
        report = _make_report(meta_description="A" * 140)
        result = Scorer().score(report)
        assert result["category_scores"]["meta_description"]["score"] == 10

    def test_short_meta_description(self):
        report = _make_report(meta_description="Short")
        result = Scorer().score(report)
        assert result["category_scores"]["meta_description"]["score"] == 5

    def test_long_meta_description(self):
        report = _make_report(meta_description="A" * 200)
        result = Scorer().score(report)
        assert result["category_scores"]["meta_description"]["score"] == 5

    def test_missing_meta_description(self):
        report = _make_report(meta_description=None)
        result = Scorer().score(report)
        assert result["category_scores"]["meta_description"]["score"] == 0


# -- H1 scoring --

class TestH1Scoring:
    def test_single_h1(self):
        report = _make_report(headings=[(1, "H1")])
        result = Scorer().score(report)
        assert result["category_scores"]["h1_count"]["score"] == 15

    def test_no_h1(self):
        report = _make_report(headings=[(2, "H2")])
        result = Scorer().score(report)
        assert result["category_scores"]["h1_count"]["score"] == 0

    def test_multiple_h1(self):
        report = _make_report(headings=[(1, "H1"), (1, "H1b")])
        result = Scorer().score(report)
        assert result["category_scores"]["h1_count"]["score"] == 7


# -- Canonical scoring --

class TestCanonicalScoring:
    def test_canonical_present(self):
        report = _make_report(canonical_link="https://example.com/c")
        result = Scorer().score(report)
        assert result["category_scores"]["canonical"]["score"] == 10

    def test_no_canonical(self):
        report = _make_report(canonical_link=None)
        result = Scorer().score(report)
        assert result["category_scores"]["canonical"]["score"] == 0


# -- Content length scoring --

class TestContentLengthScoring:
    def test_good_content(self):
        report = _make_report(word_count=500)
        result = Scorer().score(report)
        assert result["category_scores"]["content_length"]["score"] == 30

    def test_medium_content(self):
        report = _make_report(word_count=200)
        result = Scorer().score(report)
        assert result["category_scores"]["content_length"]["score"] == 15

    def test_thin_content(self):
        report = _make_report(word_count=50)
        result = Scorer().score(report)
        assert result["category_scores"]["content_length"]["score"] == 0


# -- OG tags scoring --

class TestOgTagsScoring:
    def test_all_og_tags(self):
        report = _make_report(
            og_tags=[
                type("OG", (), {"property": "og:title", "content": "T"})(),
                type("OG", (), {"property": "og:description", "content": "D"})(),
                type("OG", (), {"property": "og:image", "content": "I"})(),
            ]
        )
        result = Scorer().score(report)
        assert result["category_scores"]["og_tags"]["score"] == 10

    def test_partial_og_tags(self):
        report = _make_report(
            og_tags=[
                type("OG", (), {"property": "og:title", "content": "T"})(),
            ]
        )
        result = Scorer().score(report)
        assert result["category_scores"]["og_tags"]["score"] == 4

    def test_no_og_tags(self):
        report = _make_report(og_tags=[])
        result = Scorer().score(report)
        assert result["category_scores"]["og_tags"]["score"] == 0


# -- Images scoring --

class TestImagesScoring:
    def test_all_images_have_alt(self):
        report = _make_report(
            images=[
                type("Img", (), {"src": "a.jpg", "alt": "A"})(),
                type("Img", (), {"src": "b.jpg", "alt": "B"})(),
            ]
        )
        result = Scorer().score(report)
        assert result["category_scores"]["images"]["score"] == 5

    def test_some_images_no_alt(self):
        report = _make_report(
            images=[
                type("Img", (), {"src": "a.jpg", "alt": "A"})(),
                type("Img", (), {"src": "b.jpg", "alt": None})(),
            ]
        )
        result = Scorer().score(report)
        assert result["category_scores"]["images"]["score"] == 4

    def test_no_images(self):
        report = _make_report(images=[])
        result = Scorer().score(report)
        assert result["category_scores"]["images"]["score"] == 0


# -- Links scoring --

class TestLinksScoring:
    def test_good_links(self):
        report = _make_report(
            internal_links=[type("Link", (), {"href": "/a"})()],
            external_links=[type("Link", (), {"href": "https://other.com"})()],
            link_count=2,
        )
        result = Scorer().score(report)
        assert result["category_scores"]["links"]["score"] == 5

    def test_no_links(self):
        report = _make_report(internal_links=[], external_links=[], link_count=0)
        result = Scorer().score(report)
        assert result["category_scores"]["links"]["score"] == 0


# -- Headings scoring --

class TestHeadingsScoring:
    def test_good_headings(self):
        report = _make_report(headings=[(1, "H1"), (2, "H2"), (3, "H3")])
        result = Scorer().score(report)
        assert result["category_scores"]["headings"]["score"] == 5

    def test_no_headings(self):
        report = _make_report(headings=[])
        result = Scorer().score(report)
        assert result["category_scores"]["headings"]["score"] == 0
