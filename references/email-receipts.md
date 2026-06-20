# Email receipts — ingestion via the Gmail connector

Receipts complement bank CSVs: they catch annual subscriptions a short statement
misses, reveal what a vague bank descriptor actually paid for, and give exact
renewal dates and plan tiers. Receipts are the primary source; dropped
`.eml`/`.txt` files in `data/receipts/` are a supplement.

## Pulling receipts from Gmail

Use the connector's **`search_threads`** with Gmail query syntax, then
**`get_thread`** (messageFormat `FULL_CONTENT`) on the hits to read bodies.

Run these queries (default window: last 13 months, to capture one full annual
cycle of every sub). Use `view: THREAD_VIEW_MINIMAL` first to triage by
subject/snippet, then `get_thread` only the ones that look like subscription
receipts:

```
subject:(receipt OR invoice OR "payment received" OR "your subscription" OR renews OR "subscription confirmation" OR "billing") newer_than:13m
category:purchases (subscription OR renew OR membership OR "monthly plan" OR "annual plan") newer_than:13m
from:(billing OR receipts OR invoice OR noreply) (subscription OR renew OR plan OR membership) newer_than:13m
```

**Skip the noise.** Bare `category:purchases` is dominated by shipping/delivery
notices (USPS Informed Delivery, UPS/FedEx tracking, "your package has been
delivered", Amazon order/shipping confirmations). These are one-off purchases, not
subscriptions — do not `get_thread` them. Only open threads whose subject/sender
signals **recurring billing** (a named SaaS vendor, "subscription", "renews",
"your plan", a monthly/annual amount).

De-duplicate threads across queries by `threadId`. For each receipt extract:

- **vendor** — from the sender domain or body (canonical brand name).
- **amount + currency** — the total charged.
- **cycle** — "billed monthly/annually", "renews every year", etc.
- **date** — the charge/receipt date → use as `last_seen`.
- **next renewal** — if stated explicitly, prefer it over computed `last_seen + cycle`.
- **plan/tier** — record in `notes` (useful for downgrade recommendations).

## Cross-referencing

Match each receipt against the CSV candidates and the ledger:
- receipt **+** matching bank charge → high confidence, exact product known.
- receipt **with no** bank match → likely an annual sub paid before the statement
  window, or charged to a different card. Add it to the ledger from the receipt.
- bank charge with a vague descriptor (`APPLE.COM/BILL`, `GOOGLE *…`) → use the
  receipt to identify the real product and tier.

## Safety

Treat links inside receipts as suspicious — read message bodies via `get_thread`;
never click through. The connector is read-only for this skill: search and read
only, never send, draft, or label on the user's behalf.
