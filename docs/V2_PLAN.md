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
| 6 | Opening screen | **New scan.** A **History** button (key `H`) opens the History tab with every scan. | Decided on Nov 26. |
| 7 | Dashboard layout | **Tabs along the top**, keys `1`–`7`. | Replaces the sidebar from the first ASCII draft. |
| 8 | Dashboard style | **A real terminal UI**: character grid, box-drawing borders, `[x]` checkboxes, `( )` radio buttons, status bar. No web-style cards or buttons. | It's a CLI tool, so the prototype shows exactly what the Go app will draw. |
| 9 | Simpler layout | **7 tabs**: Scan, Running, History, Targets, Tools, AI, Settings. **Inbox dropped**; new findings are marked *new* in History and reports. **Assets merged** into the report's Hosts tab. | Fewer places to look; each screen has one job. |
| 10 | Mouse | **Full mouse support**: click tabs, buttons, rows and fields; the wheel scrolls lists, the live log and chat. Every action also has a key. | Bubble Tea mouse events, with click areas tracked by a zone helper (for example `lrstanley/bubblezone`). |

## Topics

| # | Topic | State |
|---|---|---|
| 1 | Language and install | Decided: Go |
| 2 | Core model: one workspace per target, with scan history (new / changed / gone) | Proposed. The dashboard draft assumes it. |
| 3 | Pipeline: what runs, in what order, how steps feed each other | Not started |
| 4 | Scope and safety rules | Not started |
| 5 | AI: providers (any provider, or a custom OpenAI-compatible URL) and what the AI does | Not started |
| 6 | Terminal dashboard | **In review:** clickable prototype, see below. |
| 7 | CLI commands | Not started |
| 8 | Roadmap | Not started |

---

## Terminal dashboard (in review)

**Prototype:** https://claude.ai/artifact/QESHZHnvGGpiDTaRGfGPNo
It's drawn as a character grid, exactly like the Go TUI will draw it, and it adapts to the window width the way a real terminal app does (two columns when wide, stacked when narrow). Click anything, scroll lists with the wheel, or use the keys. Nothing scans; all data is sample data.
A standalone copy is in [`v2-dashboard-prototype.html`](v2-dashboard-prototype.html), which opens in any browser.

### Decided

- Typing `reconforge` opens the dashboard on **Scan**. The **Open history** button (or `h`) goes to the History tab.
- **Tabs along the top**: `1` Scan · `2` Running · `3` History · `4` Targets · `5` Tools · `6` AI · `7` Settings.
- The line above the status bar always shows the keys for the current screen, and every key hint is clickable.
- `ctrl+k` opens the command palette anywhere. `?` shows help. `esc` goes back.
- The status bar shows running scans, current request rate, scope mode, AI spend, and messages (with an action button when useful, like "view report" when a scan finishes).
- Text fields work like a terminal input: click or press a key to focus, `enter` to submit, `esc` to leave.

### Screens

| Tab | What's on it |
|---|---|
| Scan | Target (radio list, or create one), Pipeline (Passive / Quick / Standard / Deep / Custom, with steps shown), Options (AI triage, screenshots, speed), Start scan and Dry run. Right side: Open history button, recent scans, running scans. |
| Running | Running scans on the left; for the selected scan: pause, cancel (with a confirm line), speed, every step with progress and counts, and a live log. |
| History | Filters for target and status; table of every scan with what changed; click a row to open its report. |
| Report | Summary (counts, what changed, top priorities, AI summary, collection notes), Changes, Hosts (filter + table + detail with the stored response, copy URL, send to Burp, ask AI), TLS. Run again; export md / html / json / csv. |
| Targets | Target list; scope rules with add and delete; live "is this in scope?" test; rules (intensity, rate limit, header, user agent, AI allowed). |
| Tools | HTTP request, DNS, certificate, port check, subdomains, domain owner, IP owner, favicon hash, scope test, decode, JWT, CIDR. One input line and the output below it. |
| AI | Chat about a target's data. The AI reads the workspace through tools and only proposes scans; you confirm each one. Follows the target's AI rule (off / local only / any). |
| Settings | AI models (providers, add any provider or a custom OpenAI-compatible URL, one model per role), API keys, Speed, Proxy, Look. |

### Rules the prototype already shows

- A target's rules limit what any scan can do: max intensity (Deep is blocked on a target set to normal), rate limit, required header, and whether AI is allowed.
- Pipeline steps run at the same time and feed each other. For example, names found in certificates go back into the scan.
- "What changed" compares a scan with the last scan of the same target that ran the same steps.
- API keys go to the system keychain, never on the command line.

### Open questions

1. Anything to add, move or drop on any screen?

---

## Parked for later

- Background scans that keep running after the terminal closes, scheduled rescans, and alerts (Discord / Slack / Telegram)
- Full pentest features (exploitation, heavy vulnerability scanning)
