# Security policy

## What to report here

- A flaw in the specification that lets someone pass off a record as another business's, bypass the signature or domain checks, or make a conforming consumer fetch something it should not.
- A flaw in the reference validator (`scripts/validate.py`) or the schemas that makes them accept what the specification rejects, or the reverse, where that has a security effect.
- A leaked secret in this repository.

A problem in one provider's or one implementer's software belongs with that provider, unless it follows from doing what the specification says.

## How to report

Use **Report a vulnerability** on the Security tab of this repository. That opens a private report that only the maintainers can read. Please do not open a public issue or pull request for a security problem.

Include the section of `SPEC.md` or the file concerned, what an attacker can do, and the smallest example that shows it.

## What happens next

- We aim to acknowledge a report within 5 working days.
- We will tell you whether we agree it is a flaw and what we plan to do.
- A fix to the specification is published as a new tagged version with a `CHANGELOG.md` entry that says what changed and what implementers need to do. We credit the reporter unless they ask us not to.
- We ask you to keep the details private until a fixed version is published or 90 days have passed, whichever is first.

These are aims, not guarantees. The project has a small number of maintainers.

## Supported versions

Security fixes are made to the latest published version of the specification. Earlier versions are not changed.

## Keys in this repository

The public keys and signatures in `examples/` and `SPEC.md` are demonstration values. Their private keys were discarded. Do not report them as leaked secrets, and do not reuse them.
