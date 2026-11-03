# ABIZ — Agentic Business Record

**An open standard that helps compatible AI assistants find and check a business's public facts.**

A business can publish an ABIZ DNS pointer on a domain it controls. The pointer leads to a public business record over HTTPS. The business record must meet the published JSON Schema to be conformant. ABIZ proves neither legal identity nor inclusion in an AI service.

**Version:** **ABIZ 1.0**, published specification and normative JSON Schema. A proposed 1.1 revision is in the specification: a relaxed DNS tag-list syntax (optional spaces around `;` and `=`, as in DKIM and DMARC), a required Ed25519 key in the DNS `p` tag, a well-known file (`/.well-known/abiz.json`) as an alternative to DNS, a `format` parameter (`html`, `markdown`, `json`) at the record host, business-key rules, and business units on path-based record hosts. It is not the published baseline. **IANA registration for `_abiz` remains pending**; publication does not mean IANA approval.

- **Independent standards website:** [abizrecord.org](https://abizrecord.org) (planned)
- **Canonical public repository:** [abiz-org/abiz-agentic-business-record](https://github.com/abiz-org/abiz-agentic-business-record)
- **Specification:** [SPEC.md](SPEC.md)
- **Normative business-record schema:** [schemas/abiz-business-record-v1.schema.json](schemas/abiz-business-record-v1.schema.json) (`$id` `https://abizrecord.org/schema/abiz-business-record-v1.schema.json`)
- **Well-known file schema:** [schemas/abiz-well-known-v1.schema.json](schemas/abiz-well-known-v1.schema.json)
- **Validation script:** [scripts/validate.py](scripts/validate.py)
- **Conformance fixtures:** [examples/](examples/)
- **Feedback:** use [GitHub Issues](https://github.com/abiz-org/abiz-agentic-business-record/issues); do not publish individuals' direct contact details.

## Guides by region

Country-specific help for becoming an agentic business with ABIZ:

- [Asia](docs/countries/asia/)

## How ABIZ works

1. Publish one business record over HTTPS, yourself or through a compatible provider.
2. Point a DNS TXT record at it from a domain you control: `_abiz.yourdomain.example`. If you cannot edit DNS, publish the same values at `https://yourdomain.example/.well-known/abiz.json` instead (SPEC section 3.4). If both exist, DNS wins.
3. Compatible software reads the pointer, fetches `https://<h>?format=json`, **validates the JSON Schema**, then checks the DNS / document relationship. The same address serves HTML by default and Markdown with `?format=markdown` (SPEC section 4.5).

Every DNS assertion MUST include `p`, the business's Ed25519 public key (SPEC section 3.3). It MAY include a business key, `k`, in the form `country[-subdivision]-registration-number` (SPEC section 4.2). `k` is optional for every business. A subdivision is required only for the United States, Canada (provincial corporations) and the United Arab Emirates:

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p=oS5YhE6Qz35Id1hMp3XOI3eQWW03DVgY3kU6rEdlodQ="
```

Without a key, for example for an unregistered business:

```dns
_abiz.marketstand.example. 300 IN TXT "v=abiz1;h=market-stand-repairs-portland.biz.to.co;p=Tsm/xWh0gGtkjIe1choYo3zCLCt/0OTX46QLuWBzGJI="
```

The same values as a well-known file, `https://harbourbikes.example/.well-known/abiz.json` (see `examples/well-known-registered-us.json`):

```json
{ "v": "abiz1", "k": "us-or-123456", "h": "harbour-bike-repair.or.us.to.co", "p": "oS5YhE6Qz35Id1hMp3XOI3eQWW03DVgY3kU6rEdlodQ=" }
```

**These are different fictional businesses, not two simultaneous ABIZ records at the same DNS owner name.** Each `p` is a throwaway key. Hostnames ending in `.or.us.to.co` and `.biz.to.co` illustrate one particular provider. ABIZ itself does not require to.co.

## Validate a record

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/registered-us.json
python scripts/validate.py examples/registered-us.json --domain harbourbikes.example --dns-value 'v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p=oS5YhE6Qz35Id1hMp3XOI3eQWW03DVgY3kU6rEdlodQ='
python scripts/validate.py examples/registered-us.json --domain harbourbikes.example --well-known examples/well-known-registered-us.json
python scripts/validate.py examples/well-known-registered-us.json
python -m unittest discover -s tests -v
```

Passing the local schema establishes **record conformance only**. Passing the DNS checks additionally establishes a valid domain-to-record assertion; it is not an independent government-register confirmation.

With both `--dns-value` and `--well-known`, the validator applies the precedence rule (SPEC section 3.4.4): the DNS assertion is used, and a disagreeing file is reported as a warning.

## The proposed 1.1 `p` key

`p` is required. The validator rejects an assertion (or well-known file) without `p`, and always checks that `p` is a 44-character standard-base64 Ed25519 public key (32 bytes, one trailing `=`). Any other value fails, including an ABIZ 1.0 hexadecimal token and base64url. See SPEC section 3.3.7 for migrating existing values. The format check needs no extra package. To verify a detached signature, add `--p-message` and `--p-signature`; that needs the optional `cryptography` package:

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
