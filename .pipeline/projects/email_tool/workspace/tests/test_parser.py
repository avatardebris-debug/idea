"""Unit tests for the email parser."""

import pytest
from datetime import datetime
from email_tool.parser import (
    parse_email_file,
    parse_email_content,
    _decode_mime_word,
    _parse_date,
    _get_header_value,
    _get_addresses,
    _extract_attachments,
    _extract_body_parts,
)
from email_tool.models import Email


class TestDecodeMimeWord:
    """Tests for MIME word decoding."""

    def test_decode_plain_text(self):
        """Test decoding of plain text without encoding."""
        result = _decode_mime_word("Hello World")
        assert result == "Hello World"

    def test_decode_utf8_base64(self):
        """Test decoding of UTF-8 base64 encoded text."""
        result = _decode_mime_word("=?UTF-8?B?SGVsbG8gV29ybGQ=?=")
        assert result == "Hello World"

    def test_decode_iso8859_q_encoded(self):
        """Test decoding of ISO-8859-1 Q-encoded text."""
        result = _decode_mime_word("=?ISO-8859-1?Q?Hello_World?=")
        assert result == "Hello World"

    def test_decode_multiple_mime_words(self):
        """Test decoding of multiple MIME words in sequence."""
        result = _decode_mime_word("=?UTF-8?B?SGVsbG8=?= =?UTF-8?B?IFdvcmxk?=")
        assert result == "Hello World"

    def test_decode_empty_string(self):
        """Test decoding of empty string."""
        result = _decode_mime_word("")
        assert result == ""


class TestParseDate:
    """Tests for date parsing."""

    def test_parse_valid_date(self):
        """Test parsing of valid RFC 2822 date."""
        result = _parse_date("Mon, 01 Jan 2024 12:00:00 +0000")
        assert result is not None
        assert isinstance(result, datetime)

    def test_parse_date_with_timezone(self):
        """Test parsing of date with timezone offset."""
        result = _parse_date("Mon, 01 Jan 2024 12:00:00 +0530")
        assert result is not None

    def test_parse_invalid_date(self):
        """Test parsing of invalid date string."""
        result = _parse_date("Not a valid date")
        assert result is None

    def test_parse_empty_date(self):
        """Test parsing of empty date string."""
        result = _parse_date("")
        assert result is None

    def test_parse_none_date(self):
        """Test parsing of None date."""
        result = _parse_date(None)
        assert result is None


class TestGetHeaderValue:
    """Tests for header value extraction."""

    def test_get_header_value(self, mock_email):
        """Test getting a header value."""
        result = _get_header_value(mock_email, "Subject")
        assert result == "Test Subject"

    def test_get_header_value_case_insensitive(self, mock_email):
        """Test getting header value with different case."""
        result = _get_header_value(mock_email, "subject")
        assert result == "Test Subject"

    def test_get_header_value_missing(self, mock_email):
        """Test getting a missing header value."""
        result = _get_header_value(mock_email, "Missing-Header")
        assert result is None


class TestGetAddresses:
    """Tests for address extraction."""

    def test_get_addresses_single(self, mock_email):
        """Test getting addresses from single recipient."""
        result = _get_addresses(mock_email, "To")
        assert len(result) == 1
        assert "recipient@example.com" in result

    def test_get_addresses_multiple(self, mock_email_multi):
        """Test getting addresses from multiple recipients."""
        result = _get_addresses(mock_email_multi, "To")
        assert len(result) == 2
        assert "recipient1@example.com" in result
        assert "recipient2@example.com" in result

    def test_get_addresses_empty(self, mock_email_empty):
        """Test getting addresses when header is empty."""
        result = _get_addresses(mock_email_empty, "To")
        assert result == []

    def test_get_addresses_display_name(self, mock_email_display):
        """Test getting addresses with display names."""
        result = _get_addresses(mock_email_display, "From")
        assert len(result) == 1
        assert "sender@example.com" in result


class TestExtractBodyParts:
    """Tests for body part extraction."""

    def test_extract_plain_text_body(self, mock_email_plain):
        """Test extracting plain text body."""
        plain, html = _extract_body_parts(mock_email_plain)
        assert plain == "This is a plain text email body."
        assert html is None

    def test_extract_html_body(self, mock_email_html):
        """Test extracting HTML body."""
        plain, html = _extract_body_parts(mock_email_html)
        assert plain is None
        assert html == "<html><body><p>HTML content</p></body></html>"

    def test_extract_both_body_types(self, mock_email_multipart):
        """Test extracting both plain and HTML bodies."""
        plain, html = _extract_body_parts(mock_email_multipart)
        assert plain == "Plain text version"
        assert html == "<html><body>HTML version</body></html>"

    def test_extract_empty_body(self, mock_email_empty_body):
        """Test extracting empty body."""
        plain, html = _extract_body_parts(mock_email_empty_body)
        assert plain is None
        assert html is None


