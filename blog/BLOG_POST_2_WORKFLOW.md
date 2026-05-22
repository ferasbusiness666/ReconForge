# Bug Bounty Recon Workflow with ReconForge

**Published:** May 2026  
**Author:** Feras  
**Read Time:** 10 minutes  
**Difficulty:** Intermediate

## Introduction

Reconnaissance is the first and most critical phase of bug bounty hunting. A thorough recon can reveal hidden assets, misconfigurations, and potential vulnerabilities before you even start active testing.

In this guide, I'll walk you through a complete bug bounty recon workflow using ReconForge, sharing real-world tips and tricks I've learned from hundreds of engagements.

## The Complete Workflow

```
1. Target Scoping
   ↓
2. Subdomain Discovery
   ↓
3. Port Scanning
   ↓
4. Technology Detection
   ↓
5. Vulnerability Analysis
   ↓
6. Report Generation
   ↓
7. Active Testing
```

## Step 1: Target Scoping

Before you scan, define your scope clearly.

**What to include:**
- Primary domain (example.com)
- Wildcard subdomains (*.example.com)
- IP ranges (if provided)
- Acquisition domains (recently acquired companies)

**What to exclude:**
- Third-party services
- Partner domains
- Out-of-scope IP ranges
- Staging/development environments (unless explicitly in scope)

**Pro tip:** Always get written authorization. Screenshot the scope from the bug bounty platform.

## Step 2: Subdomain Discovery

Start with comprehensive subdomain enumeration.

### Basic Discovery

```bash
reconforge subdomains -d example.com --output subdomains.txt
```

**What you get:**
- All subdomains from certificate transparency logs
- Typically 50-500 subdomains for large organizations
- Fast (usually <1 minute)

### Analyzing Subdomains

```bash
# Count subdomains
wc -l subdomains.txt

# Find interesting patterns
grep -E "(admin|api|staging|dev|test)" subdomains.txt

# Check for subdomain takeover candidates
grep -E "(cdn|s3|github|heroku)" subdomains.txt
```

### Filtering Results

Not all subdomains are interesting. Filter strategically:

```bash
# Remove staging/dev (usually out of scope)
grep -v -E "(staging|dev|test|qa)" subdomains.txt > production.txt

# Focus on API subdomains
grep "api" subdomains.txt > api_subdomains.txt

# Find internal-looking subdomains
grep -E "(internal|private|admin)" subdomains.txt > internal.txt
```

**Pro tip:** Some organizations have hundreds of subdomains. Focus on production systems first.

## Step 3: Port Scanning

Scan for open ports on discovered subdomains.

### Quick Scan (Top 20 Ports)

```bash
# Scan first 10 subdomains for common ports
for subdomain in $(head -10 production.txt); do
    reconforge portscan -t $subdomain --concurrent
done
```

### Comprehensive Scan (All Common Ports)

```bash
# Create a batch scan
reconforge batch-scan --input production.txt --output port_results.json
```

### Analyzing Results

```bash
# Find interesting ports
grep -E "(22|3306|5432|6379|27017)" port_results.json

# Find all open ports
grep '"status": "open"' port_results.json
```

**Common interesting ports:**

| Port | Service | Risk |
|------|---------|------|
| 22 | SSH | High (if exposed) |
| 3306 | MySQL | Critical |
| 5432 | PostgreSQL | Critical |
| 6379 | Redis | Critical |
| 27017 | MongoDB | Critical |
| 8080 | HTTP Alt | Medium |
| 9000 | SonarQube | Medium |
| 3000 | Node.js Dev | Medium |

**Pro tip:** Exposed databases are gold. Check for authentication requirements.

## Step 4: Technology Detection

Identify what technologies are running.

### Detect Technologies

```bash
# Scan all subdomains
for subdomain in $(cat production.txt); do
    reconforge techdetect -u https://$subdomain
done
```

### Analyze Technologies

