#!/usr/bin/env python3
"""Detect recurring charges from bank/card CSV exports.

Stdlib only. Reads one or more CSV files, auto-detects the date / description /
amount columns, normalizes merchant strings, groups by merchant, and flags
groups that recur at a regular cadence with a stable amount.

Output: JSON array on stdout, one object per recurring candidate:
  {merchant, raw_examples, amount, currency, cadence, occurrences,
   first_seen, last_seen, amount_changed, confidence}

Run:  python3 detect_recurring.py data/statements/*.csv
Anything that is NOT recurring (one-off purchases, noise) is dropped.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime

# --- column detection ---------------------------------------------------------

DATE_HINTS = ("date", "posted", "transaction date", "post date")
DESC_HINTS = ("description", "details", "merchant", "name", "memo", "payee", "narration")
AMOUNT_HINTS = ("amount", "debit", "charge", "value")

DATE_FORMATS = (
    "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m/%d/%y", "%d/%m/%y",
    "%Y/%m/%d", "%d-%m-%Y", "%m-%d-%Y", "%d %b %Y", "%b %d, %Y", "%d.%m.%Y",
)


def pick_column(header, hints):
    lower = [h.strip().lower() for h in header]
    for i, h in enumerate(lower):
        if h in hints:
            return i
    for i, h in enumerate(lower):
        if any(hint in h for hint in hints):
            return i
    return None


def parse_date(s):
    s = s.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(s):
    """Return a positive float for an outflow, or None. Handles $, commas,
    parentheses-for-negative, and leading minus signs."""
    s = s.strip()
    if not s:
        return None
    neg = s.startswith("(") and s.endswith(")")
    cur = "USD"
    if "€" in s:
        cur = "EUR"
    elif "£" in s:
        cur = "GBP"
    cleaned = re.sub(r"[^\d.\-]", "", s.replace(",", ""))
    if cleaned in ("", "-", ".", "-."):
        return None, cur
    try:
        val = float(cleaned)
    except ValueError:
        return None, cur
    if neg:
        val = -abs(val)
    return val, cur


# --- merchant normalization ---------------------------------------------------

NOISE_PATTERNS = [
    r"\bxx+\d+\b",            # masked card fragments
    r"\b\d{4,}\b",            # long digit runs (store / txn ids)
    r"#\s*\d+",               # store numbers
    r"\b(purchase|payment|recurring|autopay|pos|debit|card|visa|mastercard)\b",
    r"\b(http|www)\S*",       # urls
    r"\b\d{1,2}/\d{1,2}\b",   # embedded dates
    r"[*]+",                  # asterisk separators
]


def normalize_merchant(desc):
    s = desc.lower()
    for pat in NOISE_PATTERNS:
        s = re.sub(pat, " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # keep the first 3 tokens — usually the brand
    tokens = s.split()
    return " ".join(tokens[:3]) if tokens else desc.strip().lower()


# --- cadence detection --------------------------------------------------------

def classify_cadence(gaps_days):
    """Given sorted inter-charge gaps (days), return a cadence label or None."""
    if not gaps_days:
        return None
    avg = sum(gaps_days) / len(gaps_days)
    for label, lo, hi in (
        ("weekly", 5, 9),
        ("monthly", 25, 35),
        ("quarterly", 80, 100),
        ("semiannual", 165, 200),
        ("annual", 350, 385),
    ):
        if lo <= avg <= hi:
            return label
    return None


def amounts_stable(amounts, tol=0.05):
    """True if max amount is within tol of min (ignoring sign)."""
    a = [abs(x) for x in amounts]
    lo, hi = min(a), max(a)
    return lo > 0 and (hi - lo) / lo <= tol


# --- main ---------------------------------------------------------------------

def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = csv.excel
        reader = csv.reader(f, dialect)
        rows = list(reader)
    if not rows:
        return []
    header = rows[0]
    di = pick_column(header, DATE_HINTS)
    si = pick_column(header, DESC_HINTS)
    ai = pick_column(header, AMOUNT_HINTS)
    if di is None or si is None or ai is None:
        sys.stderr.write(
            f"WARN: {path}: could not detect columns "
            f"(date={di}, desc={si}, amount={ai}); skipping\n")
        return []
    out = []
    for r in rows[1:]:
        if len(r) <= max(di, si, ai):
            continue
        d = parse_date(r[di])
        amt = parse_amount(r[ai])
        if amt is None:
            continue
        val, cur = amt if isinstance(amt, tuple) else (amt, "USD")
        if d is None or val is None:
            continue
        out.append((d, r[si].strip(), val, cur))
    return out


def main(argv):
    paths = argv[1:]
    if not paths:
        sys.stderr.write("usage: detect_recurring.py <csv> [csv ...]\n")
        return 2

    txns = []
    for p in paths:
        txns.extend(load_rows(p))

    # only outflows (charges). Statements vary on sign; treat negatives as
    # charges, but if a file is all-positive we keep positives too.
    has_neg = any(v < 0 for _, _, v, _ in txns)
    if has_neg:
        charges = [(d, desc, -v, cur) for d, desc, v, cur in txns if v < 0]
    else:
        charges = [(d, desc, v, cur) for d, desc, v, cur in txns if v > 0]

    groups = defaultdict(list)
    for d, desc, v, cur in charges:
        groups[normalize_merchant(desc)].append((d, desc, v, cur))

    results = []
    for merchant, items in groups.items():
        if len(items) < 2:
            continue
        items.sort(key=lambda x: x[0])
        dates = [i[0] for i in items]
        amounts = [i[2] for i in items]
        gaps = [(dates[k + 1] - dates[k]).days for k in range(len(dates) - 1)]
        gaps = [g for g in gaps if g > 0]
        cadence = classify_cadence(gaps)
        if cadence is None:
            continue
        stable = amounts_stable(amounts)
        # confidence: regular cadence + stable amount + >=3 occurrences = high
        if stable and len(items) >= 3:
            confidence = "high"
        elif stable or len(items) >= 3:
            confidence = "medium"
        else:
            confidence = "low"
        results.append({
            "merchant": merchant,
            "raw_examples": sorted({i[1] for i in items})[:3],
            "amount": round(amounts[-1], 2),            # most recent amount
            "currency": items[-1][3],
            "cadence": cadence,
            "occurrences": len(items),
            "first_seen": dates[0].isoformat(),
            "last_seen": dates[-1].isoformat(),
            "amount_changed": not stable,
            "confidence": confidence,
        })

    results.sort(key=lambda r: (r["confidence"] != "high", r["merchant"]))
    json.dump(results, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
