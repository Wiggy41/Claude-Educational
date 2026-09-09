---
name: qb-dashboard
description: Build a financial dashboard or forward forecast for the user's connected QuickBooks company. Use when the user asks for a "QuickBooks dashboard", "QB dashboard", "financial dashboard", "show my financials", "forecast next month/quarter/6 months", "project June", or any request to visualize their company's P&L, cash flow, benchmarking, or forward-looking projections. Supports two render modes — stitched native widgets or a unified custom HTML page — and a forecast mode.
---

# QuickBooks Dashboard Skill

Builds a consolidated financial dashboard for the user's connected QuickBooks
company by orchestrating the QuickBooks MCP connector
(`mcp__*__company-info`, `profit-loss-quickbooks-account`,
`cash-flow-quickbooks-account`, `benchmarking-quickbooks-account`).

## Arguments

Parse from the user's invocation. All optional.

- `mode`: `stitched` (default), `unified`, or `forecast`
  - `stitched` — render each native QB widget sequentially in one response.
    Fastest path; preserves QuickBooks' interactive visuals.
  - `unified` — extract the numbers from each tool result and render a single
    self-contained HTML dashboard (one pane, custom layout).
  - `forecast` — project P&L and cash for the next N months using YTD run-rate,
    open A/R, seasonality, and any user-supplied scenario levers (price, OT,
    headcount). See the Forecast section below.
- `period`: `ytd` (default), `last-quarter`, `ttm` (trailing 12 months), or an
  explicit `YYYY-MM-DD..YYYY-MM-DD` range. Used by stitched/unified modes.
- `horizon`: forecast modes only — `1m`, `3m` (default), `6m`, or `12m`.
- `sections`: comma-separated subset of `pnl,cashflow,benchmark`. Default: all.
- `accounting_basis`: `cash` (default) or `accrual`. **Always confirm** with
  the user — the connector returns whatever the QB account is set to and it
  materially changes interpretation of revenue timing.
- `scenario`: optional named scenario for forecast mode, e.g.
  `min_price=95,ot_cap_hrs_per_week=5,churn_pct=5`.

If the user said "dashboard" without specifying, default to
`mode=stitched`, `period=ytd`, all sections.
If the user said "forecast" / "project" / "predict next month", default to
`mode=forecast`, `horizon=3m`, `accounting_basis=cash`.

## Procedure

1. **Establish the connection.** Call `company-info` first (required by the
   downstream tools to attach OAuth). Capture `Company Name` and `Industry`
   (NAICS code) — you'll need them for benchmarking and the header.

2. **Resolve the period** to `periodStart` / `periodEnd` (YYYY-MM-DD):
   - `ytd` → Jan 1 of current year through today.
   - `last-quarter` → previous full calendar quarter.
   - `ttm` → today minus 365 days through today.
   - explicit range → split on `..`.

3. **Fetch sections in parallel** (single message, multiple tool calls):
   - `profit-loss-quickbooks-account` with the resolved period.
   - `cash-flow-quickbooks-account` with the resolved period.
   - `benchmarking-quickbooks-account` with `metricType=profit`,
     `aggregationPeriod=yearly` (do not pass extra args — the tool reads
     industry from the QB profile).

   Skip any section the user excluded via `sections`.

4. **Render based on mode:**

   ### Mode: `stitched` (default)
   Output a short header (company name, period, generated date), then let each
   tool's native widget render in turn. Add a one-line caption above each
   widget. Close with a brief plain-text takeaway (2–3 bullets) drawn from the
   numbers in the tool results.

   ### Mode: `unified`
   Extract these key figures from the tool outputs:
   - P&L: total revenue, total COGS, gross profit, gross margin, total
     operating expenses, net profit, net margin, monthly revenue series.
   - Cash flow: operating cash, investing cash, financing cash, net cash
     change, ending cash balance.
   - Benchmark: peer median for the chosen metric, company value, percentile
     band.

   Then write a single self-contained HTML file to
   `./qb-dashboard-output/dashboard-<YYYYMMDD-HHMM>.html` containing:
   - A header with company name, NAICS industry label, period covered.
   - A KPI strip (Revenue, Gross Margin, Net Profit, Net Margin, Ending Cash).
   - A revenue trend chart (inline SVG; no external JS/CSS).
   - A cash flow waterfall (inline SVG).
   - A benchmark bar (company vs peer median, inline SVG).
   - A short auto-generated narrative summary at the bottom.

   Use only inline CSS and inline SVG — no CDN, no external fetches. The file
   must open standalone in a browser. Print the absolute file path in the
   reply so the user can open it.

