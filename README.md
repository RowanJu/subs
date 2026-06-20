# subs

A portable **agent skill** that analyzes your SaaS subscription spending — **spend
summary**, **waste detection** (duplicates, overlaps, price hikes, forgotten
subs), **renewal tracking**, and **savings recommendations** — output as a
markdown report and a self-contained HTML dashboard.

It works with **any coding agent that can follow a `SKILL.md`** (Claude Code, or
any agent you point at this skill). It pulls bank transactions via the **Plaid
CLI**, enriches them with **Gmail receipts**, runs deterministic recurrence
detection, and reconciles everything into a `subscriptions.yaml` ledger that each
run updates rather than re-deriving.

```
Plaid CLI ──► transactions ─┐
                            ├─► detect recurring ─► reconcile into ─► report (.md + .html)
Gmail receipts ─────────────┘   (deterministic)     subscriptions.yaml
```

## Install

Clone the repo, then make it available to your agent:

```bash
git clone git@github.com:RowanJu/subs.git
```

- **Claude Code** — symlink it into your skills dir, then run `/subs`:
  ```bash
  ln -s "$(pwd)/subs" ~/.claude/skills/subs
  ```
- **Any other coding agent** — point it at this folder's `SKILL.md` (add the folder
  to the agent's skills/rules, or just tell the agent to follow `SKILL.md`).
  Throughout the skill, `<skill-dir>` refers to this cloned folder.

## Prerequisites

- A **coding agent** (Claude Code, or any agent that follows `SKILL.md`).
- A **Gmail connector/MCP** available to the agent (e.g. Claude Code's Gmail
  connector) — for receipts.
- **Plaid CLI** — `brew install plaid/plaid-cli/plaid`, then `plaid login` + `plaid link`.
- **jq** — `brew install jq` (ships on most macs).

## Usage

1. `plaid login` + `plaid link` (once per bank).
2. Invoke the skill from any folder you want as your data workspace — in Claude
   Code, `/subs`; in other agents, ask it to run the subs skill / follow `SKILL.md`.
   It pulls bank data + Gmail receipts, builds `subscriptions.yaml`, and writes a
   dated report to `reports/`.
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