```bash
# Find specific frameworks
grep -i "wordpress" tech_results.json
grep -i "joomla" tech_results.json
grep -i "drupal" tech_results.json

# Find outdated versions
grep -i "php/5" tech_results.json
grep -i "apache/2.2" tech_results.json
```

### Security Headers Analysis

```bash
# Check for missing security headers
grep -L "Strict-Transport-Security" tech_results.json
grep -L "Content-Security-Policy" tech_results.json
grep -L "X-Frame-Options" tech_results.json
```

**Pro tip:** Missing security headers often indicate misconfigurations. Document them for your report.

## Step 5: Vulnerability Analysis

Use ReconForge's analysis engine to identify potential vulnerabilities.

### Generate Risk Assessment

```python
from reconforge.api import ReconForgeAPI
from reconforge.analyzer import FindingsAnalyzer
import json

api = ReconForgeAPI()

# Scan domain
result = api.generate_report("example.com", "findings.json")

# Load findings
with open("findings.json") as f:
    findings = json.load(f)

# Analyze
analyzer = FindingsAnalyzer(findings)

# Get risk assessment
risk = analyzer.get_risk_assessment()
print(f"Risk Score: {risk['risk_score']}/100")
print(f"Risk Level: {risk['risk_level']}")

# Get vulnerabilities
vulns = analyzer.find_potential_vulnerabilities()
for vuln in vulns:
    print(f"- {vuln['finding']} ({vuln['severity']})")
```

### Manual Vulnerability Hunting

Based on findings, manually check for:

1. **Subdomain Takeover**
   ```bash
   # Check if subdomain resolves
   nslookup subdomain.example.com
   
   # Check if CNAME points to unclaimed service
   dig subdomain.example.com CNAME
   ```

2. **Exposed APIs**
   ```bash
   # Check for API endpoints
   curl -s https://api.example.com/v1/
   curl -s https://api.example.com/swagger.json
   ```

3. **Misconfigurations**
   ```bash
   # Check for common misconfigurations
   curl -s -I https://example.com
   curl -s https://example.com/.well-known/
   ```

4. **Outdated Software**
   - Check version numbers
   - Search for known vulnerabilities (CVE)
   - Test common exploits

## Step 6: Report Generation

Generate a professional report for the organization.

### Create Comprehensive Report

```bash
reconforge report -d example.com \
    --output report.md \
    --format md
```

### Report Structure

```markdown
# Security Assessment Report

## Executive Summary
- Scope: example.com
- Date: 2026-05-20
- Findings: X critical, Y high, Z medium

## Methodology
- Subdomain discovery via certificate transparency
- Port scanning on discovered hosts
- Technology fingerprinting
- Vulnerability analysis

## Findings
### Critical
- [Finding 1]
- [Finding 2]

### High
- [Finding 3]

### Medium
- [Finding 4]

## Remediation
- [Recommendation 1]
- [Recommendation 2]

## Timeline
- Discovered: 2026-05-20
- Reported: 2026-05-20
- Expected Fix: 2026-06-20
```

**Pro tip:** Always include remediation steps. Organizations appreciate actionable recommendations.

## Step 7: Active Testing

Now that you've mapped the target, begin active testing.

### Testing Checklist

- [ ] Test discovered APIs for authentication bypass
- [ ] Check for CORS misconfigurations
- [ ] Test for SQL injection on found parameters
- [ ] Check for XSS vulnerabilities
- [ ] Test for broken access control
- [ ] Check for sensitive data exposure
- [ ] Test for insecure deserialization
- [ ] Check for SSRF vulnerabilities

**Pro tip:** Use tools like Burp Suite, OWASP ZAP, or Nuclei to automate testing.

## Real-World Example

Let's walk through a complete recon of a fictional company.

### Scenario: Acme Corp Bug Bounty

**Target:** acme.com  
**Scope:** *.acme.com, 10.0.0.0/24  
**Budget:** 1 week

### Day 1: Initial Reconnaissance

```bash
# Discover subdomains
reconforge subdomains -d acme.com

# Output: Found 127 subdomains
# Interesting ones: api.acme.com, admin.acme.com, dev.acme.com
```

