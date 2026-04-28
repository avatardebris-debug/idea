"""SEO Analyzer — evaluates a product's SEO readiness."""

from __future__ import annotations

import re
from dropship_seo.config import AppConfig, SEOConfig, get_config
from dropship_seo.models import Issue, Product, SEOReport


class Analyzer:
    """Analyzes a Product and produces an SEOReport with scores and issues."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or get_config().config
        self.scoring = self.config.seo

    def analyze(self, product: Product) -> SEOReport:
        """Analyze a product and return an SEOReport.

        Scores are computed across 5 categories (each 0-20 pts):
        - title: product name length optimization
        - meta_description: description length optimization
        - keywords: target keyword presence and density
        - images: image alt text coverage
        - content: description richness
        """
        category_scores: dict[str, int] = {}
        issues: list[Issue] = []
        recommendations: list[str] = []

        # Score each category
        category_scores["title"] = self._score_title(product, issues)
        category_scores["meta_description"] = self._score_meta_description(product, issues)
        category_scores["keywords"] = self._score_keywords(product, issues)
        category_scores["images"] = self._score_images(product, issues)
        category_scores["content"] = self._score_content(product, issues)

        # Compute total (sum of 5 categories, each 0-20 = 0-100)
        total_score = sum(category_scores.values())

        # Build recommendations from issues
        recommendations = self._build_recommendations(product, issues)

        return SEOReport(
            product_name=product.name,
            total_score=total_score,
            category_scores=category_scores,
            issues=issues,
            recommendations=recommendations,
        )

    # ── Category scorers ───────────────────────────────────────────────────

    def _score_title(self, product: Product, issues: list[Issue]) -> int:
        """Score title (product name) optimization. Max 20 pts."""
        name = product.name.strip()
        length = len(name)

        if not name:
            issues.append(Issue(
                severity="critical",
                category="title",
                message="Product name is empty.",
                suggestion="Provide a descriptive product name between 50-70 characters.",
            ))
            return 0

        # Ideal length: 50-70 chars
        if self.scoring.min_title_length <= length <= self.scoring.max_title_length:
            return 20
        elif 30 <= length < self.scoring.min_title_length:
            issues.append(Issue(
                severity="warning",
                category="title",
                message=f"Product name is too short ({length} chars).",
                suggestion=f"Expand the product name to at least {self.scoring.min_title_length} characters for better SEO.",
            ))
            return 10
        elif length > self.scoring.max_title_length:
            issues.append(Issue(
                severity="warning",
                category="title",
                message=f"Product name is too long ({length} chars).",
                suggestion=f"Trim the product name to around {self.scoring.max_title_length} characters for optimal display.",
            ))
            return 12
        else:
            # Between 20 and 30 chars
            issues.append(Issue(
                severity="warning",
                category="title",
                message=f"Product name is short ({length} chars).",
                suggestion=f"Expand the product name to at least {self.scoring.min_title_length} characters.",
            ))
            return 5

    def _score_meta_description(self, product: Product, issues: list[Issue]) -> int:
        """Score meta description optimization. Max 20 pts."""
        desc = product.description.strip()
        length = len(desc)

        if not desc:
            issues.append(Issue(
                severity="critical",
                category="meta_description",
                message="Product description is empty.",
                suggestion="Write a compelling product description between 120-160 characters.",
            ))
            return 0

        if self.scoring.min_description_length <= length <= self.scoring.max_description_length:
            return 20
        elif 80 <= length < self.scoring.min_description_length:
            issues.append(Issue(
                severity="warning",
                category="meta_description",
                message=f"Meta description is too short ({length} chars).",
                suggestion=f"Expand the description to at least {self.scoring.min_description_length} characters.",
            ))
            return 10
        elif length > self.scoring.max_description_length:
            issues.append(Issue(
                severity="warning",
                category="meta_description",
                message=f"Meta description is too long ({length} chars).",
                suggestion=f"Trim the description to around {self.scoring.max_description_length} characters.",
            ))
            return 12
        else:
            issues.append(Issue(
                severity="warning",
                category="meta_description",
                message=f"Meta description is short ({length} chars).",
                suggestion=f"Expand the description to at least {self.scoring.min_description_length} characters.",
            ))
            return 5

    def _score_keywords(self, product: Product, issues: list[Issue]) -> int:
        """Score keyword presence and density. Max 20 pts."""
        keywords = product.target_keywords
        desc = product.description.lower()
        name = product.name.lower()

        if not keywords:
            issues.append(Issue(
                severity="warning",
                category="keywords",
                message="No target keywords specified.",
                suggestion="Add 5-15 relevant target keywords for the product.",
            ))
            # Partial credit for having a primary keyword derived from name
            if product.primary_keyword:
                return 5
            return 0

        # Check keyword presence in description
        present_count = sum(1 for kw in keywords if kw in desc or kw in name)
        presence_ratio = present_count / len(keywords)

        if presence_ratio >= 0.8:
            score = 20
        elif presence_ratio >= 0.5:
            score = 14
            missing = [kw for kw in keywords if kw not in desc and kw not in name]
            issues.append(Issue(
                severity="warning",
                category="keywords",
                message=f"{len(missing)} of {len(keywords)} keywords not found in description.",
                suggestion=f"Incorporate these keywords: {', '.join(missing)}",
            ))
        elif presence_ratio >= 0.2:
            score = 8
            missing = [kw for kw in keywords if kw not in desc and kw not in name]
            issues.append(Issue(
                severity="critical",
                category="keywords",
                message=f"Only {present_count}/{len(keywords)} keywords found in description.",
                suggestion=f"Add these missing keywords: {', '.join(missing)}",
            ))
        else:
            score = 2
            issues.append(Issue(
                severity="critical",
                category="keywords",
                message="Very few keywords found in description.",
                suggestion="Incorporate more target keywords into the product description.",
            ))

        # Check keyword count
        if len(keywords) < self.scoring.keyword_count_min:
            issues.append(Issue(
                severity="info",
                category="keywords",
                message=f"Only {len(keywords)} keywords specified (recommended: {self.scoring.keyword_count_min}-{self.scoring.keyword_count_max}).",
                suggestion=f"Add more keywords (aim for {self.scoring.keyword_count_min}-{self.scoring.keyword_count_max}).",
            ))
        elif len(keywords) > self.scoring.keyword_count_max:
            issues.append(Issue(
                severity="info",
                category="keywords",
                message=f"Too many keywords ({len(keywords)}). Consider focusing on the most important ones.",
                suggestion=f"Reduce to {self.scoring.keyword_count_max} or fewer high-quality keywords.",
            ))

        return score

    def _score_images(self, product: Product, issues: list[Issue]) -> int:
        """Score image alt text coverage. Max 20 pts."""
        images = product.images
        if not images:
            issues.append(Issue(
                severity="warning",
                category="images",
                message="No images specified.",
                suggestion="Add product images with descriptive alt text.",
            ))
            return 0

        # Count images with alt text
        alt_count = sum(1 for img in images if img.get("alt", "").strip())
        total = len(images)
        ratio = alt_count / total if total > 0 else 0

        if ratio >= self.scoring.image_alt_ratio:
            return 20
        elif ratio >= 0.5:
            missing = [i for i, img in enumerate(images) if not img.get("alt", "").strip()]
            issues.append(Issue(
                severity="warning",
                category="images",
                message=f"{len(missing)} of {total} images missing alt text.",
                suggestion=f"Add alt text to images at index: {missing}",
            ))
            return 12
        else:
            issues.append(Issue(
                severity="critical",
                category="images",
                message=f"Only {alt_count}/{total} images have alt text.",
                suggestion="Add descriptive alt text to all product images.",
            ))
            return 5

        return 20  # Should not reach here

    def _score_content(self, product: Product, issues: list[Issue]) -> int:
        """Score content richness. Max 20 pts."""
        desc = product.description.strip()
        length = len(desc)
        word_count = product.word_count

        if not desc:
            issues.append(Issue(
                severity="critical",
                category="content",
                message="Product description is empty.",
                suggestion="Write a detailed product description.",
            ))
            return 0

        # Check length
        if self.scoring.description_min <= length <= self.scoring.description_max:
            length_score = 10
        elif length >= self.scoring.description_min:
            length_score = 7
        else:
            issues.append(Issue(
                severity="warning",
                category="content",
                message=f"Description is too short ({length} chars, {word_count} words).",
                suggestion=f"Expand the description to at least {self.scoring.description_min} characters.",
            ))
            length_score = 3

        # Check word diversity (unique words / total words)
        words = desc.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio >= 0.5:
                diversity_score = 10
            elif unique_ratio >= 0.3:
                diversity_score = 6
            else:
                diversity_score = 3
                issues.append(Issue(
                    severity="info",
                    category="content",
                    message="Low word diversity in description.",
                    suggestion="Use more varied vocabulary to improve content quality.",
                ))
        else:
            diversity_score = 0

        return min(length_score + diversity_score, 20)

    # ── Recommendations ────────────────────────────────────────────────────

    def _build_recommendations(self, product: Product, issues: list[Issue]) -> list[str]:
        """Build human-readable recommendations from issues."""
        recs: list[str] = []

        # Extract title recommendation
        title_issues = [i for i in issues if i.category == "title"]
        if title_issues:
            recs.append(f"Title: {title_issues[0].suggestion}")
        else:
            recs.append(f"Title: Product name is well-optimized ({len(product.name.strip())} chars).")

        # Extract meta description recommendation
        meta_issues = [i for i in issues if i.category == "meta_description"]
        if meta_issues:
            recs.append(f"Meta Description: {meta_issues[0].suggestion}")
        else:
            recs.append(f"Meta Description: Description length is optimal ({len(product.description.strip())} chars).")

        # Extract keyword recommendations
        kw_issues = [i for i in issues if i.category == "keywords"]
        if kw_issues:
            for issue in kw_issues:
                recs.append(f"Keywords: {issue.suggestion}")
        else:
            recs.append(f"Keywords: {len(product.target_keywords)} keywords specified and well-integrated.")

        # Extract image recommendations
        img_issues = [i for i in issues if i.category == "images"]
        if img_issues:
            for issue in img_issues:
                recs.append(f"Images: {issue.suggestion}")
        else:
            recs.append("Images: All images have alt text.")

        # Extract content recommendations
        content_issues = [i for i in issues if i.category == "content"]
        if content_issues:
            for issue in content_issues:
                recs.append(f"Content: {issue.suggestion}")
        else:
            recs.append("Content: Description is well-written and detailed.")

        return recs
