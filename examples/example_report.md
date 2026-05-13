# ReconForge Report: example.com

**Generated:** 2026-05-12 14:30:00 UTC
**Target domain:** `example.com`

## Summary

- Subdomains found: **4**
- Hosts scanned for ports: **3**
- Technology fingerprints collected: **3**

## Subdomains Found

- `api.example.com`
- `cdn.example.com`
- `login.example.com`
- `www.example.com`

## Port Scan Results

### `www.example.com`

| Port | Status | Banner / Note |
| --- | --- | --- |
| 80 | open | HTTP/1.1 301 Moved Permanently Server: nginx |
| 443 | open | No banner |
| 8080 | filtered/timeout | Connection timed out |
| 8443 | closed | Connection refused |

### `api.example.com`

| Port | Status | Banner / Note |
| --- | --- | --- |
| 443 | open | No banner |
| 8080 | open | HTTP/1.1 403 Forbidden Server: nginx |
| 3306 | filtered/timeout | Connection timed out |

## Detected Technologies

### `https://www.example.com`

- HTTP status: `200`
- Technologies: `nginx`, `HSTS`, `Content Security Policy`

| Header | Value |
| --- | --- |
| `Server` | `nginx` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `Content-Security-Policy` | `default-src 'self'` |

### `https://api.example.com`

- HTTP status: `403`
- Technologies: `Cloudflare`, `Express.js`

| Header | Value |
| --- | --- |
| `CF-Ray` | `sample-ray-id` |
| `X-Powered-By` | `Express` |

## GitHub Recon

| Repository | Stars | Forks | Language | Default Branch | Updated | Flags | URL |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| example-api | 42 | 8 | Python | main | 2026-05-10T12:00:00Z | - | https://github.com/example/example-api |

### `example-api`

- Detected tech stack: `Docker`, `Python`
- Interesting files: `README.md`, `requirements.txt`, `Dockerfile`, `.github/workflows/ci.yml`, `.env.example`
- Recon notes:
  - CI/CD workflows detected
  - Docker usage detected
  - Environment example file present
  - Python project indicators detected

## Scope Notes

- example.com: matched exact host example.com
- api.example.com: matched wildcard *.example.com
- cdn.example.com: matched wildcard *.example.com
- login.example.com: matched wildcard *.example.com
- www.example.com: matched wildcard *.example.com

## Collection Notes

- crt.sh request failed: 502 Server Error.
- Treat all findings as recon leads until manually validated.
