---
name: subs
description: Analyze SaaS subscription spending from bank CSVs and receipts — spend summary, waste detection, renewal tracking, savings recommendations.
disable-model-invocation: true
---

# subs — SaaS subscription spend analyzer

Analyze the user's recurring subscription spending from bank/card CSV exports and
email receipts. Produce a spend summary, flag waste, track renewals, and
recommend savings.

## The ledger is the spine

`subscriptions.yaml` in the workspace is the **single source of truth**. Every run
*reconciles* fresh data into it — it never re-derives everything from scratch.
This is what makes renewal tracking and run-to-run consistency real, and it makes
"waste" computable (a sub charged for months then suddenly absent = lapsed or
worth cancelling). Never overwrite the ledger wholesale; merge into it.

**Ledger entry schema** (one entry per subscription):

```yaml
- vendor: GitHub               # canonical name
  amount: 4.00                 # most recent charge
  currency: USD
  cycle: monthly               # weekly | monthly | quarterly | semiannual | annual
  category: Dev tools
  first_seen: 2025-01-12       # ISO date of earliest known charge
  last_seen: 2026-06-03        # ISO date of most recent charge
  next_renewal: 2026-07-03     # last_seen + one cycle
  status: active               # active | price_hike | lapsed? | cancelled
  notes: "was 4.00 since signup"
```

## Prerequisite: the Gmail connector

This skill reads subscription receipts from Gmail via Claude Code's **Gmail
connector**. Before step 1, confirm its tools are available (a `search_threads` /
`get_thread` pair — find them with `ToolSearch` for `gmail search_threads`). If
the connector is **not** available, stop and tell the user to enable it
(Connectors → Gmail → connect/authorize), then re-run `/subs`. Details and queries
in [email-receipts.md](references/email-receipts.md).

## Process

Work through these steps in order. Do not report until step 5.

### 0. Locate the workspace
Use the current working directory as the workspace. Ensure `data/statements/`,
`data/receipts/`, and `reports/` exist (create them if missing). Load
`subscriptions.yaml` if it exists; otherwise treat the ledger as empty.
**Done when:** the workspace dirs exist and the ledger is loaded (possibly empty).
If `data/statements/` is empty AND no `subscriptions.yaml` exists yet AND the user
isn't using Plaid (next section), tell the user to drop their bank/card CSV exports
into `data/statements/` and stop — the CSVs are the spine of recurrence detection;
Gmail receipts enrich them.

### 1. Gather inputs
**Bank data via the Plaid CLI** (preferred — no manual CSV export). If the user
wants automatic bank data, ensure the `plaid` CLI is ready and pull transactions
into a CSV the detector reads, per [plaid.md](references/plaid.md): install it if
missing (`brew install plaid/plaid-cli/plaid`), ensure `plaid login` + `plaid
link` have been done, then `plaid transactions list --all --json …` → convert to
`data/statements/plaid-transactions.csv`. Otherwise rely on CSVs the user dropped
into `data/statements/`.

Then list every CSV in `data/statements/`. Pull subscription receipts from
**Gmail** per [email-receipts.md](references/email-receipts.md), and also read any
supplementary `.eml`/`.txt` files in `data/receipts/`.
**Done when:** every statement file is listed and the Gmail receipt search has
run (or the connector-missing message was shown and the run stopped).

### 2. Detect recurring charges
Run the deterministic detector over every statement CSV (including the
Plaid-derived one) — do **not** eyeball rows:

```
python3 ~/.claude/skills/subs/scripts/detect_recurring.py data/statements/*.csv
```

The detector emits JSON candidates (merchant, amount, currency, cadence,
occurrences, first_seen, last_seen, amount_changed, confidence). For
`low`-confidence candidates and merchant-normalization edge cases, consult
[recurrence-detection.md](references/recurrence-detection.md). Combine these
candidates with the Gmail receipts gathered in step 1 — receipts catch annual subs
a short statement misses and identify vague descriptors.
**Done when:** every recurring candidate has a merchant, cadence, amount, and
last-seen date.

### 3. Reconcile into the ledger
Merge candidates into `subscriptions.yaml`:
- **New** merchant → add an entry; categorize via [categories.md](references/categories.md).
- **Existing** → refresh `last_seen` and `next_renewal`; if the amount rose, set
  `status: price_hike` and record the old amount in `notes`.
- **In the ledger but absent from recent data** (no charge within ~1.5 cycles of
  today) → set `status: lapsed?`.

**Done when:** every ledger entry has a status reflecting the latest data, and
every candidate maps to exactly one ledger entry.

### 4. Analyze
From the reconciled ledger compute all four:
- **(a) Spend summary** — monthly total and annualized total, grouped by category,
  by vendor, and by billing cycle. Normalize every entry to a monthly figure
  (annual ÷ 12, quarterly ÷ 3, weekly × 4.33) for comparison.
- **(b) Waste** — duplicates (same service twice), overlapping tools (two products
  in the same category doing the same job), price hikes (`status: price_hike`),
  and lapsed/unused (`status: lapsed?`).
- **(c) Upcoming renewals** — entries whose `next_renewal` falls within the next
  60 days, soonest first.
- **(d) Savings recommendations** — annual-vs-monthly switches, downgrades,
  consolidations, and cancellations. Each must cite a ledger entry and a dollar
  impact.

**Done when:** all four are produced and every recommendation cites an entry + a
dollar figure.

### 5. Report
Save the ledger, then write **both** reports from it:
- markdown `reports/<YYYY-MM-DD>-subscriptions.md` per
  [report-template.md](references/report-template.md);
- a self-contained HTML dashboard `reports/<YYYY-MM-DD>-subscriptions.html` per
  [html-report.md](references/html-report.md), and open it (`open <path>`).

Then present a concise summary in chat (headline totals + top 3 actions).
**Done when:** both reports cover all four outputs and `subscriptions.yaml` is
saved.
