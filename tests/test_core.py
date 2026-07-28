"""Focused regression tests for ReconForge core behavior."""

from __future__ import annotations

import socket
import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner
import requests

from reconforge import __version__
from reconforge.cli import cli
from reconforge.config import load_config
from reconforge.github_recon import (
    detect_repo_tech,
    fetch_interesting_files,
    github_get,
    github_headers,
    parse_repo,
)
from reconforge.httpprobe import extract_title, probe_host, probe_hosts_file
from reconforge.portscan import resolve_ports, scan_port, scan_ports
from reconforge.report import generate_report, generate_report_from_json
from reconforge.summarize import summarize_report
from reconforge.subdomains import fetch_subdomains, filter_resolvable


class PortScanTests(unittest.TestCase):
    """Port scanning status behavior."""

    def test_resolve_ports_supports_profiles_and_custom_ports(self) -> None:
        self.assertIn(3000, resolve_ports(profile="normal"))
        self.assertIn(9200, resolve_ports(profile="deep"))
        self.assertEqual(resolve_ports(profile="deep", ports_text="80,443,3000"), [80, 443, 3000])

    def test_resolve_ports_rejects_invalid_ports(self) -> None:
        with self.assertRaises(ValueError):
            resolve_ports(ports_text="80,99999")

    @patch("reconforge.portscan.socket.create_connection", side_effect=socket.timeout)
    def test_connect_timeout_is_filtered_timeout(self, _mock_connect: Mock) -> None:
        result = scan_port("example.com", 8080, timeout=0.1)

        self.assertEqual(result["status"], "filtered/timeout")
        self.assertIn("timed out", result["error"].lower())

    @patch("reconforge.portscan.grab_banner", return_value="No banner")
    @patch("reconforge.portscan.socket.create_connection")
    def test_banner_timeout_after_connect_stays_open(self, mock_connect: Mock, _mock_banner: Mock) -> None:
        mock_socket = Mock()
        mock_connect.return_value.__enter__.return_value = mock_socket

        result = scan_port("example.com", 443, timeout=0.1)

        self.assertEqual(result["status"], "open")
        self.assertEqual(result["banner"], "No banner")

    @patch("reconforge.portscan.scan_port")
    def test_scan_ports_keeps_partial_results_after_port_error(self, mock_scan: Mock) -> None:
        mock_scan.side_effect = [
            {"host": "example.com", "port": 80, "status": "open", "banner": "HTTP", "error": ""},
            {"host": "example.com", "port": 443, "status": "error", "banner": "", "error": "socket failed"},
            {"host": "example.com", "port": 8080, "status": "closed", "banner": "", "error": "Connection refused"},
        ]

        result = scan_ports("example.com", ports=[80, 443, 8080], workers=2)

        self.assertEqual([row["port"] for row in result["results"]], [80, 443, 8080])
        self.assertEqual(result["results"][2]["status"], "closed")
        self.assertIn("443: socket failed", result["errors"])


