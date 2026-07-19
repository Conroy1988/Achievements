import assert from 'node:assert/strict';
import process from 'node:process';
import { chromium } from 'playwright';

const baseUrl = process.env.SEARCH_BASE_URL ?? 'http://127.0.0.1:4173/Achievements';
const browser = await chromium.launch({ headless: true });

const waitForCount = async (page, expected) => {
  await page.waitForFunction(
    (value) => document.getElementById('search-results')?.dataset.resultCount === String(value),
    expected,
  );
};

try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const response = await page.goto(`${baseUrl}/search/`, { waitUntil: 'networkidle' });
  assert(response?.ok(), `Search page returned ${response?.status() ?? 'no response'}`);

  await waitForCount(page, 17);
  assert.equal(await page.locator('[data-result-type="achievement"]').count(), 9);
  assert.equal(await page.locator('[data-result-type="reference"]').count(), 8);

  await page.locator('#search-query').fill('merged PR badge');
  await waitForCount(page, 1);
  await page.locator('[data-result-slug="pull-shark"]').waitFor({ state: 'visible' });

  await page.locator('#search-reset').click();
  await waitForCount(page, 17);

  await page.locator('#search-status').selectOption('retired');
  await waitForCount(page, 2);
  assert.equal(await page.locator('[data-result-type="achievement"]').count(), 2);

  await page.locator('#search-reset').click();
  await waitForCount(page, 17);
  await page.locator('#search-tiered').selectOption('yes');
  await waitForCount(page, 4);

  await page.locator('#search-reset').click();
  await waitForCount(page, 17);
  await page.locator('#search-status').selectOption('reference');
  await waitForCount(page, 8);

  await page.locator('#search-reset').click();
  await waitForCount(page, 17);
  await page.locator('#search-query').fill('verification methodology');
  await waitForCount(page, 1);
  await page.locator('[data-result-slug="verification-methodology"]').waitFor({ state: 'visible' });

  const liveRegion = await page.locator('#search-count').getAttribute('aria-live');
  assert.equal(liveRegion, 'polite');
  console.log('Search page passed alias, status, tier, reference, and accessibility checks.');
} finally {
  await browser.close();
}
