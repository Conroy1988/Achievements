# Structured Metadata Validation

Validation date: 19 July 2026

## Scope

Reviewed the homepage metadata source, Jekyll configuration, default layout, sitemap plugin configuration, robots policy, and social-image defaults.

## Results

- The default layout emits one `WebSite` JSON-LD object.
- The JSON-LD object uses the configured site title, description, public URL, base path, language, publisher, free-access status, and MIT licence.
- `jekyll-seo-tag` is loaded once in the document head and is responsible for canonical, title, description, Open Graph, and social metadata.
- The configured public origin is `https://conroy1988.github.io` with `/Achievements` as the base path.
- The default social image is `/assets/social-card.svg`.
- `jekyll-sitemap` is enabled.
- `robots.txt` permits crawling and points to `https://conroy1988.github.io/Achievements/sitemap.xml` through the configured origin and base path.
- The document language resolves to `en-GB`.

## Duplication review

No manually duplicated canonical, description, Open Graph, or social-card tags were found alongside `jekyll-seo-tag`. The standalone JSON-LD block describes the site and does not duplicate the SEO plugin's page metadata responsibilities.

## Validation sources

- `_config.yml`
- `_layouts/default.html`
- `index.md`
- `robots.txt`
- Production Jekyll build validation in GitHub Actions

## Maintenance rule

Metadata changes must preserve one canonical source for page-level SEO tags, retain the public base path, pass the production Jekyll build, and update this audit when the public origin or social image changes.
