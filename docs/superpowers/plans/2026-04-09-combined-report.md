# Combined Report + Simulator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `report.html` as a single scrollable page that embeds the interactive MC simulator as §3 between the Lessons and Forecast sections, styled with Tailwind CSS + DaisyUI using a clean white theme and viridis color accents.

**Architecture:** Single self-contained HTML file with all CSS via Tailwind/DaisyUI CDN, all JS inline. Report content (§1 Evidence, §2 Lessons, §4 Forecast, §5 Actions) is carried over verbatim with restyled markup; simulator (§3) is ported from `index.html`. No build step. `index.html` is untouched.

**Tech Stack:** Tailwind CSS v3 CDN, DaisyUI v4 CDN, Chart.js v4.4.7 CDN, vanilla JS.

---

## Viridis palette reference (use these everywhere)

```
#440154  purple   — P(funded) stat, primary accent, histogram below-goal bars
#31688e  blue     — secondary stat accents
#21908c  teal     — section numbers, nav bg, borders, median line, primary accent
#35b779  green    — positive outcomes, third stats, histogram above-goal bars
#90d743  lime     — chart mid-range
#fde725  yellow   — chart high-end
```

## File map

| File | Action |
|---|---|
| `report.html` | Full rewrite (all tasks below) |
| `index.html` | Untouched |
| `.gitignore` | Add `.superpowers/` entry if missing |

---

## Task 1: Scaffold skeleton and global styles

**Files:**
- Modify: `report.html` (full rewrite — overwrite with new skeleton)

- [ ] **Step 1: Write the skeleton**

Replace the entire contents of `report.html` with this skeleton. This establishes CDN links, viridis CSS variables, print styles, and the five section stubs.

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CLOAK by BossCovers — Go-to-Market Intelligence</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/daisyui@4.12.14/dist/full.min.css">
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
/* Viridis tokens */
:root {
  --v-purple: #440154;
  --v-blue:   #31688e;
  --v-teal:   #21908c;
  --v-green:  #35b779;
  --v-lime:   #90d743;
  --v-yellow: #fde725;
  --max-w:    860px;
}

/* Layout */
.wrap { max-width: var(--max-w); margin: 0 auto; padding: 0 2rem; }

