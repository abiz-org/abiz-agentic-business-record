# ABIZ — Agentic Business Record

**An open standard that helps compatible AI assistants find and check a business's public facts.**

A business can publish an ABIZ DNS pointer on a domain it controls. The pointer leads to a public business record over HTTPS. The business record must meet the published JSON Schema to be conformant. ABIZ proves neither legal identity nor inclusion in an AI service.

**Version:** **ABIZ 1.0**, published specification and normative JSON Schema. **IANA registration for `_abiz` remains pending**; publication does not mean IANA approval.

- **Independent standards website:** [abizrecord.org](https://abizrecord.org) (planned)
- **Canonical public repository:** [abiz-org/abiz-agentic-business-record](https://github.com/abiz-org/abiz-agentic-business-record)
- **Specification:** [SPEC.md](SPEC.md)
- **Normative business-record schema:** [schemas/abiz-business-record-v1.schema.json](schemas/abiz-business-record-v1.schema.json)
- **Validation script:** [scripts/validate.py](scripts/validate.py)
- **Conformance fixtures:** [examples/](examples/)
- **Feedback:** use [GitHub Issues](https://github.com/abiz-org/abiz-agentic-business-record/issues); do not publish individuals' direct contact details.

## How ABIZ works

1. Publish one business record over HTTPS, yourself or through a compatible provider.
2. Point a DNS TXT record at it from a domain you control: `_abiz.yourdomain.example`.
3. Compatible software reads the pointer, fetches JSON, **validates the JSON Schema**, then checks the DNS / document relationship.

For a **registered business**, the DNS assertion can include a canonical registration key:

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-OR123456;h=harbour-bike-repair.or.us.to.co"
```

For an **unregistered business**, registration fields and the `k` tag are not mandatory:

```dns
_abiz.marketstand.example. 300 IN TXT "v=abiz1;h=market-stand-repairs-portland.biz.to.co"
```

**These are different fictional businesses, not two simultaneous ABIZ records at the same DNS owner name.** Hostnames ending in `.or.us.to.co` and `.biz.to.co` illustrate one particular provider. ABIZ itself does not require to.co.

## Validate a record

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/registered-us.json
python scripts/validate.py examples/registered-us.json --domain harbourbikes.example --dns-value 'v=abiz1;k=us-OR123456;h=harbour-bike-repair.or.us.to.co'
python -m unittest discover -s tests -v
```

Passing the local schema establishes **record conformance only**. Passing the DNS checks additionally establishes a valid domain-to-record assertion; it is not an independent government-register confirmation.

## Standards governance

Anyone may implement the specification without membership or a per-use standards fee. Proposed changes should be discussed publicly. The `_abiz` IANA request is not confirmed. The managing organisation is To.Co Technologies Limited (UK).
