# ABIZ — Agentic Business Record Specification

**Published version:** ABIZ 1.0  
**DNS wire version:** `v=abiz1` (unchanged)  
**Date:** 2026-10-23  
**Managing organisation:** To.Co Technologies Limited, United Kingdom  
**Planned official site:** `abizrecord.org`  
**Public source:** https://github.com/abiz-org/agentic-business-record  
**Normative schema:** `schemas/abiz-business-record-v1.schema.json`

This is the **ABIZ 1.0 published specification**. Publication does not imply IANA registration or endorsement. Implementers MUST NOT present domain control as proof of a registered business's legal identity, and MUST NOT claim guaranteed AI discovery, ranking or recommendation.

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
| `p=<proof-token>` | MAY | Provider-specific or optional verification token; not a password or a general proof of legal identity |

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

## 4. Published business record and normative schema

The `h` target MUST be fetched over HTTPS with `Accept: application/json`. It MUST return a JSON object that validates against [the normative ABIZ schema](schemas/abiz-business-record-v1.schema.json) in **JSON Schema Draft 2020-12**. Record conformance is a REQUIRED step for ABIZ conformance; a document that merely parses as JSON does not qualify.

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

The schema defines optional `description`, `website`, `contact-email`, `contact-phone`, `logo-url`, `last-updated`, `services`, `locations`, `opening-hours` and `links`. Public data MUST not claim a check that did not occur. A producer MUST omit private personal addresses rather than marking them private in a public record.

Implementations MAY add namespaced values inside `extensions` (reverse-domain keys). Unknown top-level properties MUST be rejected. Extensions MUST NOT override the meaning of mandatory fields.

### 4.4 Independent semantic checks

A Draft 2020-12 structural validator MUST evaluate required properties, types, constraints and dependencies; an implementation MUST also enforce HTTPS URLs and `format` constraints explicitly. Some Draft 2020-12 validators treat `format` as an annotation by default.

Schema validation does **not** check:
- whether a business actually controls a domain;
- whether `identity-host` matches a fetched DNS `h` value;
- whether `business-key` matches `k` and `country`;
- whether a registration number is real;
- whether URLs are reachable;
- whether the business is genuine.

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

DNS assertions are public and not authenticated by default. Producers SHOULD use DNSSEC where available; consumers SHOULD verify DNSSEC where supported. DNS control alone does not prove business ownership. Consumers MUST implement SSRF safeguards, HTTPS-only target handling, host/redirect validation, content size/time limits and output escaping. MCP endpoints MUST not be called automatically solely because they appear in a record.

A publisher MUST consider personal data and only publish intentionally public facts. A domain claim MUST NOT be presented as a legal verification badge.

## 10. IANA and governance

The intended globally scoped underscore label is `_abiz`, RR type TXT. Registration has been **requested but is not confirmed**. Publication does not claim completed IANA registration.

The standard is open and provider-independent. To.Co Technologies Limited is the managing organisation. Implementers can comment or propose changes through the [public repository](https://github.com/abiz-org/agentic-business-record). No personal email address is required for participation.

## 11. References

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [RFC 8552 — Underscored and Globally Scoped DNS Node Names](https://www.rfc-editor.org/rfc/rfc8552)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)
- [Model Context Protocol](https://modelcontextprotocol.io/)
