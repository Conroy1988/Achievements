---
layout: default
title: Deployment and metadata audit
permalink: /project/deployment-audit/
description: Operational checklist for validating the GitHub Achievement Encyclopedia deployment.
---

## Deployment and metadata audit

## Canonical deployment

- Source branch: `main`
- Public host: `https://conroy1988.github.io`
- Base path: `/Achievements`
- Sitemap: `/Achievements/sitemap.xml`
- Robots policy: `/Achievements/robots.txt`

## Release audit checklist

1. Confirm the Pages build completed successfully.
2. Open the homepage and one achievement guide on desktop and mobile widths.
3. Confirm navigation, footer, stylesheet, and social-preview asset load under the repository base path.
4. Confirm `robots.txt` references the generated sitemap.
5. Confirm canonical and social metadata use the public Pages URL.
6. Validate structured data with a recognised schema validator.
7. Run the repository link and accessibility workflows.
8. Record material deployment changes in `CHANGELOG.md`.

## Current architecture

The site uses Jekyll, the Cayman theme as a base, a repository-owned layout and stylesheet, `jekyll-seo-tag`, and `jekyll-sitemap`. A `WebSite` JSON-LD record is emitted by the default layout.

## Known operational constraints

GitHub Pages deployment and indexing are asynchronous. A successful merge does not guarantee immediate public rendering or search-engine discovery. Checks against deployed pages should allow for publication delay without weakening source validation.

## Failure handling

- Broken source links: repair before merge.
- Failed accessibility checks: identify the affected selector and remediate the underlying markup or contrast.
- Missing Pages output: inspect Pages deployment settings and the latest workflow/build status.
- Metadata mismatch: correct `_config.yml` or the default layout and rerun validation.
