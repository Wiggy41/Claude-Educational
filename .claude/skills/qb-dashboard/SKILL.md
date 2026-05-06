---
name: qb-dashboard
description: Build a financial dashboard for the user's connected QuickBooks company. Use when the user asks for a "QuickBooks dashboard", "QB dashboard", "financial dashboard", "show my financials", or any request to visualize their company's P&L, cash flow, and benchmarking together. Supports two render modes — stitched native widgets or a unified custom HTML page.
---

# QuickBooks Dashboard Skill

Builds a consolidated financial dashboard for the user's connected QuickBooks
company by orchestrating the QuickBooks MCP connector
(`mcp__*__company-info`, `profit-loss-quickbooks-account`,
`cash-flow-quickbooks-account`, `benchmarking-quickbooks-account`).

## Arguments

Parse from the user's invocation. All optional.

- `mode`: `stitched` (default) or `unified`
  - `stitched` — render each native QB widget sequentially in one response.
    Fastest path; preserves QuickBooks' interactive visuals.
  - `unified` — extract the numbers from each tool result and render a single
    self-contained HTML dashboard (one pane, custom layout).
- `period`: `ytd` (default), `last-quarter`, `ttm` (trailing 12 months), or an
  explicit `YYYY-MM-DD..YYYY-MM-DD` range.
- `sections`: comma-separated subset of `pnl,cashflow,benchmark`. Default: all.

If the user said "dashboard" without specifying, default to
`mode=stitched`, `period=ytd`, all sections.

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
