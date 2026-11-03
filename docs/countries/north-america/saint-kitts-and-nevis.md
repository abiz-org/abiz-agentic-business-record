# Becoming an Agentic Business using ABIZ in Saint Kitts and Nevis

*A guide to ABIZ 1.1 (proposed). [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.*

## 1. What this means for a business in Saint Kitts and Nevis

People increasingly ask AI assistants things like "which bakery near me is open on Sunday?" or "does this company really own this website?". ABIZ (Agentic Business Record) is an open standard that lets a business publish its public facts in a form that compatible software can find and check: a small JSON document with those facts, and a DNS TXT record on the business's own domain that points to it.

With ABIZ, a compatible assistant can start from your domain, find your record, validate it against the published JSON Schema, and confirm that the domain and the record refer to each other. It works for registered companies and for businesses that are not registered. It does not guarantee that any assistant will find, rank or recommend you, and it is not an official badge.

In Saint Kitts and Nevis, any business, registered or not, can publish an ABIZ record. The optional business key `k` is not yet available (see below).

## 2. How to publish an ABIZ record

### Required fields

| Field | What to put | Example |
| --- | --- | --- |
| `record-version` | Always `abiz1` | `abiz1` |
| `business-name` | Your public business name | `Brimstone Hill Tours Ltd` |
| `country` | The ISO 3166-1 alpha-2 country code, lower case | `kn` |
| `identity-host` | The host, and optional path, where the record is served; it must match DNS `h` | `brimstonehilltours.kn.to.co` |
| `domains` | The domains you control that this record claims | `["brimstonehilltours.example"]` |

### The optional business key `k`

`k` is optional for every business. If you publish it, it must follow section 4.2 of the specification and it must equal the record's `business-key`. Case does not matter when keys are compared, but the canonical form has a lower-case country code and an upper-case registration number.

**No business key for now.** Section 4.2.2 of the specification says that, outside the countries it names, `k` uses the number from the national company register. Saint Kitts and Nevis has separate company registers for St Kitts and for Nevis, so a company number is not known to be unique across the federation. The specification says a country with only subdivision-level registers that is not in its first table cannot yet carry a business key, so leave out `k`, `business-key` and `registration-number` until a revision of the specification decides how to handle the two registers. Everything else in this guide works without `k`.

**Normalising the number (section 4.2.3).** Start from the number exactly as the register issues it. Apply Unicode NFKC normalisation; remove spaces, hyphens, dots and slashes; convert letters to upper case; keep leading zeros and letter prefixes. If anything else is left, such as brackets, `&` or an accented letter, the number cannot be expressed and you cannot publish a business key: leave out `k`, `business-key` and `registration-number`.

If you include `business-key` and `registration-number` in the record, include both, and make the number part of the key equal `registration-number`. Including them does not oblige you to publish `k` in DNS. If you do publish `k`, the record must contain the matching `business-key`.

### The DNS TXT record

Publish exactly one TXT record starting with `v=abiz1` at `_abiz.` followed by your domain. Use the compact form with no spaces (section 3.1.1) and a TTL of 300 seconds:

```dns
_abiz.brimstonehilltours.example. 300 IN TXT "v=abiz1;h=brimstonehilltours.kn.to.co"
```

### Example record (JSON)

This example is fictional. It passes the reference validator.

```json
{
  "record-version": "abiz1",
  "business-name": "Brimstone Hill Tours Ltd",
  "country": "kn",
  "identity-host": "brimstonehilltours.kn.to.co",
  "domains": [
    "brimstonehilltours.example"
  ],
  "description": "Island tours of St Kitts, including Brimstone Hill Fortress.",
  "website": "https://brimstonehilltours.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Basseterre",
      "country": "kn",
      "public": true
    }
  ],
  "opening-hours": [
    "Mo-Sa 08:00-17:00"
  ]
}
```

### Where the record lives

You can serve the record yourself from any HTTPS URL that returns the JSON document, for example `h=www.brimstonehilltours.example/abiz.json`, or use any compatible provider. ABIZ does not require a particular provider or naming scheme. Whichever you choose, `identity-host` in the record must match `h`, and `domains` must include the domain where you publish the TXT record.

Before you publish, check the record and the DNS value with the reference validator:

```sh
python scripts/validate.py record.json \
  --domain brimstonehilltours.example \
  --dns-value 'v=abiz1;h=brimstonehilltours.kn.to.co'
```

## 3. Using a provider and MCP

The Model Context Protocol (MCP) is an open protocol that lets AI assistants call tools and read data from outside services in a standard way. An ABIZ record may include an optional `mcp-server-url`, an HTTPS address of an MCP server that can answer questions about the business, such as opening hours, services or availability. ABIZ does not require an MCP server, and a listed server is not vouched for: compatible software must not call it automatically just because it appears in a record, and must apply its own access controls.

For example, a provider might host the record for Brimstone Hill Tours at `brimstonehilltours.kn.to.co`, publish the DNS TXT record through its own set-up flow, and list its MCP server in `mcp-server-url`. You can move to another provider, or to self-hosting, by changing `h` and the record's `identity-host`.

## 4. Keys and signatures (ABIZ 1.1)

- **`p` is optional.** When present, it must be an Ed25519 public key in standard base64: exactly 44 characters, ending in a single `=`, decoding to 32 bytes (section 3.3.2). Any other value, such as an old ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid. Replace it with a key or remove it.
- **Example** (the key below is a throwaway example key; its private key was discarded). Never copy it: publish your own key or leave `p` out.

  ```dns
  _abiz.brimstonehilltours.example. 300 IN TXT "v=abiz1;h=brimstonehilltours.kn.to.co;p=koo2aFtI+PX9aOmvyb+cZJeOPYzIS7Cj3Y22NW+ceao="
  ```

- **The private key belongs to the business.** It must never appear in DNS, in the record or in a public repository. A provider may generate and hold it for you (hosted mode), but it must let you export it at any time, for example as PKCS#8, and delete its copy on request (section 3.3.4).
- **Signing.** Software can check a detached Ed25519 signature against the published key. ABIZ 1.1 does not yet define which bytes of a business record a signature covers, so a signature check only means something for a message both sides have agreed.
- **Rotation and retired keys.** To rotate, publish the new key in `p`; the old key stops being current once the TXT TTL has passed. ABIZ 1.1 does not publish retired keys: not in DNS, and not in the record (a `retired-keys` property is rejected).
- **What a key proves.** It shows which key the controller of the domain published. It does not sign the TXT record by itself, and it does not prove legal identity. Use DNSSEC where your DNS host supports it.

## 5. What AI tools will see

Compatible software that reads your record can answer questions such as:

- "Is Brimstone Hill Tours open on Saturday?"
- "What does Brimstone Hill Tours offer in Basseterre?"
- "What is the official website of Brimstone Hill Tours?"

It can also report that the domain and the record point at each other, that the record passes the schema, and whether a valid `p` key is published.

**Limits.** An ABIZ record is not proof of legal registration. A tool may describe a business as registry-confirmed only if it has checked the official register separately and labels that check as such. ABIZ is not an endorsement, a quality mark or a promise of visibility in any AI service.

## 6. Local practical notes

**Registration number.** Companies are registered with the Registrar of Companies on St Kitts or with the Nevis registry, depending on where they were formed.

**Adding the TXT record.** Sign in wherever your domain's DNS is managed: usually the registrar where you bought the domain, or a DNS host such as your web host. Add a record of type TXT with the name `_abiz` (some panels want the full name, `_abiz.brimstonehilltours.example`), paste the value without the surrounding quotes, and set the TTL to 300 seconds if the panel allows it.

**Privacy.** The record and the TXT value are public. Publish only facts you intend to be public. A sole trader should not publish a home address or personal phone number; leave a field out rather than marking it private (section 4.3). The Data Protection Act, 2018 applies to personal data.

## 7. Further reading

- [ABIZ specification](../../../SPEC.md): section 3.1.1 (TXT syntax), section 3.3 (`p` keys), section 4.2 (business keys)
- [Business record JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Reference validator](../../../scripts/validate.py) and [examples](../../../examples/)
- [All North America guides](index.md)
