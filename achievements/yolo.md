---
layout: default
title: GitHub YOLO Achievement
permalink: /achievements/yolo/
description: How the GitHub YOLO achievement is triggered, review conditions, safe testing, and troubleshooting.
---

## YOLO

**Status:** Earnable  
**Tiered:** No  
**Evidence level:** Strong community consensus; the exact implementation is not formally specified by GitHub.

## Trigger

YOLO is generally awarded when you merge your own pull request without an approving review.

## Typical qualifying sequence

1. Create a real change on a branch.
2. Open a pull request against a repository where you can merge.
3. Do not obtain an approving pull-request review.
4. Merge the pull request yourself.

Comments are not necessarily reviews. The important distinction is whether the pull request received a formal approving review before merge.

## Safe use

Use a personal learning or documentation repository where self-merging is permitted. Do not bypass review requirements in production, security-sensitive, or team-controlled repositories merely to unlock an achievement.

## Common misconceptions

- A pull request comment is not always a formal review.
- Merging someone else's pull request may not satisfy the self-merge condition.
- Direct pushes to the default branch are not pull-request merges.
- A repository's branch protection may correctly prevent the qualifying sequence.

## Troubleshooting

Verify the pull request shows you as both author and merger, and that no approval appears in its review history. Achievement processing can be delayed.

## Confidence statement

The self-merge-without-review description is consistently reported by established community references. GitHub's official profile documentation confirms that achievement-generating events are attached to profile badges but does not publish this precise trigger.

## Last verified

**19 July 2026** — reviewed the reported self-merge trigger, formal-review distinction, safe testing conditions, and known processing delays.

[Back to the achievement index]({{ site.baseurl }}/docs/achievement-index.html)
