import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import pixelmatch from 'pixelmatch';
import { chromium } from 'playwright';
import { PNG } from 'pngjs';

const root = process.cwd();
const update = process.argv.includes('--update');
const baseUrl = process.env.VISUAL_BASE_URL ?? 'http://127.0.0.1:4173';
const baselineDir = path.join(root, 'tests', 'visual', 'baselines');
const resultDir = path.join(root, 'visual-results');
const maxDiffRatio = Number(process.env.VISUAL_MAX_DIFF_RATIO ?? '0.01');

const pages = [
  ['home', '/'],
  ['achievement-index', '/docs/achievement-index.html'],
  ['active-guide', '/achievements/pull-shark/'],
  ['retired-guide', '/docs/arctic-code-vault-contributor.html'],
  ['methodology', '/docs/verification-methodology.html'],
];

const viewports = [
  ['desktop', { width: 1440, height: 1000 }],
  ['mobile', { width: 390, height: 844 }],
];

await fs.mkdir(baselineDir, { recursive: true });
await fs.rm(resultDir, { recursive: true, force: true });
await fs.mkdir(resultDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
let failures = 0;

try {
  for (const [pageName, pathname] of pages) {
    for (const [viewportName, viewport] of viewports) {
      const context = await browser.newContext({
        viewport,
        colorScheme: 'light',
        reducedMotion: 'reduce',
        deviceScaleFactor: 1,
      });
      const page = await context.newPage();
      const response = await page.goto(new URL(pathname, baseUrl).href, {
        waitUntil: 'networkidle',
      });
      if (!response || !response.ok()) {
        throw new Error(`${pathname} returned ${response?.status() ?? 'no response'}`);
      }

      await page.addStyleTag({
        content: `
          *, *::before, *::after {
            animation-duration: 0s !important;
            animation-delay: 0s !important;
            transition: none !important;
            caret-color: transparent !important;
          }
        `,
      });

      const filename = `${pageName}-${viewportName}.png`;
      const baselinePath = path.join(baselineDir, filename);
      const actualPath = path.join(resultDir, filename);
      await page.screenshot({ path: actualPath, fullPage: true, animations: 'disabled' });

      if (update) {
        await fs.copyFile(actualPath, baselinePath);
        console.log(`Updated ${path.relative(root, baselinePath)}`);
        await context.close();
        continue;
      }

      try {
        await fs.access(baselinePath);
      } catch {
        console.error(`Missing baseline: ${path.relative(root, baselinePath)}`);
        failures += 1;
        await context.close();
        continue;
      }

      const expected = PNG.sync.read(await fs.readFile(baselinePath));
      const actual = PNG.sync.read(await fs.readFile(actualPath));
      if (expected.width !== actual.width || expected.height !== actual.height) {
        console.error(
          `${filename}: dimensions changed from ${expected.width}x${expected.height} to ${actual.width}x${actual.height}`,
        );
        failures += 1;
        await context.close();
        continue;
      }

      const diff = new PNG({ width: expected.width, height: expected.height });
      const changedPixels = pixelmatch(
        expected.data,
        actual.data,
        diff.data,
        expected.width,
        expected.height,
        { threshold: 0.1, includeAA: false },
      );
      const diffRatio = changedPixels / (expected.width * expected.height);
      if (diffRatio > maxDiffRatio) {
        const diffPath = path.join(resultDir, `${pageName}-${viewportName}-diff.png`);
        await fs.writeFile(diffPath, PNG.sync.write(diff));
        console.error(`${filename}: ${(diffRatio * 100).toFixed(3)}% pixels changed`);
        failures += 1;
      } else {
        console.log(`${filename}: ${(diffRatio * 100).toFixed(3)}% pixels changed`);
      }
      await context.close();
    }
  }
} finally {
  await browser.close();
}

if (update) {
  console.log('Visual baselines updated.');
} else if (failures) {
  console.error(`Visual regression detected in ${failures} capture(s).`);
  process.exitCode = 1;
} else {
  console.log('All visual captures match the committed baseline.');
}
