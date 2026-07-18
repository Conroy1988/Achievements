# YOLO

YOLO recognises merging a pull request without a review.

## Reproduction path

1. Create a branch with a useful change.
2. Open a pull request against the default branch.
3. Merge it without submitting or receiving a pull-request review.

## Caveats

Repository protection rules may require reviews and therefore prevent this route. A repository owner should not weaken protections on an important production repository solely to obtain the badge.

## Verification

A normal issue or commit is insufficient: the qualifying event is an unreviewed pull-request merge.