class ReportTests(unittest.TestCase):
    """Markdown report generation behavior."""

    @patch("reconforge.report.detect_technologies", return_value={"errors": [], "technologies": [], "headers": {}, "status_code": None})
    @patch("reconforge.report.scan_ports", return_value={"results": [], "errors": []})
    @patch("reconforge.report.fetch_subdomains", return_value=([], []))
    def test_generate_report_creates_parent_directory(self, _subs: Mock, _ports: Mock, _tech: Mock) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "nested" / "example.md"

            result = generate_report("example.com", str(output))

            self.assertTrue(output.exists())
            self.assertEqual(result["output"], str(output))

    @patch("reconforge.report.detect_technologies", return_value={"errors": [], "technologies": [], "headers": {}, "status_code": None})
    @patch("reconforge.report.scan_ports", return_value={"results": [], "errors": []})
    @patch("reconforge.report.fetch_subdomains", return_value=(["api.example.com"], []))
    def test_generate_report_includes_scope_notes(self, _subs: Mock, _ports: Mock, _tech: Mock) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            scope = Path(temp_dir) / "scope.txt"
            output = Path(temp_dir) / "reports" / "example.md"
            scope.write_text("example.com\n*.example.com\n", encoding="utf-8")

            generate_report("example.com", str(output), scope_file=str(scope))

            markdown = output.read_text(encoding="utf-8")
            self.assertIn("example.com: matched exact host example.com", markdown)
            self.assertIn("api.example.com: matched wildcard *.example.com", markdown)

    def test_generate_report_from_json_uses_saved_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "recon.json"
            output = Path(temp_dir) / "report.md"
            source.write_text(
                json.dumps(
                    {
                        "domain": "example.com",
                        "subdomains": ["api.example.com"],
                        "ports": {"example.com": [{"port": 80, "status": "open", "banner": "HTTP", "error": ""}]},
                        "technologies": {},
                        "github": {},
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )

            result = generate_report_from_json(str(source), str(output))

            self.assertTrue(output.exists())
            self.assertEqual(result["output"], str(output))
            self.assertIn("api.example.com", output.read_text(encoding="utf-8"))

    def test_generate_report_from_multiple_json_files_merges_command_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subdomains = root / "subdomains.json"
            ports = root / "ports.json"
            probes = root / "probes.json"
            scope = root / "scope.json"
            output = root / "report.md"
            subdomains.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "command": "subdomains",
                        "domain": "example.com",
                        "subdomains": ["api.example.com"],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            ports.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "command": "portscan",
                        "host": "example.com",
                        "results": [{"port": 443, "status": "open", "banner": "No banner", "error": ""}],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            probes.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "command": "httpprobe",
                        "results": [
                            {
                                "host": "api.example.com",
                                "probes": [
                                    {
                                        "status_code": 200,
                                        "content_length": 42,
                                        "server": "nginx",
                                        "technologies": ["nginx"],
                                        "title": "API",
                                        "final_url": "https://api.example.com/",
                                    }
                                ],
                            }
                        ],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            scope.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "command": "scopecheck",
                        "in_scope": [{"target": "api.example.com", "reason": "matched wildcard *.example.com"}],
                        "out_of_scope": [],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )

            result = generate_report_from_json(
                [str(subdomains), str(ports), str(probes), str(scope)],
                str(output),
            )

            markdown = output.read_text(encoding="utf-8")
            self.assertTrue(result["written"])
            self.assertEqual(len(result["sources"]), 4)
            self.assertIn("api.example.com", markdown)
            self.assertIn("| 443 | open | No banner |", markdown)
            self.assertIn("https://api.example.com/", markdown)
            self.assertIn("matched wildcard *.example.com", markdown)

    @patch("reconforge.report.detect_technologies", side_effect=RuntimeError("tech collector failed"))
    @patch("reconforge.report.scan_ports", side_effect=RuntimeError("port collector failed"))
    @patch("reconforge.report.fetch_subdomains", return_value=([], ["provider failed"]))
    def test_generate_report_writes_collection_notes_after_collector_failures(
        self, _subs: Mock, _ports: Mock, _tech: Mock
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.md"

            result = generate_report("example.com", str(output))

            markdown = output.read_text(encoding="utf-8")
            self.assertIn("## Collection Notes", markdown)
            self.assertIn("provider failed", markdown)
            self.assertIn("Port scan failed for example.com", markdown)
            self.assertIn("Technology detection failed for example.com", markdown)
            self.assertGreaterEqual(len(result["errors"]), 3)

    def test_report_from_malformed_json_is_hard_failure(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("bad.json").write_text("{not json", encoding="utf-8")
            result = runner.invoke(cli, ["report", "--from-json", "bad.json", "--output", "report.md"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Invalid JSON", result.output)
        self.assertNotIn("Report written", result.output)


class SummaryTests(unittest.TestCase):
    """AI-ready summary behavior."""

    def test_summarize_report_compacts_markdown_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "report.md"
            report.write_text("# ReconForge Report: example.com\n\n## Summary\n\n- Subdomains found: **1**\n\n## Collection Notes\n\n- crt.sh failed\n", encoding="utf-8")

            summary = summarize_report(str(report))

            self.assertIn("AI-ready ReconForge summary", summary["summary"])
            self.assertIn("Subdomains found", summary["summary"])
            self.assertEqual(summary["errors"], [])


class CliJsonTests(unittest.TestCase):
    """JSON CLI output behavior."""

    @patch("reconforge.cli.fetch_subdomains", return_value=(["api.example.com"], ["provider failed"]))
    def test_subdomains_json_outputs_machine_readable_payload(self, _fetch: Mock) -> None:
        result = CliRunner().invoke(cli, ["subdomains", "-d", "example.com", "--json"])

        self.assertEqual(result.exit_code, 0)
        payload = json.loads(result.output)
        self.assertEqual(payload["subdomains"], ["api.example.com"])
        self.assertEqual(payload["errors"], ["provider failed"])
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertEqual(payload["command"], "subdomains")

    @patch("reconforge.cli.scan_ports", return_value={"host": "example.com", "results": [{"port": 80, "status": "open", "banner": "HTTP", "error": ""}], "errors": []})
    def test_portscan_json_outputs_machine_readable_payload(self, _scan: Mock) -> None:
        result = CliRunner().invoke(cli, ["portscan", "-t", "example.com", "--json"])

        self.assertEqual(result.exit_code, 0)
        payload = json.loads(result.output)
        self.assertEqual(payload["results"][0]["status"], "open")

    @patch("reconforge.cli.fetch_subdomains", return_value=(["api.example.com"], []))
    def test_subdomains_output_writes_file(self, _fetch: Mock) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "nested" / "subs.txt"
            result = CliRunner().invoke(cli, ["subdomains", "-d", "example.com", "--output", str(output)])

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(output.read_text(encoding="utf-8").strip(), "api.example.com")

    @patch("reconforge.cli.scan_ports", return_value={"host": "example.com", "results": [], "errors": []})
    def test_portscan_reads_default_profile_from_config(self, mock_scan: Mock) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("reconforge.json").write_text('{"portscan": {"profile": "normal"}}', encoding="utf-8")
            result = runner.invoke(cli, ["portscan", "-t", "example.com", "--json"])

        self.assertEqual(result.exit_code, 0)
        called_ports = mock_scan.call_args.kwargs["ports"]
        self.assertIn(3000, called_ports)

    def test_cli_version_matches_package_version(self) -> None:
        result = CliRunner().invoke(cli, ["--version"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(__version__, result.output)

    def test_invalid_subdomain_input_returns_nonzero_pure_json(self) -> None:
        result = CliRunner().invoke(cli, ["subdomains", "-d", "not-a-domain", "--json"])

        self.assertNotEqual(result.exit_code, 0)
        payload = json.loads(result.output)
        self.assertIn("Invalid domain", payload["errors"][0])

    def test_invalid_techdetect_url_returns_nonzero_pure_json(self) -> None:
        result = CliRunner().invoke(cli, ["techdetect", "-u", "example.com", "--json"])

        self.assertNotEqual(result.exit_code, 0)
        payload = json.loads(result.output)
        self.assertIn("must start with", payload["errors"][0])

    @patch("reconforge.cli.fetch_subdomains", return_value=([], []))
    def test_quiet_suppresses_normal_terminal_output(self, _fetch: Mock) -> None:
        result = CliRunner().invoke(cli, ["subdomains", "-d", "example.com", "--quiet"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "")

    def test_report_cli_merges_repeated_from_json_options(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("subdomains.json").write_text(
                json.dumps(
                    {
                        "command": "subdomains",
                        "domain": "example.com",
                        "subdomains": ["api.example.com"],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            Path("ports.json").write_text(
                json.dumps(
                    {
                        "command": "portscan",
                        "host": "example.com",
                        "results": [{"port": 80, "status": "open", "banner": "HTTP", "error": ""}],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            result = runner.invoke(
                cli,
                [
                    "report",
                    "--from-json",
                    "subdomains.json",
                    "--from-json",
                    "ports.json",
                    "--output",
                    "report.md",
                    "--quiet",
                ],
            )

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output, "")
            self.assertIn("api.example.com", Path("report.md").read_text(encoding="utf-8"))


class ConfigTests(unittest.TestCase):
    """Config loading behavior."""

    def test_load_config_reads_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "reconforge.json"
            config.write_text('{"portscan": {"profile": "normal"}}', encoding="utf-8")

            data, errors = load_config(str(config))

            self.assertEqual(errors, [])
            self.assertEqual(data["portscan"]["profile"], "normal")


class HttpProbeTests(unittest.TestCase):
    """HTTP probe behavior."""

    def test_extract_title_returns_compact_title(self) -> None:
        self.assertEqual(extract_title("<html><title> Example Site </title></html>"), "Example Site")

    @patch("reconforge.httpprobe.requests.get")
    def test_probe_host_checks_https_and_http(self, mock_get: Mock) -> None:
        first = Mock()
        first.url = "https://example.com/"
        first.status_code = 200
        first.text = "<title>Example</title>"
        first.content = first.text.encode()
        first.headers = {
            "Content-Length": "512",
            "Content-Type": "text/html",
            "Server": "nginx",
        }
        second = Mock()
        second.url = "http://example.com/"
        second.status_code = 301
        second.text = ""
        second.content = b""
        second.headers = {"Server": "cloudflare", "CF-Ray": "abc"}
        mock_get.side_effect = [first, second]

        rows = probe_host("example.com", timeout=0.1)

        self.assertEqual(rows[0]["url"], "https://example.com")
        self.assertEqual(rows[0]["title"], "Example")
        self.assertEqual(rows[0]["content_length"], 512)
        self.assertEqual(rows[0]["server"], "nginx")
        self.assertIn("nginx", rows[0]["technologies"])
        self.assertEqual(rows[1]["status_code"], 301)
        self.assertIn("Cloudflare", rows[1]["technologies"])

    @patch("reconforge.httpprobe.probe_host")
    def test_probe_hosts_file_keeps_results_when_one_host_fails(self, mock_probe: Mock) -> None:
        def fake_probe(host: str, timeout: float) -> list[dict[str, object]]:
            if host == "bad.example":
                raise RuntimeError("unexpected probe failure")
            return [{"url": f"https://{host}", "ok": True, "status_code": 200, "error": ""}]

        mock_probe.side_effect = fake_probe
        with tempfile.TemporaryDirectory() as temp_dir:
            targets = Path(temp_dir) / "targets.txt"
            targets.write_text("good.example\nbad.example\nlater.example\n", encoding="utf-8")

            result = probe_hosts_file(str(targets), timeout=0.1, workers=2)

        self.assertEqual([row["host"] for row in result["results"]], ["good.example", "bad.example", "later.example"])
        self.assertIn("bad.example: unexpected probe failure", result["errors"])
        self.assertTrue(result["results"][2]["probes"][0]["ok"])


class SubdomainTests(unittest.TestCase):
    """Subdomain provider fallback behavior."""

    @patch("reconforge.subdomains.requests.get")
    def test_fetch_subdomains_merges_fallback_provider_when_crtsh_fails(self, mock_get: Mock) -> None:
        crt_response = Mock()
        crt_response.raise_for_status.side_effect = requests.HTTPError("502 Server Error")
        ht_response = Mock()
        ht_response.raise_for_status.return_value = None
        ht_response.text = "api.example.com,1.2.3.4\n*.www.example.com,1.2.3.5\n"
        certspotter_response = Mock()
        certspotter_response.raise_for_status.return_value = None
        certspotter_response.json.return_value = [{"dns_names": ["dev.example.com", "*.api.example.com"]}]
        mock_get.side_effect = [crt_response, ht_response, certspotter_response]

        subdomains, errors = fetch_subdomains("example.com", timeout=0.1)

        self.assertEqual(subdomains, ["api.example.com", "dev.example.com", "www.example.com"])
        self.assertTrue(any("crt.sh" in error for error in errors))

    @patch("reconforge.subdomains.socket.getaddrinfo")
    def test_filter_resolvable_keeps_only_dns_answers(self, mock_getaddrinfo: Mock) -> None:
        def fake_getaddrinfo(hostname: str, _port: object, type: object) -> list[tuple[object, ...]]:
            if hostname == "dead.example.com":
                raise socket.gaierror("not found")
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.10", 0))]

        mock_getaddrinfo.side_effect = fake_getaddrinfo

        names, resolutions, errors = filter_resolvable(
            ["api.example.com", "dead.example.com"],
            workers=2,
        )

        self.assertEqual(names, ["api.example.com"])
        self.assertEqual(resolutions["api.example.com"], ["192.0.2.10"])
        self.assertEqual(errors, [])


class GitHubReconTests(unittest.TestCase):
    """GitHub recon parsing and detection behavior."""

    def test_github_headers_never_exposes_token_value(self) -> None:
        headers = github_headers("secret-token")

        self.assertEqual(headers["Authorization"], "Bearer secret-token")

    def test_parse_repo_detects_metadata_and_files(self) -> None:
        repo = parse_repo(
            {
                "name": "demo",
                "description": "API service",
                "html_url": "https://github.com/acme/demo",
                "stargazers_count": 5,
                "forks_count": 2,
                "language": "Python",
                "default_branch": "main",
                "updated_at": "2026-05-12T00:00:00Z",
                "archived": False,
                "private": False,
                "fork": False,
            },
            files=["requirements.txt", "Dockerfile", ".github/workflows/ci.yml", ".env.example"],
        )

        self.assertIn("Python", repo["tech_stack"])
        self.assertIn("Docker", repo["tech_stack"])
        self.assertIn("Docker usage detected", repo["recon_notes"])
        self.assertIn("CI/CD workflows detected", repo["recon_notes"])
        self.assertIn("Environment example file present", repo["recon_notes"])

    def test_detect_repo_tech_from_files(self) -> None:
        tech, notes = detect_repo_tech(
            "TypeScript",
            ["package.json", "next.config.js", "vercel.json", "SECURITY.md", ".github/dependabot.yml", "terraform/main.tf"],
        )

        self.assertIn("TypeScript", tech)
        self.assertIn("Node.js", tech)
        self.assertIn("Next.js", tech)
        self.assertIn("Possible deployment configuration detected", notes)
        self.assertIn("Security policy file present", notes)
        self.assertIn("Dependency automation detected", notes)
        self.assertIn("Infrastructure-as-code indicators detected", notes)

    @patch("reconforge.github_recon.requests.get")
    def test_github_get_reports_rate_limit_without_token(self, mock_get: Mock) -> None:
        response = Mock()
        response.status_code = 403
        response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": "1780000000",
        }
        response.reason = "rate limit exceeded"
        mock_get.return_value = response

        data, errors, status, rate_limit = github_get("/users/example", token=None, timeout=0.1)

        self.assertIsNone(data)
        self.assertEqual(status, 403)
        self.assertIn("GITHUB_TOKEN", errors[0])
        self.assertEqual(rate_limit["remaining"], 0)
        self.assertNotIn("secret", " ".join(errors))

    @patch("reconforge.github_recon.github_get")
    def test_fetch_interesting_files_uses_single_tree_request(self, mock_get: Mock) -> None:
        mock_get.return_value = (
            {
                "tree": [
                    {"path": "README.md", "type": "blob"},
                    {"path": "Dockerfile", "type": "blob"},
                    {"path": ".github/workflows/ci.yml", "type": "blob"},
                    {"path": "src/app.py", "type": "blob"},
                ]
            },
            [],
            200,
            {"remaining": 58, "limit": 60, "reset": 1780000000},
        )

        files, errors, rate_limit = fetch_interesting_files("acme", "demo", "main", None, 0.1)

        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(files, [".github/workflows/ci.yml", "Dockerfile", "README.md"])
        self.assertEqual(errors, [])
        self.assertEqual(rate_limit["remaining"], 58)


if __name__ == "__main__":
    unittest.main()
