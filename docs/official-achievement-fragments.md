---
layout: default
title: Official GitHub achievement fragments
description: GitHub-owned live product fragments that explicitly state achievement criteria and tier milestones.
permalink: /official-achievement-fragments/
---

## Official GitHub achievement fragments

GitHub profile badges expose public achievement-detail fragments through the platform's own hovercard endpoints. These first-party fragments state the material criterion, link qualifying history, and—where present—publish tier milestone ordinals.

**Fragments:** 6  
**Official claims supported:** 9  
**Complete tier tables:** 3  
**Contradictions resolved:** 3  
**Automatic canonical mutations:** 0

| Achievement | GitHub criterion | Published milestones | Source account |
|---|---|---|---|
| quickdraw | Closed within 5 minutes of opening | 5 minutes | [`Schweinepriester`](https://github.com/users/Schweinepriester/achievements/quickdraw/detail?hovercard=1) |
| yolo | Merged without a review | not published  | [`Schweinepriester`](https://github.com/users/Schweinepriester/achievements/yolo/detail?hovercard=1) |
| pair-extraordinaire | coauthored commits on merged pull requests | not published  | [`Schweinepriester`](https://github.com/users/Schweinepriester/achievements/pair-extraordinaire/detail?hovercard=1) |
| pull-shark | opened pull requests that have been merged | 2, 16, 128, 1024 merged pull requests | [`ljharb`](https://github.com/users/ljharb/achievements/pull-shark/detail?hovercard=1) |
| galaxy-brain | answered discussions | 2, 8, 16, 32 accepted answers | [`ljharb`](https://github.com/users/ljharb/achievements/galaxy-brain/detail?hovercard=1) |
| starstruck | created a repository that has many stars | 16, 128, 512, 4096 repository stars | [`Schweinepriester`](https://github.com/users/Schweinepriester/achievements/starstruck/detail?hovercard=1) |

## Scope boundaries

- Quickdraw's fragment states a five-minute maximum; processing delay remains separate.
- YOLO's fragment states `Merged without a review`; alternate review-state and merger-identity edge cases remain under research.
- Pair Extraordinaire's fragment states the broad co-authored-commit trigger but does not publish numerical tier thresholds.
- Pull Shark and Galaxy Brain expose complete x4 milestone histories.
- Starstruck exposes the complete star table but not transfer, organization-ownership, archival, fork, or falling-count persistence.

## Machine-readable data

See [`/api/official-achievement-fragments.json`](../api/official-achievement-fragments.json).
