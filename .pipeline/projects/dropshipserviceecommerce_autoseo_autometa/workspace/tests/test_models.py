"""Tests for data models."""

import pytest
from dropship_seo.models import (
    Product,
    SEOReport,
    MetaTag,
    MetaTagType,
    Issue,
)


class TestProduct:
    """Tests for Product dataclass."""

    def test_product_creation_valid(self):
        """Test valid product creation."""
        product = Product(
            name="Test Product",
            description="A great product",
            category="Electronics",
            price=99.99,
            target_keywords=["keyword1", "keyword2"],
            images=[{"url": "https://example.com/img.jpg", "alt": "Test image"}],
            brand="TestBrand",
            sku="SKU-001",
        )
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.brand == "TestBrand"
        assert product.sku == "SKU-001"

    def test_product_creation_minimal(self):
        """Test product creation with minimal required fields."""
        product = Product(
            name="Minimal Product",
            description="Description",
            category="Test",
            price=0,
            target_keywords=[],
            images=[],
        )
        assert product.name == "Minimal Product"
        assert product.brand is None
        assert product.sku is None

    def test_product_from_dict(self):
        """Test Product.from_dict() method."""
        data = {
            "name": "From Dict Product",
            "description": "Test description",
            "category": "Books",
            "price": 29.99,
            "target_keywords": ["book", "reading"],
            "images": [{"url": "https://example.com/book.jpg", "alt": "Book cover"}],
            "brand": "BookPublisher",
            "sku": "BOOK-001",
        }
        product = Product.from_dict(data)
        assert product.name == "From Dict Product"
        assert product.price == 29.99
        assert product.brand == "BookPublisher"

    def test_product_from_dict_missing_optional_fields(self):
        """Test Product.from_dict() with missing optional fields."""
        data = {
            "name": "No Brand Product",
            "description": "Description",
            "category": "Toys",
            "price": 19.99,
            "target_keywords": ["toy"],
            "images": [],
        }
        product = Product.from_dict(data)
        assert product.name == "No Brand Product"
        assert product.brand is None
        assert product.sku is None

    def test_product_to_dict(self):
        """Test Product.to_dict() serialization."""
        product = Product(
            name="Serialization Test",
            description="Test",
            category="Test",
            price=49.99,
            target_keywords=["test"],
            images=[{"url": "https://example.com/test.jpg", "alt": "Test"}],
            brand="TestBrand",
            sku="TEST-001",
        )
        data = product.to_dict()
        assert data["name"] == "Serialization Test"
        assert data["price"] == 49.99
        assert data["brand"] == "TestBrand"
        assert data["sku"] == "TEST-001"

    def test_product_to_dict_roundtrip(self):
        """Test serialization round-trip."""
        original = Product(
            name="Round Trip Product",
            description="Test description",
            category="Electronics",
            price=199.99,
            target_keywords=["electronics", "gadget"],
            images=[{"url": "https://example.com/img.jpg", "alt": "Image"}],
            brand="RoundTripBrand",
            sku="RT-001",
        )
        data = original.to_dict()
        restored = Product.from_dict(data)
        assert restored.name == original.name
        assert restored.price == original.price
        assert restored.brand == original.brand
        assert restored.sku == original.sku

    def test_product_empty_name(self):
        """Test product with empty name."""
        product = Product(
            name="",
            description="Test",
            category="Test",
            price=0,
            target_keywords=[],
            images=[],
        )
        assert product.name == ""

    def test_product_unicode_characters(self):
        """Test product with unicode characters."""
        product = Product(
            name="日本語製品",
            description="テスト説明",
            category="電子機器",
            price=10000,
            target_keywords=["日本語", "製品"],
            images=[{"url": "https://example.com/日本語.jpg", "alt": "画像"}],
            brand="日本ブランド",
            sku="JP-001",
        )
        assert product.name == "日本語製品"
        assert product.brand == "日本ブランド"

    def test_product_very_long_description(self):
        """Test product with very long description."""
        long_desc = "A" * 10000
        product = Product(
            name="Long Description Product",
            description=long_desc,
            category="Test",
            price=0,
            target_keywords=[],
            images=[],
        )
        assert len(product.description) == 10000

    def test_product_zero_price(self):
        """Test product with zero price."""
        product = Product(
            name="Free Product",
            description="Free item",
            category="Test",
            price=0,
            target_keywords=[],
            images=[],
        )
        assert product.price == 0

    def test_product_negative_price(self):
        """Test product with negative price (edge case)."""
        product = Product(
            name="Negative Price Product",
            description="Test",
            category="Test",
            price=-10.0,
            target_keywords=[],
            images=[],
        )
        assert product.price == -10.0

    def test_product_no_images(self):
        """Test product with no images."""
        product = Product(
            name="No Images Product",
            description="Test",
            category="Test",
            price=0,
            target_keywords=[],
            images=[],
        )
        assert product.images == []

    def test_product_multiple_images(self):
        """Test product with multiple images."""
        images = [
            {"url": "https://example.com/img1.jpg", "alt": "Image 1"},
            {"url": "https://example.com/img2.jpg", "alt": "Image 2"},
            {"url": "https://example.com/img3.jpg", "alt": "Image 3"},
        ]
        product = Product(
            name="Multi Image Product",
            description="Test",
            category="Test",
            price=0,
            target_keywords=[],
            images=images,
        )
        assert len(product.images) == 3
        assert product.images[0]["url"] == "https://example.com/img1.jpg"

    def test_product_empty_target_keywords(self):
        """Test product with empty target keywords."""
        product = Product(
            name="No Keywords Product",
            description="Test",
            category="Test",
            price=0,
            target_keywords=[],
            images=[],
        )
        assert product.target_keywords == []

    def test_product_with_primary_keyword(self):
        """Test product with primary keyword."""
        product = Product(
            name="Keyword Product",
            description="Test",
            category="Test",
            price=0,
            target_keywords=["primary", "secondary"],
            images=[],
        )
        assert product.primary_keyword == "primary"

    def test_product_primary_keyword_none(self):
        """Test product with no target keywords has no primary keyword."""
        product = Product(
            name="No Primary Product",
            description="Test",
            category="Test",
            price=0,
            target_keywords=[],
            images=[],
        )
        assert product.primary_keyword is None