class TestExtractAttachments:
    """Tests for attachment extraction."""

    def test_extract_attachments(self, mock_email_with_attachment):
        """Test extracting attachment filenames."""
        attachments = _extract_attachments(mock_email_with_attachment)
        assert len(attachments) == 1
        assert "document.pdf" in attachments

    def test_extract_multiple_attachments(self, mock_email_multiple_attachments):
        """Test extracting multiple attachments."""
        attachments = _extract_attachments(mock_email_multiple_attachments)
        assert len(attachments) == 2
        assert "file1.txt" in attachments
        assert "file2.pdf" in attachments

    def test_extract_no_attachments(self, mock_email_no_attachment):
        """Test extracting when no attachments exist."""
        attachments = _extract_attachments(mock_email_no_attachment)
        assert attachments == []

    def test_extract_inline_attachments(self, mock_email_inline_attachment):
        """Test extracting inline attachments."""
        attachments = _extract_attachments(mock_email_inline_attachment)
        assert len(attachments) == 1
        assert "image.png" in attachments


class TestParseEmailContent:
    """Tests for parsing email content."""

    def test_parse_plain_text_email(self):
        """Test parsing a plain text email."""
        content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 01 Jan 2024 12:00:00 +0000

This is a plain text email body."""
        
        email = parse_email_content(content)
        assert email is not None
        assert email.from_addr == "sender@example.com"
        assert email.to_addrs == ["recipient@example.com"]
        assert email.subject == "Test Email"
        assert email.body_plain == "This is a plain text email body."
        assert email.body_html is None

    def test_parse_html_email(self):
        """Test parsing an HTML email."""
        content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 01 Jan 2024 12:00:00 +0000
Content-Type: text/html

<html><body><p>HTML content</p></body></html>"""
        
        email = parse_email_content(content)
        assert email is not None
        assert email.body_html == "<html><body><p>HTML content</p></body></html>"

    def test_parse_multipart_email(self):
        """Test parsing a multipart email."""
        content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 01 Jan 2024 12:00:00 +0000
Content-Type: multipart/alternative; boundary="boundary"

--boundary
Content-Type: text/plain

Plain text body

--boundary
Content-Type: text/html

<html><body>HTML body</body></html>
--boundary--"""
        
        email = parse_email_content(content)
        assert email is not None
        assert email.body_plain == "Plain text body"
        assert email.body_html == "<html><body>HTML body</body></html>"

    def test_parse_email_with_attachments(self):
        """Test parsing an email with attachments."""
        content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 01 Jan 2024 12:00:00 +0000
Content-Type: multipart/mixed; boundary="boundary"

--boundary
Content-Type: text/plain

Email body

--boundary
Content-Disposition: attachment; filename="test.txt"
Content-Type: text/plain

Attachment content
--boundary--"""
        
        email = parse_email_content(content)
        assert email is not None
        assert len(email.attachments) == 1
        assert "test.txt" in email.attachments

    def test_parse_email_with_missing_headers(self):
        """Test parsing an email with missing headers."""
        content = """From: sender@example.com
Subject: Test Email

Email body without To or Date headers."""
        
        email = parse_email_content(content)
        assert email is not None
        assert email.from_addr == "sender@example.com"
        assert email.subject == "Test Email"
        assert email.to_addrs == []
        assert email.date is None

    def test_parse_invalid_email(self):
        """Test parsing an invalid email."""
        content = "This is not a valid email format"
        email = parse_email_content(content)
        assert email is not None  # Should still parse, just with minimal data


class TestParseEmailFile:
    """Tests for parsing email files."""

    def test_parse_valid_eml_file(self, tmp_path, sample_eml_file):
        """Test parsing a valid .eml file."""
        email = parse_email_file(sample_eml_file)
        assert email is not None
        assert email.subject == "Test Email"

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file."""
        email = parse_email_file("/nonexistent/path/to/file.eml")
        assert email is None

    def test_parse_invalid_eml_file(self, tmp_path):
        """Test parsing an invalid .eml file."""
        invalid_file = tmp_path / "invalid.eml"
        invalid_file.write_text("This is not a valid email file")
        
        email = parse_email_file(invalid_file)
        assert email is not None  # Should still parse, just with minimal data


class TestEmailParsingEdgeCases:
    """Tests for edge cases in email parsing."""

    def test_email_with_unicode_subject(self):
        """Test parsing email with unicode in subject."""
        content = """From: sender@example.com
To: recipient@example.com
Subject: =?UTF-8?B?VGVzdCBzdWJqZWN0IHdpdGggdW5pY29kZQ==?=
Date: Mon, 01 Jan 2024 12:00:00 +0000

