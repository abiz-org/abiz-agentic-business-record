# ABIZ — Agentic Business Record Specification

**Published version:** ABIZ 1.0  
**DNS wire version:** `v=abiz1` (unchanged)  
**Date:** 2026-10-23  
**1.1 proposal:** 2026-10-31, revised 2026-11-03 (not the published version; see sections 3.1.1, 3.3 and 4.2)  
**Managing organisation:** To.Co Technologies Limited, United Kingdom  
**Planned official site:** `abizrecord.org`  
**Public source:** https://github.com/abiz-org/abiz-agentic-business-record  
**Normative schema:** `schemas/abiz-business-record-v1.schema.json`

This is the **ABIZ 1.0 published specification**. Publication does not imply IANA registration or endorsement. Implementers MUST NOT present domain control as proof of a registered business's legal identity, and MUST NOT claim guaranteed AI discovery, ranking or recommendation.

Sections 3.1.1, 3.3 and 4.2 are **proposed ABIZ 1.1** changes: a relaxed tag-list syntax that accepts optional whitespace, an Ed25519 key in the optional DNS `p` tag, and a defined business-key grammar with country, subdivision and registration-number rules, with `k` optional for every business. They are not part of the ABIZ 1.0 conformance baseline. The whitespace change and optional `k` are backwards-compatible. The `p` and business-key changes are deliberately not: a non-key `p` value is invalid (section 3.3.7), and existing keys must be re-expressed (section 4.2.5). The wire version stays `v=abiz1`.

## 1. Scope and purpose

ABIZ provides a provider-independent method for locating a business's **public business record** from a domain it controls. Producers publish a versioned DNS TXT assertion at `_abiz.{domain}` pointing to a record served over HTTPS. Consumers discover that record, validate its structure using the **normative JSON Schema**, and perform cross-source consistency checks.

ABIZ is not a legal identity registry, endorsement scheme, payment system or requirement to use one provider. **An MCP server is optional**. Business records can be published by registered or unregistered businesses.

The key words MUST, MUST NOT, SHOULD and MAY have their RFC 2119 / RFC 8174 meanings.

## 2. Terms

- **Producer:** entity publishing an ABIZ pointer at a domain it controls.
- **Consumer:** software reading and validating the pointer and published business record.
- **Business record:** JSON representation of public business facts conforming to the normative schema.
- **Record host:** the DNS hostname plus optional path in the `h=` tag (no `https://` prefix).
- **Business key:** optional registration identifier in `country[-subdivision]-registration-number` form (section 4.2.1).
- **Domain check:** checks that a DNS assertion and fetched business document refer to each other; distinct from government registration checks.
- **Record conformance:** schema and local semantic checks pass.
- **Publisher conformance:** record conformance plus the DNS / document requirements in this specification.
- **Consumer conformance:** implements the checks and rejects invalid assertions.

## 3. DNS assertion

### 3.1 Owner, RRset and version

An ABIZ DNS assertion is a TXT record at `_abiz.<domain>`. The first tag MUST be `v=abiz1` (section 3.1.1). There MUST be exactly one matching `v=abiz1` TXT record at that owner name. Zero means no ABIZ assertion; two or more means an invalid assertion. A TXT record whose first tag is not `v=abiz1` (for example an SPF record, or `V=ABIZ1`) is not an ABIZ assertion and is not counted.

A TXT record made of several character-strings (RFC 1035) is read as their concatenation, with nothing added between them, as for SPF (RFC 7208 section 3.3) and DKIM (RFC 6376 section 3.6.2.2).

The TTL SHOULD be 300 seconds. Tag names and values are case-sensitive, except that `k` is compared case-insensitively (section 4.2.4). A consumer MUST ignore unknown additional tags and MUST reject an assertion in which a recognised tag (`v`, `h`, `k`, `p`) appears more than once.

#### 3.1.1 Tag-list syntax (ABIZ 1.1, proposed)