class TestSEOReport:
    """Tests for SEOReport dataclass."""

    def test_seo_report_creation(self):
        """Test SEOReport creation."""
        report = SEOReport(
            product_name="Test Product",
            total_score=75,
            category_scores={
                "title": 20,
                "meta_description": 15,
                "keywords": 10,
                "images": 15,
                "content": 15,
            },
            issues=[
                Issue(
                    severity="warning",
                    category="meta_description",
                    message="Too long",
                    suggestion="Shorten description",
                )
            ],
            recommendations=["Improve keywords"],
        )
        assert report.product_name == "Test Product"
        assert report.total_score == 75
        assert len(report.issues) == 1

    def test_seo_report_to_dict(self):
        """Test SEOReport.to_dict() serialization."""
        report = SEOReport(
            product_name="Dict Test Product",
            total_score=80,
            category_scores={
                "title": 20,
                "meta_description": 20,
                "keywords": 10,
                "images": 15,
                "content": 15,
            },
            issues=[],
            recommendations=["Keep up the good work"],
        )
        data = report.to_dict()
        assert data["product_name"] == "Dict Test Product"
        assert data["total_score"] == 80
        assert data["recommendations"] == ["Keep up the good work"]

    def test_seo_report_to_json(self):
        """Test SEOReport.to_json() serialization."""
        import json

        report = SEOReport(
            product_name="JSON Test Product",
            total_score=90,
            category_scores={
                "title": 20,
                "meta_description": 20,
                "keywords": 20,
                "images": 20,
                "content": 10,
            },
            issues=[],
            recommendations=["Great SEO score!"],
        )
        json_str = report.to_json()
        data = json.loads(json_str)
        assert data["product_name"] == "JSON Test Product"
        assert data["total_score"] == 90

    def test_seo_report_empty_issues(self):
        """Test SEOReport with no issues."""
        report = SEOReport(
            product_name="Perfect Product",
            total_score=100,
            category_scores={
                "title": 20,
                "meta_description": 20,
                "keywords": 20,
                "images": 20,
                "content": 20,
            },
            issues=[],
            recommendations=["Excellent SEO!"],
        )
        assert report.issues == []
        assert report.total_score == 100

    def test_seo_report_multiple_issues(self):
        """Test SEOReport with multiple issues."""
        report = SEOReport(
            product_name="Multiple Issues Product",
            total_score=40,
            category_scores={
                "title": 10,
                "meta_description": 5,
                "keywords": 5,
                "images": 10,
                "content": 10,
            },
            issues=[
                Issue(
                    severity="critical",
                    category="title",
                    message="Title too short",
                    suggestion="Expand title",
                ),
                Issue(
                    severity="warning",
                    category="keywords",
                    message="Missing keywords",
                    suggestion="Add more keywords",
                ),
                Issue(
                    severity="info",
                    category="images",
                    message="Low image count",
                    suggestion="Add more images",
                ),
            ],
            recommendations=["Improve title", "Add keywords", "Add images"],
        )
        assert len(report.issues) == 3
        assert report.issues[0].severity == "critical"
        assert report.issues[1].severity == "warning"
        assert report.issues[2].severity == "info"

    def test_seo_report_score_calculation(self):
        """Test that total_score equals sum of category_scores."""
        category_scores = {
            "title": 15,
            "meta_description": 10,
            "keywords": 8,
            "images": 12,
            "content": 10,
        }
        report = SEOReport(
            product_name="Score Test Product",
            total_score=sum(category_scores.values()),
            category_scores=category_scores,
            issues=[],
            recommendations=[],
        )
        assert report.total_score == sum(category_scores.values())


