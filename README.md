# ABIZ — Agentic Business Record

**An open standard that helps compatible AI assistants find and check a business's public facts.**

A business can publish an ABIZ DNS pointer on a domain it controls. The pointer leads to a public business record over HTTPS. The business record must meet the published JSON Schema to be conformant. ABIZ proves neither legal identity nor inclusion in an AI service.

**Version:** **ABIZ 1.0**, published specification and normative JSON Schema. A proposed 1.1 revision is in the specification: a relaxed DNS tag-list syntax (optional spaces around `;` and `=`, as in DKIM and DMARC) and an Ed25519 key in the optional DNS `p` tag. It is not the published baseline. **IANA registration for `_abiz` remains pending**; publication does not mean IANA approval.

- **Independent standards website:** [abizrecord.org](https://abizrecord.org) (planned)
- **Canonical public repository:** [abiz-org/abiz-agentic-business-record](https://github.com/abiz-org/abiz-agentic-business-record)
- **Specification:** [SPEC.md](SPEC.md)
- **Normative business-record schema:** [schemas/abiz-business-record-v1.schema.json](schemas/abiz-business-record-v1.schema.json)
- **Validation script:** [scripts/validate.py](scripts/validate.py)
- **Conformance fixtures:** [examples/](examples/)
- **Feedback:** use [GitHub Issues](https://github.com/abiz-org/abiz-agentic-business-record/issues); do not publish individuals' direct contact details.

## Guides by region

Country-specific help for becoming an agentic business with ABIZ:

- [Europe](docs/countries/europe/)

## How ABIZ works

1. Publish one business record over HTTPS, yourself or through a compatible provider.
2. Point a DNS TXT record at it from a domain you control: `_abiz.yourdomain.example`.
3. Compatible software reads the pointer, fetches JSON, **validates the JSON Schema**, then checks the DNS / document relationship.

A DNS assertion MAY include a business key, `k`, in the form `country[-subdivision]-registration-number` (SPEC section 4.2). `k` is optional for every business. A subdivision is required only for the United States, Canada (provincial corporations) and the United Arab Emirates:

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co"
```

Without a key, for example for an unregistered business:

```dns
_abiz.marketstand.example. 300 IN TXT "v=abiz1;h=market-stand-repairs-portland.biz.to.co"
```

**These are different fictional businesses, not two simultaneous ABIZ records at the same DNS owner name.** Hostnames ending in `.or.us.to.co` and `.biz.to.co` illustrate one particular provider. ABIZ itself does not require to.co.

## Validate a record

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/registered-us.json
python scripts/validate.py examples/registered-us.json --domain harbourbikes.example --dns-value 'v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co'
python -m unittest discover -s tests -v
```

Passing the local schema establishes **record conformance only**. Passing the DNS checks additionally establishes a valid domain-to-record assertion; it is not an independent government-register confirmation.

## The proposed 1.1 `p` key

`p` is optional. When the DNS assertion contains `p`, the validator always checks that it is a 44-character standard-base64 Ed25519 public key (32 bytes, one trailing `=`). Any other value fails, including an ABIZ 1.0 hexadecimal token and base64url. See SPEC section 3.3.7 for migrating existing values. The format check needs no extra package. To verify a detached signature, add `--p-message` and `--p-signature`; that needs the optional `cryptography` package:

```sh
python -m pip install -r requirements-p-key.txt
python scripts/validate.py examples/registered-us.json \
  --domain harbourbikes.example \
  --dns-value "$(sed -n '/^v=abiz1/p' examples/dns-ed25519-p.txt)" \
  --p-message "abiz1.1 p-key test" \
  --p-signature "K8z1ImVMyYZF7tGBnyaL4fhI3WAnCTo1EKHS77J+uLCet14Sbg629QmXc1e6rIjn3KtZdXgKNtuakuTLmruKAg=="
```

A business record cannot carry retired keys. The schema reserves their shape only as the nested definition `$defs/retired-key`.

## Standards governance

Anyone may implement the specification without membership or a per-use standards fee. Proposed changes should be discussed publicly. The `_abiz` IANA request is not confirmed. The managing organisation is To.Co Technologies Limited (UK).