ABIZ 1.0 allowed no whitespace anywhere in the assertion. ABIZ 1.1 proposes the tag-list syntax used by other DNS TXT policy records: optional whitespace around `;` and `=`, leading and trailing whitespace, and one trailing `;`. This follows DKIM (RFC 6376 section 3.2, `tag-list`), DMARC (RFC 7489 section 6.4, `dmarc-sep = *WSP %x3b *WSP`, with a final optional separator), MTA-STS (RFC 8461 section 3.1, `sts-field-delim = *WSP ";" *WSP`) and SMTP TLS Reporting (RFC 8460 section 3, `field-delim = *WSP ";" *WSP`). SPF (RFC 7208 section 4.6.1 and section 12) likewise separates terms with one or more spaces and allows trailing spaces. Every value that was valid under ABIZ 1.0 parses under this syntax, with the same tags. (Section 3.3.7 separately makes a non-key `p` value invalid.)

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

Producers SHOULD publish the compact form with no optional whitespace, for example `v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co`. A strict ABIZ 1.0 consumer rejects any whitespace, so the compact form is the one every consumer accepts. Consumers that claim ABIZ 1.1 MUST accept the full syntax above.

### 3.2 Tags

| Tag | Required | Meaning |
| --- | --- | --- |
| `v=abiz1` | MUST | Wire protocol family; always first |
| `h=<record-host>` | MUST | HTTPS hostname plus optional path of the public business record, without URL scheme |
| `k=<business-key>` | MAY | Optional for every business, registered or not. When present, MUST follow section 4.2.1 and MUST equal the record's `business-key`, compared case-insensitively (section 4.2.4). Registration fields in the record do not require `k` |
| `p=<public-key>` | MAY | Optional. In ABIZ 1.1 (proposed), when present, MUST be an Ed25519 public key in standard base64; any other value is invalid (section 3.3). ABIZ 1.0 allowed an opaque provider token. Not a password and not proof of legal identity |

`h` MAY refer to a record hosted by an independent service. A producer need not own the host serving the record; it MUST control the queried DNS domain and have permission for the published record.

