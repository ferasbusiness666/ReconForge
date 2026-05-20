"""Unit tests for subdomain discovery module."""

import pytest
from reconforge.subdomains import is_valid_domain, normalize_name, fetch_subdomains


class TestValidation:
    """Test domain validation."""

    def test_valid_domain(self):
        """Test that valid domains pass validation."""
        assert is_valid_domain("example.com")
        assert is_valid_domain("sub.example.com")
        assert is_valid_domain("a.b.c.example.com")

    def test_invalid_domain(self):
        """Test that invalid domains fail validation."""
        assert not is_valid_domain("")
        assert not is_valid_domain("invalid")
        assert not is_valid_domain("-invalid.com")
        assert not is_valid_domain("invalid-.com")
        assert not is_valid_domain("invalid..com")

    def test_domain_normalization(self):
        """Test domain name normalization."""
        assert normalize_name("EXAMPLE.COM") == "example.com"
        assert normalize_name("*.example.com") == "example.com"
        assert normalize_name("*.*.example.com") == "example.com"
        assert normalize_name("example.com.") == "example.com"


class TestFetchSubdomains:
    """Test subdomain fetching."""

    def test_fetch_invalid_domain(self):
        """Test that invalid domains return errors."""
        subdomains, errors = fetch_subdomains("invalid")
        assert len(subdomains) == 0
        assert len(errors) > 0
        assert "Invalid domain" in errors[0]

    def test_fetch_empty_domain(self):
        """Test that empty domains return errors."""
        subdomains, errors = fetch_subdomains("")
        assert len(subdomains) == 0
        assert len(errors) > 0

    def test_fetch_returns_tuple(self):
        """Test that fetch_subdomains returns a tuple."""
        result = fetch_subdomains("example.com", timeout=5.0)
        assert isinstance(result, tuple)
        assert len(result) == 2
        subdomains, errors = result
        assert isinstance(subdomains, list)
        assert isinstance(errors, list)
