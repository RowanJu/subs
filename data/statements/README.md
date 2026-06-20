# Bank / card statements go here

Drop your **bank and credit-card CSV exports** in this folder. The `/subs` skill
reads every `.csv` here to detect recurring charges.

- Export from each account as CSV (most banks: Transactions → Download → CSV).
- Any column layout works — the detector auto-finds the date / description /
  amount columns. Common headers like `Posted Date`, `Details`, `Debit` are fine.
- Drop **multiple months** (ideally 12+) so monthly *and* annual subscriptions
  show their cadence. One file per account is fine; the skill merges them.
- Re-export and drop newer files anytime — re-running `/subs` reconciles them into
  `subscriptions.yaml` rather than duplicating.

Then run `/subs` from the `subscription-expert/` folder.
