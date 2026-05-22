"""Optional web server for viewing ReconForge reports and dashboards."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
    import threading
except ImportError:
    HTTPServer = None


class ReconForgeHTTPHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for ReconForge reports."""

    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/" or path == "/index.html":
            self.serve_dashboard()
        elif path.startswith("/api/"):
            self.serve_api(path)
        elif path.endswith(".html"):
            self.serve_file(path)
        else:
            self.send_error(404)

    def serve_dashboard(self) -> None:
        """Serve the dashboard HTML."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ReconForge Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                h1 { color: #333; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                .stat-card { background: #667eea; color: white; padding: 20px; border-radius: 8px; }
                .stat-value { font-size: 2em; font-weight: bold; }
                .stat-label { font-size: 0.9em; opacity: 0.9; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th { background: #667eea; color: white; padding: 10px; text-align: left; }
                td { padding: 10px; border-bottom: 1px solid #ddd; }
                tr:hover { background: #f9f9f9; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 ReconForge Dashboard</h1>
                <p>Welcome to ReconForge! This is a placeholder dashboard.</p>
                <p>To view your reports, place HTML files in the current directory.</p>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">0</div>
                        <div class="stat-label">Scans</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">0</div>
                        <div class="stat-label">Subdomains</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">0</div>
                        <div class="stat-label">Open Ports</div>
                    </div>
                </div>
                <h2>Available Reports</h2>
                <p>No reports found. Generate reports using the CLI and they will appear here.</p>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_api(self, path: str) -> None:
        """Serve API endpoints."""
        if path == "/api/reports":
            self.serve_reports_list()
        else:
            self.send_error(404)

    def serve_reports_list(self) -> None:
        """Serve list of available reports."""
        reports = []
        for html_file in Path(".").glob("*.html"):
            reports.append({
                "name": html_file.name,
                "path": f"/{html_file.name}",
                "size": html_file.stat().st_size,
            })

        response = json.dumps({"reports": reports})
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())

    def serve_file(self, path: str) -> None:
        """Serve a file."""
        file_path = Path(path.lstrip("/"))
        if file_path.exists() and file_path.is_file():
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default logging."""
        pass


class ReconForgeWebServer:
    """Web server for ReconForge reports."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize web server."""
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the web server."""
        if HTTPServer is None:
            raise ImportError("HTTP server not available")

        self.server = HTTPServer((self.host, self.port), ReconForgeHTTPHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        print(f"🌐 ReconForge web server running at http://{self.host}:{self.port}")
        print("Press Ctrl+C to stop")

    def stop(self) -> None:
        """Stop the web server."""
        if self.server:
            self.server.shutdown()
            print("Web server stopped")

    def run(self) -> None:
        """Run the web server (blocking)."""
        self.start()
        try:
            if self.thread:
                self.thread.join()
        except KeyboardInterrupt:
            self.stop()


def start_webserver(host: str = "localhost", port: int = 8000) -> None:
    """Start ReconForge web server."""
    server = ReconForgeWebServer(host, port)
    server.run()
