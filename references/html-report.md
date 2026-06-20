# HTML dashboard report

Generate a **self-contained** HTML dashboard (no external CSS/JS/CDN — works
offline) at `reports/<YYYY-MM-DD>-subscriptions.html`, then open it
(`open <path>` on macOS). This is the visual companion to the markdown report;
both are built from the ledger.

## Computation rules (do these first, from the ledger)

- **$/mo per sub** — normalize each to monthly: annual ÷ 12, quarterly ÷ 3,
  semiannual ÷ 6, weekly × 4.33, biweekly × 2.17, semimonthly × 2, monthly × 1.
- **Monthly burn** = Σ $/mo over `status: active` SaaS subs (exclude cancelled and
  non-SaaS). **Annualized** = monthly × 12.
- **Category split** — sum $/mo by category; **%** = category ÷ monthly burn.
- **AI share** — the AI category % (usually the headline).
- **Donut** uses a CSS `conic-gradient` with **cumulative** percent stops, largest
  category first (see template). Compute running totals, e.g. AI 0→89.66%,
  +Media→95.10%, +Design→98.64%, +Wellness→100%.
- **Bar width %** per sub = `$/mo ÷ (max $/mo) × 100` (largest sub = 100%).
- **Insights** — fill Cancel / Duplicate-overlap / Downgrade-optimize from the
  waste analysis (step 4): cancelled or unused → Cancel; same-job/same-category or
  music/storage overlap → Duplicate; usage-based, oversized tier, or annual-cheaper
  → Downgrade. Each line cites a vendor and an annual-$ figure.
- **Non-SaaS recurring** — list the excluded bills (utilities, phone, loans,
  insurance, rent) in the lower-right panel so the picture is complete.

## Template

Keep the `<style>` block **verbatim** (it defines the look). Fill only the marked
`<!-- FILL -->` regions from the ledger. Color classes for bars: default (violet =
AI), `sky` (media), `orange` (design), `green` (wellness/other), `grey` (free/$0).

