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
| 7 | Dashboard layout | **Tabs along the top**, keys `1`–`9`. | Replaces the sidebar from the first ASCII draft. |

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
It's clickable and uses sample data. Nothing in it scans.
A standalone copy is in [`v2-dashboard-prototype.html`](v2-dashboard-prototype.html), which opens in any browser.

### Decided

- Typing `reconforge` opens the dashboard on **New scan**. The **History** button (or `H`) goes to the History tab.
- **Tabs along the top**: `1` New scan · `2` Running · `3` History · `4` Targets · `5` Assets · `6` Inbox · `7` Tools · `8` AI · `9` Settings.
- The bottom bar always shows the keys for the current screen. `Ctrl+K` opens the command palette anywhere. `?` shows help.
- Arrow keys, vim keys (`j`/`k`) and the mouse all work. Scans keep running while you switch tabs.

### Screens

| Tab | What's on it |
|---|---|
| New scan | Pick a target (or create one), pick a pipeline (Passive / Quick / Standard / Deep / Custom), set options, dry run, start. Side panel: History button, recent scans, running scans. |
| Running | Every running scan; per-step progress, live feed, pause, cancel, change speed. |
| History | All scans with filters and search; what changed in each; open the report; run again. |
| Report | Summary, top priorities, AI summary, collection notes; tabs for changes, hosts, web apps, TLS, notes; export md / html / json / csv. |
| Targets | Scope rules (in / out, exclusions win), live "is this in scope?" tester, per-target rules, import scope from bug bounty platforms. |
| Assets | Everything found, filtered with a short query (`tech:jenkins port:8443 score>60 new !tag:tested`); detail pane with stored response, headers, TLS, history, notes, AI. |
| Inbox | New findings to go through one key at a time: interesting, tested, ignore, snooze. |
| Tools | HTTP request, DNS, certificate, port check, quick subdomains, domain owner, IP owner, favicon hash, scope test, encode / decode, JWT, CIDR. |
| AI | Copilot chat about a target's data. It can read the workspace but only proposes scans; you confirm each one. |
| Settings | AI providers and per-role models, AI budget and privacy, data source keys, speed limits, DNS resolvers, proxy (Burp / Caido), appearance, keyboard, storage. |

### Rules the prototype already shows

- A target's rules limit what any scan can do: max intensity (Deep is blocked on a bug bounty target set to normal), rate limit, required header, and whether AI is allowed (off / local models only / any model).
- Pipeline steps run at the same time and feed each other. For example, names found in certificates go back into the scan.
- "What changed" compares a scan with the last scan of the same target that ran the same steps.
- Any AI provider works: presets for Anthropic, OpenAI, Google Gemini, OpenRouter, Groq, Together, DeepSeek, Mistral, xAI, Fireworks, Ollama, LM Studio and vLLM, plus a custom OpenAI-compatible URL. Each role (triage, analyst, chat, vision) gets its own model.
- API keys are stored in the system keychain, never passed on the command line.

### Open questions

1. Keep the Inbox tab?
2. Anything to add, move or drop on any screen?

---

## Parked for later

- Background scans that keep running after the terminal closes, scheduled rescans, and alerts (Discord / Slack / Telegram)
- Full pentest features (exploitation, heavy vulnerability scanning)
