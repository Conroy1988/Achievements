---
layout: default
title: Submit achievement evidence
description: Structured, privacy-safe evidence submission with automated screening and mandatory human review.
permalink: /evidence-submission/
---

## Submit achievement evidence

Evidence observations are submitted through a structured GitHub issue form and processed by an automated triage workflow.

[Open the evidence observation form](https://github.com/Conroy1988/Achievements/issues/new?template=evidence-observation.yml)

## What happens after submission

1. The issue is checked against the claim and research-task registers.
2. Required dates, result state, repository visibility, controls, and limitations are validated.
3. Automated screening looks for credentials, email addresses, secret-like values, payment-card-like numbers, and other prohibited material.
4. Blocked submissions receive a correction report and do not create repository changes.
5. Passing submissions generate a privacy-screened draft evidence record.
6. The workflow creates or updates a **draft pull request** for human review.
7. Only a maintainer-reviewed change can alter the canonical evidence register.

> [!CAUTION]
> Automated screening is a safety control, not a guarantee. Do not submit sensitive information in the first place.

## Required information

- Research task ID and linked claim ID
- Canonical achievement slug
- Observation date and result
- Public repository visibility where applicable
- UTC event and first-visible timestamps where available
- Public HTTPS sources
- Environment, controls, limitations, and failed attempts
- Explicit privacy declaration and publication consent

## Evidence contract

The machine-readable submission contract is published at [`/api/submission-schema.json`](api/submission-schema.json).

## Responsible research

Evidence may document a successful award, a failed reproduction, or an inconclusive result. Negative results are valuable when the environment and limitations are recorded precisely.
