# Dependency Maintenance

Dependency updates are proposed monthly through Dependabot for GitHub Actions and Bundler.

## Update policy

- Updates are grouped by ecosystem to reduce pull-request noise.
- A maximum of five open update pull requests is permitted per ecosystem.
- GitHub Actions updates use the `ci` commit prefix.
- Bundler and Jekyll updates use the `deps` commit prefix.
- Scheduling uses the Europe/London timezone.

## Review requirements

Before merging an automated dependency update:

1. review release notes and security implications;
2. confirm the dependency source and requested version are expected;
3. run the link, Markdown, achievement-catalogue, and production Jekyll checks;
4. inspect generated-site warnings for changed or removed behaviour;
5. reject updates that require unnecessary write permissions; and
6. record any compatibility workaround in the pull request.

Major-version updates should be separated from routine grouped updates when they require migration work. Automated updates must not bypass branch protection or required checks.