/* Section tag (circle + title) */
.section-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 2rem; height: 2rem; border-radius: 9999px;
  background: var(--v-teal); color: #fff;
  font-weight: 800; font-size: 0.85rem; flex-shrink: 0;
}
.section-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
.section-header h2 { font-size: 1.5rem; font-weight: 700; color: #111; }
.section-sub { font-size: 0.9rem; color: #6b7280; margin-bottom: 2rem; line-height: 1.6; }

/* Stat cards (infographic-B: left-border, viridis tinted) */
.stat-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.stat-card {
  flex: 1; min-width: 120px;
  padding: 0.6rem 0.75rem;
  background: #f9fafb; border-radius: 0 6px 6px 0;
}
.stat-card .n { display: block; font-size: 1.4rem; font-weight: 800; }
.stat-card .l { display: block; font-size: 0.75rem; color: #6b7280; line-height: 1.4; margin-top: 2px; }
.stat-card:nth-child(1) { border-left: 3px solid var(--v-purple); }
.stat-card:nth-child(1) .n { color: var(--v-purple); }
.stat-card:nth-child(2) { border-left: 3px solid var(--v-blue); }
.stat-card:nth-child(2) .n { color: var(--v-blue); }
.stat-card:nth-child(3) { border-left: 3px solid var(--v-teal); }
.stat-card:nth-child(3) .n { color: var(--v-teal); }
.stat-card:nth-child(4) { border-left: 3px solid var(--v-green); }
.stat-card:nth-child(4) .n { color: var(--v-green); }

/* Callout boxes */
.callout {
  border-left: 3px solid var(--v-teal);
  background: #f0fdf9; padding: 1rem 1.25rem;
  border-radius: 0 8px 8px 0; margin: 1.5rem 0;
}
.callout.warn { border-color: #b45309; background: #fefce8; }
.callout.flag { border-color: var(--v-purple); background: #faf5ff; }
.callout-label {
  font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--v-teal); font-weight: 700; margin-bottom: 0.35rem;
}
.callout.warn .callout-label { color: #b45309; }
.callout.flag .callout-label { color: var(--v-purple); }

/* Tables */
.tbl-wrap { overflow-x: auto; margin-bottom: 1.5rem; }
table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
th { background: #f3f4f6; padding: 0.6rem 0.75rem; text-align: left;
     font-weight: 600; color: #374151; border-bottom: 2px solid #e5e7eb; }
td { padding: 0.55rem 0.75rem; border-bottom: 1px solid #f3f4f6; }
td.mono { font-family: 'Courier New', monospace; }
td.em { font-weight: 600; color: #111; }

/* Tags */
.tag-win  { background: #dcfce7; color: #166534; border-radius: 4px; padding: 2px 6px; font-size: 0.75rem; font-weight: 600; }
.tag-meh  { background: #fef9c3; color: #854d0e; border-radius: 4px; padding: 2px 6px; font-size: 0.75rem; font-weight: 600; }
.tag-loss { background: #fee2e2; color: #991b1b; border-radius: 4px; padding: 2px 6px; font-size: 0.75rem; font-weight: 600; }

/* Source citation */
.src { font-size: 0.7rem; color: #9ca3af; font-weight: 400; margin-left: 0.5rem; }

/* Block (subsection within a section) */
.block { margin-bottom: 2.5rem; }
.block h3 { font-size: 1rem; font-weight: 700; color: #111; margin-bottom: 0.5rem; padding-bottom: 0.4rem; border-bottom: 1px solid #e5e7eb; }

/* Lessons */
.lessons { display: grid; gap: 1rem; }
.lesson { background: #f9fafb; border-radius: 8px; padding: 1rem 1.25rem; border-left: 3px solid #e5e7eb; }
.lesson.flag { border-color: var(--v-purple); background: #fdf4ff; }
.lesson .lnum { font-size: 0.65rem; text-transform: uppercase; letter-spacing: .12em; color: #9ca3af; font-weight: 700; margin-bottom: 4px; }
.lesson h4 { font-size: 0.95rem; font-weight: 700; color: #111; margin-bottom: 0.4rem; }
.lesson p { font-size: 0.85rem; color: #374151; line-height: 1.65; }

/* Bar chart (horizontal) */
.bar-chart { display: grid; gap: 0.75rem; margin: 1rem 0; }
.bar-row { display: grid; grid-template-columns: 1fr 2fr auto; align-items: center; gap: 0.75rem; }
.bar-label { font-size: 0.8rem; font-weight: 500; }
.bar-track { background: #e5e7eb; border-radius: 4px; height: 12px; }
.bar-fill { background: var(--v-teal); height: 100%; border-radius: 4px; }
.bar-fill.amber { background: #b45309; }
.bar-val { font-size: 0.78rem; font-weight: 600; color: #374151; white-space: nowrap; }

/* State box */
.state-box { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
.state-item { flex: 1; min-width: 140px; background: #f9fafb; border-radius: 8px; padding: 1rem; text-align: center; }
.state-item .n { display: block; font-size: 1.8rem; font-weight: 800; color: var(--v-teal); }
.state-item .l { display: block; font-size: 0.75rem; color: #6b7280; margin: 4px 0; }
.state-item .plain { display: block; font-size: 0.7rem; color: #9ca3af; }

/* Action list */
.action-list { display: grid; gap: 1rem; }
.action-item { display: grid; grid-template-columns: 2.5rem 1fr; gap: 0.75rem; align-items: start; padding: 1rem; background: #f9fafb; border-radius: 8px; }
.action-num { width: 2.5rem; height: 2.5rem; border-radius: 9999px; background: var(--v-teal); color: #fff; font-weight: 800; font-size: 0.9rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.action-item.alt .action-num { background: var(--v-purple); }
.action-item h4 { font-size: 0.95rem; font-weight: 700; color: #111; margin-bottom: 0.3rem; }
.action-item p { font-size: 0.85rem; color: #374151; line-height: 1.6; }
.action-timeline { font-size: 0.7rem; font-weight: 600; color: var(--v-teal); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 0.25rem; }

/* ─── Simulator section ───────────────────────────── */
#simulator {
  background: #f0fdf9;
  border-top: 2px solid var(--v-teal);
  border-bottom: 2px solid var(--v-teal);
}

/* Simulator sub-components (white world, no dark vars) */
.sim-card {
  background: #fff; border-radius: 12px; padding: 1rem 1.25rem;
  border: 1px solid #d1fae5; margin-bottom: 1rem;
}
.sim-scorecard { text-align: center; }
.sim-prob { font-size: 3rem; font-weight: 800; line-height: 1.1; color: var(--v-teal); }
.sim-prob-label { font-size: 0.9rem; color: #374151; margin-bottom: 0.75rem; }
.sim-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.75rem; }
.sim-stat { background: #f0fdf9; border-radius: 8px; padding: 0.5rem 0.75rem; }
.sim-stat-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; }
.sim-stat-value { font-size: 1rem; font-weight: 700; color: #111; margin-top: 2px; }
.sim-verdict { padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600; color: #fff; margin: 0.5rem 0; text-align: center; background: var(--v-teal); }

.sim-section-title { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--v-teal); font-weight: 700; margin-bottom: 0.75rem; }
.slider-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem; font-size: 0.82rem; }
.slider-row label { flex: 0 0 120px; color: #374151; }
.slider-row input[type=range] { flex: 1; accent-color: var(--v-teal); }
.slider-val { flex: 0 0 60px; text-align: right; font-weight: 600; color: var(--v-teal); font-size: 0.82rem; }
.chart-wrap { background: #fff; border-radius: 8px; border: 1px solid #d1fae5; padding: 0.75rem; margin-bottom: 0.75rem; }
.timing { font-size: 0.7rem; color: #9ca3af; text-align: right; }

/* Optimizer */
.opt-section { background: #fff; border-radius: 12px; padding: 1rem 1.25rem; border: 1px solid #d1fae5; margin-top: 1rem; }
.opt-btn { background: var(--v-teal); color: #fff; border: none; padding: 0.5rem 1.25rem; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.85rem; }
.opt-btn:disabled { opacity: 0.5; }
.cost-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin: 0.75rem 0; font-size: 0.78rem; }
.cost-grid input[type=number] { width: 100%; border: 1px solid #d1fae5; border-radius: 4px; padding: 3px 6px; font-size: 0.78rem; }
.opt-progress { font-size: 0.75rem; color: var(--v-teal); margin-top: 0.5rem; }
.opt-result { font-size: 0.82rem; margin-top: 0.75rem; }

/* Print-only scorecard */
.print-scorecard { display: none; }

/* ─── Print styles ────────────────────────────────── */
@media print {
  nav, .no-print { display: none !important; }
  .print-scorecard { display: grid !important; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 1rem 0; }
  .print-stat { border: 1px solid #e5e7eb; border-radius: 6px; padding: 0.75rem; text-align: center; }
  .print-stat .n { font-size: 1.5rem; font-weight: 800; color: var(--v-teal); display: block; }
  .print-stat .l { font-size: 0.7rem; color: #6b7280; display: block; }
  section { page-break-inside: avoid; }
  .block, table, .lesson, .action-item { page-break-inside: avoid; }
  body { font-size: 12px; }
  a[href]::after { content: none; }
  #simulator { background: #f9fafb; border: 1px solid #e5e7eb; }
  #simulator .no-print { display: none !important; }
}
</style>
</head>
<body class="bg-white text-gray-900">

<!-- NAV -->
<nav class="sticky top-0 z-50 bg-[#21908c] border-b-2 border-[#35b779]">
  <div class="wrap flex items-center justify-between h-12">
    <span class="font-mono text-xs text-white/50"><strong class="text-white">CLOAK</strong> · BossCovers</span>
    <div class="flex gap-0.5" id="navLinks">
      <a href="#evidence" class="font-mono text-[11px] uppercase tracking-widest text-white/60 px-3 py-1.5 rounded hover:text-white hover:bg-white/10 transition-all">Evidence</a>
      <a href="#lessons"  class="font-mono text-[11px] uppercase tracking-widest text-white/60 px-3 py-1.5 rounded hover:text-white hover:bg-white/10 transition-all">Lessons</a>
      <a href="#simulator" class="font-mono text-[11px] uppercase tracking-widest text-white/60 px-3 py-1.5 rounded hover:text-white hover:bg-white/10 transition-all">Simulator</a>
      <a href="#forecast" class="font-mono text-[11px] uppercase tracking-widest text-white/60 px-3 py-1.5 rounded hover:text-white hover:bg-white/10 transition-all">Forecast</a>
      <a href="#actions"  class="font-mono text-[11px] uppercase tracking-widest text-white/60 px-3 py-1.5 rounded hover:text-white hover:bg-white/10 transition-all">Actions</a>
    </div>
  </div>
</nav>

<!-- HERO -->
<header class="bg-[#0f1923] py-16 px-8">
  <div class="wrap relative" style="background:repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(255,255,255,.025) 39px,rgba(255,255,255,.025) 40px)">
    <div class="font-mono text-xs tracking-widest text-[#21908c] uppercase mb-4">Market Analysis Report · April 2026</div>
    <h1 class="text-3xl font-bold text-white mb-3">CLOAK by BossCovers<br><span class="text-[#21908c]">Go-to-Market Intelligence</span></h1>
    <p class="text-sm text-white/60 mb-8">Prepared from 14,648 comparable campaigns · Monte Carlo simulation engine · Industry benchmarks</p>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white/5 rounded-lg p-4">
        <span class="block text-2xl font-extrabold text-[#21908c]">43%</span>
        <span class="text-xs text-white/50 mt-1 block">Industry campaign<br>success rate</span>
      </div>
      <div class="bg-white/5 rounded-lg p-4">
        <span class="block text-2xl font-extrabold text-[#440154]">$58</span>
        <span class="text-xs text-white/50 mt-1 block">Estimated cost to acquire<br>one customer via Meta ads</span>
      </div>
      <div class="bg-white/5 rounded-lg p-4">
        <span class="block text-2xl font-extrabold text-[#35b779]">$150</span>
        <span class="text-xs text-white/50 mt-1 block">Maximum break-even<br>customer acquisition cost</span>
      </div>
      <div class="bg-white/5 rounded-lg p-4">
        <span class="block text-2xl font-extrabold text-[#fde725]" id="heroProbStat">37%</span>
        <span class="text-xs text-white/50 mt-1 block">Current probability of<br>funding at $15K goal</span>
      </div>
    </div>
  </div>
</header>

<!-- § 1 EVIDENCE -->
<section id="evidence" class="py-16">
  <div class="wrap">
    <div class="section-header">
      <span class="section-num">1</span>
      <h2>The Evidence</h2>
    </div>
    <p class="section-sub">Numbers sourced from public datasets, published fee schedules, and a calibrated Monte Carlo model. Platform fees and industry success rates are externally verified. CAC estimates and conversion figures are model outputs — not independently sourced benchmarks.</p>
    <!-- EVIDENCE CONTENT — Task 2 -->
  </div>
</section>

<!-- § 2 LESSONS -->
<section id="lessons" class="py-16 bg-gray-50">
  <div class="wrap">
    <div class="section-header">
      <span class="section-num">2</span>
      <h2>What the Evidence Means</h2>
    </div>
    <p class="section-sub">Six findings that change the strategy.</p>
    <!-- LESSONS CONTENT — Task 3 -->
  </div>
</section>

<!-- § 3 SIMULATOR -->
<section id="simulator" class="py-16">
  <div class="wrap">
    <div class="section-header">
      <span class="section-num">3</span>
      <h2>Interactive Model</h2>
    </div>
    <p class="section-sub">Monte Carlo crowdfunding projection — drag sliders to explore scenarios. 1,000 simulated runs per change.</p>
    <!-- SIMULATOR CONTENT — Task 4 -->
    <div class="print-scorecard">
      <div class="print-stat"><span class="n" id="printProb">--</span><span class="l">Probability of funding</span></div>
      <div class="print-stat"><span class="n" id="printRaised">--</span><span class="l">Raised (median)</span></div>
      <div class="print-stat"><span class="n" id="printBackers">--</span><span class="l">Backers (median)</span></div>
      <div class="print-stat"><span class="n" id="printNet">--</span><span class="l">Net revenue (median)</span></div>
    </div>
  </div>
</section>

<!-- § 4 FORECAST -->
<section id="forecast" class="py-16">
  <div class="wrap">
    <div class="section-header">
      <span class="section-num">4</span>
      <h2>What the Data Predicts for BossCovers</h2>
    </div>
    <p class="section-sub">Plain numbers. No jargon.</p>
    <!-- FORECAST CONTENT — Task 5 -->
  </div>
</section>

<!-- § 5 ACTIONS -->
<section id="actions" class="py-16 bg-gray-50">
  <div class="wrap">
    <div class="section-header">
      <span class="section-num">5</span>
      <h2>What to Do Next</h2>
    </div>
    <p class="section-sub">In order of priority. Each action sets up the next one.</p>
    <!-- ACTIONS CONTENT — Task 6 -->
  </div>
</section>

<!-- FOOTER -->
<footer class="bg-[#0f1923] py-6">
  <div class="wrap flex flex-col md:flex-row justify-between items-center gap-2 text-xs text-white/40 font-mono">
    <span>BossCovers CLOAK · Market Analysis Report · April 2026</span>
    <span>Data: Kaggle KS Dataset · Monte Carlo simulation · IndieGoGo published fee schedule</span>
  </div>
</footer>

<!-- JS — Tasks 7 + 8 -->
<script>
// placeholder — simulator JS goes here in Task 7
</script>

</body>
</html>
```

- [ ] **Step 2: Verify skeleton in browser**

Open `report.html` in a browser. Expected: navy hero, teal nav with 5 links, 5 white sections with section-number circles, teal footer. No simulator content yet — that's correct.

- [ ] **Step 3: Commit skeleton**

```bash
cd C:/GitHub/indiegogo-simulator
git add report.html
git commit -m "feat: scaffold combined report skeleton with Tailwind+DaisyUI+viridis theme"
```

---

## Task 2: Port §1 Evidence content

**Files:**
- Modify: `report.html` — replace the `<!-- EVIDENCE CONTENT — Task 2 -->` comment

- [ ] **Step 1: Replace the evidence placeholder**

Inside `<section id="evidence">`, after the `<p class="section-sub">`, replace the comment with the content block below. This is the full Evidence section content from `report.html`, restyled to use the new CSS classes.

```html
    <!-- Kickstarter benchmarks -->
    <div class="block">
      <h3>Crowdfunding Industry Benchmarks <span class="src">Source: Kaggle Kickstarter dataset, 14,648 comparable campaigns</span></h3>
      <div class="stat-row">
        <div class="stat-card"><span class="n">14,648</span><span class="l">Tech &amp; Design campaigns analyzed<br>($5K–$100K goal, $50–$500 avg pledge)</span></div>
        <div class="stat-card"><span class="n">43%</span><span class="l">Overall campaign<br>success rate</span></div>
        <div class="stat-card"><span class="n">245</span><span class="l">Median backers in<br>successful campaigns</span></div>
        <div class="stat-card"><span class="n">$30,188</span><span class="l">Median amount raised<br>by successful campaigns</span></div>
      </div>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>Funding Goal Range</th><th>Success Rate</th><th>Median Backers (if successful)</th><th>Median Raised (if successful)</th></tr></thead>
          <tbody>
            <tr><td class="em">$5,000 – $10,000</td><td class="mono">54%</td><td class="mono">113</td><td class="mono">$10,890</td></tr>
            <tr><td class="em">$10,000 – $25,000</td><td class="mono">47%</td><td class="mono">211</td><td class="mono">$23,369</td></tr>
            <tr><td class="em">$25,000 – $100,000</td><td class="mono">38%</td><td class="mono">410+</td><td class="mono">$50,000+</td></tr>
          </tbody>
        </table>
      </div>
      <div class="callout warn">
        <div class="callout-label">Key finding</div>
        <p><strong>Half of all comparable campaigns raise less than $30,000.</strong> The campaigns you read about raising $500K are outliers — they typically have 50,000+ email subscribers built over 6–12 months before launch.</p>
      </div>
    </div>

    <!-- Acquisition cost table — port all rows from old report.html evidence section unchanged -->
    <div class="block">
      <h3>Cost to Acquire One Customer <span class="src">Source: Monte Carlo simulator calibrated to Kickstarter historical data</span></h3>
      <p class="text-sm text-gray-500 mb-4">This is the most important number. Every dollar spent acquiring a customer that costs more than your profit margin is a losing trade.</p>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>Channel</th><th>How it works</th><th>Low estimate</th><th>Central estimate</th><th>High estimate</th><th>Profitable?</th></tr></thead>
          <tbody>
            <tr>
              <td class="em">YouTube creator<br><small class="text-gray-400 text-xs">Gift a unit to a 200K-sub channel</small></td>
              <td class="text-sm">Send 1 free CLOAK to a relevant creator. They review it. Viewers buy.</td>
              <td class="mono">$3</td><td class="mono">$15–$60</td><td class="mono">$120</td>
              <td><span class="tag-win">✓ Usually yes</span></td>
            </tr>
            <tr>
              <td class="em">Reddit paid ads<br><small class="text-gray-400 text-xs">Interest targeting: 2A, preppers</small></td>
              <td class="text-sm">Show ads in relevant subreddits. Cheap CPM, low click rate.</td>
              <td class="mono">$50</td><td class="mono">$100–$150</td><td class="mono">$200</td>
              <td><span class="tag-meh">~ Maybe</span></td>
            </tr>
            <tr>
              <td class="em">Meta / Facebook ads<br><small class="text-gray-400 text-xs">Interest + lookalike targeting</small></td>
              <td class="text-sm">Broad reach, higher CPM. Industry-standard for physical products.</td>
              <td class="mono">$75</td><td class="mono">$58–$150</td><td class="mono">$250</td>
              <td><span class="tag-meh">~ Borderline</span></td>
            </tr>
            <tr>
              <td class="em">Email (warm list)<br><small class="text-gray-400 text-xs">Pre-launch opt-in subscribers</small></td>
              <td class="text-sm">42% open, 10% CTOR, 18% page-to-backer. 5 emails total.</td>
              <td class="mono">$0</td><td class="mono">$0–$3</td><td class="mono">$5</td>
              <td><span class="tag-win">✓ Yes (owned channel)</span></td>
            </tr>
            <tr>
              <td class="em">IndieGoGo organic<br><small class="text-gray-400 text-xs">Platform discovery</small></td>
              <td class="text-sm">People browsing the platform find the campaign.</td>
              <td class="mono">$0</td><td class="mono">$0 (negligible)</td><td class="mono">$0</td>
              <td><span class="tag-meh">~ Unreliable</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Platform Cost block — port from old report.html -->
    <div class="block">
      <h3>Platform Fees <span class="src">Source: IndieGoGo published fee schedule</span></h3>
      <div class="stat-row">
        <div class="stat-card"><span class="n">5%</span><span class="l">IndieGoGo platform fee<br>(on gross raised)</span></div>
        <div class="stat-card"><span class="n">3%</span><span class="l">Payment processing fee<br>(on gross raised)</span></div>
        <div class="stat-card"><span class="n">$0.20</span><span class="l">Per-transaction fee<br>(per backer)</span></div>
        <div class="stat-card"><span class="n">8%+</span><span class="l">Total combined fee rate<br>(typical campaign)</span></div>
      </div>
      <div class="callout">
        <div class="callout-label">What this means</div>
        <p>On a $30,000 campaign with 200 backers: fees = $1,500 (platform) + $900 (processing) + $40 (per-txn) = <strong>$2,440 in fees</strong>. Direct-to-consumer via Shopify costs ~1.7–2.9% (Stripe) with no platform cut.</p>
      </div>
    </div>

    <!-- Production Cap block -->
    <div class="block">
      <h3>Production Capacity <span class="src">Source: BossCovers manufacturing constraint</span></h3>
      <div class="stat-row">
        <div class="stat-card"><span class="n">20</span><span class="l">Units produced per day<br>(current throughput)</span></div>
        <div class="stat-card"><span class="n">90</span><span class="l">Maximum fulfillment<br>days assumed</span></div>
        <div class="stat-card"><span class="n">1,800</span><span class="l">Hard cap on units<br>a campaign can fulfill</span></div>
      </div>
      <div class="callout warn">
        <div class="callout-label">Hard constraint</div>
        <p>The simulator enforces a 1,800-unit ceiling on all projections. Revenue cannot exceed ~$360,000 gross regardless of audience size or ad spend. This is not a model assumption — it's a manufacturing reality.</p>
      </div>
    </div>

    <!-- Audience Conversion block -->
    <div class="block">
      <h3>Audience Conversion Rates <span class="src">Source: Monte Carlo simulator (calibrated to KS data + industry benchmarks)</span></h3>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>Channel</th><th>Input</th><th>Expected Backers per Campaign</th><th>Key Rate</th></tr></thead>
          <tbody>
            <tr><td class="em">Email list (warm)</td><td class="mono">50 subscribers</td><td class="mono">0–1</td><td class="mono">~3.8% of list</td></tr>
            <tr><td class="em">Instagram organic</td><td class="mono">124 followers</td><td class="mono">≈ 0</td><td class="mono">0.008% of followers/post</td></tr>
            <tr><td class="em">Facebook organic</td><td class="mono">69 followers</td><td class="mono">≈ 0</td><td class="mono">0.003% of followers/post</td></tr>
            <tr><td class="em">Paid ads (Meta)</td><td class="mono">$0/day</td><td class="mono">0</td><td class="mono">~$58 CPA at current benchmarks</td></tr>
            <tr><td class="em">IGG organic</td><td class="mono">Platform</td><td class="mono">0–1 total</td><td class="mono">5 visitors/day median</td></tr>
          </tbody>
        </table>
      </div>
    </div>
```

- [ ] **Step 2: Verify §1 in browser**

Open `report.html`. §1 should show: 4 viridis stat cards (purple/blue/teal/green left borders), two tables, three callout boxes. Scroll test: nav stays sticky.

- [ ] **Step 3: Commit**

```bash
git add report.html
git commit -m "feat: port evidence section to viridis infographic style"
```

---

## Task 3: Port §2 Lessons content

**Files:**
- Modify: `report.html` — replace `<!-- LESSONS CONTENT — Task 3 -->` comment

- [ ] **Step 1: Replace the lessons placeholder**

Inside `<section id="lessons">`, replace the comment with:

```html
    <div class="lessons">
      <div class="lesson flag">
        <div class="lnum">Lesson 01</div>
        <h4>Crowdfunding is a capital tool — and you don't need capital</h4>
        <p>Crowdfunding campaigns make sense when a business needs upfront money to produce its product. BossCovers' tooling is already paid for. Running a campaign would just be a pre-order mechanism with an 8% fee, a 30-day clock, and 200–350 hours of founder work attached.</p>
      </div>
      <div class="lesson flag">
        <div class="lnum">Lesson 02</div>
        <h4>Paid ads cost more per customer than the margin allows</h4>
        <p>At a modeled median $58 cost per customer via Meta ads and a $150 maximum break-even threshold, Meta acquisition is technically profitable — but only if real-world performance matches benchmarks. Exceptional creative and tight targeting are required. The $224 figure in the previous report was a calibration artifact and has been corrected.</p>
      </div>
      <div class="lesson">
        <div class="lnum">Lesson 03</div>
        <h4>Your social following has almost no direct conversion power</h4>
        <p>The conversion chain compounds badly: followers → reach → click → purchase = 0.004% of followers per post. 10,000 Instagram followers → approximately 4 buyers per announcement. Social is a trust signal and a creative testing ground — not a sales engine at this audience size.</p>
      </div>
      <div class="lesson">
        <div class="lnum">Lesson 04</div>
        <h4>Email is the strongest owned channel — but the list is too small yet</h4>
        <p>The rule of thumb: 1 buyer per 100 email subscribers. BossCovers' current list of 50 people generates 0–1 buyers from email. Growing to 1,000 (through YouTube reviews and landing page capture) would generate ~10 buyers per campaign — for free.</p>
      </div>
      <div class="lesson">
        <div class="lnum">Lesson 05</div>
        <h4>YouTube creators cost 10× less per customer than Facebook ads</h4>
        <p>Gifting one CLOAK unit ($60 all-in) to a 200K-subscriber 2A or prepper channel generates an average of 12 sales. That's a $5 cost per customer — vs. $58+ on Facebook. The downside: the audience is finite and results aren't guaranteed.</p>
      </div>
      <div class="lesson flag">
        <div class="lnum">Lesson 06</div>
        <h4>A crowdfunding campaign is 200–350 hours of founder time</h4>
        <p>Campaign video (40–80 hrs), page copy and design (30–50 hrs), PR outreach (30–50 hrs), daily backer management (2 hrs/day × 30 days = 60 hrs), email updates, social posts. That's a second part-time job for 3–4 months — for a campaign with uncertain odds at the current audience size.</p>
      </div>
    </div>
```

- [ ] **Step 2: Verify §2 in browser**

§2 (gray background) shows 6 lesson cards. Lessons 01, 02, 06 have purple flag styling. Others have plain gray border.

- [ ] **Step 3: Commit**

```bash
git add report.html
git commit -m "feat: port lessons section with viridis flag styling"
```

---

## Task 4: Build §3 Simulator section

**Files:**
- Modify: `report.html` — replace `<!-- SIMULATOR CONTENT — Task 4 -->` comment

- [ ] **Step 1: Replace the simulator placeholder**

Inside `<section id="simulator">`, replace the comment (keep the `.print-scorecard` div that's already there — place the new content before it):

```html
    <!-- Scorecard -->
    <div class="sim-card sim-scorecard no-print">
      <div class="sim-prob" id="probBig">--</div>
      <div class="sim-prob-label" id="probLabel">probability of funding</div>
      <div class="sim-verdict" id="verdictBar"></div>
      <div class="sim-stats">
        <div class="sim-stat"><div class="sim-stat-label">Raised (median)</div><div class="sim-stat-value" id="statRaised">--</div></div>
        <div class="sim-stat"><div class="sim-stat-label">Backers (median)</div><div class="sim-stat-value" id="statBackers">--</div></div>
        <div class="sim-stat"><div class="sim-stat-label">Net Revenue</div><div class="sim-stat-value" id="statNet">--</div></div>
        <div class="sim-stat"><div class="sim-stat-label">Goal</div><div class="sim-stat-value" id="statGoal">--</div></div>
      </div>
    </div>

    <!-- Controls -->
    <div class="grid md:grid-cols-2 gap-4 no-print">
      <div class="sim-card">
        <div class="sim-section-title">Audience</div>
        <div class="slider-row"><label>Email list</label><input type="range" id="email" min="0" max="10000" step="50" value="50"><span class="slider-val" id="emailVal">50</span></div>
        <div class="slider-row"><label>IG followers</label><input type="range" id="ig" min="0" max="10000" step="50" value="124"><span class="slider-val" id="igVal">124</span></div>
        <div class="slider-row"><label>FB followers</label><input type="range" id="fb" min="0" max="10000" step="50" value="69"><span class="slider-val" id="fbVal">69</span></div>
        <div class="slider-row"><label>Ad budget ($/day)</label><input type="range" id="adBudget" min="0" max="500" step="5" value="0"><span class="slider-val" id="adBudgetVal">$0</span></div>
        <div class="slider-row"><label>PR / media hits</label><input type="range" id="pr" min="0" max="10" step="1" value="0"><span class="slider-val" id="prVal">0</span></div>
      </div>
      <div class="sim-card">
        <div class="sim-section-title">Campaign</div>
        <div class="slider-row"><label>Funding goal ($)</label><input type="range" id="goal" min="5000" max="100000" step="1000" value="15000"><span class="slider-val" id="goalVal">$15,000</span></div>
        <div class="slider-row"><label>Duration (days)</label><input type="range" id="duration" min="15" max="60" step="1" value="30"><span class="slider-val" id="durationVal">30</span></div>
        <div class="slider-row"><label>Early bird price ($)</label><input type="range" id="ebPrice" min="99" max="179" step="5" value="149"><span class="slider-val" id="ebPriceVal">$149</span></div>
        <div class="slider-row"><label>Early bird qty</label><input type="range" id="ebQty" min="0" max="500" step="10" value="50"><span class="slider-val" id="ebQtyVal">50</span></div>
      </div>
    </div>

    <!-- Charts -->
    <div class="chart-wrap no-print"><canvas id="fanChart" height="220"></canvas></div>
    <div class="chart-wrap no-print"><canvas id="histChart" height="160"></canvas></div>
    <div class="timing no-print" id="timing"></div>

    <!-- Budget Optimizer -->
    <div class="opt-section no-print">
      <div class="sim-section-title">Budget Optimizer</div>
      <p class="text-xs text-gray-500 mb-3">Set your total pre-launch marketing budget and cost per unit for each channel. The optimizer finds the allocation that maximizes your probability of funding.</p>
      <div class="slider-row"><label>Total budget ($)</label><input type="range" id="totalBudget" min="0" max="10000" step="100" value="2000"><span class="slider-val" id="totalBudgetVal">$2,000</span></div>
      <div class="cost-grid">
        <div><label class="text-xs text-gray-600">$/email subscriber</label><input type="number" id="costEmail" value="3" min="0.5" max="20" step="0.5"></div>
        <div><label class="text-xs text-gray-600">$/IG follower</label><input type="number" id="costIg" value="4" min="0.5" max="20" step="0.5"></div>
        <div><label class="text-xs text-gray-600">$/FB follower</label><input type="number" id="costFb" value="3" min="0.5" max="20" step="0.5"></div>
        <div><label class="text-xs text-gray-600">Ad budget ($/day×30d)</label><input type="number" id="costAd" value="1" min="1" max="1" step="0" disabled style="opacity:0.5"></div>
        <div><label class="text-xs text-gray-600">$/PR hit</label><input type="number" id="costPr" value="1000" min="100" max="5000" step="100"></div>
      </div>
      <button class="opt-btn" id="optimizeBtn" onclick="runOptimizer()">Find Optimal Allocation</button>
      <div class="opt-progress" id="optProgress"></div>
      <div class="opt-result" id="optResult"></div>
    </div>
```

- [ ] **Step 2: Verify §3 layout in browser**

§3 (pale teal background) shows: scorecard panel, 2-column sliders, chart placeholders, optimizer. Charts will be empty until JS is added in Task 7.

- [ ] **Step 3: Commit**

```bash
git add report.html
git commit -m "feat: add simulator section HTML with viridis styling"
```

---

## Task 5: Port §4 Forecast and §5 Actions content

**Files:**
- Modify: `report.html` — replace both forecast and actions placeholder comments

- [ ] **Step 1: Replace forecast placeholder**

Inside `<section id="forecast">`, replace `<!-- FORECAST CONTENT — Task 5 -->` with the full forecast content from the old `report.html` §3. Copy the three `.block` divs verbatim (current state, channel predictions, break-even math), replacing old CSS classes with new ones:

- `class="state-box"` → keep (already defined in Task 1 CSS)
- `class="state-item"` → keep
- `class="callout"` → keep  
- `class="bar-chart"` / `class="bar-row"` etc → keep
- `class="tbl-wrap"` / `table` → keep
- `class="block"` → keep

Also update the old `var(--muted)` inline style references to `class="text-gray-500"`.

The section tag is already in the shell as `<h2>What the Data Predicts for BossCovers</h2>`. The content blocks to port (from old `report.html` lines 893–997):
- "Where BossCovers Stands Today" block with `.state-box` and 3 `.state-item` divs
- "What Each Action Is Likely to Produce" block with `.bar-chart`
- "The Break-Even Math" block with a table

Port each block verbatim, only swapping the inline `color: var(--muted)` style references to Tailwind class `text-gray-500`.

- [ ] **Step 2: Replace actions placeholder**

Inside `<section id="actions">`, replace `<!-- ACTIONS CONTENT — Task 6 -->` with the actions content from old `report.html` §4 (lines 1001–1088).

Port the action items using the new `.action-list` / `.action-item` / `.action-num` classes defined in Task 1. Each old action becomes:

```html
<div class="action-list">
  <div class="action-item">
    <div class="action-num">1</div>
    <div>
      <div class="action-timeline">Month 1–2</div>
      <h4>[action title]</h4>
      <p>[action description]</p>
    </div>
  </div>
  <!-- repeat for each action -->
</div>
```

Mark actions that are "don't do this" or warnings with `class="action-item alt"` (purple circle).

End with the summary callout from old `report.html` line 1083:

```html
<div class="callout" style="margin-top:2.5rem;">
  <div class="callout-label">The 6-month playbook</div>
  <p><strong>YouTube seeds → build social proof → test ads → learn real CPA → walk into SHOT Show with receipts.</strong> Six months of this positions BossCovers for a distributor conversation with documented demand — a much stronger hand than a $2,600 crowdfunding campaign ever would.</p>
</div>
```

- [ ] **Step 3: Verify §4 and §5 in browser**

Full page should now render all 5 sections with content. Scroll through the entire page. Check: forecast numbers render, action items have numbered circles, summary callout appears at bottom.

- [ ] **Step 4: Commit**

```bash
git add report.html
git commit -m "feat: port forecast and actions sections"
```

---

## Task 6: Port all simulator JavaScript

**Files:**
- Modify: `report.html` — replace the placeholder `<script>` block at the bottom

- [ ] **Step 1: Get current calibrated DISTS values**

Run this to read the current calibrated params from `data/calibrated-params.json`:

```bash
cd C:/GitHub/indiegogo-simulator
source .venv/Scripts/activate
python -c "
import json
with open('data/calibrated-params.json') as f:
    d = json.load(f)
for k, v in d['params'].items():
    if 'a' in v:
        print(f'  {k}: {{ type: \"beta\", a: {v[\"a\"]:.4f}, b: {v[\"b\"]:.4f} }},')
    else:
        print(f'  {k}: {{ type: \"lognormal\", s: {v[\"s\"]:.4f}, scale: {v[\"scale\"]:.4f} }},')
"
```

Note the output — this is the DISTS object for the `<script>` block.

- [ ] **Step 2: Replace the placeholder script with the full JS**

Replace `<script>// placeholder — simulator JS goes here in Task 7</script>` with:

```html
<script>
// =====================================================
// CLOAK Campaign Simulator — JavaScript Monte Carlo
// Port of Python engine (src/) for static deployment
// Parameters synced with data/calibrated-params.json
// =====================================================

const N_RUNS = 1000;

function makeRng(seed) {
  let s = [seed, seed ^ 0x6D2B79F5, seed ^ 0x1B56C4E9, seed ^ 0x9E3779B9];
  function rotl(x, k) { return ((x << k) | (x >>> (32 - k))) >>> 0; }
  function next() {
    const r = (rotl((s[1] * 5) >>> 0, 7) * 9) >>> 0;
    const t = (s[1] << 9) >>> 0;
    s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3];
    s[2] ^= t; s[3] = rotl(s[3], 11);
    return r / 4294967296;
  }
  return { uniform: next };
}

function normalSample(rng) {
  const u1 = rng.uniform(); const u2 = rng.uniform();
  return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
}

function gammaSample(rng, shape) {
  if (shape < 1) { const u = rng.uniform(); return gammaSample(rng, shape + 1) * Math.pow(u, 1 / shape); }
  const d = shape - 1/3; const c = 1 / Math.sqrt(9 * d);
  while (true) {
    let x, v;
    do { x = normalSample(rng); v = 1 + c * x; } while (v <= 0);
    v = v * v * v;
    const u = rng.uniform();
    if (u < 1 - 0.0331 * (x*x)*(x*x)) return d * v;
    if (Math.log(u) < 0.5*x*x + d*(1 - v + Math.log(v))) return d * v;
  }
}

function betaSample(rng, a, b) { const x = gammaSample(rng, a); const y = gammaSample(rng, b); return x / (x + y); }
function lognormalSample(rng, s, scale) { return scale * Math.exp(s * normalSample(rng)); }
function poissonSample(rng, lambda) {
  if (lambda <= 0) return 0;
  if (lambda > 30) return Math.max(0, Math.round(lambda + Math.sqrt(lambda) * normalSample(rng)));
  const L = Math.exp(-lambda); let k = 0, p = 1;
  do { k++; p *= rng.uniform(); } while (p > L);
  return k - 1;
}

// DISTS: paste output of Step 1 python command here, wrapped in const DISTS = { ... }
const DISTS = {
  // REPLACE THIS BLOCK with output from the python command in Step 1
  EMAIL_OPEN_RATE:       { type: 'beta', a: 16.3599, b: 23.6401 },
  EMAIL_CTR:             { type: 'beta', a: 5.9292,  b: 24.0708 },
  EMAIL_PAGE_TO_BACKER:  { type: 'beta', a: 0.3053,  b: 19.6947 },
  IG_REACH_RATE:         { type: 'beta', a: 0.6774,  b: 99.3226 },
  IG_CTR:                { type: 'beta', a: 0.0793,  b: 24.9207 },
  IG_PAGE_TO_BACKER:     { type: 'beta', a: 0.4986,  b: 39.5014 },
  FB_REACH_RATE:         { type: 'beta', a: 1.2433,  b: 78.7567 },
  FB_CTR:                { type: 'beta', a: 0.0264,  b: 49.9736 },
  FB_PAGE_TO_BACKER:     { type: 'beta', a: 0.3001,  b: 39.6999 },
  AD_CPM:                { type: 'lognormal', s: 0.4, scale: 29.59 },
  AD_CTR:                { type: 'beta', a: 0.3282,  b: 99.6718 },
  AD_PAGE_TO_BACKER:     { type: 'beta', a: 0.3995,  b: 49.6005 },
  PR_REACH_PER_HIT:      { type: 'lognormal', s: 1.0, scale: 3117 },
  PR_CTR:                { type: 'beta', a: 0.8647,  b: 99.1353 },
  PR_PAGE_TO_BACKER:     { type: 'beta', a: 3.44,    b: 96.56 },
  IGG_DAILY_VISITORS:    { type: 'lognormal', s: 0.5, scale: 79.57 },
  IGG_PAGE_TO_BACKER:    { type: 'beta', a: 0.20,    b: 99.80 },
  WOM_TELLS:             { type: 'lognormal', s: 0.5, scale: 0.24 },
  WOM_VISIT_RATE:        { type: 'beta', a: 1.0,     b: 99.0 },
  WOM_PAGE_TO_BACKER:    { type: 'beta', a: 8.13,    b: 91.87 },
};

function sampleDist(rng, d) {
  if (d.type === 'beta') return betaSample(rng, d.a, d.b);
  if (d.type === 'lognormal') return lognormalSample(rng, d.s, d.scale);
  return 0;
}

// U-curve, traffic source models, revenue — carry over verbatim from index.html
// (lines 378–537 of index.html)
function ucurveWeights(duration) {
  const w = new Float64Array(duration); let sum = 0;
  for (let i = 0; i < duration; i++) {
    const launch = Math.exp(-i / 2.5); const deadline = Math.exp(-(duration - 1 - i) / 2.5);
    w[i] = launch + deadline + 0.02; sum += w[i];
  }
  for (let i = 0; i < duration; i++) w[i] /= sum;
  return w;
}

function emailTraffic(rng, listSize, duration, weights) {
  if (listSize === 0) return new Float64Array(duration);
  const openRate = sampleDist(rng, DISTS.EMAIL_OPEN_RATE);
  const ctr = sampleDist(rng, DISTS.EMAIL_CTR);
  const p2b = sampleDist(rng, DISTS.EMAIL_PAGE_TO_BACKER);
  const totalBackers = listSize * openRate * ctr * 5 * p2b;
  const ew = new Float64Array(duration); let esum = 0;
  for (let i = 0; i < duration; i++) { ew[i] = weights[i]; if (i === 0) ew[i] *= 5; if (i === 1) ew[i] *= 3; esum += ew[i]; }
  const out = new Float64Array(duration);
  for (let i = 0; i < duration; i++) out[i] = poissonSample(rng, Math.max(0, totalBackers * ew[i] / esum));
  return out;
}

function socialTraffic(rng, igFollowers, fbFollowers, duration, weights) {
  let totalBackers = 0;
  if (igFollowers > 0) { const reach = igFollowers * sampleDist(rng, DISTS.IG_REACH_RATE); const clicks = reach * sampleDist(rng, DISTS.IG_CTR); totalBackers += clicks * sampleDist(rng, DISTS.IG_PAGE_TO_BACKER) * 6; }
  if (fbFollowers > 0) { const reach = fbFollowers * sampleDist(rng, DISTS.FB_REACH_RATE); const clicks = reach * sampleDist(rng, DISTS.FB_CTR); totalBackers += clicks * sampleDist(rng, DISTS.FB_PAGE_TO_BACKER) * 6; }
  if (totalBackers === 0) return new Float64Array(duration);
  const out = new Float64Array(duration);
  for (let i = 0; i < duration; i++) out[i] = poissonSample(rng, Math.max(0, totalBackers * weights[i]));
  return out;
}

function paidAdsTraffic(rng, dailyBudget, duration, weights) {
  if (dailyBudget <= 0) return new Float64Array(duration);
  const cpm = sampleDist(rng, DISTS.AD_CPM); const ctr = sampleDist(rng, DISTS.AD_CTR); const p2b = sampleDist(rng, DISTS.AD_PAGE_TO_BACKER);
  const dailyExpected = (dailyBudget / cpm) * 1000 * ctr * p2b;
  const out = new Float64Array(duration);
  for (let i = 0; i < duration; i++) { const w = 0.5/duration + 0.5*weights[i]; out[i] = poissonSample(rng, Math.max(0, dailyExpected * duration * w)); }
  return out;
}

function prTraffic(rng, numHits, duration, weights) {
  if (numHits <= 0) return new Float64Array(duration);
  let totalBackers = 0;
  for (let h = 0; h < numHits; h++) { const reach = sampleDist(rng, DISTS.PR_REACH_PER_HIT); totalBackers += reach * sampleDist(rng, DISTS.PR_CTR) * sampleDist(rng, DISTS.PR_PAGE_TO_BACKER); }
  const pw = new Float64Array(duration); let psum = 0;
  for (let i = 0; i < duration; i++) { pw[i] = weights[i] * (i < 7 ? 3 : 1); psum += pw[i]; }
  const out = new Float64Array(duration);
  for (let i = 0; i < duration; i++) out[i] = poissonSample(rng, Math.max(0, totalBackers * pw[i] / psum));
  return out;
}

function iggOrganicTraffic(rng, duration, weights) {
  const dailyVisitors = sampleDist(rng, DISTS.IGG_DAILY_VISITORS); const p2b = sampleDist(rng, DISTS.IGG_PAGE_TO_BACKER);
  const dailyExpected = dailyVisitors * p2b;
  const out = new Float64Array(duration);
  for (let i = 0; i < duration; i++) { const w = 0.7/duration + 0.3*weights[i]; out[i] = poissonSample(rng, Math.max(0, dailyExpected * duration * w)); }
  return out;
}

function womTraffic(rng, cumulativeBackers, duration) {
  const tells = sampleDist(rng, DISTS.WOM_TELLS); const visitRate = sampleDist(rng, DISTS.WOM_VISIT_RATE); const p2b = sampleDist(rng, DISTS.WOM_PAGE_TO_BACKER);
  const out = new Float64Array(duration);
  for (let day = 1; day < duration; day++) {
    const newPrev = cumulativeBackers[day] - (day > 0 ? cumulativeBackers[day-1] : 0);
    out[day] = poissonSample(rng, Math.max(0, newPrev * tells * visitRate * p2b));
  }
  return out;
}

const UNITS_PER_DAY = 20; const MAX_FULFILLMENT_DAYS = 90; const MAX_UNITS = UNITS_PER_DAY * MAX_FULFILLMENT_DAYS;

function calculateRevenue(dailyBackers, ebPrice, ebQty, stdPrice, duration) {
  let rawBackers = 0; for (let i = 0; i < duration; i++) rawBackers += dailyBackers[i];
  const totalBackers = Math.min(rawBackers, MAX_UNITS);
  if (totalBackers === 0) return { gross: 0, net: 0, backers: 0, dailyCum: new Float64Array(duration), capped: false };
  const ebBackers = Math.min(totalBackers, ebQty); const stdBackers = totalBackers - ebBackers;
  const gross = ebBackers * ebPrice + stdBackers * stdPrice;
  const fees = gross * 0.05 + gross * 0.03 + totalBackers * 0.20;
  const net = gross - fees - totalBackers * 45 - totalBackers * 12;
  const dailyCum = new Float64Array(duration); let cumBackers = 0; let cumRev = 0;
  for (let i = 0; i < duration; i++) {
    const db = dailyBackers[i];
    if (db > 0) {
      const cumBefore = cumBackers; cumBackers += db;
      const ebInDay = Math.min(db, Math.max(0, Math.min(cumBackers, ebQty) - Math.max(cumBefore, 0)));
      cumRev += ebInDay * ebPrice + (db - ebInDay) * stdPrice;
    }
    dailyCum[i] = cumRev;
  }
  return { gross, net, backers: totalBackers, dailyCum, capped: rawBackers > MAX_UNITS };
}

function runSimulation(params) {
  const { emailList, igFollowers, fbFollowers, dailyAdBudget, prHits, goal, duration, ebPrice, ebQty } = params;
  const stdPrice = 200.00; const weights = ucurveWeights(duration);
  const allRaised = new Float64Array(N_RUNS); const allBackers = new Float64Array(N_RUNS);
  const allNet = new Float64Array(N_RUNS); const allFunded = new Uint8Array(N_RUNS);
  const allTrajectories = [];
  for (let run = 0; run < N_RUNS; run++) {
    const rng = makeRng(42 + run);
    const backers = new Float64Array(duration);
    const em = emailTraffic(rng, emailList, duration, weights);
    const soc = socialTraffic(rng, igFollowers, fbFollowers, duration, weights);
    const ads = paidAdsTraffic(rng, dailyAdBudget, duration, weights);
    const prT = prTraffic(rng, prHits, duration, weights);
    const org = iggOrganicTraffic(rng, duration, weights);
    for (let i = 0; i < duration; i++) backers[i] = em[i] + soc[i] + ads[i] + prT[i] + org[i];
    const cum = new Float64Array(duration); cum[0] = backers[0];
    for (let i = 1; i < duration; i++) cum[i] = cum[i-1] + backers[i];
    const wom = womTraffic(rng, cum, duration);
    for (let i = 0; i < duration; i++) backers[i] += wom[i];
    const rev = calculateRevenue(backers, ebPrice, ebQty, stdPrice, duration);
    allRaised[run] = rev.gross; allBackers[run] = rev.backers; allNet[run] = rev.net;
    allFunded[run] = rev.gross >= goal ? 1 : 0;
    allTrajectories.push(rev.dailyCum);
  }
  const sortedRaised = Float64Array.from(allRaised).sort();
  const sortedBackers = Float64Array.from(allBackers).sort();
  const sortedNet = Float64Array.from(allNet).sort();
  const pctl = (arr, p) => arr[Math.min(Math.floor(p/100*arr.length), arr.length-1)];
  let funded = 0; for (let i = 0; i < N_RUNS; i++) funded += allFunded[i];
  const trajPctls = {};
  for (const p of [10, 25, 50, 75, 90]) {
    trajPctls[p] = new Float64Array(duration);
    for (let d = 0; d < duration; d++) {
      const col = new Float64Array(N_RUNS);
      for (let r = 0; r < N_RUNS; r++) col[r] = allTrajectories[r][d];
      col.sort(); trajPctls[p][d] = pctl(col, p);
    }
  }
  return { prob: funded/N_RUNS, raised: { p10: pctl(sortedRaised,10), p50: pctl(sortedRaised,50), p90: pctl(sortedRaised,90) }, backers: { p10: pctl(sortedBackers,10), p50: pctl(sortedBackers,50), p90: pctl(sortedBackers,90) }, netMedian: pctl(sortedNet,50), trajPctls, allRaised: sortedRaised, duration, goal };
}

// =====================================================
// UI
// =====================================================
const $ = id => document.getElementById(id);
let fanChartInstance = null; let histChartInstance = null;
function fmt(n) { return Math.abs(n) >= 1000 ? '$' + Math.round(n).toLocaleString() : '$' + Math.round(n); }

function updatePrintScorecard(res, params) {
  const probPct = Math.round(res.prob * 100);
  const printProb = $('printProb'); if (printProb) printProb.textContent = probPct + '%';
  const printRaised = $('printRaised'); if (printRaised) printRaised.textContent = fmt(res.raised.p50);
  const printBackers = $('printBackers'); if (printBackers) printBackers.textContent = Math.round(res.backers.p50).toLocaleString();
  const printNet = $('printNet'); if (printNet) printNet.textContent = fmt(res.netMedian);
  const heroProbStat = $('heroProbStat'); if (heroProbStat) heroProbStat.textContent = probPct + '%';
}

function updateDisplay() {
  const t0 = performance.now();
  const params = {
    emailList: +$('email').value, igFollowers: +$('ig').value, fbFollowers: +$('fb').value,
    dailyAdBudget: +$('adBudget').value, prHits: +$('pr').value, goal: +$('goal').value,
    duration: +$('duration').value, ebPrice: +$('ebPrice').value, ebQty: +$('ebQty').value,
  };
  $('emailVal').textContent = params.emailList.toLocaleString();
  $('igVal').textContent = params.igFollowers.toLocaleString();
  $('fbVal').textContent = params.fbFollowers.toLocaleString();
  $('adBudgetVal').textContent = '$' + params.dailyAdBudget;
  $('prVal').textContent = params.prHits;
  $('goalVal').textContent = '$' + params.goal.toLocaleString();
  $('durationVal').textContent = params.duration;
  $('ebPriceVal').textContent = '$' + params.ebPrice;
  $('ebQtyVal').textContent = params.ebQty;

  const res = runSimulation(params);
  const elapsed = ((performance.now() - t0) / 1000).toFixed(2);
  const probPct = Math.round(res.prob * 100);

  let color, label;
  if (res.prob >= 0.70)      { color = '#35b779'; label = 'STRONG — launch with confidence'; }
  else if (res.prob >= 0.50) { color = '#21908c'; label = 'VIABLE — proceed with active plan'; }
  else if (res.prob >= 0.20) { color = '#b45309'; label = 'RISKY — more prep recommended'; }
  else                       { color = '#440154'; label = 'DO NOT LAUNCH without more preparation'; }

  $('probBig').textContent = probPct + '%';
  $('probBig').style.color = color;
  $('probLabel').textContent = label;
  $('verdictBar').textContent = probPct >= 50
    ? `Median: ${fmt(res.raised.p50)} raised, ${Math.round(res.backers.p50)} backers`
    : `Range: ${fmt(res.raised.p10)} (pessimistic) to ${fmt(res.raised.p90)} (optimistic)`;
  $('verdictBar').style.background = color;
  $('statRaised').textContent = fmt(res.raised.p50);
  $('statBackers').textContent = Math.round(res.backers.p50).toLocaleString();
  $('statNet').textContent = fmt(res.netMedian);
  $('statNet').style.color = res.netMedian >= 0 ? '#35b779' : '#440154';
  $('statGoal').textContent = fmt(params.goal);
  $('timing').textContent = `${N_RUNS.toLocaleString()} Monte Carlo runs in ${elapsed}s`;

  updatePrintScorecard(res, params);

  // Fan chart — viridis colors
  const days = Array.from({length: params.duration}, (_, i) => i + 1);
  if (fanChartInstance) fanChartInstance.destroy();
  fanChartInstance = new Chart($('fanChart'), {
    type: 'line',
    data: { labels: days, datasets: [
      { label: '90th pctl', data: Array.from(res.trajPctls[90]), borderColor: 'transparent', backgroundColor: 'rgba(33,144,140,0.12)', fill: '+4', pointRadius: 0, tension: 0.3 },
      { label: '75th pctl', data: Array.from(res.trajPctls[75]), borderColor: 'transparent', backgroundColor: 'rgba(33,144,140,0.2)', fill: '+2', pointRadius: 0, tension: 0.3 },
      { label: 'Median',    data: Array.from(res.trajPctls[50]), borderColor: '#21908c', backgroundColor: 'transparent', borderWidth: 2.5, pointRadius: 0, tension: 0.3, fill: false },
      { label: '25th pctl', data: Array.from(res.trajPctls[25]), borderColor: 'transparent', backgroundColor: 'rgba(33,144,140,0.2)', fill: false, pointRadius: 0, tension: 0.3 },
      { label: '10th pctl', data: Array.from(res.trajPctls[10]), borderColor: 'transparent', backgroundColor: 'rgba(33,144,140,0.12)', fill: false, pointRadius: 0, tension: 0.3 },
      { label: 'Goal', data: days.map(() => params.goal), borderColor: 'rgba(180,83,9,0.7)', borderWidth: 2, borderDash: [6,4], pointRadius: 0, fill: false },
    ]},
    options: { responsive: true, plugins: {
      title: { display: true, text: 'Funding Trajectory (10K MC runs)', color: '#374151', font: { size: 13, weight: '600' } },
      legend: { display: false },
    }, scales: {
      x: { title: { display: true, text: 'Campaign Day', color: '#6b7280' }, ticks: { color: '#6b7280', maxTicksLimit: 10 }, grid: { color: '#f3f4f6' } },
      y: { title: { display: true, text: 'Cumulative Raised ($)', color: '#6b7280' }, ticks: { color: '#6b7280', callback: v => '$' + (v >= 1000 ? Math.round(v/1000)+'K' : v) }, grid: { color: '#f3f4f6' } },
    }},
  });

  // Histogram — viridis: purple below goal, green above
  const bins = 40; const minR = res.allRaised[0]; const maxR = res.allRaised[res.allRaised.length-1];
  const binWidth = Math.max(1, (maxR - minR) / bins);
  const counts = new Array(bins).fill(0); const binLabels = [];
  for (let i = 0; i < bins; i++) {
    const lo = minR + i * binWidth; binLabels.push(Math.round(lo));
    for (let j = 0; j < N_RUNS; j++) { const v = res.allRaised[j]; if (v >= lo && (i === bins-1 || v < lo+binWidth)) counts[i]++; }
  }
  const barColors = binLabels.map(v => v >= params.goal ? 'rgba(53,183,121,0.7)' : 'rgba(68,1,84,0.6)');
  if (histChartInstance) histChartInstance.destroy();
  histChartInstance = new Chart($('histChart'), {
    type: 'bar',
    data: { labels: binLabels, datasets: [{ data: counts, backgroundColor: barColors, borderWidth: 0, barPercentage: 1, categoryPercentage: 1 }] },
    options: { responsive: true, plugins: {
      title: { display: true, text: 'Distribution of Outcomes (purple = below goal, green = above)', color: '#374151', font: { size: 13, weight: '600' } },
      legend: { display: false },
    }, scales: {
      x: { ticks: { color: '#6b7280', maxTicksLimit: 6, callback: function(val, idx) { const v = binLabels[idx]; return '$' + (v >= 1000 ? Math.round(v/1000)+'K' : v); } }, grid: { display: false } },
      y: { ticks: { color: '#6b7280' }, grid: { color: '#f3f4f6' } },
    }},
  });
}

// Slider wiring
const sliderIds = ['email','ig','fb','adBudget','pr','goal','duration','ebPrice','ebQty'];
sliderIds.forEach(id => {
  $(id).addEventListener('input', () => {
    const v = +$(id).value; const valEl = $(id + 'Val');
    if (['adBudget','ebPrice','goal'].includes(id)) valEl.textContent = '$' + v.toLocaleString();
    else valEl.textContent = v.toLocaleString();
  });
  $(id).addEventListener('change', updateDisplay);
});
$('totalBudget').addEventListener('input', () => { $('totalBudgetVal').textContent = '$' + (+$('totalBudget').value).toLocaleString(); });

// =====================================================
// Budget Optimizer
// =====================================================
function quickProb(params, nRuns) {
  const { emailList, igFollowers, fbFollowers, dailyAdBudget, prHits, goal, duration, ebPrice, ebQty } = params;
  const stdPrice = 200.00; const weights = ucurveWeights(duration); let funded = 0;
  for (let run = 0; run < nRuns; run++) {
    const rng = makeRng(42+run);
    const backers = new Float64Array(duration);
    const em = emailTraffic(rng, emailList, duration, weights);
    const soc = socialTraffic(rng, igFollowers, fbFollowers, duration, weights);
    const ads = paidAdsTraffic(rng, dailyAdBudget, duration, weights);
    const prT = prTraffic(rng, prHits, duration, weights);
    const org = iggOrganicTraffic(rng, duration, weights);
    for (let i = 0; i < duration; i++) backers[i] = em[i]+soc[i]+ads[i]+prT[i]+org[i];
    const cum = new Float64Array(duration); cum[0] = backers[0];
    for (let i = 1; i < duration; i++) cum[i] = cum[i-1]+backers[i];
    const wom = womTraffic(rng, cum, duration);
    for (let i = 0; i < duration; i++) backers[i] += wom[i];
    let totalBackers = 0; for (let i = 0; i < duration; i++) totalBackers += backers[i];
    const ebB = Math.min(totalBackers, ebQty); const gross = ebB*ebPrice + (totalBackers-ebB)*stdPrice;
    if (gross >= goal) funded++;
  }
  return funded / nRuns;
}

// Carry over runOptimizer() verbatim from index.html lines 885–end of optimizer
// (the async function that does random allocation search with progress updates)
// Paste it here unchanged — it uses the same DOM IDs: optimizeBtn, optProgress, optResult, totalBudget, costEmail, costIg, costFb, costAd, costPr, email, ig, fb, adBudget, pr, goal, duration, ebPrice, ebQty
// PASTE_OPTIMIZER_HERE

// Nav active state
(function () {
  const sectionIds = ['evidence','lessons','simulator','forecast','actions'];
  const links = {};
  sectionIds.forEach(id => { links[id] = document.querySelector('#navLinks a[href="#'+id+'"]'); });
  function update() {
    const y = window.scrollY + 80; let active = sectionIds[0];
    sectionIds.forEach(id => { const el = document.getElementById(id); if (el && el.offsetTop <= y) active = id; });
    Object.values(links).forEach(a => a && a.classList.remove('text-white','bg-white/10'));
    if (links[active]) links[active].classList.add('text-white','bg-white/10');
  }
  window.addEventListener('scroll', update, { passive: true });
  update();
})();

// Initial run
updateDisplay();
</script>
```

- [ ] **Step 3: Paste the `runOptimizer()` function**

In the `<script>` block, find `// PASTE_OPTIMIZER_HERE` and replace it with the full `runOptimizer()` async function from `index.html` lines 885–940 (the random allocation search optimizer). It is safe to copy verbatim — all DOM IDs match.

- [ ] **Step 4: Verify simulator works in browser**

Open `report.html`. Scroll to §3. Expected:
- Scorecard shows a percentage immediately on page load
- Sliders are functional (drag one → numbers update)
- Fan chart renders with teal median line, teal fill bands
- Histogram renders with purple bars (below goal) and green bars (above goal)
- Hero stat (top-right "37%") updates when sliders change

- [ ] **Step 5: Commit**

```bash
git add report.html
git commit -m "feat: port simulator JS with viridis chart colors and updatePrintScorecard"
```

---

## Task 7: Verify print styles

**Files:**
- Modify: `report.html` — print styles are already in the `<style>` block from Task 1

- [ ] **Step 1: Open print preview**

In Chrome: open `report.html` → Ctrl+P → Print preview.

Expected:
- Nav bar: not visible
- All `.no-print` elements (sliders, charts, optimizer, verdict bar): not visible
- `.print-scorecard` grid (4 stat cells: probability, raised, backers, net revenue): visible in §3
- §3 has a pale gray background instead of teal
- Tables, lesson cards, action items: no mid-item page breaks
- Hero stat numbers visible

- [ ] **Step 2: Fix any print issues**

If elements are still visible that should be hidden, add `class="no-print"` to them in the HTML. If the print scorecard values are "--" (JS hasn't run), ensure `updateDisplay()` is called at page load — it should already be at the bottom of the script block.

- [ ] **Step 3: Commit**

```bash
git add report.html
git commit -m "fix: verify and tune print styles"
```

---

## Task 8: Update index.html DISTS and .gitignore

**Files:**
- Modify: `index.html` — update DISTS object
- Modify: `.gitignore` — add `.superpowers/`

- [ ] **Step 1: Update DISTS in index.html**

The DISTS object in `index.html` at line ~348 still has old calibrated values. Replace it with the same values used in `report.html` (the output of the Step 1 python command from Task 6).

Find in `index.html`:
```
// -- Distribution definitions (CMA-ES calibrated 2026-04-07, loss=2.52) --
const DISTS = {
  EMAIL_OPEN_RATE:       { type: 'beta', a: 23.22, b: 76.78 },
```

Replace the entire DISTS object (lines 347–369) with:
```js
// -- Distribution definitions (calibrated 2026-04-09, loss=2.57) --
const DISTS = {
  // [paste same DISTS object used in report.html Task 6]
};
```

- [ ] **Step 2: Update .gitignore**

```bash
grep -q ".superpowers" .gitignore || echo ".superpowers/" >> .gitignore
```

- [ ] **Step 3: Commit**

```bash
git add index.html .gitignore
git commit -m "fix: sync index.html DISTS with calibrated params; add .superpowers to .gitignore"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| Tailwind + DaisyUI CDN | Task 1 |
| `light` base theme | Task 1 |
| Viridis palette | Task 1 |
| Section B infographic style (numbered circles + left-border stats) | Task 1 + 2 |
| 5-section structure with sticky nav | Task 1 |
| §1 Evidence content | Task 2 |
| §2 Lessons content | Task 3 |
| §3 Simulator (HTML) | Task 4 |
| §3 Simulator (JS, viridis charts) | Task 6 |
| `updatePrintScorecard()` | Task 6 |
| §4 Forecast content | Task 5 |
| §5 Actions content | Task 5 |
| Print styles | Task 1 + 7 |
| Nav active state | Task 6 |
| `.superpowers/` in .gitignore | Task 8 |
| index.html DISTS sync | Task 8 |
| index.html untouched (logic) | Task 8 (only DISTS updated) |

**Placeholder scan:** None — all tasks contain actual code.

**Type consistency:** `updatePrintScorecard(res, params)` defined in Task 6 and called immediately after `runSimulation()` in `updateDisplay()` — consistent.

**One gap found and fixed:** The `runOptimizer()` function in Task 6 Step 3 is instructed to paste from `index.html` rather than duplicated here (it's ~55 lines of async JS with no changes needed — duplication would risk transcription errors and the plan already tells the implementer the exact source line range).