**Example — registered business (US):**

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co"
```

**Example — unregistered business (US):**

```dns
_abiz.marketstand.example. 300 IN TXT "v=abiz1;h=market-stand-repairs-portland.biz.to.co"
```

Both are illustrative, invented businesses. These entries demonstrate alternatives on **different DNS owners**. A business MUST NOT publish both as independent matching assertions at one owner name.

These hostnames are examples of to.co's country-based registered-company hostname and town-based `.biz.to.co` hostname. ABIZ does not require either naming scheme.

**Example — ABIZ 1.1 (proposed) Ed25519 `p` key:**

```dns
_abiz.harbourbikes.example. 300 IN TXT "v=abiz1;k=us-or-123456;h=harbour-bike-repair.or.us.to.co;p=oS5YhE6Qz35Id1hMp3XOI3eQWW03DVgY3kU6rEdlodQ="
```

`p` here is a throwaway Ed25519 public key. The private key is not part of this specification and is not in the repository. See `examples/dns-ed25519-p.txt` and section 3.3.

### 3.3 The `p` tag (ABIZ 1.1, proposed)

This section is a proposal. It changes the meaning of `p` on purpose: from ABIZ 1.1, `p` is either absent or a valid Ed25519 public key. Any other value makes the assertion invalid. Section 3.3.7 covers migrating existing values.

#### 3.3.1 Role

In ABIZ 1.0, `p` was optional and provider-specific: a non-empty token that was not checked as a key. Deployments used it for a one-time domain-control handshake, including a 32-character hexadecimal token.

ABIZ 1.1 makes that tag a persistent signing identity. The business, or a provider acting for it, generates an Ed25519 keypair and publishes the public key in `p`. The private key remains the business's property (section 3.3.4). A later signature can be checked against the published key. The one-time token is replaced by a key the business can keep using.

`p` remains OPTIONAL. An assertion without `p` is valid. An assertion with `p` is valid only when `p` is a key that matches section 3.3.2.

Publishing the key shows that the controller of the domain put that public key in DNS. It does not authenticate the TXT record. It does not prove that a registered business owns the domain. Section 9 still applies: DNS assertions are public and unauthenticated by default, and DNS control alone does not prove business ownership. Producers and consumers SHOULD still use DNSSEC where they can. DNSSEC authenticates the DNS data. The key names a signer the domain controller published.

`p` is DNS-only. The business record does not contain the current key or any previous key (section 4).

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

**Discovery.** A consumer that claims ABIZ 1.1 MUST check `p` whenever it is present. If `p` does not match section 3.3.2, the assertion is invalid, exactly as for a malformed `h`. This includes opaque ABIZ 1.0 tokens such as a 32-character hexadecimal string, and base64url keys. A duplicate `p` tag MUST be rejected, as for any other recognised tag. An assertion without `p` is checked as before. The format check needs only base64 decoding, with no cryptographic library.

**Valid key.** If `p` matches section 3.3.2, the consumer MAY use those 32 bytes as the Ed25519 public key for that domain.

**Signatures.** A detached signature is the raw 64-byte Ed25519 signature (RFC 8032, PureEd25519, with no pre-hash), encoded in the same standard base64 (88 characters, including the final `==`). The message is the raw octets the producer and consumer agreed. ABIZ does not take DKIM's header canonicalisation or SHA-256 body hash from RFC 8463. Only the public-key encoding is shared with that RFC. Verification succeeds only when RFC 8032 verification succeeds for that key, message and signature.

ABIZ 1.1 does not define which octets a business-record signature covers. Until that is specified, a signature check is only meaningful for a message both sides already agreed. The reference validator can check such a pair with `--p-message` (UTF-8 text) and `--p-signature` (the 88-character standard base64 signature). Signature verification needs the optional `cryptography` package; without it, the format check still runs and the signature check fails with an error that names the missing dependency.

**Wire version.** This proposal does not change `v=abiz1`. A strict ABIZ 1.0 consumer that treats `p` as opaque still accepts a 1.1 key, because a key is a valid 1.0 token. The reverse does not hold: a 1.1 consumer rejects a non-key `p` (section 3.3.7).

#### 3.3.6 Rotation and revocation

The current signing key is only the `p` tag in DNS. Producers MUST NOT publish previous keys in DNS, and the business record does not carry them. `_abiz` stays limited to the current key.

**Rotation.** The producer generates a new keypair and publishes the new public key as DNS `p`. The TTL SHOULD remain 300 seconds (section 3.1). Once the TXT TTL has passed, consumers MUST NOT keep treating the replaced `p` as the current key.

**Revocation.** Removing `p` withdraws the key as the current identity once the TXT TTL has passed.

ABIZ 1.1 does not define a published list of retired keys. The schema reserves the shape of a retired-key entry as a nested definition, `$defs/retired-key` (section 4). It is not a record property, and a business record that contains `retired-keys` or any other unknown top-level property MUST be rejected. A later revision, or another document that references the definition, may use that shape.

#### 3.3.7 Migration of existing `p` values

All existing `p` values are upgraded by this revision. A `p` value published under ABIZ 1.0 that is not a valid key under section 3.3.2, such as a 32-character hexadecimal handshake token, fails ABIZ 1.1 validation, and the whole assertion is invalid. Producers MUST republish `p` as an Ed25519 public key (section 3.3.3) or remove it. Because `p` is optional, an assertion without `p` stays valid.

This is a deliberate breaking change for non-key `p` values. The business-key rules of section 4.2 are the other one (section 4.2.5). Every other ABIZ 1.0 assertion and record stays valid under ABIZ 1.1, with the same meaning. The whitespace relaxation of section 3.1.1 only adds accepted forms.

#### 3.3.8 Unresolved points

This proposal does not decide the following. They are recorded so implementers do not treat silence as a decision:

- whether `p` is required for any verified tier;
- whether a record host stores a copy of the public key;
- whether, and where, a later revision publishes retired keys using `$defs/retired-key`, and how long entries would be kept;
- which octets a signature over the business record would cover.

Decided in this revision: `p` uses standard base64 (RFC 4648 section 4, RFC 8463), not base64url; and from ABIZ 1.1 a non-key `p` is invalid.

## 4. Published business record and normative schema

The `h` target MUST be fetched over HTTPS with `Accept: application/json`. It MUST return a JSON object that validates against [the normative ABIZ schema](schemas/abiz-business-record-v1.schema.json) in **JSON Schema Draft 2020-12**. Record conformance is a REQUIRED step for ABIZ conformance; a document that merely parses as JSON does not qualify.

The schema does not define the current key. That value exists only as DNS `p`, and its encoding is normative in section 3.3.2: standard base64 of the raw 32-byte Ed25519 public key, the same `p=` encoding DKIM specifies for Ed25519 in RFC 8463 (RFC 4648 section 4, with padding).

ABIZ 1.1 (proposed) adds no record property. The schema's `$defs` holds a nested definition, `retired-key`, that reserves the shape of a retired Ed25519 key entry (section 3.3.6). No record property refers to it, so a business record cannot carry it.

### 4.1 Required properties

- `record-version` = `abiz1`
- `business-name`: nonempty public name
- `country`: assigned ISO 3166-1 alpha-2 country code, case-insensitive, canonically lowercase (section 4.2.4)
- `identity-host`: hostname and optional path matching `h`
- `domains`: array of business-controlled domain names this record claims

### 4.2 Registration and MCP

`business-key` and `registration-number` are OPTIONAL, for registered and unregistered businesses alike. If either is present, both MUST be present. The country part of `business-key` MUST equal the record's `country`, and its registration-number part MUST equal `registration-number`, both compared case-insensitively. Including these fields in the record does not require `k` in DNS. If the DNS assertion contains `k`, `k` MUST equal `business-key` (section 4.2.4).

#### 4.2.1 Business key grammar (ABIZ 1.1, proposed)

The business key, used as DNS `k` and record `business-key`, has this ABNF (RFC 5234; quoted strings are case-insensitive, and `ALPHA` covers both cases):

```abnf
business-key = country "-" [ subdivision "-" ] reg-number
country      = 2ALPHA              ; assigned ISO 3166-1 alpha-2 code (section 4.2.2)
subdivision  = 1*3( ALPHA / DIGIT ) ; assigned ISO 3166-2 code of that country, without its "CC-" prefix
reg-number   = 1*( ALPHA / DIGIT )  ; normalised registration number (section 4.2.3)
```

The whole key MUST NOT exceed 128 characters. `reg-number` never contains `-`, so a key splits on `-` into exactly two parts (country, number) or three parts (country, subdivision, number). Any other number of parts is invalid. The grammar is unambiguous without the country table.

- `country` MUST be an assigned ISO 3166-1 alpha-2 code. Reserved and user-assigned codes are invalid: `uk` and `eu` are not assigned, so the United Kingdom is `gb`; `xk` is user-assigned.
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

`registration-number`, and the `reg-number` part of the key, MUST be one or more ASCII letters and digits (`A–Z`, `a–z`, `0–9`). Spaces and all other characters are invalid. A consumer MUST NOT normalise a received value; it MUST reject one that is not ASCII alphanumeric.

A producer derives the value from the number as the register issues it:

1. apply Unicode NFKC normalisation, which turns full-width digits and letters (`０-９`, `Ａ-Ｚ`) into ASCII;
2. remove whitespace, `-`, `.`, `/`, and the hyphen and dash characters U+2010 to U+2015 and U+2212;
3. convert ASCII letters to uppercase (the canonical form);
4. check that the result is one or more ASCII letters and digits. If it is not, for example because it still contains kanji or `&`, the business cannot publish a business key.

Leading zeros and letter prefixes are part of the number and MUST be kept: `01234567` and `1234567` are different numbers, and `SC123456` keeps `SC`. Examples: `HRB 12345` at Hamburg becomes `K1101RHRB12345`; `１２３４５６７８９０１２３` becomes `1234567890123`; `CHE-123.456.789` becomes `CHE123456789`; `12.345.678/0001-95` becomes `12345678000195`; a Corporations Canada number shown as `1234567-8` becomes `12345678`.

#### 4.2.4 Case and comparison

Case is not significant anywhere in a business key, nor in the record's `country` and `locations[].country`. Consumers MUST compare country codes, subdivision codes, registration numbers and whole business keys case-insensitively (ASCII case folding). `US-OR-123456`, `us-or-123456` and `us-OR-123456` are the same key.

Producers SHOULD publish the canonical form: country and subdivision in lowercase, registration number in uppercase, for example `us-or-123456`, `ca-bc-BC0578072`, `de-K1101RHRB12345`. Record `country` SHOULD also be lowercase.

#### 4.2.5 Migration of existing keys

This is a breaking change for keys. ABIZ 1.0 allowed `.`, `_` and `-` inside the number and had no subdivision rule, so some 1.0 keys are invalid or ambiguous under 1.1. Producers MUST re-express existing `k` and `business-key` values in the section 4.2.1 form. For example, the 1.0 example key `us-OR123456` becomes `us-or-123456`, with `registration-number` `123456`.

#### 4.2.6 MCP

`mcp-server-url` is OPTIONAL. If present it MUST be a valid HTTPS URL, but ABIZ does not assert that the endpoint is open, safe, available or authenticated. Consumers MUST apply appropriate access controls before using any linked agent endpoint.

### 4.3 Optional useful facts

The schema defines optional `description`, `website`, `contact-email`, `contact-phone`, `logo-url`, `last-updated`, `services`, `locations`, `opening-hours` and `links`. Public data MUST not claim a check that did not occur. A producer MUST omit private personal addresses rather than marking them private in a public record.

Implementations MAY add namespaced values inside `extensions` (reverse-domain keys). Unknown top-level properties MUST be rejected. Extensions MUST NOT override the meaning of mandatory fields.

### 4.4 Independent semantic checks

A Draft 2020-12 structural validator MUST evaluate required properties, types, constraints and dependencies; an implementation MUST also enforce HTTPS URLs and `format` constraints explicitly. Some Draft 2020-12 validators treat `format` as an annotation by default.

Schema validation does **not** check:
- whether a business actually controls a domain;
- whether `identity-host` matches a fetched DNS `h` value;
- whether `business-key` matches `k` and `country`, or uses an assigned country and subdivision code (section 4.2);
- whether a registration number is real;
- whether URLs are reachable;
- whether the business is genuine.

These checks are performed separately, with clear results. The supplied offline reference validator implements schema and local DNS/document checks; it does not query registries or fetch untrusted URLs.

## 5. Producer requirements

A conforming producer MUST:

1. publish no more than one matching `v=abiz1` TXT assertion at `_abiz.<domain>`;
2. include `h=`; MAY include `k=`, for a registered or unregistered business;
3. serve a JSON object at HTTPS `h` when requested as `application/json`;
4. validate the object against the normative schema **before** publishing and whenever updated;
5. ensure its `domains` array declares the domain at which the DNS assertion was published;
6. ensure `identity-host` matches `h` exactly after canonical hostname normalization;
7. ensure DNS `k`, if present, equals the document `business-key` (section 4.2.4), and that `business-key` and `registration-number` follow sections 4.2.1 to 4.2.3.

A producer that publishes `p` MUST set it to an Ed25519 public key as specified in section 3.3, and MUST NOT publish the private key. Publishing `p` remains optional. A producer that still publishes a non-key ABIZ 1.0 `p` token MUST republish it as a key or remove it (section 3.3.7). A producer that rotates a key MUST follow section 3.3.6 and MUST NOT put the old key in DNS.

A human-readable HTML page and Markdown representation SHOULD also be offered, but MAY use content negotiation. A `.md` extension is not required.

## 6. Consumer requirements

A conforming consumer MUST:

1. query TXT at `_abiz.<domain>` and apply matching-record and tag rules;
2. reject absent, duplicate, malformed or conflicting ABIZ assertions;
3. fetch `https://<h>` safely: TLS verification, disallow private/loopback/link-local addresses and unsafe redirects, limit size and timeouts;
4. request and parse JSON without executing scripts;
5. validate it against the exact normative schema (and required format checks);
6. verify its `identity-host` and `domains` match the DNS assertion and queried domain;
7. when `k` is present, check it against section 4.2.1 and compare it case-insensitively to the record's `business-key`; reject the assertion if the record has no `business-key`;
8. label domain-link checks separately from legal registration checks.

