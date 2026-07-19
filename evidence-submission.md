---
layout: default
title: Submit achievement evidence
description: Structured, privacy-safe evidence submission with automated screening and mandatory human review.
permalink: /evidence-submission/
---

## Submit achievement evidence

The encyclopedia provides two structured submission routes. Use the general observation form for an existing research task, or the mission packet form when the evidence belongs to one of the ranked acquisition missions.

- [Open the general evidence observation form](https://github.com/Conroy1988/Achievements/issues/new?template=evidence-observation.yml)
- [Open the targeted mission evidence form](https://github.com/Conroy1988/Achievements/issues/new?template=mission-evidence.yml)

The [mission execution intake guide](docs/mission-execution-intake.md) lists every mission, required evidence key, scheduled hold, and review boundary.

## What happens after submission

1. The issue is checked against the relevant task, claim, mission, contradiction, and achievement relationships.
2. Required dates, result state, repository visibility, controls, limitations, and public evidence keys are validated.
3. Scheduled missions are rejected before their published `no_action_before` timestamp.
4. Automated screening looks for credentials, email addresses, secret-like values, payment-card-like numbers, private communications, and other prohibited material.
5. Blocked submissions receive a correction report and do not create repository changes.
6. Passing submissions generate a privacy-screened draft evidence record or mission packet.
7. The workflow creates or updates a **draft pull request** for human review.
8. Only a maintainer-reviewed change can alter canonical evidence, mission state, contradictions, or claims.

> [!CAUTION]
> Automated screening is a safety control, not a guarantee. Do not submit sensitive information in the first place.

## General observation requirements

- Research task ID and linked claim ID
- Canonical achievement slug
- Observation date and result
- Public repository visibility where applicable
- UTC event and first-visible timestamps where available
- Public HTTPS sources
- Environment, controls, limitations, and failed attempts
- Explicit privacy declaration and publication consent

## Mission packet requirements

- Mission ID and one linked research task
- One linked claim and contradiction where the mission requires them
- Every required evidence key published by the selected mission
- Safeguard declaration confirming no artificial activity, spam, false attribution, star solicitation, answer farming, or protection bypass
- Public HTTPS sources, controls, limitations, privacy declaration, and publication consent

## Evidence contracts

- General evidence observations: [`/api/submission-schema.json`](api/submission-schema.json)
- Targeted mission packets: [`/api/mission-submission-schema.json`](api/mission-submission-schema.json)
- Active mission requirements: [`/api/acquisition-missions.json`](api/acquisition-missions.json)

## Responsible research

Evidence may document a successful award, a failed reproduction, a blocked mission, processing delay, or an inconclusive result. Negative results remain valuable when the environment, controls, timing, and limitations are recorded precisely.
