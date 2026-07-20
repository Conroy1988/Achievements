# YOLO

## Summary

YOLO is an active, non-tiered GitHub profile achievement associated with merging a pull request without a submitted review.

## Trigger

GitHub's live YOLO detail fragment links a qualifying pull request and states: **Merged without a review**. This establishes the broad unreviewed-merge contract at official level; alternate review states and structured merger identity remain edge-case research.

## Progression or tiers

YOLO is generally observed as a single-level achievement with no published tier progression.

## Eligibility conditions

- The qualifying object must be a pull request.
- The pull request must be merged rather than merely closed.
- No formal pull-request review should have been submitted before merge.
- A requested reviewer is not itself a submitted review: GitHub links one award event where a reviewer was requested but the reviews endpoint remained empty.
- Branch protection, rulesets, and organisation policy may require reviews and prevent this route.
- Ordinary issue comments and pull-request conversation comments are distinct from submitted reviews; submitted COMMENT, REQUEST_CHANGES, APPROVE, dismissed, and automated review states remain under investigation.

## Award timing

The merge event appears immediately in the pull request, while profile-achievement processing may occur later. No fixed refresh interval is guaranteed.

## Verification

1. Open the merged pull request.
2. Confirm the merge event and account attribution.
3. Review the timeline for submitted reviews.
4. Distinguish conversation comments from formal pull-request reviews.
5. Recheck the profile after allowing for processing delay.

## Evidence status

- GitHub officially documents pull-request merges, reviews, branch protection, and rulesets.
- GitHub's live product fragment officially states `Merged without a review`.
- A pending review request with zero submitted reviews is observed as compatible with the linked award.
- Submitted review states and structured merger identity remain unresolved implementation edge cases.

## Known limitations and edge cases

- Required-review rules can make the trigger unavailable.
- Reviews submitted and later dismissed may still complicate qualification.
- Bot reviews, review requests, comments, and approval checks are separate concepts.
- Repository administrators should not weaken important protections solely to obtain an achievement.

## Troubleshooting

- Confirm the pull request was merged, not only closed.
- Inspect the review timeline for approvals, comments, or requested changes submitted as reviews.
- Check whether automation submitted a review.
- Allow time for profile processing.
- Treat ambiguous dismissed-review behaviour as unresolved without reproducible evidence.

## Responsible participation

Use a low-risk repository and a legitimate, reviewable change where an unreviewed merge is already consistent with repository policy. Preserve required review protections on production or collaborative repositories.

## History

YOLO was introduced with GitHub profile achievements. GitHub's live detail fragment now exposes the broad no-review contract and linked qualifying pull request.

## References

- [About pull request reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews)
- [Merging a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request)
- [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference)
- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)
- [Official achievement fragment corpus]({{ site.baseurl }}/official-achievement-fragments/)

## Last verified

**20 July 2026.** Scope: GitHub's first-party `Merged without a review` fragment, its linked pull request with a requested reviewer but zero submitted reviews, and the remaining submitted-review and merger-identity controls.

[Back to the achievement index]({{ site.baseurl }}/docs/achievement-index.html)
