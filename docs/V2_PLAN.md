# ReconForge v2: plan

> **Status:** planning in progress. Nothing has been built yet.
> This is a living document. Decisions are added as they are agreed.

ReconForge v2 is a clean rewrite. It ships as one fast binary with a full terminal dashboard, a chained recon pipeline, any AI provider, and a memory of every target it has scanned.

---

## Decisions so far

| # | Topic | Decision | Why / notes |
|---|---|---|---|
| 1 | Rewrite or evolve | **Clean v2.0 rewrite.** Breaking CLI changes are fine. | Reuse the good parts of v1 (crt.sh parsing, scope matching rules, their tests) as the spec. |
| 2 | Language | **Go** | Compiles in seconds. Ships as one binary with nothing else to install, for Linux, macOS and Windows on Intel and ARM. Handles thousands of network connections easily. Has the best terminal-dashboard libraries (Bubble Tea). Most modern recon tools are written in Go. |
| 3 | Who it's for | **Bug bounty, pentests and your own infrastructure.** Covers the core recon well. | Full pentest features (exploitation, heavy vulnerability scanning) are out of scope for now and may come later. |
| 4 | Background scans | **Later.** In v2.0, scans run inside the dashboard. Quitting while a scan runs asks first. | The scan engine is kept separate from the screens, so a background service can be added later without a rewrite. |
| 5 | Naming | A **target** is a name plus its scope plus its rules. | Neutral across bug bounty programs, client engagements and your own assets. |

## Topics

| # | Topic | State |
|---|---|---|
| 1 | Language and install | Decided: Go |
| 2 | Core model: one workspace per target, with scan history (new / changed / gone) | Proposed. The dashboard draft assumes it. |
| 3 | Pipeline: what runs, in what order, how steps feed each other | Not started |
| 4 | Scope and safety rules | Not started |
| 5 | AI: providers (any provider, or a custom OpenAI-compatible URL) and what the AI does | Not started |
| 6 | Terminal dashboard | **In discussion.** Draft below. |
| 7 | CLI commands | Not started |
| 8 | Roadmap | Not started |

---

## Terminal dashboard (draft, in discussion)

Typing `reconforge` with no arguments opens the dashboard. Every action in it is also available as a plain CLI command, for scripts.

### Layout rules

- **Sidebar** on the left lists the sections. Number keys `1`–`9` jump straight to one.
- **Top bar** shows the current target, how many scans are running, and AI spend today.
- **Bottom bar** always lists the keys for the current screen, so there's nothing to memorise.
- **`Ctrl+K` command palette** works from anywhere: type a few letters to run a tool, start a scan, or jump to a screen.
- **`/`** filters whatever list you're looking at. **`?`** shows help for the current screen.
- Arrow keys and vim keys (`j`/`k`) both work. The mouse works too, but nothing requires it.
- Narrow terminals (under 100 columns): the sidebar shrinks to numbers and detail panes move below the list.
- Scans keep running while you move around the dashboard.

### Sections

| You asked for | Where it lives |
|---|---|
| The target | **Targets**: scope rules, a live "is this in scope?" tester, per-target rules (rate limit, required headers, max intensity, AI allowed), stats |
| Running scans | **Scans ▸ Running**: per-step progress, live feed, pause, cancel, change speed |
| Finished scans | **Scans ▸ Finished**: every past scan with what changed; opens the report |
| The report | Opens from a finished scan: tabs for summary, changes, hosts, web apps, TLS, notes; export to md / html / json / csv |
| History | **Scans ▸ Finished** (scan history), **History** (everything you did and every request sent), plus a timeline on every host |
| Tools, easy and fast | **`Ctrl+K` palette** from anywhere, plus a **Tools** section (DNS, cert, HTTP request, decoders, and more) |
| Settings | **Settings**: AI providers, API keys, speed limits, DNS resolvers, proxy (Burp / Caido), look and feel, keys |
| *Proposed additions* | **Dashboard** (home), **Inbox** (new findings to go through one by one), **Assets** (search everything found), **AI** (copilot chat) |

