# Becoming an Agentic Business using ABIZ in Australia

*A guide to ABIZ 1.1 (proposed). [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.*

## 1. What this means for a business in Australia

People increasingly ask AI assistants things like "which bakery near me is open on Sunday?" or "does this company really own this website?". ABIZ (Agentic Business Record) is an open standard that lets a business publish its public facts in a form that compatible software can find and check: a small JSON document with those facts, and a DNS TXT record on the business's own domain that points to it.

With ABIZ, a compatible assistant can start from your domain, find your record, validate it against the published JSON Schema, and confirm that the domain and the record refer to each other. It works for registered companies and for businesses that are not registered. It does not guarantee that any assistant will find, rank or recommend you, and it is not an official badge.

In Australia, a company can add its ACN as a business key; a sole trader or other entity without an ACN can use its ABN, or publish its record without a key.

## 2. How to publish an ABIZ record

### Required fields

| Field | What to put | Example |
| --- | --- | --- |
| `record_version` | Always `abiz1` | `abiz1` |
| `business_name` | Your public business name | `Harbourside Bike Repairs Pty Ltd` |
| `country` | The ISO 3166-1 alpha-2 country code, lower case | `au` |
| `identity_host` | The host, and optional path, where the record is served; it must match DNS `h` | `harboursidebikerepairs.au.to.co` |
| `domains` | The domains you control that this record claims | `["harboursidebikerepairs.example"]` |

### The optional business key `k`

`k` is optional for every business. If you publish it, it must follow section 4.2 of the specification and it must equal the record's `business_key`. Case does not matter when keys are compared, but the canonical form has a lower-case country code and an upper-case registration number.

Format: `au-` followed by the 9-digit Australian Company Number (ACN), with no state code (section 4.2.2). ASIC keeps one national register, so it does not matter in which state the company trades.

- **No ACN?** An entity that has no ACN, such as a sole trader, partnership or trust, may use its 11-digit Australian Business Number (ABN): `au-12345678901`.
- **Have both?** A company uses its ACN, not its ABN, so that it has exactly one key.

**Normalising the number (section 4.2.3).** Start from the number exactly as the register issues it. Apply Unicode NFKC normalisation; remove spaces, hyphens, dots and slashes; convert letters to upper case; keep leading zeros and letter prefixes. If anything else is left, such as brackets, `&` or an accented letter, the number cannot be expressed and you cannot publish a business key: leave out `k`, `business_key` and `registration_number`.

**Example (fictional):** ACN `123 456 789` becomes `123456789`, and the key is `au-123456789`.

If you include `business_key` and `registration_number` in the record, include both, and make the number part of the key equal `registration_number`. Including them does not oblige you to publish `k` in DNS. If you do publish `k`, the record must contain the matching `business_key`.

### The DNS TXT record

Publish exactly one TXT record starting with `v=abiz1` at `_abiz.` followed by your domain. Use the compact form with no spaces (section 3.1.1) and a TTL of 300 seconds:

```dns
_abiz.harboursidebikerepairs.example. 300 IN TXT "v=abiz1;k=au-123456789;h=harboursidebikerepairs.au.to.co;p=Y06f66e3yXqdpeT3VDpbJ5iApPFpcHJlB1qPOLFPB4M="
```

A business with no registration number, or one that prefers not to publish it, simply leaves out `k`:

```dns
_abiz.marketstand.example. 300 IN TXT "v=abiz1;h=marketstand.biz.to.co"
```

### Example record (JSON)

This example is fictional. It passes the reference validator.

```json
{
  "record_version": "abiz1",
  "business_name": "Harbourside Bike Repairs Pty Ltd",
  "country": "au",
  "business_key": "au-123456789",
  "registration_number": "123456789",
  "identity_host": "harboursidebikerepairs.au.to.co",
  "domains": [
    "harboursidebikerepairs.example"
  ],
  "public_key": "Y06f66e3yXqdpeT3VDpbJ5iApPFpcHJlB1qPOLFPB4M=",
  "description": "Bicycle servicing and repairs near Circular Quay.",
  "website": "https://harboursidebikerepairs.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Sydney",
      "region": "NSW",
      "country": "au",
      "public": true
    }
  ],
  "opening_hours": [
    "Mo-Fr 07:30-18:00",
    "Sa 08:00-14:00"
  ],
  "signature": "tUewoMUAOQDBprBaP95Z9E+BpI/KEbeEgkPCQ8nBIH7HxVi8ToVm7tbzqA9ryoYggyFhHV8uy6jqUvfpvW99DA=="
}
```

### Where the record lives

You can serve the record yourself from any HTTPS URL that returns the JSON document, for example `h=www.harboursidebikerepairs.example/abiz.json`, or use any compatible provider. ABIZ does not require a particular provider or naming scheme. Whichever you choose, `identity_host` in the record must match `h`, and `domains` must include the domain where you publish the TXT record.

Before you publish, check the record and the DNS value with the reference validator:

```sh
python scripts/validate.py record.json \
  --domain harboursidebikerepairs.example \
  --dns-value 'v=abiz1;k=au-123456789;h=harboursidebikerepairs.au.to.co;p=Y06f66e3yXqdpeT3VDpbJ5iApPFpcHJlB1qPOLFPB4M='
```

## 3. Using a provider and MCP

The Model Context Protocol (MCP) is an open protocol that lets AI assistants call tools and read data from outside services in a standard way. An ABIZ record may include an optional `mcp_server_url`, an HTTPS address of an MCP server that can answer questions about the business, such as opening hours, services or availability. ABIZ does not require an MCP server, and a listed server is not vouched for: compatible software must not call it automatically just because it appears in a record, and must apply its own access controls.

For example, a provider might host the record for Harbourside Bike Repairs at `harboursidebikerepairs.au.to.co`, publish the DNS TXT record through its own set-up flow, and list its MCP server in `mcp_server_url`. You can move to another provider, or to self-hosting, by changing `h` and the record's `identity_host`.

To see how one provider describes this for Australian businesses, see [ABIZ records on to.co](https://to.co/en-au/abiz).

## 4. Keys and signatures (ABIZ 1.1)

- **`p` is optional.** When present, it must be an Ed25519 public key in standard base64: exactly 44 characters, ending in a single `=`, decoding to 32 bytes (section 3.3.2). Any other value, such as an old ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid. Replace it with a key or remove it.
- **Example** (the key below is a throwaway example key; its private key was discarded). Never copy it: publish your own key or leave `p` out.

  ```dns
  _abiz.harboursidebikerepairs.example. 300 IN TXT "v=abiz1;k=au-123456789;h=harboursidebikerepairs.au.to.co;p=Y06f66e3yXqdpeT3VDpbJ5iApPFpcHJlB1qPOLFPB4M="
  ```

- **The private key belongs to the business.** It must never appear in DNS, in the record or in a public repository. A provider may generate and hold it for you (hosted mode), but it must let you export it at any time, for example as PKCS#8, and delete its copy on request (section 3.3.4).
- **Signing.** Software can check a detached Ed25519 signature against the published key. The business record repeats the key as `public_key` and carries a `signature` over the whole record, made with the private key (SPEC section 4.6). Software verifies the signature and checks that `public_key` equals `p`; a record that fails either check is not verified.
- **Rotation and retired keys.** To rotate, publish the new key in `p`; the old key stops being current once the TXT TTL has passed. ABIZ 1.1 does not publish retired keys: not in DNS, and not in the record (a `retired_keys` property is rejected).
- **What a key proves.** It shows which key the controller of the domain published. It does not sign the TXT record by itself, and it does not prove legal identity. Use DNSSEC where your DNS host supports it.

## 5. What AI tools will see

Compatible software that reads your record can answer questions such as:

- "Is Harbourside Bike Repairs open on Saturday?"
- "What does Harbourside Bike Repairs offer in Sydney?"
- "What is the official website of Harbourside Bike Repairs?"
- "Has Harbourside Bike Repairs published a registration number?"

It can also report that the domain and the record point at each other, that the record passes the schema, and whether a valid `p` key is published.

**Limits.** An ABIZ record is not proof of legal registration. A tool may describe a business as registry-confirmed only if it has checked the official register separately and labels that check as such. ABIZ is not an endorsement, a quality mark or a promise of visibility in any AI service.

## 6. Local practical notes

**Registration number.** Your ACN is on your certificate of registration from [ASIC](https://asic.gov.au/). ABNs can be looked up on [ABN Lookup](https://abr.business.gov.au/).

**Adding the TXT record.** Sign in wherever your domain's DNS is managed: usually the registrar where you bought the domain, or a DNS host such as your web host. Add a record of type TXT with the name `_abiz` (some panels want the full name, `_abiz.harboursidebikerepairs.example`), paste the value without the surrounding quotes, and set the TTL to 300 seconds if the panel allows it. `.au` domains are overseen by [auDA](https://www.auda.org.au/) and sold through accredited registrars.

**Privacy.** The record and the TXT value are public. Publish only facts you intend to be public. A sole trader should not publish a home address or personal phone number; leave a field out rather than marking it private (section 4.3). The Privacy Act 1988 applies to many businesses; see the [Office of the Australian Information Commissioner](https://www.oaic.gov.au/).

## 7. Further reading

- [ABIZ specification](../../../SPEC.md): section 3.1.1 (TXT syntax), section 3.3 (`p` keys), section 4.2 (business keys)
- [Business record JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Reference validator](../../../scripts/validate.py) and [examples](../../../examples/)
- [All Oceania guides](index.md)
