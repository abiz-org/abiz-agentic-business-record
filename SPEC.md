# ABIZ — Agentic Business Record Specification

**Published version:** ABIZ 1.0  
**DNS wire version:** `v=abiz1` (unchanged)  
**Date:** 2026-10-23  
**1.1 proposal:** 2026-10-31 (not the published version; see section 3.3)  
**Managing organisation:** To.Co Technologies Limited, United Kingdom  
**Planned official site:** `abizrecord.org`  
**Public source:** https://github.com/abiz-org/abiz-agentic-business-record  
**Normative schema:** `schemas/abiz-business-record-v1.schema.json`

This is the **ABIZ 1.0 published specification**. Publication does not imply IANA registration or endorsement. Implementers MUST NOT present domain control as proof of a registered business's legal identity, and MUST NOT claim guaranteed AI discovery, ranking or recommendation.

Section 3.3 is a **proposed ABIZ 1.1** change to the optional DNS `p` tag. It is not part of the ABIZ 1.0 conformance baseline. The wire version stays `v=abiz1`.

## 1. Scope and purpose

ABIZ provides a provider-independent method for locating a business's **public business record** from a domain it controls. Producers publish a versioned DNS TXT assertion at `_abiz.{domain}` pointing to a record served over HTTPS. Consumers discover that record, validate its structure using the **normative JSON Schema**, and perform cross-source consistency checks.

ABIZ is not a legal identity registry, endorsement scheme, payment system or requirement to use one provider. **An MCP server is optional**. Business records can be published by registered or unregistered businesses.

The key words MUST, MUST NOT, SHOULD and MAY have their RFC 2119 / RFC 8174 meanings.

## 2. Terms

- **Producer:** entity publishing an ABIZ pointer at a domain it controls.
- **Consumer:** software reading and validating the pointer and published business record.
- **Business record:** JSON representation of public business facts conforming to the normative schema.
- **Record host:** the DNS hostname plus optional path in the `h=` tag (no `https://` prefix).
- **Business key:** optional registered-business identifier in `country-registration-number` form.
- **Domain check:** checks that a DNS assertion and fetched business document refer to each other; distinct from government registration checks.
- **Record conformance:** schema and local semantic checks pass.
- **Publisher conformance:** record conformance plus the DNS / document requirements in this specification.
- **Consumer conformance:** implements the checks and rejects invalid assertions.

## 3. DNS assertion

### 3.1 Owner, RRset and version

An ABIZ DNS assertion is a TXT record at `_abiz.<domain>`. The first semicolon-delimited tag MUST be exactly `v=abiz1`. There MUST be exactly one matching `v=abiz1` TXT record at that owner name. Zero means no ABIZ assertion; two or more means an invalid assertion.

The TTL SHOULD be 300 seconds. Tags are case-sensitive, unique, and MUST NOT contain spaces. A consumer MUST ignore unknown additional tags and MUST reject duplicate recognised tags.

### 3.2 Tags

| Tag | Required | Meaning |
| --- | --- | --- |
| `v=abiz1` | MUST | Wire protocol family; always first |
| `h=<record-host>` | MUST | HTTPS hostname plus optional path of the public business record, without URL scheme |
| `k=<country-registration>` | REQUIRED for registered businesses | Independent registration key; MAY be absent for unregistered businesses |
| `p=<token-or-key>` | MAY | Optional. In ABIZ 1.0, an opaque provider token. In ABIZ 1.1 (proposed), an Ed25519 public key; see section 3.3. Not a password and not proof of legal identity |

`h` MAY refer to a record hosted by an independent service. A producer need not own the host serving the record; it MUST control the queried DNS domain and have permission for the published record.