### Home

```text
╭─ ReconForge ────┬────────────────────────────────── target: acme ── 2 running ── AI today $0.42 ─╮
│                 │                                                                                │
│  ▸ Dashboard    │  TARGETS                              RUNNING                                  │
│    Targets      │  acme      198 hosts  +4 new          #142 acme    standard  ███████░░░  71%   │
│    Scans   (2)  │  globex     57 hosts  +0              #143 globex  quick     ██░░░░░░░░  18%   │
│    Inbox   (6)  │  initech   812 hosts  +21                                                      │
│    Assets       │                                                                                │
│    Reports      │  WHAT CHANGED · last 24h              ALERTS                                   │
│    Tools        │  + jenkins.acme.com       92          ! cert expires in 3d   pay.acme.com      │
│    AI           │  + staging-api.acme.com   87          ! takeover candidate   docs.acme.com     │
│    Settings     │  ~ grafana.acme.com  11.0 -> 11.2     ! 429s on cdn.acme.com, auto-slowed      │
│    History      │  - old.acme.com  gone (NXDOMAIN)                                               │
│                 │                                                                                │
╰─────────────────┴────────────────────────────────────────────────────────────────────────────────╯
  ^K palette   n new scan   i inbox   / search   ? help              scope: strict   ● 34 req/s
```

### Target

```text
╭─ Targets ▸ acme ────────────────────────────┬─────────────────────────── bug bounty · HackerOne ─╮
│                                             │                                                    │
│  SCOPE                                      │  RULES FOR THIS TARGET                             │
│  in    *.acme.com                           │  max intensity    normal                           │
│  in    api.acme.io                          │  rate limit       10 req/s                         │
│  in    203.0.113.0/24                       │  required header  X-Bug-Bounty: yourhandle         │
│  out   blog.acme.com                        │  user agent       ReconForge (+yourhandle)         │
│  out   *.cdn.acme.com                       │  AI allowed       local models only                │
│                                             │                                                    │
│  TEST  > admin.acme.com_                    │  STATS                                             │
│        in scope, matched *.acme.com         │  198 hosts · 61 services · 47 web apps             │
│                                             │  last scan #142 · 2h ago · took 6m12s              │
│                                             │                                                    │
├─────────────────────────────────────────────┴────────────────────────────────────────────────────┤
│  a add rule   d delete   i import scope (HackerOne / Bugcrowd / file)   e edit rules   r run     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Running scan

```text
╭─ Scans ▸ Running ▸ #142 ─────────────────────────────────────────────── acme · standard · 6m12s ─╮
│                                                                                                  │
│  MODULE              PROGRESS                    OUT        NOTES                                │
│  passive.subdomains  ████████████████████ done   312 names  7 sources, virustotal 429 -> retry   │
│  dns.resolve         ████████████████████ done   204 live   41 wildcard answers dropped          │
│  scope.gate          ████████████████████        198 in     6 out of scope, never contacted      │
│  port.scan           ██████████████░░░░░░  70%   61 svc     23 CDN edge IPs skipped              │
│  http.probe          ██████████░░░░░░░░░░  52%   47 apps    12 look-alike clusters               │
│  tls.inspect         ██████████░░░░░░░░░░  52%   +3 names   fed back from cert SANs              │
│  tech.detect         ██████████░░░░░░░░░░  52%   31 techs                                        │
│  score + ai.triage   waiting                                                                     │
│                                                                                                  │
├─ live ───────────────────────────────────────────────────────────────────────────────────────────┤
│  12:04:31  http.probe   200   https://jenkins.acme.com        "Dashboard [Jenkins]"              │
│  12:04:31  tls.inspect  SAN   ci-internal.acme.com            in scope -> queued                 │
│  12:04:30  port.scan    open  staging-api.acme.com:8443/tcp                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  p pause   c cancel   + / - rate (34 req/s)   l log   f filter   esc back (scan keeps running)   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Finished scans (history)

