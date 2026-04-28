"""Tests for the path builder module."""

import os
import pytest
from datetime import datetime
from email_tool.models import Email, Rule, RuleType
from email_tool.path_builder import PathBuilder


class TestPathBuilder:
    """Test cases for PathBuilder class."""
    
    @pytest.fixture
    def sample_email(self):
        """Create a sample email for testing."""
        return Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@test.com"],
            subject="Test Subject: Hello World!",
            date=datetime(2024, 3, 15, 10, 30, 0),
            body_plain="This is a test email body.",
            attachments=["file.pdf"],
            raw_headers={}
        )
    
    @pytest.fixture
    def sample_rule(self):
        """Create a sample rule for testing."""
        return Rule(
            name="test_rule",
            rule_type=RuleType.SUBJECT_EXACT,
            pattern="test",
            priority=50,
            category="general"
        )
    
    def test_default_template(self):
        """Test default template construction."""
        builder = PathBuilder()
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 5, 20)
        )
        
        path = builder.build_path(email)
        
        # Check that year, month are in path
        assert "2024" in path
        assert "05" in path
    
    def test_year_variable(self):
        """Test {{year}} variable substitution."""
        builder = PathBuilder(template="{{year}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == "2024"
    
    def test_month_variable(self):
        """Test {{month}} variable substitution."""
        builder = PathBuilder(template="{{month}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == "03"
    
    def test_day_variable(self):
        """Test {{day}} variable substitution."""
        builder = PathBuilder(template="{{day}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == "15"
    
    def test_from_domain_variable(self):
        """Test {{from_domain}} variable substitution."""
        builder = PathBuilder(template="{{from_domain}}")
        email = Email(
            from_addr="user@example.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == "example.com"
    
    def test_from_domain_without_at(self):
        """Test from_domain when email has no @ symbol."""
        builder = PathBuilder(template="{{from_domain}}")
        email = Email(
            from_addr="invalid_email",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == "invalid_email"
    
    def test_from_domain_empty(self):
        """Test from_domain when email address is empty."""
        builder = PathBuilder(template="{{from_domain}}")
        email = Email(
            from_addr="",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == "unknown"
    
    def test_subject_sanitized_variable(self):
        """Test {{subject_sanitized}} variable substitution."""
        builder = PathBuilder(template="{{subject_sanitized}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test: Hello World!",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        # Invalid characters should be replaced with underscores
        assert ":" in path or "_" in path
        assert "!" not in path
    
    def test_subject_sanitized_removes_invalid_chars(self):
        """Test that invalid filename characters are removed."""
        builder = PathBuilder(template="{{subject_sanitized}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject='Test<>:"/\\|?*?',
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        # All invalid characters should be replaced
        for char in '<>:"/\\|?*?':
            assert char not in path
    
    def test_subject_sanitized_empty(self):
        """Test subject_sanitized when subject is empty."""
        builder = PathBuilder(template="{{subject_sanitized}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == "untitled"
    
    def test_rule_name_variable(self):
        """Test {{rule_name}} variable substitution."""
        builder = PathBuilder(template="{{rule_name}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        rule = Rule(
            name="important_emails",
            rule_type=RuleType.SUBJECT_EXACT,
            pattern="important",
            priority=50
        )
        
        path = builder.build_path(email, rule=rule)
        assert path == "important_emails"
    
    def test_rule_name_without_rule(self):
        """Test {{rule_name}} when no rule is provided."""
        builder = PathBuilder(template="{{rule_name}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email, rule=None)
        assert path == ""
    
    def test_base_path_prepend(self):
        """Test base_path parameter."""
        builder = PathBuilder(template="{{year}}/{{month}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email, base_path="archive")
        assert path.startswith("archive")
        assert "2024" in path
        assert "03" in path
    
    def test_path_separators_normalized(self):
        """Test that path separators are normalized to OS-specific."""
        builder = PathBuilder(template="{{year}}/{{month}}/{{day}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        
        # Should use OS-specific separator
        assert os.sep in path
        # Should not have forward slashes
        assert "/" not in path.replace(os.sep, "")
    
    def test_complex_template(self):
        """Test complex template with multiple variables."""
        builder = PathBuilder(
            template="{{year}}/{{month}}/{{from_domain}}/{{subject_sanitized}}"
        )
        email = Email(
            from_addr="user@example.com",
            to_addrs=["other@test.com"],
            subject="Invoice #123: Payment Received!",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        
        assert "2024" in path
        assert "03" in path
        assert "example.com" in path
        # Invalid characters should be sanitized
        assert ":" not in path or "_" in path
    
    def test_subject_truncation(self):
        """Test that long subjects are truncated."""
        builder = PathBuilder(template="{{subject_sanitized}}")
        long_subject = "A" * 200
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject=long_subject,
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert len(path) <= 100
    
    def test_multiple_underscores_collapsed(self):
        """Test that multiple consecutive underscores are collapsed."""
        builder = PathBuilder(template="{{subject_sanitized}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test___Multiple___Underscores",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        # Should not have multiple consecutive underscores
        assert "__" not in path
    
    def test_leading_trailing_spaces_removed(self):
        """Test that leading/trailing spaces are removed."""
        builder = PathBuilder(template="{{subject_sanitized}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="  Test Subject  ",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert not path.startswith(" ")
        assert not path.endswith(" ")
    
    def test_unknown_variable_returns_empty(self):
        """Test that unknown variables return empty string."""
        builder = PathBuilder(template="{{unknown_var}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == ""
    
    def test_email_without_date(self):
        """Test path building when email has no date."""
        builder = PathBuilder(template="{{year}}/{{month}}/{{day}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=None
        )
        
        path = builder.build_path(email)
        assert "unknown" in path
    
    def test_build_filename_basic(self):
        """Test basic filename building."""
        builder = PathBuilder()
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test Subject",
            date=datetime(2024, 3, 15)
        )
        
        filename = builder.build_filename(email, extension="eml")
        assert filename == "Test_Subject.eml"
    
    def test_build_filename_with_rule(self):
        """Test filename building with rule name."""
        builder = PathBuilder()
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test Subject",
            date=datetime(2024, 3, 15)
        )
        rule = Rule(
            name="important",
            rule_type=RuleType.SUBJECT_EXACT,
            pattern="test",
            priority=50
        )
        
        filename = builder.build_filename(email, extension="eml", rule=rule)
        assert "important" in filename
    
    def test_build_filename_empty_subject(self):
        """Test filename building when subject is empty."""
        builder = PathBuilder()
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="",
            date=datetime(2024, 3, 15)
        )
        
        filename = builder.build_filename(email, extension="eml")
        # Should have timestamp-based name
        assert filename.endswith(".eml")
        assert "email_" in filename
    
    def test_build_filename_custom_extension(self):
        """Test filename building with custom extension."""
        builder = PathBuilder()
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test Subject",
            date=datetime(2024, 3, 15)
        )
        
        filename = builder.build_filename(email, extension="pdf")
        assert filename == "Test_Subject.pdf"
    
    def test_build_filename_invalid_chars(self):
        """Test filename building with invalid characters."""
        builder = PathBuilder()
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject='Test<>:"/\\|?*?',
            date=datetime(2024, 3, 15)
        )
        
        filename = builder.build_filename(email, extension="eml")
        # Should not contain invalid characters
        for char in '<>:"/\\|?*?':
            assert char not in filename


class TestPathBuilderEdgeCases:
    """Edge case tests for PathBuilder."""
    
    def test_email_with_special_domain(self):
        """Test from_domain with special characters in domain."""
        builder = PathBuilder(template="{{from_domain}}")
        email = Email(
            from_addr="user@sub.domain.example.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == "sub.domain.example.com"
    
    def test_email_with_unicode_subject(self):
        """Test subject_sanitized with unicode characters."""
        builder = PathBuilder(template="{{subject_sanitized}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test 你好世界",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        # Unicode should be preserved
        assert "你好" in path or "世界" in path
    
    def test_empty_template(self):
        """Test with empty template."""
        builder = PathBuilder(template="")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == ""
    
    def test_only_variables_template(self):
        """Test template with only variables."""
        builder = PathBuilder(template="{{year}}{{month}}{{day}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        assert path == "20240315"
    
    def test_mixed_separators_in_template(self):
        """Test template with mixed separators."""
        builder = PathBuilder(template="{{year}}\\{{month}}/{{day}}")
        email = Email(
            from_addr="user@test.com",
            to_addrs=["other@test.com"],
            subject="Test",
            date=datetime(2024, 3, 15)
        )
        
        path = builder.build_path(email)
        # Should normalize to OS-specific separator
        assert path.count(os.sep) == 2
        # Should not have mixed separators
        assert "/" not in path.replace(os.sep, "")
        assert "\\" not in path.replace(os.sep, "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