A consumer that claims ABIZ 1.1 MUST parse the assertion with the tag-list syntax of section 3.1.1, so it accepts optional whitespace around `;` and `=` and one trailing `;`. It MUST reject an assertion whose `p` is present but is not a valid key under section 3.3.2, including an ABIZ 1.0 hexadecimal token or a base64url value, and MUST follow sections 3.3.5 and 3.3.6. A key check is separate from record conformance and from legal registration.

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

DNS assertions are public and not authenticated by default. Producers SHOULD use DNSSEC where available; consumers SHOULD verify DNSSEC where supported. DNS control alone does not prove business ownership. An Ed25519 public key in `p` does not change that. It shows which key the domain controller published. It does not sign the TXT record by itself, and it does not prove legal identity. A non-key `p` value is invalid under ABIZ 1.1 (section 3.3.7) and MUST NOT be presented as a cryptographic identity. The private key is the business's property and MUST be protected. In hosted mode a provider MAY hold that key and sign for the business. It MUST follow the export and deletion rules in section 3.3.4. Holding the key does not transfer ownership. Consumers MUST implement SSRF safeguards, HTTPS-only target handling, host/redirect validation, content size/time limits and output escaping. MCP endpoints MUST not be called automatically solely because they appear in a record.

A publisher MUST consider personal data and only publish intentionally public facts. A domain claim MUST NOT be presented as a legal verification badge.

