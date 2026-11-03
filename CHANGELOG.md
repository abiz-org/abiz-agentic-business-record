# Changelog

## Unreleased — ABIZ 1.1 (proposed)

Two proposed changes: a relaxed DNS tag-list syntax, and a redefinition of the optional DNS `p` tag. The published specification remains ABIZ 1.0, and the wire tag remains `v=abiz1`. Both changes are backwards-compatible: every valid ABIZ 1.0 assertion and record stays valid, with the same meaning.

- Tag-list whitespace (section 3.1.1, with ABNF). Optional SP or HTAB is allowed around `;` and `=`, before the first tag and after the last, and one trailing `;` is allowed, as in DKIM (RFC 6376 section 3.2), DMARC (RFC 7489 section 6.4), MTA-STS (RFC 8461 section 3.1) and TLS-RPT (RFC 8460 section 3). Still invalid: whitespace inside a value, CR/LF or other whitespace, a repeated recognised tag, `V=ABIZ1` or any case change, `v=abiz1` not first, `;;`, and a tag without `=`. Unknown tags stay ignored, now including repeated ones. Producers should still publish the compact form, which strict 1.0 consumers require.
- The reference validator parses the new syntax and adds `is_abiz_assertion()` for selecting the `_abiz` record from the TXT RRset.

- `p`, when a producer opts in, is an Ed25519 public key: 32 bytes, standard base64, 44 characters, one trailing `=` (RFC 8463 and RFC 4648 section 4).
- Ordinary validation still accepts an opaque 1.0 `p` token. `--check-p-key` opts into the key check. Signature checks need the optional `cryptography` package.
- Schema description corrected to ABIZ 1.0. `p` stays DNS-only, so the JSON schema has no new property.
- Hosted mode is a supported way to deploy the key. A provider may generate it, publish `p`, and sign for the business. The private key remains the business's property and MUST be exportable.
- Retired keys are carried in the business record under the provisional property `retired-keys`, with a binding signature from the current key. DNS carries only the current `p`. Producers must not publish retired keys in DNS.

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
