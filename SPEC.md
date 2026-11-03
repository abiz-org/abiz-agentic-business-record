# ABIZ — Agentic Business Record Specification

**Published version:** ABIZ 1.0  
**DNS wire version:** `v=abiz1` (unchanged)  
**Date:** 2026-10-23  
**1.1 proposal:** 2026-10-31, revised 2026-11-03, amended 2026-11-03 three times (not the published version; see sections 3.1.1, 3.3, 3.4, 4, 4.2, 4.5, 4.6, 4.7 and 8)  
**Managing organisation:** To.Co Technologies Limited, United Kingdom  
**Planned official site:** `abizrecord.org`  
**Public source:** https://github.com/abiz-org/abiz-agentic-business-record  
**Normative schemas:** the published ABIZ 1.0 business record is [`schemas/abiz-business-record-v1.schema.json`](schemas/abiz-business-record-v1.schema.json) (`$id` `https://abizrecord.org/schema/abiz-business-record-v1.schema.json`). The proposed ABIZ 1.1 business record is [`schemas/abiz-business-record-v1.1.schema.json`](schemas/abiz-business-record-v1.1.schema.json) (`$id` `https://abizrecord.org/schema/abiz-business-record-v1.1.schema.json`). The well-known file, which is part of the 1.1 proposal and did not exist in 1.0, is [`schemas/abiz-well-known-v1.1.schema.json`](schemas/abiz-well-known-v1.1.schema.json) (`$id` `https://abizrecord.org/schema/abiz-well-known-v1.1.schema.json`). `record_version` and the DNS tag `v` stay `abiz1` in both revisions and do not select the schema.

This is the **ABIZ 1.0 published specification**. Publication does not imply IANA registration or endorsement. Implementers MUST NOT present domain control as proof of a registered business's legal identity, and MUST NOT claim guaranteed AI discovery, ranking or recommendation.

Sections 3.1.1, 3.3, 3.4, 4, 4.2, 4.5, 4.6, 4.7 and 8 are **proposed ABIZ 1.1** changes: a relaxed tag-list syntax that accepts optional whitespace; a REQUIRED Ed25519 key in the DNS `p` tag; snake_case member names throughout the business record; REQUIRED `public_key` and `signature` members that sign the business record with the `p` key (section 4.6); a well-known file, `https://<domain>/.well-known/abiz.json`, as an alternative to the DNS record; a `format` query parameter (`html`, `markdown`, `json`) at the record host; a defined business-key grammar with country, subdivision and registration-number rules, with `k` optional for every business; record hosts given as bare hostnames, with paths reserved for business units and divisions; no support for North Korea (`kp`); and structured location, contact, hours and listing facts (section 4.7). They are not part of the ABIZ 1.0 conformance baseline. The whitespace change, the well-known file, the `format` parameter and optional `k` are backwards-compatible for consumers. The `p`, business-key, snake_case and record-signature changes are deliberately not: an assertion without `p`, or with a non-key `p`, is invalid (section 3.3.7), existing keys must be re-expressed (section 4.2.5), and every business record must be republished with snake_case member names, `public_key` and a valid `signature` (section 4.6.7). The section 4.7 amendment is breaking too: `email` and `phone` replace `contact_email` and `contact_phone`, root `opening_hours` is replaced by structured hours in each location, and a location's address is nested (section 4.7.14). The wire version stays `v=abiz1`.

## 1. Scope and purpose

ABIZ provides a provider-independent method for locating a business's **public business record** from a domain it controls. Producers publish a versioned DNS TXT assertion at `_abiz.{domain}` pointing to a record served over HTTPS. Consumers discover that record, validate its structure using the **normative JSON Schema**, and perform cross-source consistency checks.

ABIZ is not a legal identity registry, endorsement scheme, payment system or requirement to use one provider. **An MCP server is optional**. Business records can be published by registered or unregistered businesses.

The key words MUST, MUST NOT, SHOULD and MAY have their RFC 2119 / RFC 8174 meanings.

## 2. Terms

- **Producer:** entity publishing an ABIZ pointer (a DNS assertion or a well-known file) at a domain it controls.
- **Consumer:** software reading and validating the pointer and published business record.
- **Business record:** JSON representation of public business facts conforming to the normative schema.
- **Record host:** the value of the `h=` tag: a DNS hostname, with an optional path only for a business unit or division (section 8), and no `https://` prefix. A business's main record SHOULD use a bare hostname, for example `hartleysbakery.uk.to.co`.
- **Well-known file:** the JSON document at `https://<domain>/.well-known/abiz.json` that carries the same tags as the DNS assertion (section 3.4).
- **Representation:** one of the HTML, Markdown and JSON forms the record host serves, selected by the `format` query parameter or by content negotiation (section 4.5).
- **Business key:** optional registration identifier in `country[-subdivision]-registration-number` form (section 4.2.1).
- **Domain check:** checks that a DNS assertion and fetched business document refer to each other; distinct from government registration checks.
- **Record conformance:** schema and local semantic checks pass.
- **Publisher conformance:** record conformance plus the DNS / document requirements in this specification.
- **Consumer conformance:** implements the checks and rejects invalid assertions.

## 3. DNS assertion

### 3.1 Owner, RRset and version

An ABIZ DNS assertion is a TXT record at `_abiz.<domain>`. The first tag MUST be `v=abiz1` (section 3.1.1). There MUST be exactly one matching `v=abiz1` TXT record at that owner name. Zero means no ABIZ assertion; two or more means an invalid assertion. A TXT record whose first tag is not `v=abiz1` (for example an SPF record, or `V=ABIZ1`) is not an ABIZ assertion and is not counted.

A TXT record made of several character-strings (RFC 1035) is read as their concatenation, with nothing added between them, as for SPF (RFC 7208 section 3.3) and DKIM (RFC 6376 section 3.6.2.2).

The TTL SHOULD be 300 seconds. Section 3.4 defines a well-known file that a producer MAY publish instead of, or as well as, this TXT record. Tag names and values are case-sensitive, except that `k` is compared case-insensitively (section 4.2.4). A consumer MUST ignore unknown additional tags and MUST reject an assertion in which a recognised tag (`v`, `h`, `k`, `p`) appears more than once.

#### 3.1.1 Tag-list syntax (ABIZ 1.1, proposed)

ABIZ 1.0 allowed no whitespace anywhere in the assertion. ABIZ 1.1 proposes the tag-list syntax used by other DNS TXT policy records: optional whitespace around `;` and `=`, leading and trailing whitespace, and one trailing `;`. This follows DKIM (RFC 6376 section 3.2, `tag-list`), DMARC (RFC 7489 section 6.4, `dmarc-sep = *WSP %x3b *WSP`, with a final optional separator), MTA-STS (RFC 8461 section 3.1, `sts-field-delim = *WSP ";" *WSP`) and SMTP TLS Reporting (RFC 8460 section 3, `field-delim = *WSP ";" *WSP`). SPF (RFC 7208 section 4.6.1 and section 12) likewise separates terms with one or more spaces and allows trailing spaces. Every value that was valid under ABIZ 1.0 parses under this syntax, with the same tags. (Section 3.3.7 separately makes an assertion without `p`, or with a non-key `p`, invalid.)

The assertion, after character-string assembly, MUST match `abiz-record` (ABNF, RFC 5234; `%s` is case-sensitive, RFC 7405):

```abnf
abiz-record  = *WSP abiz-version *( abiz-sep abiz-tag ) [ *WSP ";" ] *WSP
abiz-version = %s"v" *WSP "=" *WSP %s"abiz1"
abiz-sep     = *WSP ";" *WSP
abiz-tag     = tag-name *WSP "=" *WSP tag-value
tag-name     = 1*( %x21-3A / %x3C / %x3E-7E / %x80-FF ) ; no whitespace, ";" or "="
tag-value    = 1*( %x21-3A / %x3C-7E / %x80-FF )        ; no whitespace or ";"
WSP          = SP / HTAB
```

Rules that go with the grammar:

- Only SP and HTAB are whitespace between tokens. CR, LF, other control characters and Unicode spaces (such as U+00A0) MUST NOT appear anywhere in the assertion.
- A tag value MUST NOT contain whitespace. Whitespace around a value is not part of it. `tag-value` may contain `=`; a consumer splits each tag on its first `=` only.
- `v=abiz1` MUST be the first tag. `abiz1` and every tag name are case-sensitive: `V=abiz1` and `v=ABIZ1` are not ABIZ assertions, and `H=` is an unknown tag, not `h=`. Recognised tag names are lowercase.
- At most one trailing `;` is allowed. An empty tag (`;;`), a tag without `=`, and a tag with an empty name or value are invalid.
- A repeated recognised tag makes the assertion invalid. Unknown tags are ignored, including repeated ones.

Producers SHOULD publish the compact form with no optional whitespace, for example `v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p=6C4z0vRESsebqJiCfZmx9GkE2YSrIRV0cLgVgz24cwk=`. A strict ABIZ 1.0 consumer rejects any whitespace, so the compact form is the one every consumer accepts. Consumers that claim ABIZ 1.1 MUST accept the full syntax above.

### 3.2 Tags

| Tag | Required | Meaning |
| --- | --- | --- |
| `v=abiz1` | MUST | Wire protocol family; always first |
| `h=<record-host>` | MUST | HTTPS hostname of the public business record, without URL scheme. A bare hostname SHOULD be used; a path is for a business unit or division only (section 8). No query, fragment, port or user information |
| `k=<business-key>` | MAY | Optional for every business, registered or not. When present, MUST follow section 4.2.1 and MUST equal the record's `business_key`, compared case-insensitively (section 4.2.4). Registration fields in the record do not require `k` |
| `p=<public-key>` | MUST | REQUIRED in ABIZ 1.1 (proposed). MUST be an Ed25519 public key in standard base64, 44 characters (section 3.3.2). An assertion without `p`, or with any other value, is invalid. ABIZ 1.0 made `p` optional and allowed an opaque provider token. Not a password and not proof of legal identity |

`h` MAY refer to a record hosted by an independent service. A producer need not own the host serving the record; it MUST control the queried DNS domain and have permission for the published record.

**Example — registered business (US):**

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p=6C4z0vRESsebqJiCfZmx9GkE2YSrIRV0cLgVgz24cwk="
```

**Example — unregistered business (US):**

```dns
_abiz.marketstand.example. 300 IN TXT "v=abiz1;h=market-stand-repairs-portland.biz.to.co;p=zc6S6bKXaZXO7NCI+fjtgMWLdbdEeavjVvydQsoQCJ0="
```

Both are illustrative, invented businesses, and each `p` is a throwaway Ed25519 public key whose private key is not in the repository. These entries demonstrate alternatives on **different DNS owners**. A business MUST NOT publish both as independent matching assertions at one owner name.

These hostnames are examples of to.co's country-based registered-company hostname and town-based `.biz.to.co` hostname. ABIZ does not require either naming scheme.

**Example — the same registered business, without `k`:**

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;h=harbour-bike-repair.or.us.to.co;p=6C4z0vRESsebqJiCfZmx9GkE2YSrIRV0cLgVgz24cwk="
```

