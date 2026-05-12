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

## Open Ports and Banners

### `www.example.com`

| Port | Status | Banner |
| --- | --- | --- |
| 80 | open | HTTP/1.1 301 Moved Permanently Server: nginx |
| 443 | open | No banner |

### `api.example.com`

| Port | Status | Banner |
| --- | --- | --- |
| 443 | open | No banner |
| 8080 | open | HTTP/1.1 403 Forbidden Server: nginx |

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

## Scope Notes

- `*.example.com` matched wildcard scope.
- `staging.thirdparty.net` was excluded because no scope rule matched.

## Collection Notes

- `login.example.com:8443` timed out during banner grabbing.
- Treat all findings as recon leads until manually validated.