### Day 2: Port Scanning

```bash
# Scan top subdomains
for subdomain in api.acme.com admin.acme.com dev.acme.com; do
    reconforge portscan -t $subdomain --concurrent
done

# Findings:
# - api.acme.com: 80, 443 open
# - admin.acme.com: 80, 443, 3000 open (Node.js dev server!)
# - dev.acme.com: 80, 443, 8080 open
```

### Day 3: Technology Detection

```bash
# Detect technologies
reconforge techdetect -u https://api.acme.com
reconforge techdetect -u https://admin.acme.com
reconforge techdetect -u https://dev.acme.com

# Findings:
# - api.acme.com: Node.js, Express, MongoDB
# - admin.acme.com: React, Node.js dev server (exposed!)
# - dev.acme.com: Python Flask, outdated version
```

### Day 4-5: Vulnerability Analysis

```bash
# Check for vulnerabilities
# - admin.acme.com has exposed dev server (port 3000)
# - dev.acme.com has outdated Flask version
# - api.acme.com missing security headers
```

### Day 6-7: Active Testing

```bash
# Test API for vulnerabilities
curl -X GET https://api.acme.com/users

# Test for authentication bypass
curl -X POST https://api.acme.com/login -d "user=admin&pass=admin"

# Check for CORS issues
curl -X OPTIONS https://api.acme.com -H "Origin: evil.com"
```

### Result

**Vulnerabilities Found:**
1. **Critical:** Exposed Node.js dev server on admin.acme.com:3000
2. **High:** Missing authentication on API endpoints
3. **High:** Outdated Flask version with known RCE vulnerability
4. **Medium:** Missing security headers
5. **Medium:** Exposed MongoDB instance on internal network

**Bounty:** $5,000 (varies by program)

## Tips & Tricks

### Tip 1: Automate Everything

```bash
#!/bin/bash
# recon.sh - Automated recon script

DOMAIN=$1

echo "Starting recon for $DOMAIN..."

# Discover subdomains
reconforge subdomains -d $DOMAIN --output subs.txt

# Scan ports
reconforge batch-scan --input subs.txt --output ports.json

# Detect technologies
for sub in $(cat subs.txt); do
    reconforge techdetect -u https://$sub
done

echo "Recon complete!"
```

### Tip 2: Use Caching

```bash
# First run: Takes 5 minutes
reconforge report -d example.com

# Second run: Takes 5 seconds (uses cache)
reconforge report -d example.com
```

### Tip 3: Combine with Other Tools

```bash
# Use ReconForge output with other tools
reconforge subdomains -d example.com | while read sub; do
    nuclei -u https://$sub -t cves/
done
```

### Tip 4: Track Changes

```bash
# Initial scan
reconforge report -d example.com --output scan1.json

# Later scan
reconforge report -d example.com --output scan2.json

# Compare
reconforge compare --scan1 scan1.json --scan2 scan2.json
```

## Common Mistakes to Avoid

1. **Scanning out-of-scope targets** - Always verify scope first
2. **Missing subdomains** - Use multiple discovery methods
3. **Ignoring staging environments** - They often have vulnerabilities
4. **Not checking security headers** - Easy wins for reports
5. **Rushing the recon phase** - Thorough recon = more vulnerabilities found

## Conclusion

A thorough reconnaissance phase is the foundation of successful bug bounty hunting. ReconForge automates the tedious parts, letting you focus on finding vulnerabilities.

**Key takeaways:**
1. Define scope clearly
2. Discover all subdomains
3. Scan for open ports
4. Detect technologies
5. Analyze for vulnerabilities
6. Generate professional reports
7. Conduct active testing

## Next Steps

- Try the workflow on a test domain
- Join bug bounty programs (HackerOne, Bugcrowd, etc.)
- Share your findings responsibly
- Keep learning and improving

---

**Questions?** Open a GitHub discussion or reach out on Twitter.

**Want more examples?** Check out the [examples directory](https://github.com/ferasbusiness666/ReconForge/tree/main/examples).