```html
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Subscription report · {{DATE}}</title>
<style>
  :root{--bg:#0b0f17;--panel:#141a26;--panel2:#1b2333;--line:#26304a;--txt:#e8edf7;
    --muted:#93a0bd;--accent:#a78bfa;--ai:#a78bfa;--media:#38bdf8;--design:#fb923c;
    --well:#34d399;--dev:#64748b;--warn:#f87171;--good:#34d399;--down:#fbbf24;}
  *{box-sizing:border-box}
  body{margin:0;background:radial-gradient(1200px 600px at 70% -10%,#1a2236,transparent),var(--bg);
    color:var(--txt);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
    -webkit-font-smoothing:antialiased;padding:32px 20px 64px}
  .wrap{max-width:1080px;margin:0 auto}
  header{display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:12px;margin-bottom:24px}
  h1{font-size:26px;margin:0;letter-spacing:-.02em}
  .sub{color:var(--muted);font-size:13px;margin-top:4px}
  h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 14px}
  .grid{display:grid;gap:16px}.kpis{grid-template-columns:repeat(5,1fr);margin-bottom:20px}
  .panel{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:14px;padding:18px}
  .kpi .v{font-size:26px;font-weight:700;letter-spacing:-.02em}.kpi .l{color:var(--muted);font-size:12px;margin-top:2px}
  .kpi .v.warn{color:#fca5a5}.kpi .v.good{color:#6ee7b7}
  .cols{grid-template-columns:340px 1fr;align-items:stretch}
  @media(max-width:880px){.kpis{grid-template-columns:repeat(2,1fr)}.cols{grid-template-columns:1fr}}
  .donut-wrap{display:flex;gap:18px;align-items:center}
  .donut{position:relative;width:170px;height:170px;border-radius:50%;flex:none;
    background:conic-gradient({{DONUT_STOPS}})}
  .donut::after{content:"";position:absolute;inset:26px;border-radius:50%;background:var(--panel2)}
  .donut .center{position:absolute;inset:0;display:grid;place-content:center;text-align:center;z-index:1}
  .donut .center b{font-size:22px}.donut .center span{font-size:11px;color:var(--muted)}
  .legend{display:flex;flex-direction:column;gap:9px;font-size:13px;flex:1}
  .legend .row{display:flex;align-items:center;gap:8px}
  .dot{width:10px;height:10px;border-radius:3px;flex:none}
  .legend .amt{margin-left:auto;color:var(--muted);font-variant-numeric:tabular-nums}
  .bars{display:flex;flex-direction:column;gap:11px}
  .bar .top{display:flex;justify-content:space-between;font-size:13.5px;margin-bottom:5px}
  .bar .top .amt{font-variant-numeric:tabular-nums;color:var(--muted)}
  .track{height:9px;background:#0e1422;border-radius:6px;overflow:hidden}
  .fill{height:100%;border-radius:6px;background:linear-gradient(90deg,#7c6cf0,#a78bfa)}
  .fill.sky{background:linear-gradient(90deg,#0ea5e9,#38bdf8)}
  .fill.orange{background:linear-gradient(90deg,#f97316,#fb923c)}
  .fill.green{background:linear-gradient(90deg,#10b981,#34d399)}.fill.grey{background:#3a465e}
  .tag{font-size:10.5px;padding:1px 7px;border-radius:20px;border:1px solid var(--line);color:var(--muted);margin-left:8px}
  .ins{grid-template-columns:repeat(3,1fr);margin-top:20px}@media(max-width:880px){.ins{grid-template-columns:1fr}}
  .ins .panel{border-top:3px solid var(--line)}
  .ins .cancel{border-top-color:var(--warn)}.ins .dup{border-top-color:var(--media)}.ins .down{border-top-color:var(--down)}
  .ins h3{margin:0 0 4px;font-size:15px;display:flex;align-items:center;gap:8px}
  .ins .save{font-size:12px;color:var(--good);font-weight:600}
  .ins ul{margin:10px 0 0;padding-left:18px;color:#cdd6ea;font-size:13.5px}.ins li{margin-bottom:7px}.ins li b{color:#fff}
  .low{grid-template-columns:1fr 1fr;margin-top:20px}@media(max-width:880px){.low{grid-template-columns:1fr}}
  table{width:100%;border-collapse:collapse;font-size:13.5px}
  td,th{text-align:left;padding:7px 4px;border-bottom:1px solid var(--line)}
  th{color:var(--muted);font-weight:500;font-size:11.5px;text-transform:uppercase;letter-spacing:.05em}
  td.n{text-align:right;font-variant-numeric:tabular-nums}tr:last-child td{border-bottom:none}
  .muted{color:var(--muted)}
  footer{color:var(--muted);font-size:12px;margin-top:24px;line-height:1.6}
  .pill{display:inline-block;background:#2a1f12;color:#fbbf24;border:1px solid #4a3413;border-radius:6px;padding:1px 7px;font-size:11px}
</style></head><body><div class="wrap">
  <header><div><h1>SaaS subscription report</h1>
    <div class="sub">{{DATE}} · source: {{SOURCES}}</div></div>
    <div class="sub">Ledger: <code>subscriptions.yaml</code></div></header>

  <div class="grid kpis">
    <!-- FILL: 5 KPI cards — monthly burn, annualized, # active, AI share% (class warn), savings range (class good) -->
  </div>

  <div class="grid cols">
    <div class="panel"><h2>Spend by category</h2>
      <div class="donut-wrap">
        <div class="donut"><div class="center"><b>{{MONTHLY}}</b><span>/mo</span></div></div>
        <div class="legend"><!-- FILL: one .row per category with .dot color, name, .amt "$X · Y%" --></div>
      </div></div>
    <div class="panel"><h2>Monthly burn by subscription</h2>
      <div class="bars"><!-- FILL: one .bar per active sub (desc by $/mo): label, $amt, .fill width% + color class --></div>
    </div>
  </div>

  <div class="grid ins">
    <div class="panel cancel"><h3>✂️ Cancel</h3><div class="save">{{SAVE}}</div><ul><!-- FILL --></ul></div>
    <div class="panel dup"><h3>🔁 Duplicate / overlap</h3><div class="save">{{SAVE}}</div><ul><!-- FILL --></ul></div>
    <div class="panel down"><h3>⬇️ Downgrade / optimize</h3><div class="save">{{SAVE}}</div><ul><!-- FILL --></ul></div>
  </div>

  <div class="grid low">
    <div class="panel"><h2>📅 Upcoming renewals (next 30 days)</h2>
      <table><tr><th>Date</th><th>Vendor</th><th class="n">Amount</th></tr><!-- FILL --></table></div>
    <div class="panel"><h2>Other recurring · not SaaS <span class="muted">(excluded from totals)</span></h2>
      <table><tr><th>Vendor</th><th>Type</th><th class="n">~$/mo</th></tr><!-- FILL --></table></div>
  </div>

  <footer><b>Caveats.</b> <!-- FILL: data coverage, projected dates, anything to verify --></footer>
</div></body></html>
```