5. **Always end** with a one-line offer: "Want me to drill into any section,
   change the period, or switch render modes?"

## Forecast mode

Used when `mode=forecast`. Build a forward-looking month-by-month projection
of revenue, expenses, net income, and ending cash position. Always be explicit
about assumptions — never bury a guess inside a number.

### Known inputs for Yarddogs (confirmed 2026-09-09 — use unless user updates)
- Accounting basis: **cash**
- Monthly contract book: **$19,200/mo** (13+ locked-rate accounts incl. Laureate)
- Crew: reduced by one person Sep 2026; crew rate now **~$33/hr** (was $48/hr)
- Fully-loaded monthly payroll estimate: **~$11,700** (was ~$15,400)
- ASA Construction $8,158 A/R: **written off** — exclude from all forecasts
- Cash-basis rhythm: contract checks land days 10–20; payroll bi-weekly;
  judge any month only after day ~20

### Inputs to gather (ask the user once if not in context)
- **Accounting basis** of the QB account (`cash` or `accrual`). Critical:
  cash basis means open A/R is unrecognized revenue waiting to land.
- **Open A/R schedule**: amount + expected collection month per project /
  customer. If user gives a lump sum, ask for collection-month guess.
- **Cost-already-paid flag** per A/R item — under cash basis, projects whose
  costs are already in YTD expenses produce near-pure-margin revenue when
  collected.
- **Recurring contract revenue** — combined monthly $ from the locked-rate
  contract book. Used as the floor.
- **Variable book volume** — yard count × visit cadence × current price.
- **Crew config** — daily fully-loaded labor cost, overtime hours, day count.
- **Seasonality** — peak / shoulder / off months for the industry. For
  landscaping in the US Southeast: peak Apr–Sep, shoulder Mar/Oct, off Nov–Feb.

### Method (cash-basis forecast)
For each forecast month `m`:
1. **Operational revenue** = recurring contract revenue + (variable yards ×
   visit cadence × price) × seasonality factor.
2. **A/R collections** = sum of open A/R expected to land in `m` × user's
   collection probability (default 90% if unspecified).
3. **Total cash revenue (m)** = operational + A/R collections.
4. **Variable costs** = operational revenue × YTD variable cost ratio.
   (Do **not** apply variable costs to A/R collections — those costs are
   already in YTD expenses under cash basis. *Do* deduct any pending unpaid
   project costs separately.)
5. **Fixed costs (m)** = YTD fixed costs / YTD months.
6. **Net income (m)** = total revenue − variable − fixed − pending project
   costs.
7. **Ending cash (m)** = beginning cash + net income (+ any financing draws
   the user names).

### Sensitivities to surface
- ±$5/yard on the minimum price.
- ±5% / ±10% A/R collection slippage.
- OT hours/week (current vs. capped).
- One-truck-down scenario (drop ~10% variable + small fixed savings).

### Output
- Month-by-month table: revenue, var cost, fixed, net, cash position.
- A "drivers" panel: top 3 levers by impact, with $ effect.
- A "watch list": specific risks with trigger thresholds (e.g., "if A/R
  collection drops below 70%, June net flips negative").
- For 1-month detail mode, also include: working-day count, daily revenue
  required to hit projection, daily breakeven, and per-yard contribution
  at current and recommended pricing.

## Failure modes

- If `company-info` reports the user is not signed in, stop and tell them to
  authorize the QuickBooks connector — do **not** fall back to the
  pre-auth (`*-generator`) tools, since those need pasted transactions.
- If a section returns an error but others succeed, render what you have and
  note the missing section in the takeaway.
- If the user has not provided transactions in their message and is not
  signed in, never fabricate numbers.

## Notes

- The QB MCP tools return interactive widgets in `stitched` mode — do not
  re-describe what's already visible in the widget; keep narration tight.
- For `unified` mode, never invent figures the tool didn't return. If a
  number is missing, omit that tile rather than guessing.
- The benchmarking tool reads industry from the QB profile; if Industry comes
  back as "Unknown" from `company-info`, prompt the user to set it before
  running the benchmark section (or skip that section).