**Example — registered business (US):**

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-OR123456;h=harbour-bike-repair.or.us.to.co"
```

**Example — unregistered business (US):**

```dns
_abiz.marketstand.example. 300 IN TXT "v=abiz1;h=market-stand-repairs-portland.biz.to.co"
```

Both are illustrative, invented businesses. These entries demonstrate alternatives on **different DNS owners**. A business MUST NOT publish both as independent matching assertions at one owner name.

These hostnames are examples of to.co's country-based registered-company hostname and town-based `.biz.to.co` hostname. ABIZ does not require either naming scheme.

**Example — ABIZ 1.1 (proposed) Ed25519 `p` key:**

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-OR123456;h=harbour-bike-repair.or.us.to.co;p=oS5YhE6Qz35Id1hMp3XOI3eQWW03DVgY3kU6rEdlodQ="
```

`p` here is a throwaway Ed25519 public key. The private key is not part of this specification and is not in the repository. See `examples/dns-ed25519-p.txt` and section 3.3.

### 3.3 The `p` tag (ABIZ 1.1, proposed)

This section is a proposal. ABIZ 1.0 consumers MUST keep treating `p` as an opaque token. A 1.1 implementation MUST follow this section only when it claims the 1.1 key behaviour.

#### 3.3.1 Role

In ABIZ 1.0, `p` is optional and provider-specific. The value is a non-empty token with no spaces. It is not checked as a key. Deployments have used it for a one-time domain-control handshake, including a 32-character hexadecimal token.

ABIZ 1.1 proposes to make that tag a persistent signing identity. The business, or a provider acting for it, generates an Ed25519 keypair and publishes the public key in `p`. The private key remains the business's property (section 3.3.4). A later signature can be checked against the published key. The one-time token is replaced by a key the business can keep using.

Publishing the key shows that the controller of the domain put that public key in DNS. It does not authenticate the TXT record. It does not prove that a registered business owns the domain. Section 9 still applies: DNS assertions are public and unauthenticated by default, and DNS control alone does not prove business ownership. Producers and consumers SHOULD still use DNSSEC where they can. DNSSEC authenticates the DNS data. The key names a signer the domain controller published.

`p` is DNS-only. The business-record schema does not contain the current key (section 4). Retired keys are the exception: they are carried in that record, not in DNS (section 3.3.6).

#### 3.3.2 Key encoding

`p` MUST be the standard base64 encoding (RFC 4648, section 4) of the raw 32-byte Ed25519 public key (RFC 8032). The alphabet is `A–Z`, `a–z`, `0–9`, `+` and `/`, with `=` padding. This is the DKIM Ed25519 `p=` encoding (RFC 8463, using the base64 `p=` syntax in RFC 6376). It is not base64url (RFC 4648, section 5).

The choice follows the length and the RFC together. Standard base64 of 32 bytes is 44 characters, including one trailing `=`. Unpadded base64url of the same key is 43 characters. Padded base64url is also 44 characters, but it uses `-` and `_` in place of `+` and `/`. RFC 8463 uses standard base64 (RFC 4648 section 4), not base64url. ABIZ requires that encoding: 44 characters, standard alphabet, one trailing `=`.

A conforming `p` value MUST:

- be exactly 44 ASCII characters;
- use only the standard base64 alphabet;
- end with exactly one `=` and no other `=` character;
- decode to exactly 32 bytes;
- be canonical: encoding those 32 bytes again with standard base64 MUST reproduce the value;
- contain no whitespace. DKIM allows folding whitespace inside base64. ABIZ does not, because an ABIZ tag MUST NOT contain spaces.

The 44 characters MUST sit in a single DNS TXT character-string (RFC 1035). Producers MUST NOT split `p` across adjacent character-strings. The value fits well inside the 255-octet character-string limit. Consumers parse `p` after the usual TXT character-string assembly, splitting each tag on the first `=` only, so the padding character remains part of the value.

32 bytes encoded with standard base64 always have this shape. A 31-byte string of 44 characters ends in `==`. A 33-byte string of 44 characters has no padding. Both MUST be rejected.

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