`k` is optional; `h` and `p` are not. See `examples/dns-ed25519-p.txt` and section 3.3. An assertion such as `v=abiz1;h=harbour-bike-repair.or.us.to.co`, valid under ABIZ 1.0, is invalid under ABIZ 1.1 because it has no `p`.

### 3.3 The `p` tag (ABIZ 1.1, proposed)

This section is a proposal. It changes the meaning of `p` on purpose: from ABIZ 1.1, `p` is REQUIRED and MUST be a valid Ed25519 public key. An assertion without `p`, or with any other value, is invalid. Section 3.3.7 covers migrating existing values.

#### 3.3.1 Role

In ABIZ 1.0, `p` was optional and provider-specific: a non-empty token that was not checked as a key. Deployments used it for a one-time domain-control handshake, including a 32-character hexadecimal token.

ABIZ 1.1 makes that tag a persistent signing identity. The business, or a provider acting for it, generates an Ed25519 keypair and publishes the public key in `p`. The private key remains the business's property (section 3.3.4). A later signature can be checked against the published key. The one-time token is replaced by a key the business can keep using.

`p` is REQUIRED, for registered and unregistered businesses alike. An assertion without `p` is invalid, exactly as one without `h`. An assertion with `p` is valid only when `p` is a key that matches section 3.3.2. A consumer always has a key to check a signature against, and no consumer has to handle a second kind of assertion without a signer.

The business record repeats the key as `public_key` and is signed with the matching private key (section 4.6), so a consumer can check that the record it fetched from `h` was published by the holder of the key the domain names.

Publishing the key shows that the controller of the domain put that public key in DNS. It does not authenticate the TXT record. It does not prove that a registered business owns the domain. Section 9 still applies: DNS assertions are public and unauthenticated by default, and DNS control alone does not prove business ownership. Producers and consumers SHOULD still use DNSSEC where they can. DNSSEC authenticates the DNS data. The key names a signer the domain controller published.

The authoritative copy of the key is the pointer: the DNS assertion, or the well-known file (section 3.4), which repeats the same value. The business record carries the current key as `public_key`, which MUST equal `p` (section 4.6.4). It does not carry any previous key.

#### 3.3.2 Key encoding

`p` MUST be the standard base64 encoding (RFC 4648, section 4) of the raw 32-byte Ed25519 public key (RFC 8032). The alphabet is `A–Z`, `a–z`, `0–9`, `+` and `/`, with `=` padding. This is the DKIM Ed25519 `p=` encoding (RFC 8463, using the base64 `p=` syntax in RFC 6376). Base64url (RFC 4648, section 5), padded or unpadded, MUST be rejected.

Standard base64 of 32 bytes is 44 characters, including one trailing `=`. Unpadded base64url of the same key is 43 characters. Padded base64url is also 44 characters, but it uses `-` and `_` in place of `+` and `/`. ABIZ requires the RFC 8463 form: 44 characters, standard alphabet, one trailing `=`. `+`, `/` and `=` are ordinary octets in a TXT character-string, and `=` cannot be confused with the tag separator because a consumer splits each tag on its first `=` only.

A conforming `p` value MUST:

- be exactly 44 ASCII characters;
- use only the standard base64 alphabet;
- end with exactly one `=` and no other `=` character;
- decode to exactly 32 bytes;
- be canonical: encoding those 32 bytes again with standard base64 MUST reproduce the value;
- contain no whitespace. DKIM allows folding whitespace inside base64. ABIZ does not, because an ABIZ tag value MUST NOT contain whitespace (section 3.1.1). Whitespace around the value, before `;` or after `=`, is not part of it.

The 44 characters MUST sit in a single DNS TXT character-string (RFC 1035). Producers MUST NOT split `p` across adjacent character-strings. The value fits well inside the 255-octet character-string limit.

A 31-byte string of 44 characters ends in `==`. A 33-byte string of 44 characters has no padding. Both MUST be rejected, as MUST a 43-character value without padding.

#### 3.3.3 Generating a keypair

The business, or a provider acting for it, MUST generate a fresh Ed25519 keypair when it creates a signing identity. It MUST publish only the public key. The private key MUST remain secret. It MUST NOT appear in DNS, in the business record, or in a public repository. Who holds the private key is set out in section 3.3.4.

Any Ed25519 implementation is acceptable. The following illustrates the public-key encoding with Python and the `cryptography` library. The printed line is the `p` value.

```python
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
print(base64.b64encode(public_key).decode("ascii"))
```

#### 3.3.4 Key custody and hosted mode

The private key is the business's property at all times, whoever generates or stores it.

Two deployment modes are supported:

- **Self-custody.** The business generates the keypair and holds the private key.
- **Hosted mode.** An ABIZ provider generates the keypair, derives the public key, and publishes it in the `_abiz` TXT record (for example through Domain Connect). The provider serves the business record. It MAY hold the private key and sign on the business's behalf.

Hosted mode is a supported deployment option of this specification. The business remains the owner of the key in both modes.

In hosted mode the provider:

- MUST let the business export its private key at any time, in a standard format such as PKCS#8;
- MUST authenticate the business before an export;
- SHOULD notify the business of each export;
- MUST NOT claim exclusive possession of the key after an export;
- MUST honour a request to delete the provider's copy.

After that deletion, the business can move to another provider or to self-custody. It can keep verifying and using material signed with that key.

A provider MUST NOT make the business's signing key non-exportable. A non-exportable key, including a non-exportable HSM key, MUST NOT be the business's signing key. An HSM MAY wrap the key.

When the business changes provider, it MAY publish the same `p` through the new provider, or it MAY rotate to a new key (section 3.3.6).

#### 3.3.5 Consumer verification

**Discovery.** A consumer that claims ABIZ 1.1 MUST reject an assertion without `p`, and MUST check `p` against section 3.3.2. If `p` does not match, the assertion is invalid, exactly as for a malformed `h`. This includes opaque ABIZ 1.0 tokens such as a 32-character hexadecimal string, and base64url keys. A duplicate `p` tag MUST be rejected, as for any other recognised tag. A consumer MAY report a missing `p` separately from a malformed one, so a business can tell them apart. The format check needs only base64 decoding, with no cryptographic library.

**Valid key.** If `p` matches section 3.3.2, the consumer MAY use those 32 bytes as the Ed25519 public key for that domain.

**Signatures.** A detached signature is the raw 64-byte Ed25519 signature (RFC 8032, PureEd25519, with no pre-hash), encoded in the same standard base64 (88 characters, including the final `==`). The message is the raw octets the producer and consumer agreed. ABIZ does not take DKIM's header canonicalisation or SHA-256 body hash from RFC 8463. Only the public-key encoding is shared with that RFC. Verification succeeds only when RFC 8032 verification succeeds for that key, message and signature.

ABIZ 1.1 defines one such message: the business-record signature of section 4.6, whose message is the RFC 8785 canonical form of the record without its `signature` member. Any other detached signature is meaningful only for a message both sides already agreed. The reference validator can check such a pair with `--p-message` (UTF-8 text) and `--p-signature` (the 88-character standard base64 signature). Signature verification needs the `cryptography` package (in `requirements-dev.txt`); without it, the `p` format check still runs, and every signature check, including the record signature, fails with an error that names the missing dependency.

**Wire version.** This proposal does not change `v=abiz1`. A strict ABIZ 1.0 consumer that treats `p` as opaque still accepts a 1.1 key, because a key is a valid 1.0 token, so every valid 1.1 assertion is a valid 1.0 assertion. The reverse does not hold: a 1.1 consumer rejects a missing or non-key `p` (section 3.3.7).

#### 3.3.6 Rotation and revocation

The current signing key is the `p` tag in DNS (or the well-known file), repeated as the record's `public_key`. Producers MUST NOT publish previous keys in DNS, and the business record does not carry them. `_abiz` stays limited to the current key.

**Rotation.** The producer generates a new keypair and publishes the new public key as DNS `p`. The TTL SHOULD remain 300 seconds (section 3.1). At the same time it re-signs the business record with the new private key, with `public_key` set to the new key (section 4.6.5). Once the TXT TTL has passed, consumers MUST NOT keep treating the replaced `p` as the current key, and a record signed with the replaced key no longer verifies against `p`.

**Revocation.** Because `p` is required, a business that withdraws a key while keeping its ABIZ assertion MUST rotate to a new key. Removing `p` alone makes the assertion invalid. Removing the whole assertion (and any well-known file, section 3.4) withdraws the key and the ABIZ pointer together once the TXT TTL, or the file's cache lifetime, has passed.

ABIZ 1.1 does not define a published list of retired keys. The schema reserves the shape of a retired-key entry as a nested definition, `$defs/retired_key` (section 4). It is not a record property, and a business record that contains `retired_keys` or any other unknown top-level property MUST be rejected. A later revision, or another document that references the definition, may use that shape.

#### 3.3.7 Migration of existing `p` values

All existing assertions are upgraded by this revision. Under ABIZ 1.1 an assertion fails validation, as a whole, when:

- it has no `p` tag (valid under ABIZ 1.0, where `p` was optional); or
- its `p` value is not a valid key under section 3.3.2, such as a 32-character hexadecimal handshake token.

Producers MUST publish `p` as an Ed25519 public key (section 3.3.3). Removing a non-key `p` is no longer enough. Producers SHOULD do this before consumers move to 1.1: an assertion with a valid `p` is valid under both ABIZ 1.0 and 1.1.

This is a deliberate breaking change for assertions without a key. The others are the business-key rules of section 4.2 (section 4.2.5), dropping support for `kp` (section 4.2.7), and the snake_case member names and required record signature of the business record (section 4.6.7). Every other ABIZ 1.0 assertion stays valid under ABIZ 1.1, with the same meaning. The whitespace relaxation of section 3.1.1, the well-known file of section 3.4 and the `format` parameter of section 4.5 only add accepted forms.

#### 3.3.8 Unresolved points

This proposal does not decide the following. They are recorded so implementers do not treat silence as a decision:

- whether, and where, a later revision publishes retired keys using `$defs/retired_key`, and how long entries would be kept;

Decided in this revision: `p` uses standard base64 (RFC 4648 section 4, RFC 8463), not base64url; from ABIZ 1.1 `p` is REQUIRED for every assertion, registered or not; a missing or non-key `p` is invalid; the business record carries a copy of the key as `public_key`; and a record signature covers the RFC 8785 canonical form of the record without `signature` (section 4.6).

### 3.4 Well-known file (ABIZ 1.1, proposed)

A producer that cannot publish a DNS TXT record, or prefers not to, MAY publish the same assertion as a JSON file on the web server of the domain. A producer MAY also publish both.

#### 3.4.1 Location

The file is at:

```text
https://<domain>/.well-known/abiz.json
```

`<domain>` is exactly the name the consumer would query as `_abiz.<domain>`: the same host, with no `www.` added or removed. The scheme MUST be `https` on the default port 443. The file name is `abiz.json`, with no underscore. The path follows RFC 8615 (well-known URIs). Registration of the `abiz.json` well-known URI suffix has not been requested; publication does not claim it.

#### 3.4.2 Content

The file MUST be a UTF-8 JSON object (RFC 8259) with no byte order mark. It carries the DNS tags as members, each a JSON string:

