# subs — SaaS subscription spend analyzer (a Claude Code skill)

`/subs` analyzes your SaaS subscription spending and produces a **spend summary**,
**waste detection** (duplicates, overlaps, price hikes, forgotten subs),
**renewal tracking**, and **savings recommendations** — as a markdown report and a
self-contained HTML dashboard.

It pulls bank transactions via the **Plaid CLI**, enriches them with **Gmail
receipts**, runs deterministic recurrence detection, and reconciles everything into
a `subscriptions.yaml` ledger that each run updates rather than re-deriving.

## How it works

```
Plaid CLI ──► transactions ─┐
                            ├─► detect recurring ─► reconcile into ─► report (.md + .html)
Gmail receipts ─────────────┘   (deterministic)     subscriptions.yaml
```

## Prerequisites

- **Claude Code** with the **Gmail connector** enabled (Connectors → Gmail).
- **Plaid CLI** — `brew install plaid/plaid-cli/plaid`, then `plaid login` + `plaid link`.
- **jq** — `brew install jq` (ships on most macs).

## Install

Copy the skill into your user skills directory, then invoke it by name:

```bash
cp -R .claude/skills/subs ~/.claude/skills/subs
# in Claude Code, run:  /subs
```

Or work inside a clone of this repo (it's already a project-level skill here).

## Usage

1. `plaid login` + `plaid link` (once per bank).
2. Run **`/subs`** from a workspace folder. It pulls bank data + Gmail receipts,
   builds `subscriptions.yaml`, and writes a dated report to `reports/`.
3. Re-run anytime — it reconciles new data instead of starting over.

## Repo layout

```
.claude/skills/subs/      the skill (SKILL.md + scripts + references)
  SKILL.md                the 5-step pipeline
  scripts/detect_recurring.py   deterministic recurrence detector (stdlib only)
  references/             plaid, gmail, categories, recurrence, report templates
data/                     your input data (gitignored)
reports/                  generated reports (gitignored)
subscriptions.yaml        your ledger (gitignored)
```

## 🔒 Privacy

This repo is structured to be shareable: **your financial data never gets
committed.** The `.gitignore` excludes `subscriptions.yaml`, `reports/`, and all of
`data/` — those stay on your machine only. Only the skill code and these docs are
tracked. Double-check with `git status` before pushing.