**Ordinary discovery (ABIZ 1.0 compatible).** A consumer MUST accept a well-formed `v=abiz1` assertion whether or not `p` is a valid key. A duplicate `p` tag MUST be rejected, as for any other tag. A `p` value that does not match section 3.3.2 MUST NOT be used as a public key and MUST NOT be described as a signing identity. Discovery MUST NOT fail only because `p` is an opaque 1.0 token, such as a 32-character hexadecimal string.

**Valid key.** If `p` matches section 3.3.2, a 1.1 consumer MAY use those 32 bytes as the Ed25519 public key for that domain.

**Opt-in key check.** When a consumer is asked to check the key, it MUST reject that check if `p` is missing or does not match section 3.3.2. The reference validator does this only with `--check-p-key`. That mode is off by default, so 1.0 records still pass ordinary validation. The format check uses the standard library. It does not need a third-party package.

**Signatures.** A detached signature is the raw 64-byte Ed25519 signature (RFC 8032, PureEd25519, with no pre-hash), encoded in the same standard base64 (88 characters, including the final `==`). The message is the raw octets the producer and consumer agreed. ABIZ does not take DKIM's header canonicalisation or SHA-256 body hash from RFC 8463. Only the public-key encoding is shared with that RFC. Verification succeeds only when RFC 8032 verification succeeds for that key, message and signature.

ABIZ 1.1 does not define which octets a business-record signature covers. Until that is specified, a signature check is only meaningful for a message both sides already agreed. The reference validator can check such a pair with `--p-message` and `--p-signature`. Those arguments require `--check-p-key`. `--p-message` is UTF-8 text. `--p-signature` is the 88-character standard base64 signature. Signature verification needs the optional `cryptography` package. If it is not installed, the format check still runs and the signature check fails with an error that names the missing dependency.

**Wire version.** This proposal does not change `v=abiz1`. Ordinary consumers keep accepting 1.0 tokens. A new version tag is not required for that compatible reading. Whether a later revision should add a version tag so a non-key `p` can be rejected is unresolved (section 3.3.7).

#### 3.3.6 Revocation and retired keys

The current signing key is only the `p` tag in DNS. Producers MUST NOT publish retired keys in DNS. `_abiz` stays limited to the current key. Support for rotation and revocation is required.

A retired public key is carried in the HTTPS business record, under the optional property `retired-keys`. That name is provisional. It is an ABIZ 1.1 (proposed) schema property (section 4). An ABIZ 1.0 record omits it and remains valid.

Each entry MUST include:

- `public-key`: the retired Ed25519 public key, in the 44-character standard base64 form of section 3.3.2;
- `retired-at`: when the key stopped being current, UTC, exactly `YYYY-MM-DDThh:mm:ssZ`;
- `binding-signature`: a PureEd25519 signature made by the current key (the private key for DNS `p`), as standard base64 of the 64-byte signature (88 characters).

An entry MAY include `valid-from`, in the same timestamp form, and `reason`, which is `rotated` or `compromised`. The current `p` value MUST NOT appear in the list. A public key MUST NOT be repeated in the list.

**Binding message.** The current key signs this UTF-8 text. Every line ends with one line feed (U+000A), including the last line. Absent optional fields are empty. The signature field itself is not part of the text.

```text
ABIZ-RETIRED-KEY-V1
domains=<domains>
public-key=<public-key>
valid-from=<valid-from>
retired-at=<retired-at>
reason=<reason>
```

`<domains>` is the record's `domains` array: lowercase, a single trailing dot removed, duplicates removed, sorted by Unicode code point, then joined with `,` and no spaces. The other values are the exact JSON strings from the entry. This is a fixed octet string. It is not a JSON canonicalisation such as RFC 8785.

A consumer MUST rebuild that string from the fetched record. It MUST ignore an entry whose signature does not verify against the current DNS `p`. If `p` is not a confirmed 1.1 key, it MUST ignore every entry. Ignoring an entry does not by itself make the rest of the record invalid. The reference validator reports a bad binding signature only when `--check-p-key` is set. Ordinary validation checks the schema shape only.