class TestMetaTag:
    """Tests for MetaTag dataclass."""

    def test_metatag_creation_meta(self):
        """Test MetaTag creation with meta type."""
        tag = MetaTag(name="description", content="Test description", tag_type=MetaTagType.META)
        assert tag.name == "description"
        assert tag.content == "Test description"
        assert tag.tag_type == MetaTagType.META

    def test_metatag_creation_og(self):
        """Test MetaTag creation with og type."""
        tag = MetaTag(name="og:title", content="Test Title", tag_type=MetaTagType.OG)
        assert tag.name == "og:title"
        assert tag.tag_type == MetaTagType.OG

    def test_metatag_creation_twitter(self):
        """Test MetaTag creation with twitter type."""
        tag = MetaTag(name="twitter:card", content="summary_large_image", tag_type=MetaTagType.TWITTER)
        assert tag.name == "twitter:card"
        assert tag.tag_type == MetaTagType.TWITTER

    def test_metatag_to_dict(self):
        """Test MetaTag.to_dict() serialization."""
        tag = MetaTag(name="test", content="Test content", tag_type=MetaTagType.META)
        data = tag.to_dict()
        assert data["name"] == "test"
        assert data["content"] == "Test content"
        assert data["tag_type"] == "meta"

    def test_metatag_to_dict_roundtrip(self):
        """Test MetaTag serialization round-trip."""
        original = MetaTag(name="og:description", content="Test OG", tag_type=MetaTagType.OG)
        data = original.to_dict()
        restored = MetaTag.from_dict(data)
        assert restored.name == original.name
        assert restored.content == original.content
        assert restored.tag_type == original.tag_type

    def test_metatag_empty_content(self):
        """Test MetaTag with empty content."""
        tag = MetaTag(name="empty", content="", tag_type=MetaTagType.META)
        assert tag.content == ""

    def test_metatag_unicode_content(self):
        """Test MetaTag with unicode content."""
        tag = MetaTag(name="unicode", content="日本語コンテンツ", tag_type=MetaTagType.META)
        assert tag.content == "日本語コンテンツ"


class TestIssue:
    """Tests for Issue dataclass."""

    def test_issue_creation_critical(self):
        """Test Issue creation with critical severity."""
        issue = Issue(
            severity="critical",
            category="title",
            message="Title is missing",
            suggestion="Add a title",
        )
        assert issue.severity == "critical"
        assert issue.category == "title"
        assert issue.message == "Title is missing"
        assert issue.suggestion == "Add a title"

    def test_issue_creation_warning(self):
        """Test Issue creation with warning severity."""
        issue = Issue(
            severity="warning",
            category="meta_description",
            message="Description too long",
            suggestion="Shorten description",
        )
        assert issue.severity == "warning"
        assert issue.message == "Description too long"

    def test_issue_creation_info(self):
        """Test Issue creation with info severity."""
        issue = Issue(
            severity="info",
            category="images",
            message="No images found",
            suggestion="Add product images",
        )
        assert issue.severity == "info"
        assert issue.message == "No images found"

    def test_issue_to_dict(self):
        """Test Issue.to_dict() serialization."""
        issue = Issue(
            severity="critical",
            category="keywords",
            message="Keywords missing",
            suggestion="Add keywords",
        )
        data = issue.to_dict()
        assert data["severity"] == "critical"
        assert data["category"] == "keywords"
        assert data["message"] == "Keywords missing"
        assert data["suggestion"] == "Add keywords"

    def test_issue_to_dict_roundtrip(self):
        """Test Issue serialization round-trip."""
        original = Issue(
            severity="warning",
            category="content",
            message="Content short",
            suggestion="Expand content",
        )
        data = original.to_dict()
        restored = Issue.from_dict(data)
        assert restored.severity == original.severity
        assert restored.category == original.category
        assert restored.message == original.message
        assert restored.suggestion == original.suggestion

    def test_issue_empty_suggestion(self):
        """Test Issue with empty suggestion."""
        issue = Issue(
            severity="warning",
            category="test",
            message="Test issue",
            suggestion="",
        )
        assert issue.suggestion == ""
