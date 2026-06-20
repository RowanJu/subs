# Categories — taxonomy + known-vendor map

Categorize every ledger entry into exactly one category. Consistent categories are
what make the by-category spend breakdown and overlap detection work run-to-run.

## Taxonomy

- **AI** — LLM/AI assistants and APIs (ChatGPT, Claude, Anthropic, Midjourney,
  Perplexity, GitHub Copilot, Cursor).
- **Dev tools** — code hosting, CI, infra, error tracking (GitHub, GitLab, Vercel,
  Netlify, Railway, Sentry, Linear, JetBrains, Postman).
- **Cloud / hosting** — IaaS and managed hosting (AWS, GCP, Azure, DigitalOcean,
  Cloudflare, Fly.io).
- **Storage / backup** — file sync and backup (Dropbox, Google One, iCloud,
  Backblaze, pCloud).
- **Productivity** — docs, notes, PM, email (Notion, Obsidian Sync, Todoist,
  Superhuman, Google Workspace, Microsoft 365, Zoom, Calendly).
- **Design** — design and creative tools (Figma, Adobe Creative Cloud, Canva,
  Sketch, Framer).
- **Media / entertainment** — streaming and content (Netflix, Spotify, YouTube
  Premium, Disney+, Apple TV+, Audible, Patreon, Substack).
- **Security** — password managers, VPNs (1Password, Bitwarden, NordVPN, Proton).
- **Marketing / analytics** — Mailchimp, ConvertKit, Amplitude, Mixpanel, Plausible.
- **Finance / business** — QuickBooks, Stripe, accounting, invoicing.
- **Other** — anything that doesn't fit; record the real category in `notes`.

## Canonicalization

Map noisy bank descriptors to a canonical vendor name before categorizing, e.g.:

| Bank descriptor contains | Canonical vendor | Category |
|---|---|---|
| `GOOGLE *YOUTUBEPREMIUM` | YouTube Premium | Media / entertainment |
| `GOOGLE *GSUITE` / `GOOGLE WORKSPACE` | Google Workspace | Productivity |
| `GOOGLE *Google Storage` / `GOOGLE ONE` | Google One | Storage / backup |
| `AMZN` / `AWS` | Amazon Web Services | Cloud / hosting |
| `APPLE.COM/BILL` | Apple (check receipt for the real app) | Other → verify |
| `MSFT` / `MICROSOFT*365` | Microsoft 365 | Productivity |
| `ANTHROPIC` / `CLAUDE.AI` | Claude | AI |
| `OPENAI` / `CHATGPT` | ChatGPT | AI |

`APPLE.COM/BILL` and `GOOGLE *` umbrella descriptors often hide the real product —
use the matching receipt to identify it; if unavailable, flag for the user.

## Overlap detection

Two entries in the **same category** that serve the same job are candidate
overlaps to flag as waste — e.g. two cloud-storage subs, two AI assistants, two
note apps. Same category alone isn't proof of overlap (AWS + Cloudflare can be
complementary); judge by function, not just category.