Someone who controls only the web host can omit an entry. They cannot add or change one without the current private key. Changing `domains` changes the signed string, so the producer MUST re-sign each entry with the current key after that change.

**Rotation.** The producer generates a new keypair, adds the old public key to `retired-keys` with `retired-at` set and a binding signature from the new key, and publishes the new public key as DNS `p`. Until DNS shows that new `p`, consumers ignore the new entry. Producers SHOULD publish the record and the TXT change together. The TTL SHOULD remain 300 seconds (section 3.1). `examples/registered-us-retired-key.json` is an illustration, with the matching current `p` in `examples/dns-retired-keys.txt`. The private keys are not in the repository.

**Compromise.** When `reason` is `compromised`, `retired-at` is the compromise time the producer asserts. A consumer MUST NOT accept another signature checked with that retired key when that signature is associated with a time later than `retired-at`. A time equal to `retired-at` is not later. These times are producer-asserted. This specification does not define a trusted clock. If the consumer cannot place the other signature in time, it SHOULD refuse the compromised key.

Removing `p`, or replacing it without a `retired-keys` entry, still withdraws the old key as the current identity once the TXT TTL has passed. Consumers MUST NOT keep treating a replaced `p` as the current key after that.

#### 3.3.7 Unresolved points

This proposal does not decide the following. They are recorded so implementers do not treat silence as a decision:

- whether `p` is required for any verified tier;
- where retired keys are carried is decided: the business record, not DNS (section 3.3.6). Still open: the property name (`retired-keys` is provisional), and how long a producer should keep entries;
- whether a record host stores a copy of the public key;
- whether a future wire version should make a non-key `p` invalid, instead of ignoring it for signing;
- whether ABIZ should move to the unpadded base64url form used by `draft-morrison-mcp-dns-discovery` (section 12);
- which octets a signature over the rest of the business record would cover. The retired-key binding message is defined in section 3.3.6.

## 4. Published business record and normative schema

The `h` target MUST be fetched over HTTPS with `Accept: application/json`. It MUST return a JSON object that validates against [the normative ABIZ schema](schemas/abiz-business-record-v1.schema.json) in **JSON Schema Draft 2020-12**. Record conformance is a REQUIRED step for ABIZ conformance; a document that merely parses as JSON does not qualify.

The schema does not define the current key. That value exists only as DNS `p`. When section 3.3 applies, its encoding is normative there: standard base64 of the raw 32-byte Ed25519 public key, the same `p=` encoding DKIM specifies for Ed25519 in RFC 8463 (RFC 4648 section 4, with padding).

ABIZ 1.1 (proposed) adds one optional schema property, `retired-keys` (section 3.3.6). The name is provisional. The property is not required, so an ABIZ 1.0 record stays valid.

### 4.1 Required properties

- `record-version` = `abiz1`
- `business-name`: nonempty public name
- `country`: ISO 3166-1 alpha-2 country code
- `identity-host`: hostname and optional path matching `h`
- `domains`: array of business-controlled domain names this record claims

### 4.2 Registration and MCP

Registered businesses MUST provide `registration-number` and matching `business-key`. Unregistered businesses MAY omit both. If either registration field is present, both MUST be present. The value of `business-key` MUST match `k` where the DNS assertion contains it, and the key's country prefix MUST match the record's `country` in lowercase.

`mcp-server-url` is OPTIONAL. If present it MUST be a valid HTTPS URL, but ABIZ does not assert that the endpoint is open, safe, available or authenticated. Consumers MUST apply appropriate access controls before using any linked agent endpoint.

### 4.3 Optional useful facts

The schema defines optional `description`, `website`, `contact-email`, `contact-phone`, `logo-url`, `last-updated`, `services`, `locations`, `opening-hours`, `links` and, in ABIZ 1.1 (proposed), `retired-keys`. Public data MUST not claim a check that did not occur. A producer MUST omit private personal addresses rather than marking them private in a public record.

