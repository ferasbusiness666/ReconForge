# ReconForge JSON Output

ReconForge machine-readable payloads use schema version `1.0`.

Every command that emits JSON includes:

```json
{
  "schema_version": "1.0",
  "command": "subdomains",
  "errors": []
}
```

Within schema `1.x`, fields may be added but existing field meanings and types remain stable. Removing, renaming, or changing the type of a documented field requires a new schema major version.

## Command Payloads

### `subdomains`

- `domain`: requested domain
- `subdomains`: normalized hostnames
- `resolvable_only`: whether DNS filtering was requested
- `resolutions`: hostname-to-address mapping when DNS filtering is enabled
- `errors`: provider and unexpected resolver errors

### `portscan`

- `host`: scanned host
- `profile`: selected profile
- `workers`: bounded worker count
- `results`: rows containing `host`, `port`, `status`, `banner`, and `error`
- `errors`: per-port errors that did not stop the scan

Port status values are `open`, `closed`, `filtered/timeout`, and `error`.

### `techdetect`

- `url`: final URL
- `status_code`: HTTP status or `null`
- `headers`: selected response headers
- `technologies`: lightweight indicators
- `errors`: request or input errors

### `httpprobe`

- `input`: source host file
- `workers`: bounded worker count
- `results`: ordered host groups
- `errors`: host-level unexpected errors

Each probe contains `url`, `final_url`, `status_code`, `title`, `content_length`, `content_type`, `server`, `technologies`, `ok`, and `error`.

### `scopecheck`

- `in_scope`: target and match-reason rows
- `out_of_scope`: target and reason rows
- `errors`: input errors

### `github`

- `owner`: requested GitHub owner
- `repo`: requested repository or `null`
- `repos`: normalized repository results
- `rate_limit`: `limit`, `remaining`, and `reset`
- `errors`: API, rate-limit, or network errors

### `report`

- `output`: markdown output path
- `written`: whether the report was written
- `hard_failure`: whether invalid input prevented report creation
- `sources`: merged JSON inputs when `--from-json` is used
- `hosts`: hosts represented in port findings
- `scope_notes`: normalized scope notes
- `errors`: collection or input errors

### `summarize`

- `report`: source markdown report
- `summary`: AI-ready text
- `errors`: input errors

## Merging Saved Results

Repeat `--from-json` to merge command outputs:

```powershell
reconforge report `
  --from-json subdomains.json `
  --from-json ports.json `
  --from-json http.json `
  --from-json scope.json `
  --output reports/merged.md
```

ReconForge deduplicates subdomains, port rows, GitHub repositories, HTTP probe groups, errors, and scope notes while preserving their first-seen order. Unversioned ReconForge JSON from earlier releases remains accepted.

An unreadable, malformed, or non-object input is a hard failure. ReconForge does not write a partial merged report when a requested input file is invalid.
