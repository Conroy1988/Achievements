# Release and Version Policy

The encyclopedia uses tagged documentation releases to make material changes traceable without implying that GitHub's achievement system itself follows this repository's version numbers.

## Version format

Use semantic versioning in the form `MAJOR.MINOR.PATCH`.

- **MAJOR:** governance model, information architecture, evidence taxonomy, or compatibility change that requires contributors to alter established workflows.
- **MINOR:** new achievement guide, substantial guide expansion, new validation control, or completed documentation phase.
- **PATCH:** factual correction, source refresh, accessibility repair, metadata correction, link repair, or non-breaking maintenance update.

## Release requirements

A tagged release must:

1. identify the included pull requests or completion report;
2. describe user-visible documentation changes;
3. state the validation date;
4. confirm link, Markdown, catalogue, and Jekyll checks passed;
5. identify any unresolved evidence limitations; and
6. avoid claiming that community-observed behaviour is guaranteed by GitHub.

## Pre-release identifiers

Use `-rc.N` only when a large structural change requires public review before it becomes the documented baseline. Routine pull requests do not require pre-releases.

## Release notes

Release notes should group changes under:

- Added
- Changed
- Corrected
- Verification
- Known limitations

Empty sections may be omitted. Notes should link to the relevant guides, audits, or policies rather than restating them in full.

## Tags and branches

- Tags are immutable release records.
- `main` is the current documentation baseline.
- Feature branches must be short-lived and scoped to one independently reviewable purpose.
- A release must not be tagged from an unmerged feature branch.

## Emergency corrections

A materially false, unsafe, inaccessible, or broken production page may receive an immediate patch release after the smallest safe correction passes required checks. The release notes must identify the incident and prevention measure.

## Deprecation

Retired achievement behaviour remains documented historically. Pages should be marked retired or restricted rather than deleted when they retain research value. Superseded policies remain available through repository history and release tags.
