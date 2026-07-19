---
layout: default
title: GitHub achievement profile auditor
description: Read-only analysis of public GitHub signals with explicit uncertainty and no private-data access.
permalink: /profile-auditor/
---

<link rel="stylesheet" href="{{ '/assets/css/research-operations.css' | relative_url }}">

## GitHub achievement profile auditor

Enter a GitHub username to inspect **public signals** relevant to achievement research.

> [!IMPORTANT]
> This tool does not detect profile badges. GitHub does not expose a complete public achievement API. Results are estimates, limitations, and manual-review prompts—not proof that an achievement is present or absent.

<div
  id="profile-auditor"
  class="operations-app"
  data-rules="{{ '/api/auditor-rules.json' | relative_url }}"
>
  <form id="auditor-form" class="operations-form" role="search" aria-label="Audit public GitHub achievement signals">
    <div class="operations-field operations-field-wide">
      <label for="auditor-username">GitHub username</label>
      <input id="auditor-username" name="username" type="text" autocomplete="off" pattern="[A-Za-z0-9-]{1,39}" placeholder="octocat" required>
    </div>
    <button type="submit">Audit public signals</button>
  </form>

  <p id="auditor-status" class="operations-status" role="status" aria-live="polite">No profile has been audited.</p>
  <p id="auditor-error" class="operations-error" role="alert" hidden></p>
  <section id="auditor-summary" class="operations-summary" hidden aria-label="Profile summary"></section>
  <div id="auditor-results" class="operations-grid" aria-label="Achievement signal results"></div>

  <noscript>
    <p>JavaScript is required for the interactive auditor. The underlying rules remain available from <a href="{{ '/api/auditor-rules.json' | relative_url }}">the public API</a>.</p>
  </noscript>
</div>

## Data use

The auditor makes unauthenticated, read-only requests to GitHub's public REST API. It does not request a token, access private repositories, submit changes, or retain profile data.
<script src="{{ '/assets/js/profile-auditor.js' | relative_url }}" defer></script>