## 10. IANA and governance

The intended globally scoped underscore label is `_abiz`, RR type TXT. Registration has been **requested but is not confirmed**. Publication does not claim completed IANA registration.

The standard is open and provider-independent. To.Co Technologies Limited is the managing organisation. Implementers can comment or propose changes through the [public repository](https://github.com/abiz-org/abiz-agentic-business-record). No personal email address is required for participation.

## 11. References

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [RFC 8552 — Underscored and Globally Scoped DNS Node Names](https://www.rfc-editor.org/rfc/rfc8552)
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

ABIZ 1.1 (proposed) encodes the DNS `p` tag as standard base64 with padding, matching the Ed25519 public key in DKIM (RFC 8463). That is a 44-character encoding of 32 bytes. ABIZ shares that public-key encoding only. Signature checks use PureEd25519 over the agreed message octets (section 3.3.5). See section 3.3.2.

[draft-morrison-mcp-dns-discovery](https://datatracker.ietf.org/doc/draft-morrison-mcp-dns-discovery/) also puts Ed25519 public keys in DNS TXT records. The current draft name is unchanged. Revision 09 (21 October 2026) is the revision consulted for this text; the datatracker link above tracks later revisions. In that draft, `_mcp` and `_alter` carry the key as `pk=ed25519:` followed by unpadded base64url (RFC 4648 section 5). A 32-byte key is then 43 characters, not 44. ABIZ MUST NOT be read as using that encoding. A consumer MUST NOT treat an ABIZ `p` value as that draft's `pk` value, or the reverse, without decoding and encoding again.

The two mechanisms can appear in one zone at different owner names (`_abiz`, and the draft's `_mcp` or `_alter`). The draft is an individual submission. It is not an IETF standard, and this specification does not require it.

ABIZ does not adopt that draft's base64url form. `p` uses the RFC 8463 standard base64 form, and a base64url `p` value is invalid (section 3.3.2). The DKIM precedent applies to the same kind of record, a DNS TXT tag-list, and standard base64 needs no escaping in TXT.
