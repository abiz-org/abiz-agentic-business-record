# ABIZ — Agentic Business Record

**An open standard that helps compatible AI assistants find and check a business's public facts.**

A business can publish an ABIZ DNS pointer on a domain it controls. The pointer leads to a public business record over HTTPS. The business record must meet the published JSON Schema to be conformant. ABIZ proves neither legal identity nor inclusion in an AI service.

**Version:** **ABIZ 1.0**, published specification and normative JSON Schema. A proposed 1.1 revision is in the specification: a relaxed DNS tag-list syntax (optional spaces around `;` and `=`, as in DKIM and DMARC), a required Ed25519 key in the DNS `p` tag, a well-known file (`/.well-known/abiz.json`) as an alternative to DNS, snake_case member names and a REQUIRED `public_key` and `signature` in every business record (an Ed25519 signature over the RFC 8785 canonical record, verified against `p`), a `format` parameter (`html`, `markdown`, `json`) at the record host, business-key rules, and business units on path-based record hosts. It is not the published baseline. **IANA registration for `_abiz` remains pending**; publication does not mean IANA approval.

- **Independent standards website:** [abizrecord.org](https://abizrecord.org) (planned)
- **Canonical public repository:** [abiz-org/abiz-agentic-business-record](https://github.com/abiz-org/abiz-agentic-business-record)
- **Specification:** [SPEC.md](SPEC.md)
- **Normative business-record schema:** [schemas/abiz-business-record-v1.schema.json](schemas/abiz-business-record-v1.schema.json) (`$id` `https://abizrecord.org/schema/abiz-business-record-v1.schema.json`)
- **Well-known file schema:** [schemas/abiz-well-known-v1.schema.json](schemas/abiz-well-known-v1.schema.json)
- **Validation script:** [scripts/validate.py](scripts/validate.py)
- **Conformance fixtures:** [examples/](examples/)
- **Feedback:** use [GitHub Issues](https://github.com/abiz-org/abiz-agentic-business-record/issues); do not publish individuals' direct contact details.

## Country guides

Country-specific help for becoming an agentic business with ABIZ.

Choose your region to find instructions for your country:

- [Africa](docs/countries/africa/index.md)
- [Asia](docs/countries/asia/index.md)
- [Europe](docs/countries/europe/index.md)
- [North America](docs/countries/north-america/index.md)
- [Oceania](docs/countries/oceania/index.md)
- [South America](docs/countries/south-america/index.md)

[Browse all country guides](docs/countries/README.md)

## How ABIZ works

1. Publish one business record over HTTPS, yourself or through a compatible provider.
2. Point a DNS TXT record at it from a domain you control: `_abiz.yourdomain.example`. If you cannot edit DNS, publish the same values at `https://yourdomain.example/.well-known/abiz.json` instead (SPEC section 3.4). If both exist, DNS wins.
3. Compatible software reads the pointer, fetches `https://<h>?format=json`, **validates the JSON Schema**, **verifies the record's `signature`** with its `public_key`, checks that `public_key` equals `p`, then checks the rest of the DNS / document relationship. The same address serves HTML by default and Markdown with `?format=markdown` (SPEC section 4.5).

Every DNS assertion MUST include `p`, the business's Ed25519 public key (SPEC section 3.3). It MAY include a business key, `k`, in the form `country[-subdivision]-registration-number` (SPEC section 4.2). `k` is optional for every business. A subdivision is required only for the United States, Canada (provincial corporations) and the United Arab Emirates:

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p=bknJGPICOYXD4VJvtV+2rL8q+LjfgoPFJEDFvEB6iQo="
```

Without a key, for example for an unregistered business:

```dns
_abiz.marketstand.example. 300 IN TXT "v=abiz1;h=market-stand-repairs-portland.biz.to.co;p=HKmFn2cg/6EXCYZ75lHdr7S7vfq1GUfodvTyb6pl5Uc="
```

The same values as a well-known file, `https://harbourbikes.example/.well-known/abiz.json` (see `examples/well-known-registered-us.json`):

```json
{ "v": "abiz1", "k": "us-or-123456", "h": "harbour-bike-repair.or.us.to.co", "p": "bknJGPICOYXD4VJvtV+2rL8q+LjfgoPFJEDFvEB6iQo=" }
```

**These are different fictional businesses, not two simultaneous ABIZ records at the same DNS owner name.** Each `p` is a throwaway key. Hostnames ending in `.or.us.to.co` and `.biz.to.co` illustrate one particular provider. ABIZ itself does not require to.co.

## Signed business records

Every business record carries `public_key` (the same value as `p`) and `signature`: an Ed25519 signature over the UTF-8 bytes of the RFC 8785 (JCS) canonical form of the record without its `signature` member (SPEC section 4.6). All member names are snake_case. A shortened example; the full, signed file is [`examples/registered-us.json`](examples/registered-us.json):

```text
{
  "record_version": "abiz1",
  "business_name": "Harbour Bike Repair LLC",
  "country": "us",
  "business_key": "us-or-123456",
  "registration_number": "123456",
  "identity_host": "harbour-bike-repair.or.us.to.co",
  "domains": ["harbourbikes.example"],
  "public_key": "bknJGPICOYXD4VJvtV+2rL8q+LjfgoPFJEDFvEB6iQo=",
  …
  "signature": "tp0XN8oW…riPBg=="
}
```

A record whose signature does not verify is not verified. A record whose `public_key` differs from the domain's `p` has its identity claim rejected. Producers can sign with `sign_record()` in `scripts/validate.py`; [`examples/registered-us.signing-input.txt`](examples/registered-us.signing-input.txt) is a canonicalisation test vector.

## Validate a record

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/registered-us.json
python scripts/validate.py examples/registered-us.json --domain harbourbikes.example --dns-value 'v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p=bknJGPICOYXD4VJvtV+2rL8q+LjfgoPFJEDFvEB6iQo='
python scripts/validate.py examples/registered-us.json --domain harbourbikes.example --well-known examples/well-known-registered-us.json
python scripts/validate.py examples/well-known-registered-us.json
python scripts/validate.py examples/registered-us.json --p 'bknJGPICOYXD4VJvtV+2rL8q+LjfgoPFJEDFvEB6iQo='
python -m unittest discover -s tests -v
```

The validator always verifies the record signature. With `--dns-value`, `--well-known` or `--p` it also checks `public_key` against `p`; without them it reports the identity claim as unconfirmed. Passing the local checks establishes **record conformance only**. Passing the DNS checks additionally establishes a valid domain-to-record assertion; it is not an independent government-register confirmation.

With both `--dns-value` and `--well-known`, the validator applies the precedence rule (SPEC section 3.4.4): the DNS assertion is used, and a disagreeing file is reported as a warning.

## The proposed 1.1 `p` key

`p` is required. The validator rejects an assertion (or well-known file) without `p`, and always checks that `p` is a 44-character standard-base64 Ed25519 public key (32 bytes, one trailing `=`). Any other value fails, including an ABIZ 1.0 hexadecimal token and base64url. See SPEC section 3.3.7 for migrating existing values. The format check needs no extra package. To verify a separate detached signature over an agreed message, add `--p-message` and `--p-signature`. Signature checks use the `cryptography` package, which is in `requirements-dev.txt`:

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/registered-us.json \
  --domain harbourbikes.example \
  --dns-value "$(sed -n '/^v=abiz1/p' examples/dns-ed25519-p.txt)" \
  --p-message "abiz1.1 p-key test" \
  --p-signature "qyKerWm4IqgOEeKqK67muf7CDIoU9PxzGz2KCTjSgg/XBtg43YiQHo/QzX/avaSMTc/G0UxL5kV8uc3VA6OABg=="
```

A business record cannot carry retired keys. The schema reserves their shape only as the nested definition `$defs/retired_key`.

## Standards governance

Anyone may implement the specification without membership or a per-use standards fee. Proposed changes should be discussed publicly. The `_abiz` IANA request is not confirmed. The managing organisation is To.Co Technologies Limited (UK).
