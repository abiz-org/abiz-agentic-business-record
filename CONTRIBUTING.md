# Contributing to ABIZ

ABIZ is an open specification. Anyone may propose a change, report a problem or ask a question. You do not need to be a member of anything, and you do not need to use any particular provider.

## Ways to contribute

- **A question or a problem with the text.** Open an issue. Quote the section number.
- **An implementation report.** If you have built a producer or consumer, open an issue saying what you implemented and what was unclear. Independent implementations are the most useful contribution the project can receive.
- **A change.** Open a pull request. For anything beyond a typo, open an issue first so the change can be discussed before you write it.
- **A security problem.** Do not open a public issue. Use GitHub's "Report a vulnerability" button on the Security tab of this repository. See [`SECURITY.md`](SECURITY.md).

## What kind of change is it?

Say which of these your pull request is. It decides how it is reviewed and how it is released.

| Kind | Examples | Released as |
| --- | --- | --- |
| Editorial | Typos, clearer wording, a corrected example, with no change to what conforms | A patch tag (1.1.x) |
| Normative, compatible | A new optional member, a clarified rule that no conforming implementation breaks | A minor version (1.x) |
| Normative, breaking | A changed or removed requirement, a schema that rejects records it accepted | A new major version or wire version, after public discussion |
| Tooling | The validator, tests, scripts | With the next tag |

A normative change must update, in the same pull request: `SPEC.md`, the schema where it applies, at least one example or test that shows the new behaviour, and `CHANGELOG.md`.

## Before you open a pull request

```
python -m pip install -r requirements-dev.txt pytest
python -m pytest tests
```

All tests must pass. Some tests read earlier commits, so use a full clone, not a shallow one.

Keep each pull request to one subject. Write the text in plain English, in the style of the surrounding section, using the BCP 14 key words (MUST, SHOULD, MAY) only where a requirement is intended.

Published tags are never moved or deleted. A correction to a published version is a new tag.

## Licence of contributions

By contributing you agree that your contribution is licensed under the licence that applies to the file you change, as set out in [`LICENSING.md`](LICENSING.md):

- specification text and documentation: CC BY 4.0;
- schemas, code and tests: Apache License 2.0, including its patent licence;
- examples: CC0 1.0.

You keep the copyright in what you write. No separate contributor agreement is needed.

Do not contribute material you do not have the right to license in this way. If your contribution includes or is derived from someone else's work, say so in the pull request and name its source and licence.

## Sign your commits off

Every commit must carry a `Signed-off-by` line, which certifies the Developer Certificate of Origin in [`DCO`](DCO):

```
git commit -s -m "SPEC: clarify the trailing semicolon rule"
```

This adds a line such as `Signed-off-by: Your Name <you@example.com>`. Use a name and address you are content to have in the public history; a GitHub no-reply address is accepted.

## How decisions are made

To.Co Technologies Limited is the managing organisation and currently decides what is merged. Changes are discussed in public issues and pull requests in this repository, reach `main` only through a pull request whose tests pass, and are published only as tagged versions. [`GOVERNANCE.md`](GOVERNANCE.md) sets out the rules.

## Conduct

Be civil and stay on the subject. See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
