(() => {
  'use strict';

  const app = document.getElementById('research-command-centre');
  if (!app) return;

  const statusNode = document.getElementById('command-status');
  const errorNode = document.getElementById('command-error');
  const kpisNode = document.getElementById('command-kpis');
  const coverageNode = document.getElementById('command-coverage');
  const prioritiesNode = document.getElementById('command-priorities');
  const disputesNode = document.getElementById('command-disputes');

  const loadJson = async (url) => {
    const response = await fetch(url, { credentials: 'same-origin' });
    if (!response.ok) throw new Error(`Could not load ${url}.`);
    return response.json();
  };

  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  const kpi = (label, value, note = '') => {
    const card = element('article', 'operations-kpi');
    card.append(
      element('span', 'operations-kpi-value', String(value)),
      element('span', 'operations-kpi-label', label)
    );
    if (note) card.append(element('span', 'operations-kpi-note', note));
    return card;
  };

  const progress = (value) => {
    const wrapper = element('div', 'operations-progress');
    const bar = element('span', 'operations-progress-bar');
    bar.style.width = `${Math.max(0, Math.min(100, Number(value)))}%`;
    wrapper.append(bar);
    wrapper.setAttribute('aria-label', `${value} percent`);
    return wrapper;
  };

  const renderCoverage = (coverage) => {
    coverageNode.replaceChildren(...coverage.achievements.map((item) => {
      const card = element('article', 'operations-card');
      card.append(
        element('h3', '', item.achievement_name),
        element('p', 'operations-card-lead', `${item.coverage_score}/100 · ${item.rating}`),
        progress(item.coverage_score),
        element(
          'p',
          '',
          `${item.open_disputes.length} open dispute${item.open_disputes.length === 1 ? '' : 's'} · ${item.unassigned_gaps.length} unassigned gap${item.unassigned_gaps.length === 1 ? '' : 's'}`
        )
      );
      return card;
    }));
  };

  const renderPriorities = (priorities) => {
    prioritiesNode.replaceChildren(...priorities.priorities.slice(0, 8).map((item) => {
      const row = element('article', 'operations-list-row');
      const copy = element('div', 'operations-list-copy');
      copy.append(
        element('h4', '', `${item.rank}. ${item.title}`),
        element('p', '', `${item.task_id} · ${item.declared_priority} · ${item.status}`)
      );
      row.append(copy, element('strong', 'operations-score', String(item.score)));
      return row;
    }));
  };

  const renderDisputes = (payload) => {
    const open = payload.records.filter((item) => item.status !== 'resolved');
    disputesNode.replaceChildren(...open.map((item) => {
      const row = element('article', 'operations-list-row');
      const copy = element('div', 'operations-list-copy');
      copy.append(
        element('h4', '', item.title),
        element('p', '', `${item.id} · ${item.severity} · ${item.claim_ids.join(', ')}`),
        element('p', '', item.resolution_criteria)
      );
      row.append(copy);
      return row;
    }));
  };

  const load = async () => {
    try {
      const [health, coverage, priorities, contradictions, research, protocols, command] = await Promise.all([
        loadJson(app.dataset.status),
        loadJson(app.dataset.coverage),
        loadJson(app.dataset.priorities),
        loadJson(app.dataset.contradictions),
        loadJson(app.dataset.research),
        loadJson(app.dataset.protocols),
        loadJson(app.dataset.command)
      ]);

      kpisNode.replaceChildren(
        kpi('Operational health', `${health.health.score}/100`, health.health.label),
        kpi('Evidence coverage', `${coverage.overall_coverage_score}/100`, coverage.overall_rating),
        kpi('Unassigned gaps', coverage.unassigned_gap_count, command.targets.unassigned_gap_count === 0 ? 'Target: zero' : ''),
        kpi('Open research tasks', research.tasks.filter((item) => item.status !== 'resolved').length),
        kpi('Open contradictions', contradictions.records.filter((item) => item.status !== 'resolved').length, `Target: ≤${command.targets.maximum_open_contradictions}`),
        kpi('Ready protocols', protocols.protocols.filter((item) => item.status === 'ready').length)
      );
      renderCoverage(coverage);
      renderPriorities(priorities);
      renderDisputes(contradictions);
      statusNode.textContent = `Research state loaded. Operational health is ${health.health.score}/100 and evidence coverage is ${coverage.overall_coverage_score}/100.`;
    } catch (error) {
      statusNode.textContent = 'Research command centre unavailable.';
      errorNode.hidden = false;
      errorNode.textContent = error instanceof Error ? error.message : 'The research state could not be loaded.';
    }
  };

  load();
})();
