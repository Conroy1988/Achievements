---
layout: default
title: Search the encyclopedia
description: Search and filter GitHub achievements, evidence classifications, verification status, and core methodology pages.
permalink: /search/
---

<link rel="stylesheet" href="{{ '/assets/css/search.css' | relative_url }}">

## Search the encyclopedia

Search achievement names, triggers, aliases, evidence labels, and core project references. Filters can be combined and all controls are keyboard accessible.

<div
  id="achievement-search"
  class="search-app"
  data-achievements="{{ '/data/achievements.json' | relative_url }}"
  data-resources="{{ '/data/search-resources.json' | relative_url }}"
>
  <form class="search-controls" role="search" aria-label="Achievement encyclopedia search">
    <div class="search-field search-field-wide">
      <label for="search-query">Search</label>
      <input
        id="search-query"
        name="query"
        type="search"
        autocomplete="off"
        placeholder="Try: merged PR badge"
      >
    </div>

    <div class="search-field">
      <label for="search-status">Status</label>
      <select id="search-status" name="status">
        <option value="all">All statuses</option>
        <option value="active">Active</option>
        <option value="retired">Retired</option>
        <option value="reference">Project references</option>
      </select>
    </div>

    <div class="search-field">
      <label for="search-tiered">Progression</label>
      <select id="search-tiered" name="tiered">
        <option value="all">All progression types</option>
        <option value="yes">Tiered</option>
        <option value="no">Single level</option>
      </select>
    </div>

    <div class="search-field">
      <label for="search-evidence">Evidence</label>
      <select id="search-evidence" name="evidence">
        <option value="all">All evidence levels</option>
        <option value="official">Official</option>
        <option value="confirmed">Confirmed</option>
        <option value="observed">Observed</option>
        <option value="community-reported">Community-reported</option>
        <option value="unknown">Unknown</option>
      </select>
    </div>

    <div class="search-field">
      <label for="search-category">Category</label>
      <select id="search-category" name="category">
        <option value="all">All categories</option>
      </select>
    </div>

    <div class="search-field">
      <label for="search-freshness">Verification</label>
      <select id="search-freshness" name="freshness">
        <option value="all">All verification ages</option>
        <option value="fresh">Fresh</option>
        <option value="due-soon">Review due soon</option>
        <option value="overdue">Overdue</option>
      </select>
    </div>

    <button id="search-reset" class="search-reset" type="reset">Reset filters</button>
  </form>

  <p id="search-count" class="search-count" role="status" aria-live="polite">Loading search index…</p>
  <p id="search-error" class="search-error" role="alert" hidden></p>
  <div id="search-results" class="search-results" aria-label="Search results"></div>

  <noscript>
    <p>JavaScript is required for interactive filtering. Use the <a href="{{ '/docs/achievement-index.html' | relative_url }}">achievement index</a> instead.</p>
  </noscript>
</div>

<script src="{{ '/assets/js/achievement-search.js' | relative_url }}" defer></script>
