# Contributing

Contributions should improve the accuracy, usability, accessibility, or maintainability of the GitHub Achievement Encyclopedia.

## Choose the correct route

- Use the correction issue form for inaccurate or outdated documentation.
- Use the evidence issue form for a dated observation or reproduction result.
- Open a pull request when the correction is understood and you can provide the finished change.
- Use the security policy for credentials, private data, malicious links, or workflow risks.

## Before opening a pull request

1. Check whether an issue or pull request already covers the subject.
2. Verify that the claim is current and reproducible.
3. Distinguish official documentation from community-observed behaviour.
4. Remove private information, tokens, billing details, and unrelated account data.
5. Keep the change focused on one independently reviewable purpose.
6. Run the applicable local validation commands below.

## Local validation

Install Node.js, Ruby, and Bundler before running the complete documentation checks.

```bash
python scripts/check_links.py
npx --yes markdownlint-cli2@0.18.1
bundle install
JEKYLL_ENV=production bundle exec jekyll build --trace
```

The Markdown rules are defined in `.markdownlint-cli2.yaml`. Jekyll dependencies are declared in `Gemfile`. Validation failures should be corrected rather than broadly suppressed.

## Evidence expectations

Preferred evidence order:

1. current official GitHub documentation or announcements;
2. dated and reproducible observations;
3. repeated independent community reports;
4. clearly labelled unconfirmed reports.

Screenshots should include enough context to understand the observation while excluding private repository content and personal information.

## Documentation style

Use concise headings, explicit conditions, reproducible steps, caveats, and an evidence-confidence statement where relevant. Avoid presenting community thresholds as official guarantees.

## Pull requests

Explain what changed, why it is useful, how it was validated, and which issue it addresses. Complete the pull-request checklist. Corrections are preferred over silently deleting disputed or historical material.

## Conduct and scope

Follow `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`, and `SECURITY.md`. Empty activity, fabricated evidence, deceptive attribution, fake engagement, and instructions designed solely to manipulate contribution metrics are not accepted.