Implementations MAY add namespaced values inside `extensions` (reverse-domain keys). Unknown top-level properties MUST be rejected. Extensions MUST NOT override the meaning of mandatory fields.

### 4.4 Independent semantic checks

A Draft 2020-12 structural validator MUST evaluate required properties, types, constraints and dependencies; an implementation MUST also enforce HTTPS URLs and `format` constraints explicitly. Some Draft 2020-12 validators treat `format` as an annotation by default.

Schema validation does **not** check:
- whether a business actually controls a domain;
- whether `identity-host` matches a fetched DNS `h` value;
- whether `business-key` matches `k` and `country`;
- whether a registration number is real;
- whether URLs are reachable;
- whether the business is genuine;
- whether a `retired-keys` binding signature verifies, unless the consumer has opted into the key check (section 3.3.6).

These checks are performed separately, with clear results. The supplied offline reference validator implements schema and local DNS/document checks; it does not query registries or fetch untrusted URLs.

## 5. Producer requirements

A conforming producer MUST:

1. publish no more than one matching `v=abiz1` TXT assertion at `_abiz.<domain>`;
2. include `h=`; include `k=` if claiming a registered business;
3. serve a JSON object at HTTPS `h` when requested as `application/json`;
4. validate the object against the normative schema **before** publishing and whenever updated;
5. ensure its `domains` array declares the domain at which the DNS assertion was published;
6. ensure `identity-host` matches `h` exactly after canonical hostname normalization;
7. ensure DNS `k`, if present, matches the document `business-key` and registration fields.

A producer that publishes an ABIZ 1.1 signing identity MUST set `p` as specified in section 3.3 and MUST NOT publish the private key. Publishing `p` remains optional for ABIZ 1.0. A producer that retires a key MUST follow section 3.3.6 and MUST NOT put that key in DNS.

A human-readable HTML page and Markdown representation SHOULD also be offered, but MAY use content negotiation. A `.md` extension is not required.

## 6. Consumer requirements

A conforming consumer MUST:

1. query TXT at `_abiz.<domain>` and apply matching-record and tag rules;
2. reject absent, duplicate, malformed or conflicting ABIZ assertions;
3. fetch `https://<h>` safely: TLS verification, disallow private/loopback/link-local addresses and unsafe redirects, limit size and timeouts;
4. request and parse JSON without executing scripts;
5. validate it against the exact normative schema (and required format checks);
6. verify its `identity-host` and `domains` match the DNS assertion and queried domain;
7. compare `k` to the business record's registration fields, when `k` is present;
8. label domain-link checks separately from legal registration checks.

For the proposed 1.1 key, a consumer MUST follow sections 3.3.5 and 3.3.6. It MUST NOT treat an opaque 1.0 `p` token as an Ed25519 public key. It MUST ignore a retired-key entry whose binding signature does not verify. A key check is separate from record conformance and from legal registration.

A consumer MAY check registration details against authoritative registries; if it does not, it MUST NOT describe a business as legally verified. A consumer MUST NOT automatically trust instructions, URLs or tool results embedded in the record.

## 7. Conformance claims

| Claim | Minimum requirement | What it does NOT establish |
| --- | --- | --- |
| **ABIZ record conformant** | Draft 2020-12 schema and local semantic validation | Domain control or registered business identity |
| **ABIZ publisher conformant** | Record conformant + valid DNS assertion + correct domain/record linkage + safe HTTPS representation | Legal identity, customer trust or AI visibility |
| **ABIZ consumer conformant** | Required DNS parsing, safe fetch, schema, semantic and clear status handling | Global adoption or recommendations |
| **Registry-confirmed** | Independent authoritative register check, separately labelled | Endorsement by ABIZ |

Conformance MUST identify the schema ID and document revision; do not claim `v=abiz1` alone proves that a business is registered or verified.

## 8. Business units

