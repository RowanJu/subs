# Report template

Write the report to `reports/<YYYY-MM-DD>-subscriptions.md`. Use the user's
primary currency. Every dollar figure must trace to a ledger entry. Omit a section
only if it is genuinely empty (and say so).

```markdown
# Subscription report — <YYYY-MM-DD>

## Headline
- **Monthly spend:** $X / mo  (annualized **$Y / yr**)
- **Active subscriptions:** N  across M categories
- **Potential savings identified:** $Z / yr

## Spend by category
| Category | $/mo | $/yr | # subs |
|---|---|---|---|
| AI | … | … | … |
| … | … | … | … |
| **Total** | **…** | **…** | **…** |

## All subscriptions
| Vendor | Category | Amount | Cycle | $/mo | Next renewal | Status |
|---|---|---|---|---|---|---|
| … | … | … | … | … | … | active |

(Sort by $/mo descending. Normalize each to a monthly figure in the $/mo column.)

## ⚠️ Waste flags
- **Duplicates / overlaps:** …
- **Price hikes:** <vendor> rose from $A → $B (+C%) on <date>
- **Lapsed / possibly unused:** <vendor> — last charged <date>, no charge since

## 📅 Upcoming renewals (next 60 days)
| Date | Vendor | Amount |
|---|---|---|
| … | … | … |

## 💡 Recommendations (ranked by annual savings)
1. **<action>** — <vendor>: <why>. Saves **$N/yr**.
2. …

_Generated from `subscriptions.yaml`. Sources: <list statement files + receipts used>._
```

Keep the in-chat summary to the headline numbers plus the top 3 recommendations —
the full detail lives in the file.