```text
╭─ Scans ▸ Finished ───────────────────────────────────────────────────────────────── all targets ─╮
│                                                                                                  │
│    #    TARGET    PIPELINE   STARTED        TOOK     RESULT                  CHANGES             │
│  ▸ 142  acme      standard   today 10:58    6m12s    198 hosts · 47 apps     +4  ~1  -2          │
│    141  acme      quick      Nov 24 09:12   1m40s    195 hosts · 44 apps     +2                  │
│    140  initech   deep       Nov 23 22:05   41m03s   812 hosts · 230 apps    +21 ~6              │
│    139  globex    passive    Nov 23 18:30   38s       57 hosts               —                   │
│    138  acme      standard   Nov 19 11:02   6m45s    194 hosts · 43 apps     +9  -1              │
│                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  enter open report   d diff with previous   R run again   e export   x delete   / filter         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Report

```text
╭─ Report ▸ acme ▸ scan #142 ─────────────── 1 summary  2 changes  3 hosts  4 web  5 tls  6 notes ─╮
│                                                                                                  │
│  198 hosts · 61 services · 47 web apps · 12 look-alike clusters                                  │
│  Since scan #138 (Nov 19):  4 new · 1 changed · 2 gone                                           │
│                                                                                                  │
│  TOP PRIORITIES                                                                                  │
│  92  jenkins.acme.com        new CI server, login page exposed, no WAF in front                  │
│  87  staging-api.acme.com    /debug/vars open here, 404 on prod                                  │
│  74  grafana.acme.com        version changed 11.0 -> 11.2                                        │
│                                                                                                  │
│  AI SUMMARY  (analyst model)                                                                     │
│  Most of this week's new surface is build and staging infrastructure. The CI server              │
│  and staging API both appeared after the Nov 19 scan and sit outside the CDN ...                 │
│                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  1-6 jump to section   / search   e export md / html / json / csv   a redo AI summary            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Command palette

```text
╭─ Command palette ───────────────────────────────────────────────────────── ctrl+k ─╮
│  > dns                                                                             │
│                                                                                    │
│  ▸ tool dns            Look up A / AAAA / CNAME / MX / TXT / NS / CAA for a name   │
│    tool dns-brute      Brute-force names with wildcard filtering                   │
│    run passive         Passive-only pipeline on the current target                 │
│    assets has:cname    Jump to assets that have CNAME records                      │
│    settings resolvers  Edit and health-check DNS resolvers                         │
╰────────────────────────────────────────────────────────────────────────────────────╯
```

### More screens (proposed)

**Inbox.** New findings land here and you go through them one key at a time, like email: interesting, tested, ignore, snooze.

