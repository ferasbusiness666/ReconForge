"""Unit tests for technology detection module."""

import pytest
from reconforge.techdetect import infer_technologies, detect_technologies


class TestInferTechnologies:
    """Test technology inference."""

    def test_infer_from_server_header(self):
        """Test technology inference from Server header."""
        headers = {"Server": "nginx/1.19.0"}
        body = ""
        techs = infer_technologies(headers, body)
        assert "nginx" in techs

    def test_infer_from_powered_by(self):
        """Test technology inference from X-Powered-By header."""
        headers = {"X-Powered-By": "Express"}
        body = ""
        techs = infer_technologies(headers, body)
        assert "Express.js" in techs

    def test_infer_hsts(self):
        """Test HSTS detection."""
        headers = {"Strict-Transport-Security": "max-age=31536000"}
        body = ""
        techs = infer_technologies(headers, body)
        assert "HSTS" in techs

    def test_infer_csp(self):
        """Test CSP detection."""
        headers = {"Content-Security-Policy": "default-src 'self'"}
        body = ""
        techs = infer_technologies(headers, body)
        assert "Content Security Policy" in techs

    def test_infer_from_body(self):
        """Test technology inference from response body."""
        headers = {}
        body = "<html><script>console.log('React')</script></html>"
        techs = infer_technologies(headers, body)
        assert "React" in techs

    def test_infer_multiple_technologies(self):
        """Test inferring multiple technologies."""
        headers = {
            "Server": "nginx",
            "X-Powered-By": "Express",
            "Strict-Transport-Security": "max-age=31536000",
        }
        body = ""
        techs = infer_technologies(headers, body)
        assert len(techs) >= 3
        assert "nginx" in techs
        assert "Express.js" in techs
        assert "HSTS" in techs


class TestDetectTechnologies:
    """Test technology detection."""

    def test_detect_invalid_url(self):
        """Test that invalid URLs return errors."""
        result = detect_technologies("invalid-url")
        assert result["status_code"] is None
        assert len(result["errors"]) > 0
        assert "http" in result["errors"][0].lower()

    def test_detect_returns_dict(self):
        """Test that detect_technologies returns a dictionary."""
        result = detect_technologies("http://localhost:9999", timeout=0.5)
        assert isinstance(result, dict)
        assert "url" in result
        assert "status_code" in result
        assert "headers" in result
        assert "technologies" in result
        assert "errors" in result