Body content."""
        
        email = parse_email_content(content)
        assert email is not None
        assert email.subject == "Test subject with unicode"

    def test_email_with_multiple_from_addresses(self):
        """Test parsing email with multiple From addresses."""
        content = """From: sender1@example.com, sender2@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 01 Jan 2024 12:00:00 +0000

Body content."""
        
        email = parse_email_content(content)
        assert email is not None
        assert len(email.from_addr) > 0

    def test_email_with_cc_and_bcc(self):
        """Test parsing email with CC and BCC."""
        content = """From: sender@example.com
To: recipient@example.com
Cc: cc1@example.com, cc2@example.com
Bcc: bcc1@example.com
Subject: Test Email
Date: Mon, 01 Jan 2024 12:00:00 +0000

Body content."""
        
        email = parse_email_content(content)
        assert email is not None
        assert "cc1@example.com" in email.raw_headers.get("Cc", "")
        assert "bcc1@example.com" in email.raw_headers.get("Bcc", "")

    def test_email_with_special_characters_in_body(self):
        """Test parsing email with special characters in body."""
        content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 01 Jan 2024 12:00:00 +0000

Special chars: <>&"' and newlines
and more text."""
        
        email = parse_email_content(content)
        assert email is not None
        assert "<>&" in email.body_plain

    def test_email_with_long_subject(self):
        """Test parsing email with very long subject."""
        long_subject = "A" * 1000
        content = f"""From: sender@example.com
To: recipient@example.com
Subject: {long_subject}
Date: Mon, 01 Jan 2024 12:00:00 +0000

Body content."""
        
        email = parse_email_content(content)
        assert email is not None
        assert email.subject == long_subject


# Fixtures for test data
@pytest.fixture
def mock_email():
    """Create a mock email with basic headers."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    msg['Date'] = 'Mon, 01 Jan 2024 12:00:00 +0000'
    msg.set_payload('This is a plain text email body.')
    return msg


@pytest.fixture
def mock_email_multi():
    """Create a mock email with multiple recipients."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient1@example.com, recipient2@example.com'
    msg['Subject'] = 'Test Subject'
    msg['Date'] = 'Mon, 01 Jan 2024 12:00:00 +0000'
    msg.set_payload('Body')
    return msg


@pytest.fixture
def mock_email_empty():
    """Create a mock email with empty headers."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['Subject'] = 'Test Subject'
    msg.set_payload('Body')
    return msg


@pytest.fixture
def mock_email_display():
    """Create a mock email with display names."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = '"Sender Name" <sender@example.com>'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    msg.set_payload('Body')
    return msg


@pytest.fixture
def mock_email_plain():
    """Create a mock email with plain text body."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    msg.set_payload('This is a plain text email body.')
    return msg


@pytest.fixture
def mock_email_html():
    """Create a mock email with HTML body."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    msg.set_content('<html><body><p>HTML content</p></body></html>', subtype='html')
    return msg


@pytest.fixture
def mock_email_multipart():
    """Create a mock email with multipart body."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    
    msg.set_content('Plain text version')
    msg.add_alternative('<html><body>HTML version</body></html>', subtype='html')
    return msg


@pytest.fixture
def mock_email_empty_body():
    """Create a mock email with empty body."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    return msg


@pytest.fixture
def mock_email_with_attachment():
    """Create a mock email with attachment."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    
    msg.set_content('Email body')
    msg.add_attachment('Attachment content', filename='document.pdf')
    return msg


@pytest.fixture
def mock_email_multiple_attachments():
    """Create a mock email with multiple attachments."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    
    msg.set_content('Email body')
    msg.add_attachment('File 1', filename='file1.txt')
    msg.add_attachment('File 2', filename='file2.pdf')
    return msg


@pytest.fixture
def mock_email_no_attachment():
    """Create a mock email without attachments."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    msg.set_payload('Body content')
    return msg


@pytest.fixture
def mock_email_inline_attachment():
    """Create a mock email with inline attachment."""
    from email.message import EmailMessage
    from email.policy import default
    
    msg = EmailMessage(policy=default)
    msg['From'] = 'sender@example.com'
    msg['To'] = 'recipient@example.com'
    msg['Subject'] = 'Test Subject'
    
    msg.set_content('Email body')
    msg.add_attachment('Image data', filename='image.png', disposition='inline')
    return msg


@pytest.fixture
def sample_eml_file(tmp_path):
    """Create a sample .eml file for testing."""
    eml_file = tmp_path / "test.eml"
    eml_file.write_text("""From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 01 Jan 2024 12:00:00 +0000

This is a test email body.""")
    return eml_file
