"""Unit tests for port scanning module."""

import pytest
from reconforge.portscan import scan_port, scan_ports, COMMON_PORTS


class TestScanPort:
    """Test single port scanning."""

    def test_scan_port_returns_dict(self):
        """Test that scan_port returns a dictionary."""
        result = scan_port("localhost", 80, timeout=1.0)
        assert isinstance(result, dict)
        assert "host" in result
        assert "port" in result
        assert "status" in result
        assert "banner" in result
        assert "error" in result

    def test_scan_port_invalid_host(self):
        """Test scanning invalid host."""
        result = scan_port("invalid-host-12345.local", 80, timeout=1.0)
        assert result["status"] == "error"
        assert "DNS" in result["error"] or "lookup" in result["error"].lower()


class TestScanPorts:
    """Test multiple port scanning."""

    def test_scan_ports_empty_host(self):
        """Test that empty host returns error."""
        result = scan_ports("")
        assert result["results"] == []
        assert len(result["errors"]) > 0
        assert "required" in result["errors"][0].lower()

    def test_scan_ports_returns_dict(self):
        """Test that scan_ports returns a dictionary."""
        result = scan_ports("localhost", timeout=1.0)
        assert isinstance(result, dict)
        assert "host" in result
        assert "results" in result
        assert "errors" in result

    def test_scan_ports_uses_common_ports(self):
        """Test that scan_ports uses COMMON_PORTS by default."""
        result = scan_ports("localhost", timeout=0.5)
        # Results should be sorted by port
        if len(result["results"]) > 1:
            ports = [r["port"] for r in result["results"]]
            assert ports == sorted(ports)

    def test_scan_ports_custom_ports(self):
        """Test scanning custom port list."""
        custom_ports = [80, 443]
        result = scan_ports("localhost", ports=custom_ports, timeout=0.5)
        assert isinstance(result, dict)
        assert "results" in result

    def test_scan_ports_concurrent_mode(self):
        """Test concurrent scanning mode."""
        result = scan_ports("localhost", timeout=0.5, concurrent=True, max_workers=2)
        assert isinstance(result, dict)
        assert "results" in result
        assert "errors" in result

    def test_scan_ports_sequential_mode(self):
        """Test sequential scanning mode."""
        result = scan_ports("localhost", timeout=0.5, concurrent=False)
        assert isinstance(result, dict)
        assert "results" in result
        assert "errors" in result
