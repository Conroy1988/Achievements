(() => {
  'use strict';

  const FRESH_DAYS = 270;
  const ANNUAL_REVIEW_DAYS = 365;

  const app = document.getElementById('achievement-search');
  if (!app) return;

  const controls = {
    form: app.querySelector('.search-controls'),
    query: document.getElementById('search-query'),
    status: document.getElementById('search-status'),
    tiered: document.getElementById('search-tiered'),
    evidence: document.getElementById('search-evidence'),
    category: document.getElementById('search-category'),
    freshness: document.getElementById('search-freshness'),
    count: document.getElementById('search-count'),
    error: document.getElementById('search-error'),
    results: document.getElementById('search-results')
  };

  const achievementDataUrl = new URL(app.dataset.achievements, window.location.href);
  const siteRootPath = achievementDataUrl.pathname.replace(/\/data\/achievements\.json$/, '/');
  let records = [];

  const normalise = (value) => String(value || '').toLocaleLowerCase('en-GB').trim();
  const tokenise = (value) => normalise(value).split(/[^a-z0-9]+/).filter(Boolean);
  const routeFor = (permalink) => {
    const prefix = siteRootPath === '/' ? '' : siteRootPath.replace(/\/$/, '');
    return `${prefix}/${String(permalink).replace(/^\/+/, '')}`;
  };

  const freshnessFor = (isoDate) => {
    const verified = new Date(`${isoDate}T00:00:00Z`);
    if (Number.isNaN(verified.getTime())) return 'invalid';
    const age = Math.floor((Date.now() - verified.getTime()) / 86400000);
    if (age <= FRESH_DAYS) return 'fresh';
    if (age < ANNUAL_REVIEW_DAYS) return 'due-soon';
    return 'overdue';
  };

  const searchableRecord = (record, values) => {
    const haystack = values.map(normalise).join(' ');
    return {
      ...record,
      href: routeFor(record.permalink),
      haystack,
      searchTokens: new Set(tokenise(haystack))
    };
  };

  const achievementRecord = (item) => {
    const evidence = [...new Set(Object.values(item.evidence || {}))];
    const aliases = item.aliases || [];
    const tiers = item.tiers || [];
    return searchableRecord(
      {
        type: 'achievement',
        slug: item.slug,
        name: item.name,
        status: item.status,
        category: item.category,
        tiered: item.tiered,
        evidence,
        freshness: freshnessFor(item.last_verified),
        lastVerified: item.last_verified,
        summary: item.trigger,
        primaryAction: item.primary_action,
        permalink: item.permalink,
        aliases,
        tiers
      },
      [
        item.name,
        item.slug,
        item.primary_action,
        item.trigger,
        item.category,
        item.status,
        ...aliases,
        ...evidence,
        ...tiers.flatMap((tier) => [tier.name, tier.unit, tier.threshold]),
        ...(item.known_limitations || [])
      ]
    );
  };

  const referenceRecord = (item) => searchableRecord(
    {
      type: 'reference',
      slug: item.slug,
      name: item.name,
      status: 'reference',
      category: item.category,
      tiered: null,
      evidence: [],
      freshness: null,
      lastVerified: null,
      summary: item.summary,
      primaryAction: 'Project reference',
      permalink: item.permalink,
      aliases: item.aliases || [],
      tiers: []
    },
    [item.name, item.slug, item.category, item.summary, ...(item.aliases || [])]
  );

  const textTokens = () => tokenise(controls.query.value);
  const hasToken = (record, token) => {
    if (record.searchTokens.has(token)) return true;
    if (token.length < 3) return false;
    return [...record.searchTokens].some((word) => word.startsWith(token));
  };

  const matches = (record) => {
    if (textTokens().some((token) => !hasToken(record, token))) return false;
    if (controls.status.value !== 'all' && record.status !== controls.status.value) return false;
    if (controls.tiered.value !== 'all') {
      if (record.type !== 'achievement') return false;
      if ((controls.tiered.value === 'yes') !== record.tiered) return false;
    }
    if (controls.evidence.value !== 'all' && !record.evidence.includes(controls.evidence.value)) return false;
    if (controls.category.value !== 'all' && record.category !== controls.category.value) return false;
    if (controls.freshness.value !== 'all' && record.freshness !== controls.freshness.value) return false;
    return true;
  };

  const relevance = (record) => {
    const query = normalise(controls.query.value);
    if (!query) return record.type === 'achievement' ? 10 : 0;
    const name = normalise(record.name);
    const aliases = record.aliases.map(normalise);
    if (name === query) return 100;
    if (aliases.includes(query)) return 95;
    if (name.startsWith(query)) return 80;
    if (aliases.some((alias) => alias.startsWith(query))) return 70;
    if (name.includes(query)) return 60;
    return 20;
  };

  const pill = (text, modifier = '') => {
    const element = document.createElement('span');
    element.className = `search-pill ${modifier}`.trim();
    element.textContent = text;
    return element;
  };

  const formatDate = (isoDate) => {
    if (!isoDate) return '';
    return new Intl.DateTimeFormat('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      timeZone: 'UTC'
    }).format(new Date(`${isoDate}T00:00:00Z`));
  };

  const createCard = (record) => {
    const card = document.createElement('article');
    card.className = 'search-result-card';
    card.dataset.resultSlug = record.slug;
    card.dataset.resultType = record.type;

    const heading = document.createElement('h3');
    const link = document.createElement('a');
    link.href = record.href;
    link.textContent = record.name;
    heading.append(link);
    card.append(heading);

    const meta = document.createElement('div');
    meta.className = 'search-result-meta';
    meta.append(pill(record.status === 'reference' ? 'Reference' : record.status, `pill-${record.status}`));
    meta.append(pill(record.category));
    if (record.type === 'achievement') {
      meta.append(pill(record.tiered ? 'Tiered' : 'Single level'));
      meta.append(pill(record.freshness.replace('-', ' '), `pill-${record.freshness}`));
    }
    card.append(meta);

    const summary = document.createElement('p');
    summary.textContent = record.summary;
    card.append(summary);

    if (record.type === 'achievement') {
      const details = document.createElement('dl');
      details.className = 'search-result-details';

      const actionTerm = document.createElement('dt');
      actionTerm.textContent = 'Primary action';
      const actionDescription = document.createElement('dd');
      actionDescription.textContent = record.primaryAction;
      details.append(actionTerm, actionDescription);

      const evidenceTerm = document.createElement('dt');
      evidenceTerm.textContent = 'Evidence';
      const evidenceDescription = document.createElement('dd');
      evidenceDescription.textContent = record.evidence.join(', ');
      details.append(evidenceTerm, evidenceDescription);

      const verifiedTerm = document.createElement('dt');
      verifiedTerm.textContent = 'Last verified';
      const verifiedDescription = document.createElement('dd');
      verifiedDescription.textContent = formatDate(record.lastVerified);
      details.append(verifiedTerm, verifiedDescription);

      card.append(details);
    }
    return card;
  };

  const currentState = () => ({
    query: controls.query.value.trim(),
    status: controls.status.value,
    tiered: controls.tiered.value,
    evidence: controls.evidence.value,
    category: controls.category.value,
    freshness: controls.freshness.value
  });

  const syncUrl = () => {
    const url = new URL(window.location.href);
    for (const [key, value] of Object.entries(currentState())) {
      if (!value || value === 'all') url.searchParams.delete(key);
      else url.searchParams.set(key, value);
    }
    window.history.replaceState({}, '', url);
  };

  const render = () => {
    const filtered = records
      .filter(matches)
      .sort((left, right) => relevance(right) - relevance(left) || left.name.localeCompare(right.name, 'en-GB'));
    controls.results.replaceChildren(...filtered.map(createCard));
    controls.count.textContent = `${filtered.length} result${filtered.length === 1 ? '' : 's'} found.`;
    controls.results.dataset.resultCount = String(filtered.length);
    syncUrl();
  };

  const populateCategories = () => {
    const categories = [...new Set(records.map((record) => record.category))]
      .sort((left, right) => left.localeCompare(right, 'en-GB'));
    for (const category of categories) {
      const option = document.createElement('option');
      option.value = category;
      option.textContent = category.replaceAll('-', ' ');
      controls.category.append(option);
    }
  };

  const restoreState = () => {
    const params = new URLSearchParams(window.location.search);
    for (const field of ['query', 'status', 'tiered', 'evidence', 'category', 'freshness']) {
      const value = params.get(field);
      if (!value || !controls[field]) continue;
      if (controls[field] instanceof HTMLSelectElement) {
        if ([...controls[field].options].some((option) => option.value === value)) controls[field].value = value;
      } else {
        controls[field].value = value;
      }
    }
  };

  const load = async () => {
    try {
      const [achievementResponse, resourceResponse] = await Promise.all([
        fetch(app.dataset.achievements, { credentials: 'same-origin' }),
        fetch(app.dataset.resources, { credentials: 'same-origin' })
      ]);
      if (!achievementResponse.ok || !resourceResponse.ok) throw new Error('The search index could not be loaded.');
      const achievements = await achievementResponse.json();
      const resources = await resourceResponse.json();
      records = [
        ...achievements.achievements.map(achievementRecord),
        ...resources.resources.map(referenceRecord)
      ];
      populateCategories();
      restoreState();
      render();
    } catch (error) {
      controls.count.textContent = 'Search unavailable.';
      controls.error.hidden = false;
      controls.error.textContent = error instanceof Error ? error.message : 'The search index could not be loaded.';
    }
  };

  controls.form.addEventListener('input', render);
  controls.form.addEventListener('change', render);
  controls.form.addEventListener('submit', (event) => event.preventDefault());
  controls.form.addEventListener('reset', () => window.setTimeout(render, 0));

  load();
})();
