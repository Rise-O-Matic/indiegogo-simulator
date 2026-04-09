# Combined Report + Simulator Design Spec
**Date:** 2026-04-09  
**Output:** `report.html` (replaces existing)  
**Status:** Approved

---

## Goal

Merge `index.html` (interactive Monte Carlo simulator) and `report.html` (market analysis report) into a single scrollable page with print styles, using Tailwind CSS + DaisyUI.

---

## Stack

- **Tailwind CSS v3 + DaisyUI v4** — CDN, no build step
- **Chart.js v4.4.7** — CDN, carried over from `index.html`
- Single self-contained `report.html`, no external assets

---

## Visual Design

### Theme
- **DaisyUI base theme:** `light` on `<html>` — white background, near-black text
- **No dark section** — simulator panel gets a pale teal `#f0faf6` background wash, not a dark mode flip
- **Max content width:** 860px centered (matches current report)

### Viridis palette (accents, stats, charts)
| Token | Hex | Use |
|---|---|---|
| purple | `#440154` | P(funded) %, first stat accent |
| blue | `#31688e` | secondary stats |
| teal | `#21908c` | section numbers, borders, primary accent |
| green | `#35b779` | positive outcomes, third stats |
| lime | `#90d743` | chart mid-range |
| yellow | `#fde725` | chart high-end, highlights |

Chart.js fan chart and histogram use the viridis sequence for percentile bands.

### Section style (infographic-B pattern)
Each report section opens with:
- Viridis teal circle with section number
- Section title + sub-headline
- Key stats as left-border cards (each stat gets its own viridis-tinted left border in sequence)
- Body content below

---

## Page Structure

```
<nav>     sticky · Evidence · Lessons · Simulator · Forecast · Actions · (print: hidden)
<hero>    white background, CLOAK / BossCovers headline, viridis accent line
§1        id="evidence"  · The Evidence
§2        id="lessons"   · What the Evidence Means
§3        id="simulator" · Interactive Model  (teal wash bg: #f0faf6)
§4        id="forecast"  · What the Data Predicts
§5        id="actions"   · What to Do Next
<footer>
```

Section numbers shift: old §3 Forecast → §4, old §4 Actions → §5. Nav links updated accordingly.

---

## Simulator Section (§3)

**Screen:**
- Full simulator UI from `index.html`: scorecard, sliders (audience + campaign params), fan chart, histogram, budget optimizer
- Restyled for white world: white cards with teal borders, viridis chart colors, no dark CSS variables
- Sliders styled with DaisyUI `range` component, teal accent

**Print:**
- Sliders, budget optimizer, and run button: `@media print { display: none }`
- `.print-scorecard` div (hidden on screen, visible on print): static 2×2 grid showing last MC result — probability, raised (median), backers (median), net revenue
- `updatePrintScorecard(result)` called at end of each simulation run, writes current values into `.print-scorecard`
- Chart canvases print as-is (browser rasterises current chart state)
- Section gets a brief print heading: "Interactive Model — snapshot at time of print"

---

## Navigation

- DaisyUI `navbar` component, sticky top, viridis teal background (`bg-[#21908c]`)
- Links: monospace font, 11px, uppercase — same aesthetic as current report nav
- Active section highlighted via `IntersectionObserver` (carried over from `report.html`)
- Mobile: links wrap or horizontal scroll on narrow viewports

---

## Print Styles (`@media print`)

```css
nav, .no-print        { display: none !important; }
.print-scorecard      { display: grid !important; }
section               { page-break-inside: avoid; }
section + section     { page-break-before: auto; }
.stat-card, table, .lesson-card  { page-break-inside: avoid; }
body                  { font-size: 12px; }
a[href]::after        { content: none; }
```

---

## JavaScript

All JS from `index.html` carried into a single `<script>` block at bottom of `report.html`:

- MC simulation engine (unchanged)
- Chart.js initialisation — chart colors updated to viridis sequence
- `updatePrintScorecard(result)` — new function, called after `runSimulation()`
- `IntersectionObserver` nav active-state (from `report.html`)
- Budget optimizer (unchanged logic, restyled UI)

---

## What Changes

| File | Change |
|---|---|
| `report.html` | Full rewrite — new combined page |
| `index.html` | Unchanged — still exists as standalone simulator |
| `.gitignore` | Add `.superpowers/` if not present |

---

## What Does NOT Change

- All existing report content (evidence tables, lessons, forecast numbers, actions list)
- All simulator logic and parameter values
- `index.html` standalone functionality