| Member | Required | Value |
| --- | --- | --- |
| `v` | MUST | `abiz1` |
| `h` | MUST | The record host, with the rules of the `h` tag (section 3.2) |
| `p` | MUST | The Ed25519 public key, with the rules of section 3.3.2 |
| `k` | MAY | The business key, with the rules of section 4.2 |

Each value MUST be exactly what the producer would publish as the corresponding tag value, and MUST satisfy `tag-value` (section 3.1.1): no whitespace, no `;`, not empty. A member whose value is not a string, or does not satisfy its tag rules, makes the file invalid. Consumers MUST ignore unknown members, as they ignore unknown tags. The file MUST validate against [`schemas/abiz-well-known-v1.1.schema.json`](schemas/abiz-well-known-v1.1.schema.json) (JSON Schema Draft 2020-12, `$id` `https://abizrecord.org/schema/abiz-well-known-v1.1.schema.json`); the tag rules of sections 3.1.1 to 3.3 and 4.2 are checked in addition, as for DNS.

The file is a pointer, not the business record. It MUST NOT contain business-record properties in place of `h`; a consumer still fetches the record from `https://<h>` (section 4).

Example, matching the registered DNS example in section 3.2 (`examples/well-known-registered-us.json`):

```json
{
  "v": "abiz1",
  "k": "us-or-123456",
  "h": "harbour-bike-repair.or.us.to.co",
  "p": "6C4z0vRESsebqJiCfZmx9GkE2YSrIRV0cLgVgz24cwk="
}
```

#### 3.4.3 Serving and fetching

A producer MUST serve the file:

- over HTTPS with a valid certificate for `<domain>`, at status 200, without a redirect;
- with the media type `application/json` (a `charset=utf-8` parameter is allowed);
- at no more than 65,536 octets;
- SHOULD with `Cache-Control: max-age=300`, matching the TXT TTL of section 3.1.

A consumer that fetches the file MUST apply the safe-fetch rules of section 6 (TLS verification, no private, loopback or link-local addresses, time and size limits). In addition it MUST NOT follow redirects, MUST reject a status other than 200, a media type other than `application/json`, or a body larger than 65,536 octets, and MUST parse the body as JSON without executing anything. A consumer MAY cache the file for its HTTP freshness lifetime (RFC 9111), but for no more than 300 seconds.

#### 3.4.4 Discovery and precedence

The DNS assertion takes precedence. A consumer:

1. MUST query TXT at `_abiz.<domain>` first (section 6).
2. If the query fails (for example SERVFAIL or a timeout), MUST report the result as unavailable and MUST NOT use the well-known file in its place.
3. If the RRset holds two or more `v=abiz1` records, MUST treat the result as invalid (section 3.1) and MUST NOT use the well-known file.
4. If it holds exactly one `v=abiz1` record, MUST use that assertion. If the assertion is malformed, the result is invalid, and the well-known file MUST NOT be used in its place. The consumer MAY also fetch the file. If the file is valid and disagrees with the DNS assertion in `h`, `k` (compared case-insensitively) or `p`, the consumer MUST use the DNS assertion, MUST ignore the file, and SHOULD report the disagreement as a warning. An invalid file next to a valid DNS assertion is likewise ignored and SHOULD be reported.
5. If there is no `v=abiz1` record (NXDOMAIN, no data, or only other TXT records), SHOULD fetch the well-known file. If the file is valid, the consumer MUST treat its members exactly as the tags of a DNS assertion. If it is missing or invalid, there is no ABIZ assertion.

A consumer MUST record which source it used (DNS or well-known file) and SHOULD show it. A producer that publishes both MUST keep them identical, and SHOULD update the TXT record first when it changes either.

#### 3.4.5 What the file proves

The well-known file shows control of the HTTPS origin at `<domain>`, which is not the same as control of its DNS zone. A party that controls the web server but not the zone, such as a hosting provider, can publish the file. This is why DNS wins when both exist. The file does not prove legal identity, and section 9 applies to it as to DNS. A consumer MAY treat a DNS-sourced assertion as stronger evidence of domain control than a file-sourced one.

## 4. Published business record and normative schema

