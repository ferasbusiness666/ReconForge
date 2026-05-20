"""Export utilities for different output formats (JSON, CSV, HTML)."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def export_json(data: Dict[str, Any], output_path: str) -> None:
    """Export data to JSON format."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def export_csv_subdomains(subdomains: List[str], output_path: str) -> None:
    """Export subdomains to CSV."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Subdomain"])
        for subdomain in subdomains:
            writer.writerow([subdomain])


def export_csv_ports(port_results: Dict[str, List[Dict[str, Any]]], output_path: str) -> None:
    """Export port scan results to CSV."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Host", "Port", "Status", "Banner"])
        
        for host, results in port_results.items():
            for result in results:
                writer.writerow([
                    host,
                    result.get("port"),
                    result.get("status"),
                    result.get("banner", ""),
                ])


def export_csv_technologies(
    tech_results: Dict[str, Dict[str, Any]],
    output_path: str
) -> None:
    """Export technology detection results to CSV."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Status Code", "Technology"])
        
        for url, result in tech_results.items():
            techs = result.get("technologies", [])
            if techs:
                for tech in techs:
                    writer.writerow([
                        url,
                        result.get("status_code"),
                        tech,
                    ])
            else:
                writer.writerow([
                    url,
                    result.get("status_code"),
                    "No clear fingerprints",
                ])


def export_html_report(
    domain: str,
    findings: Dict[str, Any],
    output_path: str
) -> None:
    """Export findings as a styled HTML report."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    subdomains = findings.get("subdomains", []) or []
    port_results = findings.get("ports", {}) or {}
    tech_results = findings.get("technologies", {}) or {}
    errors = findings.get("errors", []) or []
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReconForge Report: {domain}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .summary-card h3 {{
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:hover {{
            background: #f9f9f9;
        }}
        
        .status-open {{
            color: #27ae60;
            font-weight: bold;
        }}
        
        .status-closed {{
            color: #e74c3c;
        }}
        
        .status-error {{
            color: #e67e22;
        }}
        
        .tech-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            margin: 4px;
            font-size: 0.9em;
        }}
        
        .error-box {{
            background: #fee;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}
        
        .footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .empty {{
            color: #999;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 ReconForge Report</h1>
            <p>{domain}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Summary</h2>
                <div class="summary">
                    <div class="summary-card">
                        <h3>Subdomains Found</h3>
                        <div class="value">{len(subdomains)}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Hosts Scanned</h3>
                        <div class="value">{len(port_results)}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Technologies</h3>
                        <div class="value">{len(tech_results)}</div>
                    </div>
                </div>
                <p><strong>Generated:</strong> {timestamp}</p>
            </div>
            
            <div class="section">
                <h2>🌐 Subdomains</h2>
                {_render_subdomains_table(subdomains)}
            </div>
            
            <div class="section">
                <h2>🔓 Open Ports</h2>
                {_render_ports_table(port_results)}
            </div>
            
            <div class="section">
                <h2>🧬 Technologies</h2>
                {_render_technologies_table(tech_results)}
            </div>
            
            {_render_errors_section(errors)}
        </div>
        
        <div class="footer">
            <p>Generated by <strong>ReconForge</strong> - AI-assisted recon toolkit for bug bounty hunters</p>
            <p><a href="https://github.com/ferasbusiness666/ReconForge" style="color: #667eea;">View on GitHub</a></p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output, "w", encoding="utf-8") as f:
        f.write(html_content)


def _render_subdomains_table(subdomains: List[str]) -> str:
    """Render subdomains as HTML table."""
    if not subdomains:
        return '<div class="empty">No subdomains discovered</div>'
    
    rows = "\n".join([f"<tr><td><code>{s}</code></td></tr>" for s in subdomains])
    return f"""
    <table>
        <thead>
            <tr><th>Subdomain</th></tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """


def _render_ports_table(port_results: Dict[str, List[Dict[str, Any]]]) -> str:
    """Render port scan results as HTML table."""
    if not port_results:
        return '<div class="empty">No port scan results</div>'
    
    rows = []
    for host, results in port_results.items():
        open_ports = [r for r in results if r.get("status") == "open"]
        if open_ports:
            for result in open_ports:
                status_class = f"status-{result.get('status', 'unknown')}"
                rows.append(f"""
                <tr>
                    <td><code>{host}</code></td>
                    <td>{result.get('port')}</td>
                    <td class="{status_class}">{result.get('status')}</td>
                    <td>{result.get('banner', '')}</td>
                </tr>
                """)
    
    if not rows:
        return '<div class="empty">No open ports found</div>'
    
    return f"""
    <table>
        <thead>
            <tr><th>Host</th><th>Port</th><th>Status</th><th>Banner</th></tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """


def _render_technologies_table(tech_results: Dict[str, Dict[str, Any]]) -> str:
    """Render technology detection results as HTML."""
    if not tech_results:
        return '<div class="empty">No technology fingerprints</div>'
    
    rows = []
    for url, result in tech_results.items():
        techs = result.get("technologies", [])
        tech_html = " ".join([f'<span class="tech-badge">{t}</span>' for t in techs])
        if not tech_html:
            tech_html = '<span class="tech-badge">No clear fingerprints</span>'
        
        rows.append(f"""
        <tr>
            <td><code>{url}</code></td>
            <td>{result.get('status_code', 'N/A')}</td>
            <td>{tech_html}</td>
        </tr>
        """)
    
    return f"""
    <table>
        <thead>
            <tr><th>URL</th><th>Status</th><th>Technologies</th></tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """


def _render_errors_section(errors: List[str]) -> str:
    """Render errors section if any."""
    if not errors:
        return ""
    
    error_boxes = "\n".join([f'<div class="error-box">{e}</div>' for e in errors])
    return f"""
    <div class="section">
        <h2>⚠️ Collection Notes</h2>
        {error_boxes}
    </div>
    """
