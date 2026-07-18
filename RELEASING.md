# Release Process

## Release types

- **Continuous correction:** a focused factual, accessibility, or link correction merged to `main`.
- **Documentation release:** a grouped set of new guides, structural changes, or contributor-facing features.
- **Policy release:** a material governance, security, or evidence-classification change.

## Pre-release checklist

1. Confirm all intended pull requests are merged.
2. Confirm link validation passes in strict mode.
3. Confirm the accessibility workflow passes against deployed representative pages.
4. Verify the homepage, navigation, sitemap, robots policy, and social metadata.
5. Check that claims use the correct evidence label.
6. Confirm no secrets, billing information, private repository content, or unnecessary personal data are present.
7. Update `CHANGELOG.md` and the release date.
8. Confirm `ROADMAP.md` and `BACKLOG.md` reflect completed work.

## Publishing

1. Merge the release-record change to `main`.
2. Confirm GitHub Pages publishes the resulting commit.
3. Create a GitHub release using the date-based title `Documentation release YYYY-MM-DD` when the change is substantial enough to merit a permanent release note.
4. Summarise additions, corrections, known limitations, and evidence-status changes.
5. Link the merged pull requests rather than duplicating their full technical discussion.

## Post-release verification

- Open the public Pages site in a clean browser session.
- Verify at least one desktop and one mobile viewport.
- Confirm automated checks remain green after deployment.
- Open corrective issues for any non-blocking defects discovered after publication.

## Rollback

For a harmful or materially inaccurate release, revert the responsible merge through a reviewed pull request. Document why the rollback was necessary and preserve the original discussion for auditability.