The `h` target is the URL `https://<h>`. A consumer fetches the business record from it with `?format=json` (section 4.5) and the header `Accept: application/json`. The JSON representation MUST be a JSON object that validates against the schema for the revision being claimed, in **JSON Schema Draft 2020-12**. A published ABIZ 1.0 record validates against [`schemas/abiz-business-record-v1.schema.json`](schemas/abiz-business-record-v1.schema.json) (`$id` [`https://abizrecord.org/schema/abiz-business-record-v1.schema.json`](https://abizrecord.org/schema/abiz-business-record-v1.schema.json)). A proposed ABIZ 1.1 record validates against [`schemas/abiz-business-record-v1.1.schema.json`](schemas/abiz-business-record-v1.1.schema.json) (`$id` [`https://abizrecord.org/schema/abiz-business-record-v1.1.schema.json`](https://abizrecord.org/schema/abiz-business-record-v1.1.schema.json)). `record_version` is `abiz1` in both, and `v=abiz1` is the same wire tag. Neither value selects the schema. The reference validator selects one with `--revision` (`1.0` or `1.1`); when that flag is omitted it reads the nearest `REVISION` file and otherwise uses `1.1`. An unsupported revision is not an invalid signature. A record that fails only because it belongs to the other revision is a schema mismatch, not an invalid signature. Record conformance is a REQUIRED step for ABIZ conformance; a document that merely parses as JSON does not qualify.

The authoritative current key is `p` in the DNS assertion or the well-known file (section 3.4). The record repeats it as `public_key` and carries a `signature` made with the matching private key (section 4.6). The encoding is normative in section 3.3.2: standard base64 of the raw 32-byte Ed25519 public key, the same `p=` encoding DKIM specifies for Ed25519 in RFC 8463 (RFC 4648 section 4, with padding).

ABIZ 1.1 (proposed) renames every record member to snake_case (`record_version`, `business_name`, `identity_host`, `business_key`, `registration_number`, `mcp_server_url`, `logo_url`, `last_updated`) and adds two REQUIRED members, `public_key` and `signature` (section 4.6). The section 4.7 amendment then renames `contact_email` and `contact_phone` to `email` and `phone`, removes root `opening_hours`, nests a location's address and adds the members listed in section 4.3. Hyphenated member names are unknown top-level properties and are rejected. The proposed 1.1 business-record schema has its own file and `$id`, `schemas/abiz-business-record-v1.1.schema.json`. The published 1.0 schema stays at `schemas/abiz-business-record-v1.schema.json` with its original `$id`. The 1.1 schema's `$defs` holds the shared definitions of section 4.7 (such as `address`, `opening_hours` and `media_item`) and one more nested definition, `retired_key`, that reserves the shape of a retired Ed25519 key entry (section 3.3.6). No record property refers to it, so a business record cannot carry it.

### 4.1 Required properties

- `record_version` = `abiz1`
- `business_name`: nonempty public name
- `country`: assigned ISO 3166-1 alpha-2 country code, case-insensitive, canonically lowercase (section 4.2.4); not `kp` (section 4.2.7)
- `identity_host`: the record host, matching `h` exactly (a bare hostname, or a hostname and path for a unit, section 8)
- `domains`: array of business-controlled domain names this record claims
- `public_key`: the Ed25519 public key, equal to `p` (section 4.6.1)
- `signature`: the Ed25519 signature over the record (section 4.6)

### 4.2 Registration and MCP

`business_key` and `registration_number` are OPTIONAL, for registered and unregistered businesses alike. If either is present, both MUST be present. The country part of `business_key` MUST equal the record's `country`, and its registration-number part MUST equal `registration_number`, both compared case-insensitively. Including these fields in the record does not require `k` in DNS. If the DNS assertion contains `k`, `k` MUST equal `business_key` (section 4.2.4).

#### 4.2.1 Business key grammar (ABIZ 1.1, proposed)

The business key, used as DNS `k` and record `business_key`, has this ABNF (RFC 5234; quoted strings are case-insensitive, and `ALPHA` covers both cases):

```abnf
business-key = country "-" [ subdivision "-" ] reg-number
country      = 2ALPHA              ; assigned ISO 3166-1 alpha-2 code (section 4.2.2)
subdivision  = 1*3( ALPHA / DIGIT ) ; assigned ISO 3166-2 code of that country, without its "CC-" prefix
reg-number   = 1*( ALPHA / DIGIT )  ; normalised registration number (section 4.2.3)
```

The whole key MUST NOT exceed 128 characters. `reg-number` never contains `-`, so a key splits on `-` into exactly two parts (country, number) or three parts (country, subdivision, number). Any other number of parts is invalid. The grammar is unambiguous without the country table.

- `country` MUST be an assigned ISO 3166-1 alpha-2 code. Reserved and user-assigned codes are invalid: `uk` and `eu` are not assigned, so the United Kingdom is `gb`; `xk` is user-assigned. `kp` is assigned but not supported (section 4.2.7).
- `subdivision` MUST be present when section 4.2.2 requires it, MUST be an assigned ISO 3166-2 code of that country from that table when present, and MUST NOT be present for any country that section 4.2.2 does not list as using one. One business therefore has exactly one business key.
- The reference validator checks codes against `data/iso3166.json`, extracted from pycountry 26.2.16 (Debian iso-codes data, LGPL-2.1; see `data/README.md`). A later ISO 3166 change takes effect in the validator when that file is regenerated.

#### 4.2.2 Countries whose key includes a subdivision

The key names the register where the business was formed (its home jurisdiction), not a place where it is registered as a foreign or extra-provincial entity. A subdivision is used only where the register itself is subdivision-level and no national number identifies the business uniquely.

| Country | Subdivision in key | Register | `reg-number` | Example key |
| --- | --- | --- | --- | --- |
| United States (`us`) | REQUIRED: the state of formation, or `dc`. The 50 states and `us-dc` only | The state Secretary of State or equivalent business-entity filing office, for example the [Oregon Secretary of State, Corporation Division](https://sos.oregon.gov/business/Pages/default.aspx) or the [Delaware Division of Corporations](https://corp.delaware.gov/) | That office's entity or file number | `us-or-123456`, `us-de-7654321` |
| Canada (`ca`) | REQUIRED for a provincial or territorial corporation (13 codes, `ca-ab` … `ca-yt`). ABSENT for a federal corporation | Provincial and territorial registries, for example the [Ontario Business Registry](https://www.ontario.ca/page/ontario-business-registry). Federal corporations (Canada Business Corporations Act): [Corporations Canada](https://ised-isde.canada.ca/site/corporations-canada/en) | Provincial: that registry's number (Ontario Corporation Number, BC incorporation number such as `BC0578072`, Alberta Corporate Access Number, Quebec NEQ). Federal: the Corporations Canada corporation number including its final check digit. Not the CRA Business Number | `ca-on-1001216372`, `ca-bc-BC0578072`, federal `ca-12345678` |
| United Arab Emirates (`ae`) | REQUIRED: the emirate of the licensing authority (7 codes, `ae-az` … `ae-uq`) | Mainland: the emirate's economic department (listed by the [National Economic Register](https://u.ae/en/information-and-services/business/important-digital-services/national-economic-register/)). Free zones: each free-zone authority keeps its own register | Mainland: the licence number. Free zone: the authority's official abbreviation followed by its licence or registration number, because free-zone numbers are not unique against mainland numbers in the same emirate | `ae-du-1234567`, `ae-du-DMCC123456`, `ae-az-ADGM000123` |

US territories that have their own ISO 3166-1 code (Puerto Rico `pr`, Guam `gu`, US Virgin Islands `vi`, American Samoa `as`, Northern Mariana Islands `mp`) use that country code with no subdivision, for example `pr-123456`. `us-pr` and the other outlying-area codes MUST NOT be used.

Every other country uses no subdivision. Its `reg-number` is the number from the national company register. For the following countries, which are sometimes assumed to be subdivision-level, the number to use is:

| Country | Why no subdivision | `reg-number` | Example key |
| --- | --- | --- | --- |
| Germany (`de`) | The Handelsregister is kept by local register courts (Amtsgerichte), not by states, and a number such as HRB 12345 is unique only within one court and register type. A state code would not make it unique | The register court's XJustiz code ([code list Registergerichte](https://www.xrepository.de/details/urn:xoev-de:xunternehmen:codeliste:registergerichte)), then the register type (`HRA`, `HRB`, `GNR`, `PR`, `VR`, `GSR`), then the number and any court suffix. This is the local part of the European Unique Identifier (EUID, [Commission Implementing Regulation (EU) 2021/1042](https://eur-lex.europa.eu/eli/reg_impl/2021/1042/oj)) with the `.` removed: EUID `DEK1101R.HRB12345` gives `K1101RHRB12345` | `de-K1101RHRB12345` |
| Australia (`au`) | [ASIC](https://asic.gov.au/for-business/registering-a-company/) keeps one national register | The 9-digit ACN. An entity with no ACN may use its 11-digit ABN | `au-123456789` |
| Mexico (`mx`) | The RFC is a national identifier issued by the [SAT](https://www.sat.gob.mx/) | The 12-character RFC of the legal person. An RFC containing `Ñ` or `&` cannot be expressed; that business omits the key | `mx-ABC010101AB1` |
| India (`in`) | The [Ministry of Corporate Affairs](https://www.mca.gov.in/) keeps one national register | The 21-character CIN, or the LLPIN without its hyphen | `in-U72200MH2009PLC123456` |
| Brazil (`br`) | State Juntas Comerciais register companies, but the CNPJ from the [Receita Federal](https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/cnpj) is national and unique | The 14-character CNPJ without punctuation. The [alphanumeric CNPJ](https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/acoes-e-programas/programas-e-atividades/cnpj-alfanumerico) already fits the grammar | `br-12345678000195` |
| Switzerland (`ch`) | Commercial registers are cantonal, but every entity has a national UID (searchable through [Zefix](https://www.zefix.admin.ch/)) | The UID without punctuation | `ch-CHE123456789` |
| China (`cn`) | The Unified Social Credit Code (GB 32100-2015) is national | The 18-character code | `cn-91110000123456789X` |
| Japan (`jp`) | The [National Tax Agency](https://www.houjin-bangou.nta.go.jp/en/) assigns every corporation a national 13-digit Corporate Number (法人番号). No prefecture is needed | The 13-digit Corporate Number, after NFKC (section 4.2.3). Not the Legal Affairs Bureau register number, and not a number written with kanji | `jp-1234567890123` |
| United Kingdom (`gb`) | [Companies House](https://www.gov.uk/government/organisations/companies-house) keeps one register for England and Wales, Scotland and Northern Ireland | The 8-character company number, with its prefix and leading zeros | `gb-01234567`, `gb-SC123456` |

A country with only subdivision-level registers that is not in the first table cannot yet carry a business key. Its businesses omit `k` and the registration fields until a revision adds it.

#### 4.2.3 Registration number

ABIZ cannot check a registration number against each register's format. It defines only the character set and a normalisation.

`registration_number`, and the `reg-number` part of the key, MUST be one or more ASCII letters and digits (`A–Z`, `a–z`, `0–9`). Spaces and all other characters are invalid. A consumer MUST NOT normalise a received value; it MUST reject one that is not ASCII alphanumeric.

A producer derives the value from the number as the register issues it:

1. apply Unicode NFKC normalisation, which turns full-width digits and letters (`０-９`, `Ａ-Ｚ`) into ASCII;
2. remove whitespace, `-`, `.`, `/`, and the hyphen and dash characters U+2010 to U+2015 and U+2212;
3. convert ASCII letters to uppercase (the canonical form);
4. check that the result is one or more ASCII letters and digits. If it is not, for example because it still contains kanji or `&`, the business cannot publish a business key.

Leading zeros and letter prefixes are part of the number and MUST be kept: `01234567` and `1234567` are different numbers, and `SC123456` keeps `SC`. Examples: `HRB 12345` at Hamburg becomes `K1101RHRB12345`; `１２３４５６７８９０１２３` becomes `1234567890123`; `CHE-123.456.789` becomes `CHE123456789`; `12.345.678/0001-95` becomes `12345678000195`; a Corporations Canada number shown as `1234567-8` becomes `12345678`.

#### 4.2.4 Case and comparison

Case is not significant anywhere in a business key, nor in the record's `country`. The ISO 3166 codes of section 4.7 (`address.country.code`, `address.region.code`, service-area codes and tax `jurisdiction`) are written in uppercase, as ISO 3166 writes them, and the schema requires that; a consumer compares them with `country` and `business_key` case-insensitively. Consumers MUST compare country codes, subdivision codes, registration numbers and whole business keys case-insensitively (ASCII case folding). `US-OR-123456`, `us-or-123456` and `us-OR-123456` are the same key.

Producers SHOULD publish the canonical form: country and subdivision in lowercase, registration number in uppercase, for example `us-or-123456`, `ca-bc-BC0578072`, `de-K1101RHRB12345`. Record `country` SHOULD also be lowercase.

#### 4.2.5 Migration of existing keys

This is a breaking change for keys. ABIZ 1.0 allowed `.`, `_` and `-` inside the number and had no subdivision rule, so some 1.0 keys are invalid or ambiguous under 1.1. Producers MUST re-express existing `k` and `business_key` values in the section 4.2.1 form. For example, the 1.0 example key `us-OR123456` becomes `us-or-123456`, with `registration_number` `123456`.

#### 4.2.6 MCP

`mcp_server_url` is OPTIONAL. If present it MUST be a valid HTTPS URL, but ABIZ does not assert that the endpoint is open, safe, available or authenticated. Consumers MUST apply appropriate access controls before using any linked agent endpoint.

#### 4.2.7 Unsupported country: North Korea (ABIZ 1.1, proposed)

ABIZ does not support businesses in North Korea (the Democratic People's Republic of Korea, ISO 3166-1 `kp`). A business record whose `country`, any `locations[].address.country.code`, service-area code or tax `jurisdiction` is `kp` (in any case) is invalid, and so is a business key whose country is `kp`. Producers MUST NOT publish such a record or key, and consumers MUST reject it. South Korea (`kr`) is unaffected.

### 4.3 Optional useful facts

The schema defines optional `description`, `website`, `email`, `phone`, `logo_url`, `blog_url`, `rss_url`, `last_updated`, `services`, `locations`, `tax_registrations`, `social_profiles`, `categories`, `media`, `review_summaries`, `operational_status` and `links`. Section 4.7 sets out the rules for them and for the members of a location. Public data MUST not claim a check that did not occur. A producer MUST omit private personal addresses rather than marking them private in a public record (section 4.7.6.2). A record MUST NOT contain `recent_posts` (section 4.7.12).

Implementations MAY add namespaced values inside `extensions` (reverse-domain keys). Member names inside an extension are defined by its owner; snake_case is RECOMMENDED, and the examples in this repository use it (for example `"to.co": {"badge": "registered", "business_pass": true}`). Extensions are covered by the record signature. Unknown top-level properties MUST be rejected. Extensions MUST NOT override the meaning of mandatory fields.

### 4.4 Independent semantic checks

A Draft 2020-12 structural validator MUST evaluate required properties, types, constraints and dependencies; an implementation MUST also enforce HTTPS URLs and `format` constraints explicitly. Some Draft 2020-12 validators treat `format` as an annotation by default.

Schema validation does **not** check the following. The reference validator checks the signature items locally:
- whether a business actually controls a domain;
- whether `identity_host` matches a fetched DNS or well-known `h` value, or whether the two sources agree (section 3.4.4);
- whether `business_key` matches `k` and `country`, or uses an assigned country and subdivision code (section 4.2);
- whether `signature` verifies, or whether `public_key` equals `p` (section 4.6.4);
- the rules of section 4.7.13: safe URLs, assigned codes, time zones, overlapping hours, repeated identifiers, ratings within their scale and the `recent_posts` ban anywhere;
- whether a tax registration, listing or review summary is genuine or current;
- whether a registration number is real;
- whether URLs are reachable;
- whether the business is genuine.

These checks are performed separately, with clear results. The supplied offline reference validator implements schema and local DNS/document checks; it does not query registries or fetch untrusted URLs.

### 4.5 Representations and the `format` parameter (ABIZ 1.1, proposed)

The record host serves one business in three representations at the same URL. A record host MUST support the `format` query parameter:

| `format` value | Representation | `Content-Type` |
| --- | --- | --- |
| `html` (the default when no representation is selected) | Human-readable page | `text/html; charset=utf-8` |
| `markdown` | Markdown (RFC 7763) | `text/markdown; charset=utf-8` |
| `json` | The ABIZ business record, validating against the normative schema | `application/json` (a `charset=utf-8` parameter is allowed) |

Rules:

- The parameter is appended to `https://<h>`, for example `https://hartleysbakery.uk.to.co/?format=json`, or `https://harbour-bike-repair.or.us.to.co/events?format=markdown` for a unit (section 8). `h` itself never contains a query (section 3.2).
- Values are case-sensitive and lowercase. A host MAY also accept `md` as an alias for `markdown`; consumers MUST send `markdown`.
- A recognised `format` value takes precedence over the `Accept` header.
- When `format` is absent, or its value is not recognised, the host MUST select the representation by content negotiation on `Accept` (RFC 9110 section 12.5.1): `application/json` selects JSON and `text/markdown` selects Markdown. Otherwise, including when `Accept` is absent, the host MUST serve HTML. A response chosen by negotiation SHOULD carry `Vary: Accept`.
- The JSON representation MUST be the business record itself: the same document whichever way JSON was selected, and never another JSON format such as a provider's page data.
- The HTML and Markdown representations SHOULD state the same public facts as the JSON record and MUST NOT contradict it. Only the JSON representation is checked for conformance.

A consumer MUST request JSON with `Accept: application/json` and SHOULD also add `format=json`. It MUST check that the response media type is `application/json` before parsing.

### 4.6 Record signing: `public_key` and `signature` (ABIZ 1.1, proposed)

Every business record MUST carry the business's public key and a signature over the record. Together with `p`, they let a consumer check that the record served at `https://<h>` was published by the holder of the key that the domain names, and that it has not been changed since it was signed.

#### 4.6.1 Members

| Member | Required | Value |
| --- | --- | --- |
| `public_key` | MUST | The Ed25519 public key, encoded exactly as `p` (section 3.3.2): standard base64 of the raw 32 bytes, 44 characters, one trailing `=`. It MUST equal the `p` value of the DNS assertion or well-known file that points to this record. |
| `signature` | MUST | The PureEd25519 signature (RFC 8032, no pre-hash) of the signing input (section 4.6.2), as standard base64 of the raw 64 bytes: 88 characters, ending `==`. |

`public_key` is a copy, for convenience and for detecting a mismatch. The authoritative key is always `p`. `last_updated` stays optional, but a producer SHOULD include it, and it is covered by the signature (section 4.6.6). A record without either member, or with a value of the wrong form, fails the schema.

#### 4.6.2 Signing input

The signing input is the UTF-8 encoding of the **JSON Canonicalization Scheme** (JCS, RFC 8785) serialisation of the whole business record **with the `signature` member removed**. Every other member is covered, including `public_key`, `last_updated` and everything inside `extensions`. Only the top-level `signature` member is removed; a member called `signature` inside an extension is signed like any other.

In summary, RFC 8785 serialises with no insignificant whitespace, sorts object members by the UTF-16 code units of their names, writes strings with only `"`, `\` and U+0000 to U+001F escaped (as `\b`, `\t`, `\n`, `\f`, `\r` or lowercase `\u00xx`) and all other characters as UTF-8, and writes numbers as ECMAScript does. RFC 8785 is normative; this summary is not.

- The record MUST be valid I-JSON (RFC 7493): no duplicate member names, no lone surrogates, and numbers that fit an IEEE 754 double. A consumer MUST reject a record that is not, before verifying.
- The served JSON need not be in canonical form. Member order, indentation and whitespace in the served document do not affect the signature, because the consumer canonicalises what it parsed.
- No Unicode normalisation is applied. Producers SHOULD write text in NFC before signing; a consumer MUST NOT normalise it before verifying.
- A producer MUST NOT sign a record that contains a number that cannot be represented exactly as a double. Since the section 4.7 amendment the base schema has numeric members: `geo` coordinates, ratings, counts, radii, media dimensions and positions. They are serialised with the RFC 8785 number rules (section 3.2.2.3), so `51.4550` becomes `51.455` and `5.0` becomes `5`. Producers SHOULD write coordinates with no more than seven decimal places.

`examples/registered-us.signing-input.txt` is the signing input of `examples/registered-us.json`, as a test vector:

```text
{"business_key":"us-or-123456","business_name":"Harbour Bike Repair LLC","country":"us","description":"Bicycle repair and maintenance in Portland.","domains":["harbourbikes.example"],"identity_host":"harbour-bike-repair.or.us.to.co","last_updated":"2026-11-03T09:00:00Z","locations":[{"address":{"country":{"code":"US"},"locality":"Portland","region":{"code":"US-OR","name":"Oregon"}},"kind":"trading","opening_hours":{"time_zone":"America/Los_Angeles","weekly":[{"day":"monday","periods":[{"closes":"17:00","opens":"09:00"}]},{"day":"tuesday","periods":[{"closes":"17:00","opens":"09:00"}]},{"day":"wednesday","periods":[{"closes":"17:00","opens":"09:00"}]},{"day":"thursday","periods":[{"closes":"17:00","opens":"09:00"}]},{"day":"friday","periods":[{"closes":"17:00","opens":"09:00"}]},{"day":"saturday","periods":[]},{"day":"sunday","periods":[]}]},"public":true}],"public_key":"6C4z0vRESsebqJiCfZmx9GkE2YSrIRV0cLgVgz24cwk=","record_version":"abiz1","registration_number":"123456","services":[{"name":"Bicycle servicing"},{"name":"Wheel repairs"}],"website":"https://harbourbikes.example"}
```

#### 4.6.3 Producing a signature

1. Build the complete record, including `public_key` set to the current `p` and, preferably, `last_updated`. Leave out `signature`, or remove an old one.
2. Validate it against the schema (apart from `signature`) and section 4.
3. Compute the signing input (section 4.6.2) and sign it with the Ed25519 private key that matches `p`.
4. Add `signature`, the standard base64 of the 64-byte result. Producers SHOULD place it last, so that it is easy to see.
5. Publish. Any later change to the record, however small, needs a new signature.

```python
import base64
from validate import signing_input  # scripts/validate.py; any RFC 8785 implementation is acceptable

record["public_key"] = p_value
record.pop("signature", None)
record["signature"] = base64.b64encode(private_key.sign(signing_input(record))).decode("ascii")
```

The reference validator provides `sign_record()` for producers. In hosted mode (section 3.3.4) the provider signs for the business with the business's key.

#### 4.6.4 Verification

A consumer verifies a fetched record as follows. Steps 1 to 4 need only the record; step 5 needs the pointer.

1. Parse the JSON representation as I-JSON (section 4.6.2), rejecting duplicate member names, and validate it against the schema.
2. Decode `public_key` with the rules of section 3.3.2 and `signature` as 64 bytes of canonical standard base64. A value that does not decode is a failure.
3. Remove the top-level `signature` member from the parsed object and compute the signing input (section 4.6.2).
4. Verify the signature with RFC 8032 PureEd25519 verification, using `public_key`, the signing input and the decoded signature.
5. Compare `public_key` with `p` from the assertion the consumer used (DNS, or the well-known file under section 3.4.4). Both are canonical, so the comparison is an exact string comparison.

If step 1 to 4 fails, or either member is missing, the record is **not verified**. If step 5 fails, the consumer MUST reject the record's identity claim: it MUST NOT treat the record as published by the business that controls the domain, even when the signature itself is valid. A consumer MUST NOT accept a record signed with a key that is not the domain's current `p`, and MUST NOT fall back to an unsigned interpretation of the record. It SHOULD report which check failed (missing member, bad encoding, signature does not verify, or `public_key` does not match `p`).

A consumer that shows a record that is not verified, for example to explain an error, MUST label it as not verified. The reference validator performs steps 1 to 4 for every record and step 5 when it is given `--dns-value`, `--well-known` or `--p`.

#### 4.6.5 Key rotation

The record is signed with the same key that DNS publishes, so a rotation (section 3.3.6) changes both:

1. Generate the new keypair.
2. Re-sign the record with the new private key, with `public_key` set to the new key and `last_updated` set to the time of the change.
3. Publish the new `p` (and update the well-known file, if there is one) and the re-signed record as close together as possible.

Until cached TXT records expire, some consumers still hold the old `p` and will see a `public_key` mismatch, or the reverse. The TXT TTL SHOULD therefore stay at 300 seconds (section 3.1). A consumer that finds a mismatch SHOULD query DNS again once the cached TTL has passed, and fetch the record again, before reporting a failure. It MUST NOT accept the mismatch in the meantime. A producer MUST NOT keep serving a record signed with a key it has withdrawn, and to revoke a compromised key it rotates as section 3.3.6 says; old records signed with that key then stop verifying against `p`.

#### 4.6.6 Security considerations

- **What the signature shows.** It shows that the holder of the private key for `p` published these record contents. Combined with section 3.4.4 it links the record to whoever controls the domain's DNS (or, for the well-known file, its web origin). It does not prove legal identity, does not make a registration number genuine, and does not protect against a party who controls the domain's DNS and its own key. Section 9 applies.
- **What it does not cover.** Only the JSON representation is signed. The HTML and Markdown representations (section 4.5) and HTTP headers are not, and a consumer MUST NOT treat them as verified. The DNS assertion is not signed by this mechanism; DNSSEC remains the way to authenticate it.
- **Replay.** A validly signed but older record stays valid for as long as its key is the current `p`. Producers SHOULD include `last_updated` and update it whenever they re-sign. A consumer that has seen a record with a later `last_updated` for the same key MAY reject an older one. Rotating the key invalidates every record signed with the old key.
- **Canonicalisation.** A consumer MUST canonicalise exactly as RFC 8785 specifies. A serialiser that sorts by code points instead of UTF-16 code units, escapes non-ASCII characters, or formats numbers differently produces different octets, and signatures will fail to verify. A parser that silently accepts duplicate member names lets two consumers see different records under one signature, which is why section 4.6.2 forbids them.
- **Signature checks.** Implementations MUST use RFC 8032 verification, which rejects a non-canonical `S`, and SHOULD use a maintained library. They MUST NOT verify over the raw HTTP body, or over a re-serialisation that is not RFC 8785.
- **Key protection.** Whoever holds the private key can sign any record for the domain. Section 3.3.4 applies to hosted mode. A business that suspects compromise MUST rotate (section 4.6.5).
- **Size.** Canonicalisation works on the parsed document. Consumers SHOULD apply the size limits of section 6 before parsing.

#### 4.6.7 Migration

This is a breaking change for business records. A record without `public_key` or `signature`, or one that still uses the hyphenated ABIZ 1.0 member names (`record-version`, `business-name` and so on), fails the ABIZ 1.1 schema. Producers MUST republish every record with snake_case names, `public_key` and a valid signature. A consumer MAY, for a transition period it announces, also read hyphenated names, but it MUST NOT report such a record as ABIZ 1.1 conformant or as verified.

The section 4.7 amendment is a further breaking change of the same kind. A record that still has `contact_email`, `contact_phone`, root `opening_hours` or a flat location fails the amended schema, and an amended record fails a validator built before the amendment. Producers MUST migrate as section 4.7.14 sets out and re-sign every migrated record. The key and `p` do not change because of the migration.

#### 4.6.8 Example

`examples/registered-us.json`, signed with the throwaway key of the registered DNS example in section 3.2 (the private key was discarded and is not in this repository):

```json
{
  "record_version": "abiz1",
  "business_name": "Harbour Bike Repair LLC",
  "country": "us",
  "business_key": "us-or-123456",
  "registration_number": "123456",
  "identity_host": "harbour-bike-repair.or.us.to.co",
  "domains": [
    "harbourbikes.example"
  ],
  "public_key": "6C4z0vRESsebqJiCfZmx9GkE2YSrIRV0cLgVgz24cwk=",
  "description": "Bicycle repair and maintenance in Portland.",
  "website": "https://harbourbikes.example",
  "services": [
    {
      "name": "Bicycle servicing"
    },
    {
      "name": "Wheel repairs"
    }
  ],
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Portland",
        "region": {
          "code": "US-OR",
          "name": "Oregon"
        },
        "country": {
          "code": "US"
        }
      },
      "opening_hours": {
        "time_zone": "America/Los_Angeles",
        "weekly": [
          {
            "day": "monday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "17:00"
              }
            ]
          },
          {
            "day": "tuesday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "17:00"
              }
            ]
          },
          {
            "day": "wednesday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "17:00"
              }
            ]
          },
          {
            "day": "thursday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "17:00"
              }
            ]
          },
          {
            "day": "friday",
            "periods": [
              {
                "opens": "09:00",
                "closes": "17:00"
              }
            ]
          },
          {
            "day": "saturday",
            "periods": []
          },
          {
            "day": "sunday",
            "periods": []
          }
        ]
      },
      "public": true
    }
  ],
  "last_updated": "2026-11-03T09:00:00Z",
  "signature": "tcf4loWK5IQq4wt9MFXswxUBHXHfPhkHf4puoHC1VeliwTLNHWQd75kf5CnCFvEui546QU/t7QWIRHEoX7etAA=="
}
```

### 4.7 Location, contact, hours and listing facts (ABIZ 1.1, proposed)

This section is the 2026-11-03 amendment to the ABIZ 1.1 proposal. It belongs to ABIZ 1.1 and does not make a new version. It renames the contact members, replaces the flat location members and the free-text root `opening_hours` with structured members, and adds optional members for listings, tax registrations, media and reviews. The wire version and `record_version` stay `abiz1`. The DNS and well-known tags and the signing rules of section 4.6 do not change. This amendment is part of the proposed 1.1 schema identified in section 4. It does not create a third schema, and it does not replace the published 1.0 schema. Section 4.7.14 lists the breaking changes.

#### 4.7.1 General rules

- Every member in this section is OPTIONAL unless this section says otherwise. A producer MUST omit a value it does not know or has not checked. It MUST NOT publish an empty string, an empty object or an invented placeholder in its place.
- Every URL member (`website`, `logo_url`, `mcp_server_url`, `blog_url`, `rss_url`, `services[].url`, `links[].url`, social profile URLs, `media[].url`, `external_listings[].public_url`, `review_summaries[].source_url`, and a URL `taxonomy` or `verification_source`) MUST be an absolute `https` URL of at most 2048 characters, with a public DNS host name, no user name or password, no fragment and no port other than 443. A producer MUST NOT rewrite an `http` resource into an `https` URL that does not exist; it omits the member instead.
- A signed record shows what the holder of the `p` key published (section 4.6.6). It does not prove company ownership, tax standing, the authenticity of reviews or a physical address. A consumer MUST distinguish **business-claimed** facts (everything in the record) from facts it has **verified** itself or that come from a named check, such as a tax registration's `verification_source` (section 4.7.4). It MUST NOT present a claimed fact as verified.
- A location's values are its own (section 4.7.6.3). Nothing is inherited between the business level and a location.

#### 4.7.2 Email and telephone

`email` is a public, customer-facing email address of the business, at most 320 characters, in the `email` format. A producer MUST include it only when it has authority to publish it. A verified address is not consent to publish it. `phone` is the primary public, customer-facing telephone number, at most 64 characters. E.164 form (for example `+441174960142`) is RECOMMENDED where it can be produced without losing a correctly formatted local number. A record does not claim that a number is reachable from every country. Other kinds of number (fax, text phone, mobile) are out of scope, and a producer MUST NOT put one in `phone` unless it is the primary customer number.

`email` and `phone` replace the earlier `contact_email` and `contact_phone`, which are no longer allowed.

#### 4.7.3 Blog and RSS feed

`blog_url` is the canonical URL of a public index of the business's articles or news. `rss_url` is the canonical URL of a public **RSS 2.0** feed. An Atom feed or JSON Feed is not an RSS feed and MUST NOT be given as `rss_url`. Either member may appear without the other. A producer MUST NOT invent either.

A record MUST NOT contain the posts themselves (section 4.7.12). Publishing, editing or deleting a post changes the blog or feed, not the record, and does not need a new signature. Only a change to `blog_url` or `rss_url`, or to another record member, does. A consumer SHOULD fetch a feed separately and asynchronously, and MUST NOT make resolution of the record depend on it.

#### 4.7.4 Tax registrations

`tax_registrations` is an array of at most 20 tax registrations. Each item has these members:

| Member | Required | Meaning |
| --- | --- | --- |
| `jurisdiction` | Yes | The authority's country, as an uppercase ISO 3166-1 alpha-2 code, or an ISO 3166-2 code for a subdivision's authority (for example `US-WA`). An EU VAT number uses its member state's code. |
| `scheme` | Yes | The type of registration: `vat`, `gst`, `sales_tax` or `other`. It is not a claim that the business is tax-compliant. |
| `number` | Yes | The number as the authority publishes it, 1–100 characters. |
| `verified_at` | Yes | The UTC date and time of the most recent successful check of this exact number with the authority. |
| `verification_source` | Yes | Who checked it: a short lowercase token naming the authority's checking service (for example `vies` or `hmrc_vat`) or the HTTPS URL of that service. |
| `verification_expires_at` | No | When the claim must be checked again or withdrawn. It MUST be later than `verified_at`. |

A producer MUST publish an item only when all of these are true: the most recent check of the current `jurisdiction`, `scheme` and `number` was positive; the business has expressly consented to publishing it; and `verification_expires_at`, if present, has not passed. A pending, failed, unavailable or expired check, or a check of an earlier number, MUST NOT be published. When consent is withdrawn, the number changes or the registration stops being valid, the producer MUST remove the item and re-sign the record (examples `verified-vat-fr.json` and `vat-withdrawn-fr.json`). A record MUST NOT contain the authority's full response, a registered tax address or any credential used to make the check. A tax registration is separate from the business registration of section 4.2. A consumer that relies on a tax registration SHOULD check it with the authority itself.

#### 4.7.5 Social profiles, categories, services and links

`social_profiles` is an object whose keys name a network and whose values are HTTPS URLs of the business's public profile. The keys allowed are `linkedin`, `x`, `instagram`, `facebook`, `youtube`, `tiktok`, `pinterest`, `vimeo`, `snapchat` and `clubhouse`. Any other key is rejected; a later revision of this specification adds keys.

`categories` has an optional `primary` category and up to nine `additional` ones. Each category is `{ "taxonomy", "id", "name"? }`. `taxonomy` and `id` together identify the category; `name` is an optional display label in any language and is never an identifier. `taxonomy` is either a token from the table below or an HTTPS URI that identifies a published category list, such as a listing provider's. A producer MUST NOT invent a universal category identifier, and a consumer MUST NOT treat identifiers from different taxonomies as interchangeable.

| Token | Taxonomy |
| --- | --- |
| `isic_rev4`, `isic_rev5` | UN International Standard Industrial Classification, revision 4 or 5 |
| `nace_rev2`, `nace_rev2_1` | EU statistical classification of economic activities, NACE Rev. 2 or Rev. 2.1 |
| `naics_2022` | North American Industry Classification System, 2022 |
| `uk_sic_2007` | UK Standard Industrial Classification of economic activities 2007 |
| `anzsic_2006` | Australian and New Zealand Standard Industrial Classification 2006 |

`services` and `links` are unchanged, except that their URLs are limited to 2048 characters like every other URL. Services remain business-wide.

#### 4.7.6 Locations

`locations` lists up to 100 places of business. A business without a public place of business, such as an online-only business, MAY omit `locations` (example `online-only-de.json`). Each location is an object with these members, all optional: `location_id`, `kind`, `name`, `description`, `address`, `geo`, `website`, `email`, `phone`, `logo_url`, `social_profiles`, `categories`, `opening_hours`, `service_areas`, `external_listings`, `review_summaries`, `operational_status` and `public`. A location has no `media` member.

##### 4.7.6.1 Identity, kind and visibility

- `location_id` is a stable public identifier for the location: lowercase letters, digits and hyphens, 1–100 characters, unique within `locations`. A producer SHOULD keep it unchanged when other details of the location change, and MUST NOT reuse it for a different place. It is not an internal database key and not an ABIZ record host.
- `kind` is `registered-office`, `trading` or `other`. A registered office is the address on the business register; a trading location is a place where the business deals with customers; `other` is any other place, such as a market stall or a depot.
- `name` (at most 180 characters) is the location's own display name, and may differ from `business_name`. `description` (at most 2000 characters) is a public description of the location, not private notes.
- `public: true` means that the business presents the location as a place customers or visitors can go. It is **not** consent to publish any detail of the location: a detail that is not to be published is left out, whatever `public` says.

##### 4.7.6.2 Address, geography and privacy

`address` has these members:

- `street_lines`: one to three non-empty street lines. If present, `locality` MUST be present too.
- `locality`: the city, town or village.
- `postal_code`: the postal code.
- `region`: `{ "code"?, "name"? }`, with at least one member. `code` is a complete uppercase ISO 3166-2 code (for example `GB-ENG`, `US-VT`) whose country part MUST equal `country.code`. A producer MUST publish a code only when it has checked it; a raw state or province abbreviation is not an ISO 3166-2 code until it has been mapped. `name` is a human-readable label.
- `country`: REQUIRED in an address. `{ "code", "name"? }`, where `code` is an uppercase, assigned ISO 3166-1 alpha-2 code and is authoritative. `name` is an optional, locale-dependent label, never used in place of `code`.

`geo` is `{ "latitude", "longitude" }`, WGS 84 decimal degrees, latitude between −90 and 90 and longitude between −180 and 180. Both members are REQUIRED together. `geo` gives the location of the premises and MUST NOT be given unless `address.street_lines` is published.

Privacy rules:

- The business controls which details of a location are published. A registered office's address follows the law on what the register shows.
- A producer MUST omit a private personal address, or any part of an address the business has not approved for display. It omits the street, postal code and coordinates, rather than marking them private. A location may consist of only a locality and country, or only a country (example `private-trading-address-au.json`).
- A hidden address MUST NOT leak through another member: not through `geo`, not through a service-area circle centred on the premises (section 4.7.7), not through media metadata (section 4.7.9) and not through a listing URL that has not been approved for display.
- A producer MUST NOT add precision it does not have, for example by geocoding a locality and publishing the result as `geo`.

##### 4.7.6.3 Location contact details and profiles

`website`, `email`, `phone`, `logo_url`, `social_profiles` and `categories` of a location follow the rules for the business-level members of the same names. They belong to that location. A location's values are **not inherited** from the business level, and the business-level values are not inherited from a location: a consumer MUST NOT treat a business-level `phone` as the phone number of a location that has none. A producer MUST NOT copy a business-level value into a location in the signed record unless that value is the location's own. A tool MAY offer the owner a business-level default when the owner edits a location, as long as the owner confirms it.

##### 4.7.6.4 Opening hours

`opening_hours` belongs to a location. It is an object with these members:

- `time_zone` (REQUIRED): an IANA time zone identifier, for example `Europe/London`. All times are local times in this zone, so a change to or from summer time needs no edit. A producer MUST NOT guess the zone from the country alone where the country has more than one zone.
- `weekly`: up to seven entries `{ "day", "periods" }`, at most one for each `day` (`monday` to `sunday`).
- `exceptions`: up to 100 entries `{ "date", "periods" }` for dated exceptions, at most one per `date` (`YYYY-MM-DD`, a local date). An exception replaces the weekly hours for that whole date. Producers SHOULD publish only exceptions for today or later.
- `appointment_only`: `true` when visits are by appointment only. Any periods are then the hours in which appointments are offered.

At least one of `weekly`, `exceptions` and `appointment_only` MUST be present. `periods` is an array of up to four `{ "opens", "closes" }` objects with 24-hour local times `HH:MM`. `closes` may be `24:00`, the end of the day. A `closes` earlier than `opens` means the period ends on the next day (overnight). `opens` and `closes` MUST NOT be equal. Periods MUST be listed in order of `opens` and MUST NOT overlap, and an overnight period MUST NOT overlap the first period of the next day (a Sunday overnight period runs into Monday). The meaning of each case is fixed:

| Case | Written as |
| --- | --- |
| Hours not known | The day is absent from `weekly` (or `opening_hours` is absent) |
| Closed all day | `"periods": []` |
| Split hours | Two to four periods, for example `08:00–12:30` and `13:30–18:00` |
| Overnight | One period whose `closes` is earlier than `opens`, for example `19:00–01:00` |
| Open 24 hours | One period `00:00–24:00` |
| Closed on a date | An exception with `"periods": []` |

A missing day MUST NOT be read as closed. Hours MUST NOT be used to say that a location is closed for a period of time or for good; `operational_status` says that (section 4.7.8). Root `opening_hours` is no longer allowed.

#### 4.7.7 Service areas

`locations[].service_areas` lists up to 50 areas that the location serves, for a business that goes to its customers. Each area has exactly one of these shapes:

| Shape | Members | Meaning |
| --- | --- | --- |
| Coded area | `code` | An uppercase ISO 3166-1 alpha-2 country code (`IE`) or ISO 3166-2 subdivision code (`US-VT`) |
| Postal code | `postal_code`, `country` | A full postal code, or a published outward or prefix code (`BS1`), in the country with that ISO 3166-1 code |
| Circle | `center` (`geo`), `radius_m` | A circle with a radius of 1 to 500 000 metres |

No other shape is allowed; GeoJSON and provider-specific area identifiers are not. A circle's `center` MUST be a coarse point, such as a town centre. It MUST NOT be the coordinates of an address that is not published. A service area does not need a published address (example `service-area-us.json`).

#### 4.7.8 Operational status

`operational_status`, at the business level and per location, is `open`, `temporarily_closed`, `permanently_closed` or `unknown`. A business-level value applies to the business as a whole; a location's value applies to that location only. A consumer MUST NOT work out a closure from one day's hours, and MUST NOT treat a missing `operational_status` as `open` or as closed. A temporary closure SHOULD be explained in the location's `description` (example `temporary-closure-ie.json`).

#### 4.7.9 Media

`media` is a business-level array of at most 10 curated public media items. It is a selection for the record, not a limit on the business's own gallery or on what it uploads elsewhere. Each item has:

- `id` (REQUIRED): a slug, unique within `media`;
- `kind` (REQUIRED): `logo`, `cover`, `image` or `video`;
- `url` (REQUIRED): HTTPS URL of the file;
- `content_type` (REQUIRED): for an image, `image/jpeg`, `image/png`, `image/webp`, `image/gif`, `image/avif` or `image/svg+xml`; for a video, `video/mp4` or `video/webm`.

An image item MAY also have `width` and `height` in pixels (RECOMMENDED when known), `caption`, `alt_text`, `decorative`, `position` (1–10, unique within `media`, the display order) and `updated_at`. An image that conveys information MUST have `alt_text`; an image that is only decorative has `"decorative": true` and no `alt_text`. A video item has only `id`, `kind`, `url` and `content_type` in this revision. A producer MUST publish only media it has the right to publish, MUST NOT publish unpublished or private media, and MUST remove location and other private metadata (such as EXIF GPS data) from the files it links to.

#### 4.7.10 Review summaries

`review_summaries`, at the business level and per location, lists up to 20 aggregate ratings, at most one per `platform`. Each item has `platform`, `rating`, `rating_scale` (the best possible rating, for example `5`), `review_count`, `source_url` (a public page that shows the summary) and `observed_at`; all are REQUIRED. `rating` MUST NOT exceed `rating_scale`.

Each platform's summary stands alone. A record MUST NOT contain a rating combined across platforms, reviewer names or profiles, the text of reviews, replies or moderation data. A producer MUST omit a summary that the platform's terms or licence do not allow it to republish. Because ratings change often, a producer MAY update them on a schedule rather than after every review; each update is a change to the record and needs a new signature. A consumer SHOULD show `observed_at` with the rating.

#### 4.7.11 External listings and platform names

`locations[].external_listings` lists up to 20 public listings of the location on other platforms, such as maps and directories. Each item has `platform` and `public_url` (REQUIRED), and optionally `external_id` (the platform's public identifier for the listing), `observed_at` (when the publisher last saw the listing at that URL) and `claimed_by_business`.

`public_url` MUST be the listing's real public URL, as the platform publishes it. A producer MUST NOT build it from an opaque identifier. `claimed_by_business: true` is the business's statement that it controls the listing on that platform; when it is absent or `false`, the listing was found, not claimed. Neither is a statement by the platform. A record MUST NOT contain access tokens, account identifiers, permission scopes, change logs or synchronisation state for a platform.

A `platform` value, in `external_listings` and in `review_summaries`, is either a registered token or a reverse-domain name controlled by the platform's operator (for example `com.example.maps`). The registered tokens are `google_business_profile` and `apple_maps`; a later revision may register more. ABIZ does not depend on any platform: a record that names none is fully conformant (example `blog-rss-only-nz.json`).

#### 4.7.12 Prohibited members

A record MUST NOT contain a `recent_posts` member, or any copy of posts, excerpts, article bodies or a selection of recent items, at any level, inside `extensions` included. The schema rejects `recent_posts` at the top level and in a location, and the reference validator rejects it anywhere. `blog_url` and `rss_url` (section 4.7.3) are the way to point to posts.

#### 4.7.13 Checks beyond the schema

JSON Schema cannot express every rule in this section. A conforming consumer, and the reference validator `scripts/validate.py`, MUST also check:

- that every URL meets section 4.7.1;
- that `address.country.code`, service-area codes and `tax_registrations[].jurisdiction` are assigned ISO 3166-1 codes, not `kp` (section 4.2.7), and that a region or subdivision code belongs to its country (the reference validator checks that a code is assigned for `us`, `ca` and `ae`, whose subdivisions are in `data/iso3166.json`, and checks only the form and the country part elsewhere);
- that `time_zone` is a known IANA time zone;
- that periods are in order, do not overlap within a day, and that an overnight period does not overlap the next day's periods;
- that `weekly` days, exception dates, `location_id` values, media `id` and `position` values, review platforms and tax registrations are not repeated;
- that a rating does not exceed its scale, and that `verification_expires_at` is later than `verified_at`;
- that no `recent_posts` member appears anywhere.

#### 4.7.14 Versioning and migration

This amendment keeps the `abiz1` family: `record_version` stays `abiz1` and `v=abiz1` is unchanged. The amended members belong to the proposed 1.1 schema (`schemas/abiz-business-record-v1.1.schema.json`), which is identified separately from the published 1.0 schema. Several changes are breaking, and the 1.1 schema stays strict (`additionalProperties: false`), so:

- a validator built for the ABIZ 1.1 proposal **before** this amendment rejects an amended record that uses any new member, and the amended schema rejects a record that uses a removed one;
- a consumer MUST identify the schema revision it validates against when it claims conformance (section 7), and SHOULD report a record that fails only because of a member from a different revision as such, not as a forged record;
- a producer MUST NOT serve amended records to consumers that it knows validate against the earlier revision, and SHOULD move to the amended form once and in one step, rather than publish a mixture;
- a producer MUST re-sign every record it migrates. The signing rules (section 4.6) are unchanged, so a migrated record signed with the current key verifies against the same `p`; the DNS assertion and well-known file need no change.

| Before the amendment | After the amendment |
| --- | --- |
| `contact_email` | `email` |
| `contact_phone` | `phone` |
| root `opening_hours` (list of text lines) | `locations[].opening_hours` (structured, with `time_zone`); a business with no location has no hours |
| `locations[].street` | `locations[].address.street_lines` (array of one to three lines) |
| `locations[].city` (required) | `locations[].address.locality` (optional; required with `street_lines`) |
| `locations[].region` (text) | `locations[].address.region` (`{ "code"?, "name"? }`) |
| `locations[].postal_code` | `locations[].address.postal_code` |
| `locations[].country` (required, any case) | `locations[].address.country.code` (required in an address, uppercase) |

A producer migrating text hours SHOULD convert them only when they are unambiguous, and otherwise leave the location's hours out until the business confirms them. Rolling back means publishing a record in the earlier form, re-signed; it is not possible to publish both forms at once at one record host.

A location object, for illustration (from `examples/locations-and-listings/multi-location-gb.json`, shortened):

```json
{
  "location_id": "bristol-clifton",
  "kind": "trading",
  "name": "Clifton Shop",
  "address": {
    "street_lines": ["14 Example Street"],
    "locality": "Bristol",
    "postal_code": "BS8 2XX",
    "region": { "code": "GB-ENG", "name": "England" },
    "country": { "code": "GB", "name": "United Kingdom" }
  },
  "geo": { "latitude": 51.455, "longitude": -2.6175 },
  "phone": "+441179460001",
  "opening_hours": {
    "time_zone": "Europe/London",
    "weekly": [
      { "day": "monday", "periods": [{ "opens": "08:00", "closes": "12:30" }, { "opens": "13:30", "closes": "18:00" }] },
      { "day": "sunday", "periods": [] }
    ],
    "exceptions": [{ "date": "2026-12-25", "periods": [] }]
  },
  "public": true
}
```

`examples/locations-and-listings/` has signed records for each case in this section: a minimal registered business, an online-only business, several locations, a private trading address, a service-area business, a location open 24 hours, a temporary closure, a verified VAT registration and the same record after it is withdrawn, public listing links, and a business with only a blog and feed. `dns-assertions.txt` there gives each record's DNS assertion, and `invalid/` holds records that each break one rule.

## 5. Producer requirements

A conforming producer MUST:

1. publish no more than one matching `v=abiz1` TXT assertion at `_abiz.<domain>`, or a well-known file (section 3.4), or both; if both, keep them identical;
2. include `h=` and `p=` (an Ed25519 public key, section 3.3); MAY include `k=`, for a registered or unregistered business;
3. serve the business record at `https://<h>`, supporting the `format` parameter and content negotiation of section 4.5, with the JSON representation being the business record;
4. validate the object against the normative schema **before** publishing and whenever updated;
5. ensure its `domains` array declares the domain at which the DNS assertion or well-known file was published;
6. ensure `identity_host` matches `h` exactly after canonical hostname normalization;
7. ensure DNS `k`, if present, equals the document `business_key` (section 4.2.4), and that `business_key` and `registration_number` follow sections 4.2.1 to 4.2.3;
8. set `public_key` to the `p` it publishes and sign the record as section 4.6.3 sets out, re-signing after every change to the record and every key rotation;
9. publish location, contact, hours, tax, media, review and listing facts only as section 4.7 allows, omitting private or unchecked details.

`p` MUST be an Ed25519 public key as specified in section 3.3, and a producer MUST NOT publish the private key. A producer that still publishes an assertion without `p`, or with a non-key ABIZ 1.0 `p` token, MUST republish it with a key (section 3.3.7). A producer that rotates a key MUST follow section 3.3.6 and MUST NOT put the old key in DNS or in the well-known file.

The record host MUST serve HTML, Markdown and JSON as section 4.5 sets out. A `.md` extension is not required. The main record of a business SHOULD use a bare hostname as `h`; a path is for a business unit or division (section 8).

## 6. Consumer requirements

A conforming consumer MUST:

1. query TXT at `_abiz.<domain>` and apply matching-record and tag rules, then, where section 3.4.4 allows, the well-known file, applying its precedence rules (DNS wins);
2. reject absent, duplicate, malformed or conflicting ABIZ assertions, including one without `p`;
3. fetch `https://<h>` safely: TLS verification, disallow private/loopback/link-local addresses and unsafe redirects, limit size and timeouts;
4. request JSON with `Accept: application/json` (and SHOULD add `format=json`, section 4.5), check the media type, and parse it without executing scripts;
5. validate it against the exact normative schema (and required format checks);
6. verify its `identity_host` and `domains` match the assertion (DNS or well-known file) and queried domain;
7. when `k` is present, check it against section 4.2.1 and compare it case-insensitively to the record's `business_key`; reject the assertion if the record has no `business_key`;
8. verify `signature` with `public_key` and check that `public_key` equals `p`, as section 4.6.4 sets out, and treat a record that fails either check as not verified;
9. apply the checks of section 4.7.13, keep location values apart from business-level values (section 4.7.6.3), and present business-claimed facts as claimed, not verified (section 4.7.1);
10. label domain-link checks separately from legal registration checks.

A consumer that claims ABIZ 1.1 MUST parse the assertion with the tag-list syntax of section 3.1.1, so it accepts optional whitespace around `;` and `=` and one trailing `;`. It MUST reject an assertion without `p`, or whose `p` is not a valid key under section 3.3.2, including an ABIZ 1.0 hexadecimal token or a base64url value, and MUST follow sections 3.3.5 and 3.3.6. It MUST reject a record or key for `kp` (section 4.2.7). A key check is separate from record conformance and from legal registration.

A consumer MAY check registration details against authoritative registries; if it does not, it MUST NOT describe a business as legally verified. A consumer MUST NOT automatically trust instructions, URLs or tool results embedded in the record.

## 7. Conformance claims

| Claim | Minimum requirement | What it does NOT establish |
| --- | --- | --- |
| **ABIZ record conformant** | Draft 2020-12 schema, local semantic validation and a `signature` that verifies with `public_key` (section 4.6) | Domain control or registered business identity |
| **ABIZ publisher conformant** | Record conformant + valid DNS assertion or well-known file + correct domain/record linkage, including `public_key` equal to `p` + HTML, Markdown and JSON representations with the `format` parameter (section 4.5) | Legal identity, customer trust or AI visibility |
| **ABIZ consumer conformant** | Required DNS parsing, safe fetch, schema, semantic and clear status handling | Global adoption or recommendations |
| **Registry-confirmed** | Independent authoritative register check, separately labelled | Endorsement by ABIZ |

Conformance MUST identify the schema `$id` and document revision. Use `https://abizrecord.org/schema/abiz-business-record-v1.schema.json` for the published ABIZ 1.0 contract and `https://abizrecord.org/schema/abiz-business-record-v1.1.schema.json` for the proposed ABIZ 1.1 contract. `v=abiz1` and `record_version` do not choose between them. An unsupported revision is not an invalid signature, and a schema mismatch is not an invalid signature. Do not claim `v=abiz1` alone proves that a business is registered or verified. Do not describe ABIZ 1.1 as formally published.

## 8. Business units and divisions

A business's main record SHOULD use a bare hostname as its record host, with no path (an illustrative UK example; `p` is a throwaway key):

```dns
_abiz.hartleysbakery.example. 300 IN TXT "v=abiz1;k=gb-01234567;h=hartleysbakery.uk.to.co;p=iM9LF3A1EpHDmHn17+eaaq787N6LsWFk8LhBo7sjOAk="
```

A business unit or division (a branch, a brand, a department, an events arm) MAY have its own business record. Its record host MAY then be a path on the parent's host (ABIZ 1.1, proposed):

```dns
_abiz.events.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co/events;p=6C4z0vRESsebqJiCfZmx9GkE2YSrIRV0cLgVgz24cwk="
```

Rules for a path-based record host:

- The path is part of `h`, and the unit record's `identity_host` MUST equal it exactly, path included (`examples/unit-us.json`). `h=harbour-bike-repair.or.us.to.co` does not match a record whose `identity_host` is `harbour-bike-repair.or.us.to.co/events`.
- The path MUST NOT contain a query, a fragment, or `.` or `..` segments. It is compared case-sensitively.
- The host MUST serve the unit's record at `https://<h>` with the representations and `format` parameter of section 4.5, for example `https://harbour-bike-repair.or.us.to.co/events?format=json`.
- The unit's record is a business record in its own right. Its `domains` list the domains the unit's own assertion is published at. A unit of a registered business MAY carry the parent's `business_key` and `registration_number` when it has no registration of its own.
- The unit SHOULD publish its own assertion, in DNS or a well-known file, on a domain it uses, for example `_abiz.events.harbourbikes.example`.

A parent business MAY list units and their domains in an implementation-specific extension, in `links`, or in separate business records. A consumer MUST NOT treat a parent assertion alone as proof that a unit is controlled, and MUST NOT treat a path under a parent's host as proof that the parent vouches for the unit. A stronger claim requires the unit's own ABIZ pointer and a consistent back-reference. Unit relationships are not defined by the base schema in ABIZ 1.0 or 1.1.

## 9. Security and privacy

DNS assertions and well-known files are public and not authenticated by default. A well-known file shows control of a web origin, not of a DNS zone (section 3.4.5). Producers SHOULD use DNSSEC where available; consumers SHOULD verify DNSSEC where supported. DNS control alone does not prove business ownership. An Ed25519 public key in `p` does not change that. It shows which key the domain controller published. It does not sign the TXT record by itself, and it does not prove legal identity. The record signature (section 4.6) binds the business record to that key; section 4.6.6 sets out what it does and does not protect. A non-key `p` value is invalid under ABIZ 1.1 (section 3.3.7) and MUST NOT be presented as a cryptographic identity. The private key is the business's property and MUST be protected. In hosted mode a provider MAY hold that key and sign for the business. It MUST follow the export and deletion rules in section 3.3.4. Holding the key does not transfer ownership. Consumers MUST implement SSRF safeguards, HTTPS-only target handling, host/redirect validation, content size/time limits and output escaping, for both the well-known file and the record host. A consumer that shows the HTML or Markdown representation MUST treat it as untrusted content. MCP endpoints MUST not be called automatically solely because they appear in a record.

A publisher MUST consider personal data and only publish intentionally public facts. A hidden address MUST NOT reach the record through coordinates, service areas, media metadata or listing links (section 4.7.6.2), and a tax registration needs the business's express consent (section 4.7.4). A domain claim MUST NOT be presented as a legal verification badge.

## 10. IANA and governance

The intended globally scoped underscore label is `_abiz`, RR type TXT. Registration has been **requested but is not confirmed**. Publication does not claim completed IANA registration. The well-known URI suffix `abiz.json` (RFC 8615) is intended for registration; it has not yet been requested.

The standard is open and provider-independent. To.Co Technologies Limited is the managing organisation. Implementers can comment or propose changes through the [public repository](https://github.com/abiz-org/abiz-agentic-business-record). No personal email address is required for participation.

## 11. References

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [RFC 8552 — Underscored and Globally Scoped DNS Node Names](https://www.rfc-editor.org/rfc/rfc8552)
- [RFC 8615 — Well-Known Uniform Resource Identifiers (URIs)](https://www.rfc-editor.org/rfc/rfc8615) (section 3.4)
- [RFC 8259 — The JavaScript Object Notation (JSON) Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259)
- [RFC 8785 — JSON Canonicalization Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785) (section 4.6.2)
- [RFC 7493 — The I-JSON Message Format](https://www.rfc-editor.org/rfc/rfc7493) (section 4.6.2)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110) (section 12.5.1, `Accept`) and [RFC 9111 — HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
- [RFC 7763 — The text/markdown Media Type](https://www.rfc-editor.org/rfc/rfc7763)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)
- [RFC 4648 — The Base16, Base32, and Base64 Data Encodings](https://www.rfc-editor.org/rfc/rfc4648) (section 4 is the ABIZ `p` encoding)
- [RFC 6376 — DomainKeys Identified Mail (DKIM) Signatures](https://www.rfc-editor.org/rfc/rfc6376) (`p=` base64 syntax; section 3.2 tag-list syntax)
- [RFC 1035 — Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035) (TXT character-strings)
- [RFC 5234 — Augmented BNF for Syntax Specifications: ABNF](https://www.rfc-editor.org/rfc/rfc5234) and [RFC 7405 — Case-Sensitive String Support in ABNF](https://www.rfc-editor.org/rfc/rfc7405)
- [RFC 7208 — Sender Policy Framework (SPF)](https://www.rfc-editor.org/rfc/rfc7208) (sections 3.3, 4.6.1 and 12)
- [RFC 7489 — Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://www.rfc-editor.org/rfc/rfc7489) (section 6.4)
- [RFC 8461 — SMTP MTA Strict Transport Security (MTA-STS)](https://www.rfc-editor.org/rfc/rfc8461) (section 3.1)
- [RFC 8460 — SMTP TLS Reporting](https://www.rfc-editor.org/rfc/rfc8460) (section 3)
- [RFC 8032 — Edwards-Curve Digital Signature Algorithm (EdDSA)](https://www.rfc-editor.org/rfc/rfc8032)
- [RFC 8463 — A New Cryptographic Signature Method for DomainKeys Identified Mail (DKIM)](https://www.rfc-editor.org/rfc/rfc8463)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [draft-morrison-mcp-dns-discovery](https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/) (individual Internet-Draft; see section 12)

## 12. Interoperability

ABIZ 1.1 (proposed) encodes the DNS `p` tag as standard base64 with padding, matching the Ed25519 public key in DKIM (RFC 8463). That is a 44-character encoding of 32 bytes. ABIZ shares that public-key encoding only. Signature checks use PureEd25519 over the RFC 8785 canonical record (section 4.6) or another agreed message (section 3.3.5). See section 3.3.2.

[draft-morrison-mcp-dns-discovery](https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/) also puts Ed25519 public keys in DNS TXT records. The current draft name is unchanged. Revision 09 (21 October 2026) is the revision consulted for this text; the datatracker link above tracks later revisions. In that draft, `_mcp` and `_alter` carry the key as `pk=ed25519:` followed by unpadded base64url (RFC 4648 section 5). A 32-byte key is then 43 characters, not 44. ABIZ MUST NOT be read as using that encoding. A consumer MUST NOT treat an ABIZ `p` value as that draft's `pk` value, or the reverse, without decoding and encoding again.

The two mechanisms can appear in one zone at different owner names (`_abiz`, and the draft's `_mcp` or `_alter`). The draft is an individual submission. It is not an IETF standard, and this specification does not require it.

ABIZ does not adopt that draft's base64url form. `p` uses the RFC 8463 standard base64 form, and a base64url `p` value is invalid (section 3.3.2). The DKIM precedent applies to the same kind of record, a DNS TXT tag-list, and standard base64 needs no escaping in TXT.
