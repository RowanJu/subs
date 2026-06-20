# Plaid via the Plaid CLI — automatic bank data (optional)

Pull transactions straight from the user's bank with the official **Plaid CLI**
(`plaid`), so they don't export CSVs by hand. Optional: if the user doesn't want
Plaid, use CSVs in `data/statements/` instead.

## Ensure the CLI is ready (do this automatically)

1. **Installed?** `command -v plaid`. If missing, install via Homebrew:
   ```
   brew install plaid/plaid-cli/plaid
   ```
2. **Logged in with a linked bank?** Run `plaid config` — it prints "Dashboard
   logged in", the selected environment, and a **Linked Items** count.
   - Not logged in → `plaid login` (opens the browser).
   - 0 linked items → `plaid link` (opens Plaid Link to connect a bank).
   Both are interactive: run them, tell the user to finish in the browser, then
   continue. List linked banks anytime with `plaid item list`.

## Pull transactions

Pull ~13 months (captures one full annual cycle) across **all** linked banks as
JSON. Compute the dates from today; do not hardcode:
```
plaid transactions list --all --json \
  --start-date <YYYY-MM-DD, ~13 months ago> --end-date <YYYY-MM-DD, today> \
  --count 500 > data/plaid/transactions.json
```
For very large histories (>500 txns/bank), raise `--count`, or use
`plaid transactions sync --all --json` (cursor-based, returns every record).

## Feed the deterministic detector

Convert the CLI JSON to the detector's CSV, then detect. Plaid amounts are
**positive for outflows**, so negate to get bank convention (charges negative):
```
{ echo "Date,Description,Amount,Currency"; \
  jq -r '.items[].transactions[] | [.date, (.name // .merchant_name // ""), (-.amount), (.iso_currency_code // "USD")] | @csv' \
     data/plaid/transactions.json; } > data/statements/plaid-transactions.csv

python3 <skill-dir>/scripts/detect_recurring.py data/statements/*.csv
```
`jq` ships on most macs; if missing, `brew install jq`. `<skill-dir>` is this
skill's own directory (in Claude Code: `~/.claude/skills/subs/`). The CLI JSON shape is
`{ items: [ { transactions: [ {date, name, merchant_name, amount,
iso_currency_code} ] } ] }`.

**Use the raw `.name`, not `merchant_name`.** Plaid's `merchant_name` is cleaner
but over-collapses distinct products from one vendor — e.g. `OPENAI *CHATGPT
SUBSCR` (annual subscription) and `OPENAI* CHATGPT CREDIT` (one-time top-up) both
become "OpenAI", which the detector then mis-reads as one monthly charge. The raw
`.name` keeps them apart, and `detect_recurring.py`'s normalizer already cleans the
noise. Trade-off: an **annual** subscription shows only once in a ≤1-year window,
so it won't be auto-flagged as recurring — confirm annual subs from Gmail receipts
and the ledger, and set `cycle: annual` (normalize to $/mo = amount ÷ 12).

## SaaS vs. other recurring

Plaid surfaces **all** recurring charges — utilities, phone, car loans, insurance,
gym, person-to-person (Zelle). Keep only genuine SaaS/subscription services for
the subscriptions report (categorize via [categories.md](references/categories.md));
list other recurring bills separately so they aren't mistaken for SaaS.

## Secrets & data

The CLI manages its own Dashboard credentials (`plaid login`) — you don't handle
API keys or access tokens here. Raw pulled data (`data/plaid/`,
`data/statements/*.csv`) is gitignored; it's the user's financial data.
