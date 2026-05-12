# ReconForge AI Triage Prompts

Use these model-agnostic prompts with ChatGPT, Claude, Gemini, local LLMs, or any other assistant. Paste only data that you are authorized to test and avoid sharing secrets, tokens, or customer data.

## HTTP Response Analysis

You are assisting with authorized security testing. Analyze the following HTTP request and response for security-relevant observations. Focus on misconfigurations, risky headers, authentication clues, cache behavior, exposed versions, verbose errors, and likely next manual tests. Return: summary, evidence, risk, false-positive considerations, and prioritized next steps.

```text
<PASTE REQUEST/RESPONSE HERE>
```

## Unusual Headers

Review these HTTP headers from an authorized target. Identify uncommon, deprecated, conflicting, missing, or security-sensitive headers. Explain what each observation may imply and what safe validation steps should be performed next.

```text
<PASTE HEADERS HERE>
```

## Authentication Flow Review

Analyze this login, SSO, password reset, MFA, or session-management flow. Look for weak redirects, token leakage, missing CSRF protections, insecure cookies, predictable state parameters, IDOR opportunities, replay issues, and account enumeration signals. Provide a test plan that avoids destructive actions.

```text
<PASTE FLOW NOTES / REQUESTS / RESPONSES HERE>
```

## Sensitive Endpoint Triage

Given these discovered endpoints, classify which deserve priority review for sensitive data exposure, auth bypass, IDOR, SSRF, file access, debug behavior, or admin functionality. Include why each endpoint matters and a safe validation checklist.

```text
<PASTE ENDPOINT LIST HERE>
```

## JavaScript Findings

Review these JavaScript URLs or snippets from an authorized target. Identify API routes, feature flags, source maps, secrets-looking strings, authorization assumptions, client-side validation weaknesses, and framework clues. Do not assume a string is a valid secret without validation evidence.

```text
<PASTE JS URLS OR SNIPPETS HERE>
```

## API Behavior

Analyze these API requests and responses for authorization, object-level access control, mass assignment, pagination, filtering, rate limiting, CORS, content-type handling, and error-message risks. Suggest low-impact follow-up requests.

```text
<PASTE API TRAFFIC HERE>
```

## Parameter Anomalies

Review these parameters and observed behaviors. Identify parameters that may influence redirects, file paths, templates, SQL/NoSQL queries, GraphQL operations, object IDs, roles, prices, limits, or feature access. Propose safe payload categories without providing destructive exploitation instructions.

```text
<PASTE PARAMETER LIST AND BEHAVIOR HERE>
```

## Prioritization

Prioritize the following recon findings for a bug bounty report pipeline. Rank by likely impact, exploitability, confidence, program scope, and duplicate risk. For each item, provide: priority, rationale, evidence needed, and next validation step.

```text
<PASTE FINDINGS HERE>
```

## Report Drafting

Transform these validated findings into a concise security report draft. Include title, summary, affected asset, severity rationale, reproduction steps, impact, remediation, and evidence placeholders. Keep claims tied to the provided evidence.

```text
<PASTE VALIDATED FINDING NOTES HERE>
```
