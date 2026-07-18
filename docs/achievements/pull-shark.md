# Pull Shark

## Summary

Pull Shark is an active, tiered GitHub profile achievement associated with authored pull requests that are merged. GitHub presents achievements in the profile sidebar and may link an achievement to qualifying events when the viewer has access to the relevant repository.

## Trigger

The qualifying action is having a pull request authored by your account merged into a repository.

GitHub does not publish a complete Pull Shark counting specification. Treat repository visibility, deleted repositories, transferred repositories, account changes, and historical recalculation behaviour as implementation details unless GitHub documents them.

## Progression and tiers

The following thresholds are widely reproduced by the community but are not published as guaranteed thresholds in GitHub's current profile documentation.

| Level | Reported threshold | Evidence status |
|---|---:|---|
| Base achievement | 2 merged pull requests | Community-reported |
| Bronze | 16 merged pull requests | Community-reported |
| Silver | 128 merged pull requests | Community-reported |
| Gold | 1,024 merged pull requests | Community-reported |

A threshold should not be described as reached solely from a manually counted total. GitHub's internal eligible-event count may differ from a user's own search results.

## Eligibility conditions

- The pull request must be merged rather than merely opened or closed.
- The account seeking the achievement must be recorded as the pull request author.
- The merge must be associated with GitHub.com achievement processing.
- Private or internal activity may affect achievements according to the account's contribution and achievement visibility settings.
- Event details are only visible to viewers who can access the repository or organisation where the event occurred.

The effect of repository deletion, repository transfer, author-account migration, bot authorship, and imported history remains insufficiently documented for firm guarantees.

## Award timing

Awarding and tier changes may not appear immediately after a qualifying merge. GitHub does not publish a service-level target for achievement processing.

When a threshold appears to have been reached, allow for asynchronous processing before treating the badge as missing.

## Verification

1. Open your GitHub profile and inspect the **Achievements** section.
2. Select the Pull Shark badge to view its current presentation and any linked contributing events.
3. Confirm that the relevant pull requests show your account as author and have a merged state.
4. Review **Settings → Profile settings** to ensure achievements are enabled.
5. Review contribution settings if private or internal activity is relevant.

Do not publish screenshots that expose private repository names, organisation names, billing data, tokens, email addresses, or inaccessible event URLs.

## Evidence status

| Claim | Status |
|---|---|
| GitHub displays achievements on user profiles | Official |
| Achievement event links depend on repository or organisation access | Official |
| Achievements can be hidden globally or individually | Official |
| Pull Shark is associated with merged pull requests | Confirmed |
| The four numerical thresholds in this guide | Community-reported |
| Exact processing delay | Unknown |
| Exact handling of deleted, transferred, imported, or migrated history | Unknown |

## Known limitations and edge cases

- A user's visible pull-request count is not necessarily GitHub's eligible achievement count.
- Closed but unmerged pull requests do not satisfy the documented trigger used by this guide.
- Achievement visibility settings can make an earned badge appear absent to other viewers.
- Private-profile settings can hide achievements and highlights.
- Links from an achievement may be inaccessible to viewers without repository access.
- GitHub labels achievements as a public-preview feature, so behaviour can change without the tier table being formally versioned.

## Troubleshooting

If Pull Shark or a new tier does not appear:

1. Confirm each relevant pull request is merged.
2. Confirm your account is the pull-request author, not only a reviewer, committer, or merger.
3. Check that achievements are enabled in profile settings.
4. Check whether the profile or individual achievement is hidden.
5. Allow time for profile processing and refresh the profile later.
6. Avoid assuming that every result returned by a pull-request search is eligible.
7. Record reproducible evidence and the date observed before reporting a possible threshold or platform defect.

## Responsible participation

Earn Pull Shark through useful, independently reviewable contributions. Suitable work includes documentation corrections, tests, accessibility improvements, maintenance, bug fixes, and focused feature changes.

Avoid empty pull requests, duplicate edits, artificial repository splitting, misleading changes, or deliberately noisy history created only to increase a counter.

## History

GitHub announced profile achievements as a public beta on 9 June 2022. Pull Shark appeared among the achievements shown in that launch material.

No official tier-threshold changelog was located during this verification. Threshold claims therefore remain community-reported rather than official.

## References

- [GitHub Docs: Profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference)
- [GitHub Docs: Manage visibility settings for private contributions and achievements](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements)
- [GitHub Docs: Profile contributions reference](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)
- [GitHub Changelog: Achievements public beta](https://github.blog/changelog/2022-06-09-achievements-public-beta/)
- [GitHub Achievement Index](../achievement-index.md)
- [Achievement Guide Standard](../achievement-guide-standard.md)

## Last verified

**19 July 2026** — verified against current GitHub profile, achievement-visibility, contribution-reference, and public-beta documentation. The numerical Pull Shark thresholds were not found in current official GitHub documentation and remain classified as community-reported.