A parent business MAY list units and their domains in an implementation-specific extension or separate business records. A consumer MUST NOT treat a parent assertion alone as proof that a unit is controlled. A stronger claim requires the unit's own ABIZ DNS pointer and a consistent back-reference. Unit relationships are not defined by the base schema in ABIZ 1.0.

## 9. Security and privacy

DNS assertions are public and not authenticated by default. Producers SHOULD use DNSSEC where available; consumers SHOULD verify DNSSEC where supported. DNS control alone does not prove business ownership. An Ed25519 public key in `p` does not change that. It shows which key the domain controller published. It does not sign the TXT record by itself, and it does not prove legal identity. An opaque 1.0 `p` token MUST NOT be presented as a cryptographic identity. The private key is the business's property and MUST be protected. In hosted mode a provider MAY hold that key and sign for the business. It MUST follow the export and deletion rules in section 3.3.4. Holding the key does not transfer ownership. Retired keys belong in the business record, each bound by a signature from the current key (section 3.3.6). A host that does not hold that private key cannot add a valid entry. It can omit one. Compromise times in that list are producer-asserted. Consumers MUST implement SSRF safeguards, HTTPS-only target handling, host/redirect validation, content size/time limits and output escaping. MCP endpoints MUST not be called automatically solely because they appear in a record.

A publisher MUST consider personal data and only publish intentionally public facts. A domain claim MUST NOT be presented as a legal verification badge.

## 10. IANA and governance

The intended globally scoped underscore label is `_abiz`, RR type TXT. Registration has been **requested but is not confirmed**. Publication does not claim completed IANA registration.

The standard is open and provider-independent. To.Co Technologies Limited is the managing organisation. Implementers can comment or propose changes through the [public repository](https://github.com/abiz-org/abiz-agentic-business-record). No personal email address is required for participation.

## 11. References

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [RFC 8552 — Underscored and Globally Scoped DNS Node Names](https://www.rfc-editor.org/rfc/rfc8552)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)
- [RFC 4648 — The Base16, Base32, and Base64 Data Encodings](https://www.rfc-editor.org/rfc/rfc4648) (section 4 is the ABIZ `p` encoding)
- [RFC 6376 — DomainKeys Identified Mail (DKIM) Signatures](https://www.rfc-editor.org/rfc/rfc6376) (`p=` base64 syntax)
- [RFC 8032 — Edwards-Curve Digital Signature Algorithm (EdDSA)](https://www.rfc-editor.org/rfc/rfc8032)
- [RFC 8463 — A New Cryptographic Signature Method for DomainKeys Identified Mail (DKIM)](https://www.rfc-editor.org/rfc/rfc8463)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [draft-morrison-mcp-dns-discovery](https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/) (individual Internet-Draft; see section 12)

## 12. Interoperability

ABIZ 1.1 (proposed) encodes the DNS `p` tag as standard base64 with padding, matching the Ed25519 public key in DKIM (RFC 8463). That is a 44-character encoding of 32 bytes. ABIZ shares that public-key encoding only. Signature checks use PureEd25519 over the agreed message octets (section 3.3.5). See section 3.3.2.

[draft-morrison-mcp-dns-discovery](https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/) also puts Ed25519 public keys in DNS TXT records. The current draft name is unchanged. Revision 09 (21 October 2026) is the revision consulted for this text; the datatracker link above tracks later revisions. In that draft, `_mcp` and `_alter` carry the key as `pk=ed25519:` followed by unpadded base64url (RFC 4648 section 5). A 32-byte key is then 43 characters, not 44. ABIZ MUST NOT be read as using that encoding. A consumer MUST NOT treat an ABIZ `p` value as that draft's `pk` value, or the reverse, without decoding and encoding again.

The two mechanisms can appear in one zone at different owner names (`_abiz`, and the draft's `_mcp` or `_alter`). The draft is an individual submission. It is not an IETF standard, and this specification does not require it.

Whether ABIZ should adopt that draft's base64url form instead of RFC 8463 is unresolved. See section 3.3.7.
