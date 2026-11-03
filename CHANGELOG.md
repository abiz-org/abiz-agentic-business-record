# Changelog

## Unreleased — ABIZ 1.1 (proposed)

Proposed changes: a relaxed DNS tag-list syntax, a redefinition of the DNS `p` tag (now required), and defined business-key rules with `k` optional for everyone. The published specification remains ABIZ 1.0, and the wire tag remains `v=abiz1`. The whitespace change and optional `k` are backwards-compatible. The `p` and business-key changes are deliberately breaking: for any `p` value that is not a valid key, and for existing `k` and `business_key` values, which must be re-expressed.

- Tag-list whitespace (section 3.1.1, with ABNF). Optional SP or HTAB is allowed around `;` and `=`, before the first tag and after the last, and one trailing `;` is allowed, as in DKIM (RFC 6376 section 3.2), DMARC (RFC 7489 section 6.4), MTA-STS (RFC 8461 section 3.1) and TLS-RPT (RFC 8460 section 3). Still invalid: whitespace inside a value, CR/LF or other whitespace, a repeated recognised tag, `V=ABIZ1` or any case change, `v=abiz1` not first, `;;`, and a tag without `=`. Unknown tags stay ignored, now including repeated ones. Producers should still publish the compact form, which strict 1.0 consumers require.
- The reference validator parses the new syntax and adds `is_abiz_assertion()` for selecting the `_abiz` record from the TXT RRset.

- `p` is an Ed25519 key (made REQUIRED by the 2026-11-03 amendment below). It MUST be an Ed25519 public key: 32 bytes, standard base64, 44 characters, one trailing `=` (RFC 8463 and RFC 4648 section 4). Base64url, padded or unpadded, is rejected. Any other value makes the assertion invalid.
- **Migration (breaking).** All existing `p` values are upgraded by 1.1 and fail unless they are a valid key. ABIZ 1.0 hexadecimal handshake tokens, such as `p=ede69a675ead36c690cc8689e1d3e21d`, now fail. Producers must republish `p` as an Ed25519 public key or remove it. A record with no `p` is still valid.
- The reference validator checks `p` by default whenever it is present. The `--check-p-key` opt-in flag is removed. `--p-message` and `--p-signature` verify a detached signature and need the optional `cryptography` package.
- Schema description corrected to ABIZ 1.0. (Superseded by the second amendment below: the record now carries `public_key` and `signature`.)
- Hosted mode is a supported way to deploy the key. A provider may generate it, publish `p`, and sign for the business. The private key remains the business's property and MUST be exportable.
- Retired keys are not part of the business record. A top-level `retired_keys` property is rejected as an unknown property. The schema reserves the shape of one entry as the nested definition `$defs/retired_key` only. DNS carries only the current `p`. Rotation is replacing `p`; revocation is removing it.

- `k` is OPTIONAL for every business, registered or not (section 3.2; producer step 2 is now MAY). If `k` is present it MUST equal the record's `business_key`, compared case-insensitively, and the record MUST have a `business_key`. `business_key` and `registration_number` stay paired. Registration fields in the record no longer require `k` in DNS.
- Business-key grammar (section 4.2.1, with ABNF): `country "-" [ subdivision "-" ] reg-number`, at most 128 characters, split unambiguously on `-`. The country MUST be an assigned ISO 3166-1 alpha-2 code (`gb`, not `uk`). A subdivision is REQUIRED for the United States (state or `dc`), the United Arab Emirates (emirate) and Canadian provincial or territorial corporations. A federal Canadian corporation has none. Every other country MUST NOT have one (section 4.2.2, with a normative table and register citations for the US, Canada, UAE, Germany, Australia, Mexico, India, Brazil, Switzerland, China, Japan and the UK).
- Registration numbers are ASCII letters and digits only (section 4.2.3). Producers apply NFKC, remove whitespace, hyphens, dots and slashes, and uppercase, keeping leading zeros and prefixes. Consumers do not normalise. German keys carry the register court code (the EUID local part, for example `de-K1101RHRB12345`); Japanese keys use the 13-digit NTA Corporate Number.
- Case is not significant in country codes, subdivisions, registration numbers or business keys (section 4.2.4). Canonical form: lowercase country and subdivision, uppercase number. The schema now accepts `country` and `locations[].country` in either case.
- **Migration (breaking).** Existing `k` and `business_key` values must be re-expressed in the new form. The 1.0 example `us-OR123456` becomes `us-or-123456` with `registration_number` `123456`, and is rejected under 1.1 because a US key needs a state. Registration numbers containing spaces or punctuation must be normalised.
- The reference validator checks codes against a bundled list, `data/iso3166.json`, extracted from pycountry 26.2.16 (Debian iso-codes, LGPL-2.1) by `scripts/build_iso3166.py`. It adds `parse_business_key()`, `canonical_business_key()` and the producer helper `normalise_registration_number()`.

### Amendment, 2026-11-03

Further changes within ABIZ 1.1 (proposed). The wire tag remains `v=abiz1`, and the business-record schema and its `$id` (`https://abizrecord.org/schema/abiz-business-record-v1.schema.json`) are unchanged.

