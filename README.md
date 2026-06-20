# subs

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![install: npx skills add](https://img.shields.io/badge/install-npx%20skills%20add-black)](https://github.com/vercel-labs/skills)
[![agents: Claude Code · Cursor · 68+](https://img.shields.io/badge/agents-Claude%20Code%20%C2%B7%20Cursor%20%C2%B7%2068%2B-blue)](https://github.com/vercel-labs/skills)

A portable **agent skill** that analyzes your SaaS subscription spending — **spend
summary**, **waste detection** (duplicates, overlaps, price hikes, forgotten
subs), **renewal tracking**, and **savings recommendations** — output as a
markdown report and a self-contained HTML dashboard.

Works with **Claude Code, Cursor, Cline, OpenCode, and 68+ agents** via the open
[`skills`](https://github.com/vercel-labs/skills) ecosystem. It pulls bank
transactions via the **Plaid CLI**, enriches them with **Gmail receipts**, runs
deterministic recurrence detection, and reconciles everything into a
`subscriptions.yaml` ledger that each run updates rather than re-deriving.

```
Plaid CLI ──► transactions ─┐
                            ├─► detect recurring ─► reconcile into ─► report (.md + .html)
Gmail receipts ─────────────┘   (deterministic)     subscriptions.yaml
```

## Install

Add it to your agent with the [`skills`](https://github.com/vercel-labs/skills) CLI:

```bash
npx skills@latest add RowanJu/subs              # auto-detects your agent
npx skills@latest add RowanJu/subs -a cursor    # or target one: claude-code, cursor, cline, …
```

<details>
<summary><b>Manual install</b></summary>

```bash
git clone git@github.com:RowanJu/subs.git
ln -s "$(pwd)/subs" ~/.claude/skills/subs   # Claude Code
```

For other agents, point them at the folder's `SKILL.md`. Throughout the skill,
`<skill-dir>` is wherever it's installed.
</details>

## Prerequisites

- A **coding agent** (Claude Code, Cursor, Cline, OpenCode, …).
- A **Gmail connector/MCP** available to the agent — for receipts.
- **Plaid CLI** — `brew install plaid/plaid-cli/plaid`, then `plaid login` + `plaid link`.
- **jq** — `brew install jq` (ships on most macs).

## Usage

1. `plaid login` + `plaid link` (once per bank).
2. Invoke the skill from any folder you want as your data workspace — in Claude
   Code, `/subs`; in other agents, ask it to run the **subs** skill. It pulls bank
   data + Gmail receipts, builds `subscriptions.yaml`, and writes a dated report to
   `reports/`.
3. Re-run anytime — it reconciles new data instead of starting over.

## Structure

```
SKILL.md                      the 5-step pipeline
scripts/detect_recurring.py   deterministic recurrence detector (stdlib only)
references/                   plaid, gmail, categories, recurrence, report templates
```

## 🔒 Privacy

This repo contains **only the skill** — no financial data. When you run it, your
ledger, reports, and raw bank data are created in your working directory and are
**gitignored** (`data/`, `reports/`, `subscriptions.yaml`); they never leave your
machine. Verify with `git status` before pushing.

## License

MIT — see [LICENSE](LICENSE).
