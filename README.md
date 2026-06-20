# subs

A Claude Code skill that analyzes your SaaS subscription spending — **spend
summary**, **waste detection** (duplicates, overlaps, price hikes, forgotten
subs), **renewal tracking**, and **savings recommendations** — output as a
markdown report and a self-contained HTML dashboard.

It pulls bank transactions via the **Plaid CLI**, enriches them with **Gmail
receipts**, runs deterministic recurrence detection, and reconciles everything
into a `subscriptions.yaml` ledger that each run updates rather than re-deriving.

```
Plaid CLI ──► transactions ─┐
                            ├─► detect recurring ─► reconcile into ─► report (.md + .html)
Gmail receipts ─────────────┘   (deterministic)     subscriptions.yaml
```

## Install

```bash
git clone git@github.com:RowanJu/subs.git
ln -s "$(pwd)/subs" ~/.claude/skills/subs   # symlink so /subs works globally
```

Then in Claude Code, run **`/subs`**.

## Prerequisites

- **Claude Code** with the **Gmail connector** enabled (Connectors → Gmail).
- **Plaid CLI** — `brew install plaid/plaid-cli/plaid`, then `plaid login` + `plaid link`.
- **jq** — `brew install jq` (ships on most macs).

## Usage

1. `plaid login` + `plaid link` (once per bank).
2. Run **`/subs`** from any folder you want as your data workspace. It pulls bank
   data + Gmail receipts, builds `subscriptions.yaml`, and writes a dated report
   to `reports/`.
3. Re-run anytime — it reconciles new data instead of starting over.

## Structure

```
SKILL.md                      the 5-step pipeline
scripts/detect_recurring.py   deterministic recurrence detector (stdlib only)
references/                   plaid, gmail, categories, recurrence, report templates
```

## 🔒 Privacy

This repo contains **only the skill** — no financial data. When you run `/subs`,
your ledger, reports, and raw bank data are created in your working directory and
are **gitignored** (`data/`, `reports/`, `subscriptions.yaml`); they never leave
your machine. Verify with `git status` before pushing.

## License

MIT — see [LICENSE](LICENSE).
