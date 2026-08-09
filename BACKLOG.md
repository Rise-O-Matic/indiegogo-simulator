# Indiegogo Simulator — backlog

Claude's open work for this project. Migrated out of Todoist on 2026-08-08 (Todoist now carries only work that needs Steven, or that has a due date).

Conventions: one block per item, highest priority first. Deep detail belongs in the design doc an item points to, not inline. **Prune when you touch this file** — an item whose premise no longer matches the code gets deleted, not left to rot.


## P1

- [ ] **Fix apply_params() Beta regex in calibrate.py**
      src/calibrate.py:431-435 — Beta pattern lacks \s* after DistParam\( so it matches 0/16 Beta params on the multi-line format; re.sub silently no-ops. Add \s* (mirror the LogNormal pattern), assert every substitution changed the source, add a regression test against the real file format. Blocks all recalibration work.

- [ ] **Secure uncommitted calibration work before it's lost**
      Copy src/distributions.py.bak (clean grounded priors — gitignored, destroyed by next --apply) to a safe location. Commit CLAUDE.md + data/calibrated-params.json + calibration-history.json. Commit verifications.txt as docs/report-fact-check-2026-04.md. Do NOT commit the hybrid distributions.py yet. From repo audit 2026-07-06.


## P2

- [ ] **Fix calibration inputs before any CMA-ES re-run**
      data_loader.py: use usd_pledged_real (not the broken 'usd pledged' col — 3,797 NaNs, 17.5% rows >10% off); keep zero-backer failures in the success-rate target (currently dropped, inflating the weight-3.0 target). calibrate.py: deterministic seeds (hash(preset_name) is per-process random; rng_base_seed=eval_count). Add prior-anchoring penalties/bounds for AD_CPM/AD_CTR so the optimizer can't drift them again.

- [ ] **Harden tests: revenue cap bug, CSV skipif, determinism, CI**
      Fix revenue.py daily_cumulative_revenue ignoring the 1,800-unit cap (trajectory contradicts gross_revenue in capped runs) + add daily_cumulative_revenue[-1] == gross_revenue assertion. skipif-guard the two test_calibrate tests needing the gitignored Kickstarter CSV (suite fails on fresh clone). Add determinism test (same seed → same arrays) and word-of-mouth tests. Add a pytest GitHub Actions workflow.

- [ ] **Repair both notebooks or demote them in CLAUDE.md**
      cloak-campaign-simulator.ipynb: cell 18 SyntaxError (print(\"\"\" * 60)), cell 5 mangled separator, cells 9/16 pass removed monthly_site_visitors field (TypeError). interactive-simulator.ipynb: same TypeError on slider use. CLAUDE.md still names the broken notebook as primary deliverable and never mentions index.html/report.html.

- [ ] **Resolve distributions.py hybrid state — restore grounded priors from .bak**
      Working tree mixes 16 grounded Beta means with 4 CMA-ES LogNormal scales (never jointly evaluated). Recommendation from audit: restore grounded priors; the CMA-ES run re-drifted AD_CPM to $29.59 and produced degenerate a<1 Beta shapes.


## P3

- [ ] **Generate HTML DISTS blocks from distributions.py**
      index.html:348 and report.html:903 embed a third divergent parameter set incl. PR_CTR transcription bug (b=99.1353, should be 19.1353 → PR conversion 5x low). Write a small script that emits the DISTS JS from distributions.py so there's one source of truth. Do after the engine's params are settled.

- [ ] **Repo hygiene batch**
      Pages workflow publishes entire repo (path: '.') — restrict to the two HTML files. Redact Meta ad account ID in data/meta-insights-2026-04-07.md or make repo private. Add README. git branch -u origin/feat/simulator (fixes false 'ahead 17'). Delete dead master branch. Rename 12 Meta CSVs + image files violating lowercase-hyphen rule; decide tracked-vs-ignored for the 4.9MB Instagram creatives. Add ipywidgets to requirements.txt; drop unused plotly/requests.

