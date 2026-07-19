# Maintenance Policy

This policy defines how the GitHub Achievement Encyclopedia remains accurate, reviewable, and operational after a documentation phase closes.

## Maintenance objectives

1. Preserve evidence classifications and dated verification.
2. Detect broken navigation, build failures, and catalogue drift through automated checks.
3. Correct material inaccuracies through focused pull requests.
4. Keep historical information without presenting retired behaviour as currently earnable.
5. Avoid collecting private account, billing, repository, or analytics data.

## Review cadence

- **Weekly:** scheduled full-repository link validation.
- **Monthly:** review open issues, failed workflows, dependency notices, and unresolved evidence submissions.
- **Quarterly:** sample every active guide for source freshness, award behaviour, and verification-date accuracy.
- **Annually:** conduct a complete guide, governance, accessibility, metadata, and automation review.
- **Event-driven:** review immediately after GitHub announces achievement, profile, Discussions, Sponsors, or contribution-attribution changes.

## Evidence ageing

A verification date records when a claim was last checked; it is not a permanent guarantee. A claim should be reassessed when:

- its primary source is removed or materially changed;
- independent observations conflict;
- GitHub changes the relevant product surface;
- an award no longer appears within the documented timing window; or
- twelve months have passed since the last complete verification.

Unresolved claims must be downgraded rather than silently retained at a stronger confidence level.

## Incident handling

A maintenance incident includes a broken production build, widespread broken links, invalid metadata, inaccessible navigation, compromised workflow dependency, or materially false achievement guidance.

1. Open a focused issue describing impact and evidence.
2. Stop unrelated changes when they would complicate diagnosis.
3. Apply the smallest safe correction.
4. Run link, Markdown, catalogue, and Jekyll validation.
5. Record the cause and prevention measure in the pull request.

## Phase reopening criteria

A completed phase may be reopened only when its acceptance criteria no longer hold, new evidence materially changes its conclusions, or a platform change invalidates the implemented control. Routine wording changes do not reopen a phase.

## Ownership

The repository owner is accountable for accepting maintenance changes and resolving conflicts. Contributors may propose corrections, evidence, automation, and audits through the documented contribution process.
