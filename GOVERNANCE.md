# Governance

This document says who decides what goes into ABIZ, how a change is made, and how a version is published.

## Who decides

To.Co Technologies Limited is the managing organisation. Its maintainers decide what is merged into this repository and what is published as a version.

The specification gives no provider a privilege, To.Co included. A rule that would favour one provider's hosts, formats or services is out of scope.

Maintainers are listed in the repository's settings. The project intends to add maintainers from outside To.Co as independent implementers join, and to revise this document when it does.

## How a change is made

1. Anyone may open an issue or a pull request. [`CONTRIBUTING.md`](CONTRIBUTING.md) says how.
2. Discussion happens in public, in the issue or pull request.
3. Changes reach `main` only through a pull request whose automated tests pass.
4. A maintainer merges or declines it, and gives the reason when declining.

A normative change (one that alters what conforms) stays open for comment for at least 7 days before it is merged, unless it fixes a security flaw. Editorial and tooling changes may be merged as soon as the tests pass.

While the project has one maintainer, that maintainer may merge their own pull request after the tests pass. Once there are two or more, a normative change needs the approval of a maintainer other than its author.

## How a version is published

No version of ABIZ is published without all three of:

1. **Passing tests.** The automated conformance, schema, signature and documentation tests pass on the commit being published.
2. **A release tag.** The commit is tagged `vMAJOR.MINOR.PATCH`. A published tag is never moved or deleted. A correction is a new tag.
3. **A compatibility note.** `CHANGELOG.md` says, for that version, whether records, producers and consumers that conformed to the previous version still conform, and what anyone must change if not.

This applies equally to changes from To.Co and from anyone else.

## Version numbers

| Change | Number |
| --- | --- |
| Editorial: no change to what conforms | Patch (1.1.0 → 1.1.1) |
| Normative and compatible: everything that conformed still conforms | Minor (1.1 → 1.2) |
| Normative and breaking | Major, or a new DNS wire version (`v=abiz2`), after public discussion and with a migration period stated in the changelog |

The DNS tag `v=abiz1` and `record_version` change only with a breaking change to the wire format.

## Registrations and other bodies

To.Co Technologies Limited is the contact for registrations made for ABIZ, such as the `_abiz` DNS node name and the `abiz.json` well-known URI. `SPEC.md` section 10 states the current status of each, and says "requested" or "registered" only when that is true.

## Changing this document

A change to this document is made by pull request, like any other, and stays open for comment for at least 7 days.
