---
layout: default
title: Unified repository audit
description: One command that executes and reports the encyclopedia's complete quality, evidence, research, data, site, release, search, and visual controls.
permalink: /audit/
---

## Unified repository audit

The repository exposes one authoritative audit command:

```bash
python scripts/repository_audit.py
```

The command runs every major control, preserves individual logs, and writes both `repository-audit.md` and `repository-audit.json`.

## Controls included

| Area | Control |
|---|---|
| Content | Repository-wide Markdown validation |
| Catalogue | Achievement index and navigation consistency |
| Data | Achievement dataset, schema, guide, and index agreement |
| Evidence | Verification-date freshness with annual staleness enforcement |
| Research | Public evidence-register alignment and output drift |
| Research | Achievement verification-timeline chronology and coverage |
| Research | Contributor research-queue references and acceptance criteria |
| Research | Official GitHub documentation baseline integrity |
| Navigation | Full repository internal-link baseline |
| Sources | External-source resilience inventory |
| API | Core and research endpoint discovery and drift |
| Operations | Repository health dashboard generation |
| Metadata | Required Jekyll configuration and SEO contract |
| Accessibility | Language, viewport, landmarks, labelled navigation, visible focus, and reduced motion |
| Release | Semantic-version policy and release-note structure |
| Site | Production Jekyll build |
| Search | Playwright alias, filter, routing, and live-region checks |
| Visual | Desktop and mobile baseline comparison |

The complete browser-enabled audit currently reports **17 controls** because metadata and accessibility are evaluated as one site contract.

## Reports

The Markdown report is designed for review. The JSON report is designed for automation and contains:

- schema version;
- audit start and completion time;
- total duration;
- overall pass or fail status;
- totals for passed and failed controls;
- command, category, duration, summary, and log path for every control.

The workflow retains the consolidated reports, generated evidence, command logs, browser failure captures, and visual differences for 30 days.

## Local use

Install the repository's Ruby and Node dependencies plus Playwright Chromium, then run the command from the repository root. A content-only diagnostic can omit browser checks:

```bash
python scripts/repository_audit.py --skip-browser
```

The browser option is intended only for rapid local diagnosis. Formal CI and release verification use the complete audit.

## Failure behaviour

The audit does not stop at the first failed control. It continues wherever safe, records all results, and exits non-zero when any control fails. Search and visual checks are marked failed when the production Jekyll build is unavailable rather than being reported as successful.

The official-document contract validates committed reviewed baselines without performing network access. The separate scheduled monitor performs live comparisons and opens a review issue when a material fingerprint changes.

## Relationship to specialised workflows

The unified audit is the authoritative whole-repository result. Existing focused workflows remain because they provide faster feedback and narrower diagnostics for ordinary pull requests.

## Related material

- [Contributor research hub](research-hub.md)
- [Public evidence register](evidence-register.md)
- [Achievement verification timelines](verification-timelines.md)
- [Official documentation monitor](official-document-monitor.md)
- [Repository health dashboard](health-dashboard.md)
- [Verification methodology](verification-methodology.md)
- [Achievement data reference](data-reference.md)
- [Maintenance policy](../MAINTENANCE.md)
- [Release policy](../RELEASES.md)
