---
layout: default
title: Research command centre
description: Live operational and evidence-research status for the GitHub Achievement Encyclopedia.
permalink: /research-command-centre/
---

<link rel="stylesheet" href="{{ '/assets/css/research-operations.css' | relative_url }}">

## Research command centre

The command centre joins repository health, claim coverage, contradictions, protocols, and the research queue into one public operating view.

The generated [evidence intelligence dashboard](docs/evidence-intelligence-dashboard.md) adds achievement-level pressure rankings and the exact remaining distance to the evidence-quality release gates.

The [targeted evidence acquisition missions](docs/targeted-evidence-missions.md) convert those rankings into bounded work with prerequisites, controls, required evidence, and stop conditions.

The [mission execution intake](docs/mission-execution-intake.md) converts completed, blocked, delayed, or inconclusive mission observations into privacy-screened draft packets for mandatory human review.

<div
  id="research-command-centre"
  class="operations-app"
  data-status="{{ '/api/status.json' | relative_url }}"
  data-coverage="{{ '/api/coverage.json' | relative_url }}"
  data-priorities="{{ '/api/priorities.json' | relative_url }}"
  data-contradictions="{{ '/api/contradictions.json' | relative_url }}"
  data-research="{{ '/api/research-queue.json' | relative_url }}"
  data-protocols="{{ '/api/lab-protocols.json' | relative_url }}"
  data-command="{{ '/api/command-centre.json' | relative_url }}"
>
  <p id="command-status" class="operations-status" role="status" aria-live="polite">Loading research state…</p>
  <p id="command-error" class="operations-error" role="alert" hidden></p>

  <section id="command-kpis" class="operations-kpis" aria-label="Research key performance indicators"></section>

  <section class="operations-section" aria-labelledby="coverage-heading">
    <h3 id="coverage-heading">Evidence coverage by achievement</h3>
    <div id="command-coverage" class="operations-grid"></div>
  </section>

  <section class="operations-section" aria-labelledby="priority-heading">
    <h3 id="priority-heading">Highest-priority research</h3>
    <div id="command-priorities" class="operations-list"></div>
  </section>

  <section class="operations-section" aria-labelledby="dispute-heading">
    <h3 id="dispute-heading">Open contradictions</h3>
    <div id="command-disputes" class="operations-list"></div>
  </section>

  <noscript>
    <p>JavaScript is required for the live view. Use the <a href="{{ '/docs/research-priorities.html' | relative_url }}">priority report</a> and <a href="{{ '/docs/evidence-coverage.html' | relative_url }}">coverage report</a> instead.</p>
  </noscript>
</div>

<script src="{{ '/assets/js/research-command-centre.js' | relative_url }}" defer></script>
