# Source Resilience Inventory

The repository generates a machine-readable and human-readable inventory of every external URL referenced by Markdown content.

## Inventory fields

- source URL and domain;
- source classification and stability rating;
- total reference count;
- every referencing repository file;
- last availability-check date;
- current availability result; and
- an Internet Archive lookup route.

## Automation

Pull requests generate a structural inventory without making external requests. The monthly scheduled workflow and manual runs also test source availability.

The workflow publishes:

- `source-inventory.csv` for filtering and analysis; and
- `source-inventory.md` for direct review.

Availability results are diagnostic rather than permanent evidence. Restricted responses, rate limits, transient outages, and bot protection must be reviewed before a source is replaced or downgraded.

## Maintenance response

1. Confirm an unavailable source manually.
2. Check for an official replacement or maintained successor.
3. Review the archive lookup route.
4. Update every dependent claim through a traceable pull request.
5. Preserve the original source context where it remains historically relevant.
