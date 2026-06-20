# Recurrence detection — heuristics

`scripts/detect_recurring.py` encodes these rules. Read this when a candidate is
flagged `low` confidence, when the script's merchant grouping looks wrong, or
when a CSV's columns weren't auto-detected.

## What the script does

1. **Column detection** — picks date / description / amount columns by header
   name (handles `Posted Date`, `Details`, `Debit`, etc.). If a CSV is skipped
   with a `WARN: could not detect columns`, the headers are nonstandard — open
   the file, identify the columns, and either rename the headers or pass the data
   to the user to relabel.
2. **Outflow sign** — if any amount is negative, charges are the negatives
   (typical bank export). If the file is all-positive, every positive is treated
   as a charge (typical card-only "amount" column).
3. **Merchant normalization** — lowercases, strips card masks (`xx1234`), long
   digit runs, store numbers (`#123`), boilerplate words (`PURCHASE`, `RECURRING`,
   `POS`, `VISA`…), URLs, asterisks; keeps the first 3 words as the brand key.
4. **Grouping + cadence** — groups by normalized merchant; a group needs ≥2
   charges and an average inter-charge gap matching a cadence band:
   weekly 5–9d, monthly 25–35d, quarterly 80–100d, semiannual 165–200d,
   annual 350–385d. Groups with no matching cadence are dropped as one-offs.
5. **Amount stability** — amounts within ±5% are "stable"; otherwise
   `amount_changed: true` (a likely price hike — worth confirming in the ledger).

## Confidence levels

- **high** — stable amount AND ≥3 occurrences. Trust it.
- **medium** — stable OR ≥3 occurrences. Likely real; sanity-check the merchant.
- **low** — only 2 occurrences with a varying amount. Could be coincidence (two
  similar one-off purchases). Confirm against the raw description before adding to
  the ledger; if unsure, add with `notes: "low confidence — verify"`.

## Manual judgment the script can't make

- **Same vendor, different normalized keys** (e.g. `GOOGLE *YOUTUBE` vs
  `GOOGLE STORAGE`) — these are *different* subscriptions; keep them separate.
- **One vendor billing several products** under one descriptor — note it; you may
  not be able to split it from CSV alone. Use receipts to disambiguate.
- **Annual subscriptions** only show one charge per year, so a fresh statement
  covering <1 year shows them as a single non-recurring row. The detector cannot
  catch these from one occurrence — rely on receipts or the existing ledger to
  carry them. When in doubt, ask the user.
