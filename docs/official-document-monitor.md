---
layout: default
title: Official documentation monitor
description: Monitored GitHub documentation and the achievement guides affected by material changes.
permalink: /official-doc-monitor/
---

## Official documentation monitor

This monitor fingerprints normalized visible content from selected official GitHub documentation. A changed fingerprint is a review signal, not automatic proof that an achievement rule changed.

| Document | Affected achievements | Baseline checked | Fingerprint |
|---|---|---|---|
| [github-profile-reference](https://docs.github.com/en/account-and-profile/reference/profile-reference) | pull-shark, quickdraw, yolo, pair-extraordinaire, galaxy-brain, starstruck, public-sponsor, mars-2020-contributor | 2026-08-09T13:47:37Z | `a6e34db5f3b8` |
| [multiple-authors](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors) | pair-extraordinaire | 2026-08-09T13:47:37Z | `ce40e3bb5167` |
| [pull-request-reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews) | yolo | 2026-08-09T13:47:37Z | `bf9f44244b3a` |
| [github-discussions](https://docs.github.com/en/discussions/collaborating-with-your-community-using-discussions/about-discussions) | galaxy-brain | 2026-08-09T13:47:37Z | `07b2e7037b48` |
| [repository-stars](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars) | starstruck | 2026-08-09T13:47:37Z | `e9f71012f00d` |
| [github-sponsors](https://docs.github.com/en/sponsors) | public-sponsor | 2026-08-09T13:47:37Z | `ccfdebf043e0` |

## Change handling

1. Scheduled checks compare current normalized content with the committed baseline.
2. Material differences produce a dated report and an open review issue.
3. A maintainer inspects the official wording and identifies affected guide claims.
4. Baselines change only through a reviewed pull request after the guide impact is resolved.

Navigation, footer, style, script, and SVG content are excluded before hashing to reduce cosmetic noise.