- **`p` is REQUIRED** (sections 3.2, 3.3.1). Every assertion MUST carry an Ed25519 public key in `p`, for registered and unregistered businesses alike. An assertion without `p` is invalid, as one without `h` is. **Migration (breaking):** assertions without `p`, valid under 1.0 and the earlier 1.1 text, now fail; removing a 1.0 hex token is no longer enough, and revoking a key while keeping the assertion means rotating it (sections 3.3.6, 3.3.7). The open point "whether `p` is required for any verified tier" is closed.
- **Well-known file** (new section 3.4): `https://<domain>/.well-known/abiz.json`, a JSON object with the same `v`, `h`, `p` and optional `k` as the TXT record, as an alternative to DNS. HTTPS only, status 200, no redirects, `application/json`, at most 65,536 octets, cached for at most 300 seconds. **DNS takes precedence**: a consumer queries DNS first; a DNS failure, two `v=abiz1` records or a malformed assertion is not replaced by the file; when both are valid and disagree, DNS is used and the file ignored, with a warning; the file is used only when there is no `v=abiz1` record. New schema `schemas/abiz-well-known-v1.schema.json` (`$id` `https://abizrecord.org/schema/abiz-well-known-v1.schema.json`) and examples `examples/well-known-*.json`.
- **`format` parameter** (new section 4.5): the record host MUST support `?format=html` (the default), `?format=markdown` and `?format=json`, with `text/html`, `text/markdown` and `application/json` responses. A recognised `format` wins over `Accept`; otherwise `Accept` negotiation applies, then HTML. `md` MAY be accepted as an alias. The JSON representation MUST be the business record itself. Consumers send `Accept: application/json` and SHOULD add `format=json`.
- **Bare record hosts; business units and divisions** (sections 2, 3.2, 8). The main record SHOULD use a bare hostname as `h` (for example `hartleysbakery.uk.to.co`). A path-based `h` (for example `harbour-bike-repair.or.us.to.co/events`) is for a unit or division, whose record's `identity_host` matches it exactly. New example `examples/unit-us.json`.
- **North Korea (`kp`) is not supported** (new section 4.2.7). A record, location or business key with country `kp` is invalid.
- Producer, consumer and conformance requirements (sections 5 to 7), security (section 9), IANA (section 10, `abiz.json` well-known suffix intended for registration, not yet requested) and references updated.
- The reference validator: rejects a missing `p`; adds `--well-known` (a local copy of the file), `well_known_tags()`, `validate_well_known()`, `resolve_sources()` (the precedence rules) and the reference host helper `select_representation()`; checks a well-known document passed on its own; rejects `kp`. Tests cover each change, and every DNS and well-known example in SPEC.md and README.md is checked.

### Second amendment, 2026-11-03: snake_case and signed records

Still ABIZ 1.1 (proposed). The wire tag remains `v=abiz1`; the DNS tags `v`, `h`, `k` and `p` and the well-known file members are unchanged; the business-record schema keeps its file name and `$id`.

- **snake_case member names (breaking).** Every business-record member is renamed: `record_version`, `business_name`, `identity_host`, `business_key`, `registration_number`, `mcp_server_url`, `contact_email`, `contact_phone`, `logo_url`, `last_updated`, `opening_hours` and `locations[].postal_code`, and inside `$defs/retired_key`: `public_key`, `valid_from`, `retired_at`, `binding_signature`. Hyphenated names are now unknown properties and are rejected. Example extension members use snake_case too (`"to.co": {"badge": …, "business_pass": …}`); extension namespace keys stay reverse-domain.
- **`public_key` REQUIRED** (section 4.6.1): the Ed25519 public key in the `p` encoding (standard base64, 44 characters). It MUST equal `p` from DNS or the well-known file; a consumer MUST reject the record's identity claim if it differs.
- **`signature` REQUIRED** (sections 4.6.2 to 4.6.4): an Ed25519 (PureEd25519, RFC 8032) signature, standard base64, 88 characters, over the UTF-8 bytes of the RFC 8785 (JCS) canonical serialisation of the whole record with the top-level `signature` member removed, verified with `public_key`. The record must be I-JSON (no duplicate members). A missing or invalid signature means the record is not verified. `last_updated` stays optional and is covered by the signature. New sections on key rotation (4.6.5), security considerations (4.6.6) and migration (4.6.7).
- **Record conformance** now requires a signature that verifies; the identity claim also requires `public_key` to equal `p`.
- **Reference validator.** Adds an RFC 8785 canonicaliser (`jcs_canonicalize()`, `signing_input()`), `sign_record()`, `verify_record_signature()` and `check_public_key_matches_p()`, rejects duplicate members, always verifies the record signature, and checks `public_key` against `p` from `--dns-value`, `--well-known` or the new `--p`. `cryptography` moves into `requirements-dev.txt`; `requirements-p-key.txt` remains for compatibility.
- **Examples.** All record examples are renamed and signed with new throwaway keys (the private keys were discarded); the example `p` values in DNS and well-known examples change to match. New test vector `examples/registered-us.signing-input.txt`.
- **Migration (breaking).** Every ABIZ 1.0 or earlier-1.1 record fails until it is republished with snake_case names, `public_key` and a valid `signature`.
- The schema is not yet republished at `https://abizrecord.org/schema/`.

## 1.0 — 2026-10-23

ABIZ 1.0 published specification, retaining the DNS wire tag `v=abiz1`.

- Normative JSON Schema (Draft 2020-12), with conformance tests and a reference offline validator.
- Separate record, publisher and consumer conformance checks.
- Support for both registered and unregistered businesses.
- MCP server endpoint optional; domain control is not legal identity verification.
- Provider-independent examples for country-based and `.biz.to.co` hosted record paths.
- Independent abizrecord.org website source, build and implementation guides.
- `_abiz` IANA request remains unconfirmed.

The original unratified 1.0 public-review text did not contain a conformance schema. That text is superseded by this full ABIZ 1.0 publication once released on the designated public source repository.
