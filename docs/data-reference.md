---
layout: default
title: Achievement data reference
permalink: /data/
description: Machine-readable achievement records, schema guarantees, validation rules, and maintenance expectations.
---

## Achievement data reference

The encyclopedia publishes its canonical structured catalogue in [`data/achievements.json`](../data/achievements.json). The file represents the same nine guides listed in the [achievement index](achievement-index.md) and is validated against guide metadata on every relevant change.

## Dataset contract

Each record contains:

- a stable slug and display name;
- active, retired, or restricted status;
- category, trigger, and primary action;
- tier information and evidence classifications;
- canonical guide path and public permalink;
- verification date;
- search aliases;
- official and community source arrays; and
- known limitations.

The dataset uses semantic versioning through its `schema_version` field. A schema-breaking change requires a major schema version.

## Schema

[`data/achievement.schema.json`](../data/achievement.schema.json) is a JSON Schema draft 2020-12 document. It defines the public field names, supported evidence labels, tier structure, status values, date format, and URI requirements.

## Validation guarantees

`scripts/validate_achievement_data.py` checks that:

1. exactly nine unique achievement records exist;
2. the dataset contains seven active and two retired records;
3. dataset names, guide paths, primary actions, and tiered flags match the achievement index;
4. every guide exists and its permalink matches the dataset;
5. every dataset verification date matches the guide's `Last verified` section;
6. tier thresholds are valid, unique, and increasing;
7. aliases, sources, evidence labels, and known limitations follow the data contract; and
8. the schema document declares the expected JSON Schema version and achievement definition.

## Evidence interpretation

Structured data does not strengthen a claim. Values marked `community-reported`, `observed`, or `unknown` retain the same limitations described in the human-readable guides. Consumers should display the evidence classification and verification date alongside thresholds or triggers.

## Consumer guidance

- Treat `slug` as the stable record identifier.
- Use `permalink` for public-page navigation.
- Use `guide_path` when working with repository content.
- Do not present community-reported thresholds as official GitHub guarantees.
- Revalidate cached data when `schema_version` changes.

## Related material

- [Achievement index](achievement-index.md)
- [Evidence strength levels](evidence-strength-levels.md)
- [Verification methodology](verification-methodology.md)
- [Repository health dashboard](health-dashboard.md)
