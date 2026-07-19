---
layout: default
title: GitHub Pair Extraordinaire Achievement
permalink: /achievements/pair-extraordinaire/
description: Co-authored commits, merged pull requests, Pair Extraordinaire tiers, attribution rules, verification, and troubleshooting.
---

## Pair Extraordinaire

## Summary

**Status:** Earnable  
**Tiered:** Yes  
**Evidence status:** GitHub's live achievement fragment officially states the broad trigger: coauthored commits on merged pull requests. Numerical tier thresholds and rewrite edge cases remain community-reported.

Pair Extraordinaire recognises genuine collaboration recorded through co-authored commits that are incorporated into merged pull requests.

## Trigger

GitHub's live detail fragment states that Pair Extraordinaire recognises **coauthored commits on merged pull requests**.

A visible `Co-authored-by:` trailer proves commit attribution, while squash, rebase, email matching and rewritten-history counting remain separate limitations.

## Community-reported progression

| Level | Reported qualifying merged pull requests | Evidence classification |
|---|---:|---|
| Base | 1 | Community-reported |
| Bronze | 10 | Community-reported |
| Silver | 24 | Community-reported |
| Gold | 48 | Community-reported |

These values have broad community support but should not be described as official GitHub thresholds.

## Eligibility conditions

For GitHub to associate a co-authored commit with the intended account:

- the commit message must contain a correctly formatted `Co-authored-by: Name <email>` trailer;
- there must be a blank line between the main commit message and the trailer;
- the email must be associated with the co-author's GitHub account, or be that account's GitHub-provided no-reply address;
- each co-author must have a separate trailer line;
- the commit must be pushed to GitHub and remain in the merged pull request history;
- the attribution must represent a real contribution.

The treatment of private repositories, squash merges, rebases, rewritten commit messages, and unusual merge strategies is not comprehensively documented by GitHub.

## Award timing

Achievement processing is not guaranteed to be immediate. A correctly attributed merged contribution may appear on the profile before the achievement badge or tier updates.

No official maximum processing time is published. Allow a reasonable delay before treating a missing badge as evidence of failure.

## Verification

1. Open the merged pull request.
2. Open the relevant commit from the pull request timeline or commit list.
3. Confirm GitHub displays the expected co-author attribution.
4. Confirm the pull request is merged rather than merely closed.
5. Check the contributor's public profile achievement section after processing time has elapsed.
6. Record the pull-request URL, merge date, and visible attribution when collecting reproducible evidence.

Do not publish private repository names, private commit content, personal email addresses, or other sensitive information as evidence.

## Evidence status

- **Official:** GitHub supports `Co-authored-by:` commit trailers and requires an account-associated email for the commit to count as a contribution.
- **Confirmed:** Correctly formatted co-author trailers are displayed on GitHub after the commit is pushed.
- **Official:** GitHub's live product fragment states that the achievement recognises coauthored commits on merged pull requests.
- **Community-reported:** The thresholds are 1, 10, 24, and 48 qualifying merged pull requests.
- **Unknown:** The exact treatment of every private-repository, squash-merge, rebase, rewritten-history, and delayed-processing scenario.

## Known limitations and edge cases

- A trailer using an unassociated email may display as text without linking to the intended account.
- Rewriting or squashing commits can remove or alter the original trailer.
- Attribution added only to a pull-request description or comment does not create a co-authored commit.
- A co-authored commit on an unmerged branch does not satisfy the commonly reported merged-pull-request condition.
- GitHub may process contribution attribution and achievement progression on different schedules.
- Repository visibility and profile privacy settings can make public verification incomplete.
- Multiple co-authored commits in one pull request should not automatically be assumed to represent multiple qualifying units; community evidence generally describes progression by merged pull requests.

## Troubleshooting

When an expected badge or tier does not appear:

1. Confirm the pull request shows a merged state.
2. Inspect the final commit history rather than the pre-merge branch history.
3. Verify the trailer uses the exact `Co-authored-by:` syntax.
4. Check for the required blank line before the trailer.
5. Confirm the email belongs to the intended GitHub account or uses its valid no-reply format.
6. Check whether squash merging or rebasing replaced the attributed commit.
7. Confirm the co-author is visibly linked on GitHub.
8. Allow additional processing time.
9. Treat the event as an observation until independently reproduced.

## Responsible participation

Use co-author attribution only when another person made a substantive contribution to the commit. Accurate authorship is part of the permanent project record and should take priority over profile recognition.

## History

GitHub has long supported multiple-author attribution through commit-message trailers. Pair Extraordinaire later exposed this form of collaboration as a profile achievement. GitHub has not published a complete public change log for the achievement's thresholds or counting logic.

Material changes should therefore be documented with dated, reproducible evidence and should retain earlier claims until contradictions are resolved.

## References

- [Creating a commit with multiple authors](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors)
- [Viewing contributions on your profile](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/viewing-contributions-on-your-profile)
- [GitHub achievement index]({{ site.baseurl }}/docs/achievement-index.html)
- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)
- [Official achievement fragment corpus]({{ site.baseurl }}/official-achievement-fragments/)

## Last verified

**19 July 2026** — verified GitHub's first-party Pair Extraordinaire fragment and linked co-author history. The broad trigger is official; numerical tier thresholds and merge-rewrite edge cases remain community-reported or unknown.

[Back to the achievement index]({{ site.baseurl }}/docs/achievement-index.html)
