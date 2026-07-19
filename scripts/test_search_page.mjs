import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

const baseUrl = process.env.SEARCH_BASE_URL ?? 'http://127.0.0.1:4173/Achievements';
const resultDir = path.join(process.cwd(), 'search-test-results');
const [achievementData, resourceData] = await Promise.all([
  fs.readFile(path.join(process.cwd(), 'data', 'achievements.json'), 'utf-8').then(JSON.parse),
  fs.readFile(path.join(process.cwd(), 'data', 'search-resources.json'), 'utf-8').then(JSON.parse),
]);
const expectedAchievementCount = achievementData.achievements.length;
const expectedReferenceCount = resourceData.resources.length;
const expectedTotalCount = expectedAchievementCount + expectedReferenceCount;
const browser = await chromium.launch({ headless: true });

const snapshot = async (page, label) => {
  const count = await page.locator('#search-results').getAttribute('data-result-count');
  const slugs = await page.locator('[data-result-slug]').evaluateAll((items) =>
    items.map((item) => item.getAttribute('data-result-slug')),
  );
  console.log(`${label}: count=${count}; slugs=${slugs.join(',')}`);
  return { count: Number(count), slugs };
};

const expectCount = async (page, expected, label) => {
  await page.waitForTimeout(100);
  const state = await snapshot(page, label);
  assert.equal(state.count, expected, `${label} expected ${expected} results but found ${state.count}: ${state.slugs.join(', ')}`);
};

await fs.mkdir(resultDir, { recursive: true });

try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('console', (message) => console.log(`browser:${message.type()}: ${message.text()}`));
  page.on('pageerror', (error) => console.error(`browser:error: ${error.message}`));

  const response = await page.goto(`${baseUrl}/search/`, { waitUntil: 'networkidle' });
  assert(response?.ok(), `Search page returned ${response?.status() ?? 'no response'}`);

  await page.waitForFunction(() => document.getElementById('search-results')?.dataset.resultCount !== undefined);
  await expectCount(page, expectedTotalCount, 'initial');
  assert.equal(await page.locator('[data-result-type="achievement"]').count(), expectedAchievementCount);
  assert.equal(await page.locator('[data-result-type="reference"]').count(), expectedReferenceCount);

  await page.locator('#search-query').fill('merged PR badge');
  await expectCount(page, 1, 'alias query');
  await page.locator('[data-result-slug="pull-shark"]').waitFor({ state: 'visible' });
  const pullSharkHref = await page.locator('[data-result-slug="pull-shark"] h3 a').getAttribute('href');
  assert.equal(pullSharkHref, '/Achievements/achievements/pull-shark/');

  await page.locator('#search-reset').click();
  await expectCount(page, expectedTotalCount, 'reset after alias');

  await page.locator('#search-status').selectOption('retired');
  await expectCount(page, 2, 'retired filter');
  assert.equal(await page.locator('[data-result-type="achievement"]').count(), 2);

  await page.locator('#search-reset').click();
  await expectCount(page, expectedTotalCount, 'reset after retired');
  await page.locator('#search-tiered').selectOption('yes');
  await expectCount(page, 4, 'tiered filter');

  await page.locator('#search-reset').click();
  await expectCount(page, expectedTotalCount, 'reset after tiered');
  await page.locator('#search-status').selectOption('reference');
  await expectCount(page, expectedReferenceCount, 'reference filter');

  await page.locator('#search-reset').click();
  await expectCount(page, expectedTotalCount, 'reset after references');
  await page.locator('#search-query').fill('verification methodology');
  await expectCount(page, 1, 'methodology query');
  await page.locator('[data-result-slug="verification-methodology"]').waitFor({ state: 'visible' });

  await page.locator('#search-query').fill('good first research issue');
  await expectCount(page, 1, 'research hub query');
  await page.locator('[data-result-slug="contributor-research-hub"]').waitFor({ state: 'visible' });
  const researchHref = await page.locator('[data-result-slug="contributor-research-hub"] h3 a').getAttribute('href');
  assert.equal(researchHref, '/Achievements/research-hub/');

  await page.locator('#search-query').fill('achievement checker');
  await expectCount(page, 1, 'profile auditor query');
  const auditorHref = await page.locator('[data-result-slug="profile-auditor"] h3 a').getAttribute('href');
  assert.equal(auditorHref, '/Achievements/profile-auditor/');

  await page.locator('#search-query').fill('research dashboard');
  await expectCount(page, 1, 'command centre query');
  const commandHref = await page.locator('[data-result-slug="research-command-centre"] h3 a').getAttribute('href');
  assert.equal(commandHref, '/Achievements/research-command-centre/');

  await page.locator('#search-query').fill('100 evidence score');
  await expectCount(page, 1, 'road to 100 query');
  const roadHref = await page.locator('[data-result-slug="evidence-road-to-100"] h3 a').getAttribute('href');
  assert.equal(roadHref, '/Achievements/evidence-road-to-100/');

  await page.locator('#search-query').fill('mission board');
  await expectCount(page, 1, 'mission board query');
  const missionBoardHref = await page.locator('[data-result-slug="targeted-evidence-missions"] h3 a').getAttribute('href');
  assert.equal(missionBoardHref, '/Achievements/targeted-evidence-missions/');

  await page.locator('#search-query').fill('mission triage');
  await expectCount(page, 1, 'mission intake query');
  const missionIntakeHref = await page.locator('[data-result-slug="mission-execution-intake"] h3 a').getAttribute('href');
  assert.equal(missionIntakeHref, '/Achievements/mission-execution-intake/');

  await page.locator('#search-query').fill('adjudication queue');
  await expectCount(page, 1, 'mission review query');
  const missionReviewHref = await page.locator('[data-result-slug="mission-review-queue"] h3 a').getAttribute('href');
  assert.equal(missionReviewHref, '/Achievements/mission-review-queue/');

  await page.locator('#search-query').fill('canonical change plan');
  await expectCount(page, 1, 'promotion planner query');
  const promotionPlannerHref = await page.locator('[data-result-slug="promotion-planner"] h3 a').getAttribute('href');
  assert.equal(promotionPlannerHref, '/Achievements/promotion-planner/');

  await page.locator('#search-query').fill('public event reconstruction');
  await expectCount(page, 1, 'public reconstruction query');
  const reconstructionHref = await page.locator('[data-result-slug="public-reconstruction-corpus"] h3 a').getAttribute('href');
  assert.equal(reconstructionHref, '/Achievements/public-reconstruction-corpus/');

  const liveRegion = await page.locator('#search-count').getAttribute('aria-live');
  assert.equal(liveRegion, 'polite');
  console.log('Search page passed dynamic catalogue counts, achievement, research, routing, filters, mission intake, mission review, promotion planner, and accessibility checks.');
} catch (error) {
  const pages = browser.contexts().flatMap((context) => context.pages());
  if (pages[0]) {
    await pages[0].screenshot({ path: path.join(resultDir, 'failure.png'), fullPage: true });
    await fs.writeFile(path.join(resultDir, 'failure.html'), await pages[0].content(), 'utf-8');
  }
  throw error;
} finally {
  await browser.close();
}
