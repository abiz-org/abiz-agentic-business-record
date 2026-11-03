# Changelog

## Unreleased — ABIZ 1.1 (proposed)

Two proposed changes: a relaxed DNS tag-list syntax, and a redefinition of the optional DNS `p` tag. The published specification remains ABIZ 1.0, and the wire tag remains `v=abiz1`. The whitespace change is backwards-compatible. The `p` change is a deliberate breaking change for any `p` value that is not a valid key.

- Tag-list whitespace (section 3.1.1, with ABNF). Optional SP or HTAB is allowed around `;` and `=`, before the first tag and after the last, and one trailing `;` is allowed, as in DKIM (RFC 6376 section 3.2), DMARC (RFC 7489 section 6.4), MTA-STS (RFC 8461 section 3.1) and TLS-RPT (RFC 8460 section 3). Still invalid: whitespace inside a value, CR/LF or other whitespace, a repeated recognised tag, `V=ABIZ1` or any case change, `v=abiz1` not first, `;;`, and a tag without `=`. Unknown tags stay ignored, now including repeated ones. Producers should still publish the compact form, which strict 1.0 consumers require.
- The reference validator parses the new syntax and adds `is_abiz_assertion()` for selecting the `_abiz` record from the TXT RRset.

- `p` stays optional. When present it MUST be an Ed25519 public key: 32 bytes, standard base64, 44 characters, one trailing `=` (RFC 8463 and RFC 4648 section 4). Base64url, padded or unpadded, is rejected. Any other value makes the assertion invalid.
- **Migration (breaking).** All existing `p` values are upgraded by 1.1 and fail unless they are a valid key. ABIZ 1.0 hexadecimal handshake tokens, such as `p=ede69a675ead36c690cc8689e1d3e21d`, now fail. Producers must republish `p` as an Ed25519 public key or remove it. A record with no `p` is still valid.
- The reference validator checks `p` by default whenever it is present. The `--check-p-key` opt-in flag is removed. `--p-message` and `--p-signature` verify a detached signature and need the optional `cryptography` package.
- Schema description corrected to ABIZ 1.0. `p` stays DNS-only, so the JSON schema has no new record property.
- Hosted mode is a supported way to deploy the key. A provider may generate it, publish `p`, and sign for the business. The private key remains the business's property and MUST be exportable.
- Retired keys are not part of the business record. A top-level `retired-keys` property is rejected as an unknown property. The schema reserves the shape of one entry as the nested definition `$defs/retired-key` only. DNS carries only the current `p`. Rotation is replacing `p`; revocation is removing it.

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