```text
╭─ Inbox · acme ───────────────────────────────────────────────────── 6 new since your last visit ─╮
│                                                                                                  │
│  ▸ 92  jenkins.acme.com        Jenkins login, no WAF, certificate issued 2 days ago              │
│    87  staging-api.acme.com    /debug/vars answers 200 here, 404 on prod api.acme.com            │
│    74  grafana.acme.com        Grafana login, version moved 11.0 -> 11.2                         │
│    55  uat.acme.com            Basic auth realm "UAT" on a new IP outside the CDN                │
│    41  docs.acme.com           CNAME -> acme.github.io: "There isn't a GitHub Pages site"        │
│    12  cdn2.acme.com           Same page as 14 other hosts (cluster #3), auto-collapsed          │
│                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  i interesting   t tested   x ignore   s snooze 7d   a ask AI   r rescan   enter details         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**Assets.** Everything found for a target, searchable with a short query language, with a detail pane.

```text
╭─ Assets · acme ─────────────────────────────────────────────────────────────────────── 6 of 198 ─╮
│  / tech:jenkins OR port:8080 new:7d !tag:tested                             sort: score ▾        │
├───────────────────────────────────────────────────────────┬──────────────────────────────────────┤
│  SCORE  HOST                    PORT  CODE  TITLE / TECH  │ jenkins.acme.com:443                 │
│  ▸ 92   jenkins.acme.com         443   200  Jenkins       │ first seen  2d ago (scan #141)       │
│    87   staging-api.acme.com    8443   200  Express       │ ip          203.0.113.17  AS64500    │
│    74   grafana.acme.com         443   302  Grafana 11.2  │ tls         expires 88d · 4 SANs     │
│    61   ci-internal.acme.com    8080   403  nginx 1.18    │ tech        Jenkins · Jetty · Java   │
│    55   uat.acme.com             443   401  Basic auth    │ score       92 = new + CI server     │
│    48   api-v1.acme.com          443   200  nginx  (x14)  │             + login + no WAF         │
│                                                           │ tags        —                        │
│                                                           │                                      │
│                                                           │ 1 response  2 headers  3 tls         │
│                                                           │ 4 history   5 notes    6 ai          │
├───────────────────────────────────────────────────────────┴──────────────────────────────────────┤
│  enter open  t tag  n note  r rescan  a ask AI  b send to Burp  o browser  y copy  e export      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**AI copilot.** Ask questions about the target's data. The AI can read the workspace, but it only *proposes* scans; you confirm each one, and scope rules still apply.

```text
╭─ AI copilot ──────────────────────── claude/claude-sonnet-5-5 · context: acme · this chat $0.03 ─╮
│                                                                                                  │
│  you  which hosts look non-prod and expose something prod doesn't?                               │
│                                                                                                  │
│  ai   tool  query_assets(host ~ "stag|dev|uat|test", code:200)   -> 9 rows                       │
│       tool  diff_assets(staging-api.acme.com, api.acme.com)     -> 3 differences                 │
│                                                                                                  │
│       Three stand out:                                                                           │
│       1. staging-api.acme.com  /debug/vars returns 200 (prod: 404). Go's expvar exposes          │
│          cmdline flags and memstats. Next: one GET to /debug/pprof/.                             │
│       2. uat.acme.com  Basic auth on a fresh IP outside the CDN. Next: check whether the         │
│          same app is reachable via the CDN hostname without auth.                                │
│       3. ci-internal.acme.com  nginx 403 on 8080, sibling of jenkins.acme.com ...                │
│                                                                                                  │
│  you  run a top-1000 port scan on those 9                                                        │
│                                                                                                  │
│  ai   Proposed  port.scan top-1000 on 9 hosts   (9/9 in scope)                                   │
│       ~9,000 probes at 10 req/s ≈ 15 min        enter run   e edit   esc cancel                  │
│                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  > _                                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**Settings.**

```text
╭─ Settings ──────────────┬────────────────────────────────────────────────────────────────────────╮
│                         │                                                                        │
│   General               │  AI PROVIDERS                                         a add   t test   │
│   Targets & scope       │                                                                        │
│   Rate & concurrency    │  ● claude       anthropic           keychain    ok   420 ms            │
│   DNS resolvers         │  ● local        ollama              —           ok    90 ms            │
│   Proxy (Burp / Caido)  │  ● openrouter   openai-compatible   env var     ok   610 ms            │
│   Data sources & keys   │  ○ work-vllm    openai-compatible   keychain    unreachable            │
│ ▸ AI providers & roles  │                                                                        │
│   Budgets & privacy     │  ROLES                                                                 │
│   Notifications         │  triage    local/llama3.1:8b           bulk scoring of every asset     │
│   Appearance            │  analyst   claude/claude-opus-5-5      reports, deep hypotheses        │
│   Keybindings           │  chat      claude/claude-sonnet-5-5    copilot                         │
│   Storage               │  vision    claude/claude-sonnet-5-5    screenshot classification       │
│                         │                                                                        │
╰─────────────────────────┴────────────────────────────────────────────────────────────────────────╯
```

### Open questions on the dashboard

1. Sidebar on the left (as drawn), or tabs along the top?
2. What opens first: the home screen, or the last target you worked on?
3. Keep the Inbox idea?

---

## Parked for later

- Background scans that keep running after the terminal closes, scheduled rescans, and alerts (Discord / Slack / Telegram)
- Full pentest features (exploitation, heavy vulnerability scanning)
