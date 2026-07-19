(() => {
  'use strict';

  const app = document.getElementById('profile-auditor');
  if (!app) return;

  const form = document.getElementById('auditor-form');
  const usernameInput = document.getElementById('auditor-username');
  const status = document.getElementById('auditor-status');
  const errorBox = document.getElementById('auditor-error');
  const summary = document.getElementById('auditor-summary');
  const results = document.getElementById('auditor-results');

  const api = async (url) => {
    const response = await fetch(url, {
      headers: { Accept: 'application/vnd.github+json' }
    });
    if (!response.ok) {
      if (response.status === 404) throw new Error('GitHub user not found.');
      if (response.status === 403) throw new Error('GitHub API rate limit reached. Try again later.');
      throw new Error(`GitHub API request failed with status ${response.status}.`);
    }
    return response.json();
  };

  const tierFor = (value, thresholds) => {
    if (!thresholds.length) return null;
    const names = ['Base', 'Bronze', 'Silver', 'Gold'];
    let current = null;
    thresholds.forEach((threshold, index) => {
      if (value >= threshold) current = { name: names[index], threshold };
    });
    return current;
  };

  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  const pill = (text, modifier = '') => {
    const node = element('span', `operations-pill ${modifier}`.trim(), text);
    return node;
  };

  const manualResult = (rule) => ({
    headline: 'Manual verification required',
    detail: rule.method,
    metric: null,
    tier: null
  });

  const audit = async (username, rulesPayload) => {
    const encoded = encodeURIComponent(username);
    const [user, repositories, pullSearch] = await Promise.all([
      api(`https://api.github.com/users/${encoded}`),
      api(`https://api.github.com/users/${encoded}/repos?per_page=100&type=owner&sort=updated`),
      api(`https://api.github.com/search/issues?q=${encodeURIComponent(`author:${username} is:pr is:merged`)}&per_page=1`)
    ]);

    const maximumStars = repositories.reduce(
      (maximum, repository) => Math.max(maximum, Number(repository.stargazers_count || 0)),
      0
    );
    const mergedPullRequests = Number(pullSearch.total_count || 0);

    const rows = rulesPayload.rules.map((rule) => {
      if (rule.signal === 'public-merged-pull-request-count') {
        return {
          rule,
          headline: `${mergedPullRequests.toLocaleString('en-GB')} public merged pull requests found`,
          detail: rule.method,
          metric: mergedPullRequests,
          tier: tierFor(mergedPullRequests, rule.tier_thresholds)
        };
      }
      if (rule.signal === 'maximum-owned-repository-stars') {
        return {
          rule,
          headline: `${maximumStars.toLocaleString('en-GB')} stars on the highest-starred inspected repository`,
          detail: rule.method,
          metric: maximumStars,
          tier: tierFor(maximumStars, rule.tier_thresholds)
        };
      }
      return { rule, ...manualResult(rule) };
    });

    return { user, repositories, rows, mergedPullRequests, maximumStars };
  };

  const renderSummary = (auditResult) => {
    summary.replaceChildren();
    const avatar = document.createElement('img');
    avatar.src = auditResult.user.avatar_url;
    avatar.alt = '';
    avatar.width = 72;
    avatar.height = 72;
    avatar.loading = 'lazy';

    const details = element('div', 'operations-summary-copy');
    const heading = element('h3', '', auditResult.user.name || auditResult.user.login);
    const link = document.createElement('a');
    link.href = auditResult.user.html_url;
    link.textContent = `@${auditResult.user.login}`;
    link.rel = 'noopener noreferrer';
    const meta = element(
      'p',
      '',
      `${auditResult.user.public_repos.toLocaleString('en-GB')} public repositories · ${auditResult.user.followers.toLocaleString('en-GB')} followers`
    );
    details.append(heading, link, meta);
    summary.append(avatar, details);
    summary.hidden = false;
  };

  const renderRows = (rows) => {
    results.replaceChildren(...rows.map(({ rule, headline, detail, tier }) => {
      const card = element('article', 'operations-card');
      const heading = element('h3', '', rule.name);
      const meta = element('div', 'operations-meta');
      meta.append(pill(rule.confidence, `pill-${rule.confidence}`));
      if (tier) meta.append(pill(`${tier.name} signal`, 'pill-positive'));

      const headlineNode = element('p', 'operations-card-lead', headline);
      const detailNode = element('p', '', detail);
      const limitationsHeading = element('h4', '', 'Limitations');
      const list = element('ul', 'operations-compact-list');
      rule.limitations.forEach((limitation) => list.append(element('li', '', limitation)));
      card.append(heading, meta, headlineNode, detailNode, limitationsHeading, list);
      return card;
    }));
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const username = usernameInput.value.trim();
    if (!/^[A-Za-z0-9-]{1,39}$/.test(username)) {
      errorBox.textContent = 'Enter a valid GitHub username.';
      errorBox.hidden = false;
      return;
    }

    errorBox.hidden = true;
    summary.hidden = true;
    results.replaceChildren();
    status.textContent = `Auditing public signals for ${username}…`;

    try {
      const rulesResponse = await fetch(app.dataset.rules, { credentials: 'same-origin' });
      if (!rulesResponse.ok) throw new Error('Auditor rules could not be loaded.');
      const rules = await rulesResponse.json();
      const auditResult = await audit(username, rules);
      renderSummary(auditResult);
      renderRows(auditResult.rows);
      status.textContent = `Public-signal audit complete for ${auditResult.user.login}. Results do not prove badge visibility.`;
      const url = new URL(window.location.href);
      url.searchParams.set('username', auditResult.user.login);
      window.history.replaceState({}, '', url);
    } catch (error) {
      status.textContent = 'Audit unavailable.';
      errorBox.hidden = false;
      errorBox.textContent = error instanceof Error ? error.message : 'The audit could not be completed.';
    }
  });

  const initial = new URLSearchParams(window.location.search).get('username');
  if (initial && /^[A-Za-z0-9-]{1,39}$/.test(initial)) {
    usernameInput.value = initial;
    form.requestSubmit();
  }
})();
