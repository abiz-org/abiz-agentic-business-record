# Becoming an Agentic Business using ABIZ in Ireland

*A guide to ABIZ 1.1 (proposed). [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.*

## 1. What this means for a business in Ireland

People increasingly ask AI assistants about businesses: who they are, what they offer, where to find them. ABIZ (Agentic Business Record) lets a business publish one public, machine-readable record of its own facts, such as its name, country, website, services and opening hours, and a DNS record on its own domain that points to that record.

Only the business, or someone it authorises, can change the DNS of its domain. So compatible software can find the record from the domain and check that the domain and the record refer to each other, instead of piecing facts together from scattered web pages. ABIZ is open and provider-independent: no membership, fee or particular provider is required.

## 2. How to publish an ABIZ record

### Required fields

The business record is a JSON document that must validate against the [normative schema](../../../schemas/abiz-business-record-v1.schema.json). Five fields are required:

| Field | Example for Ireland | Notes |
| --- | --- | --- |
| `record-version` | `abiz1` | Always this value |
| `business-name` | `Burren Crafts Limited` | The public name, usually as it appears on the register, with the legal form if you use it |
| `country` | `ie` | ISO 3166-1 alpha-2 code; lowercase is the canonical form |
| `identity-host` | `burrencrafts.ie.to.co` | Exactly the DNS `h` value: a hostname with an optional path, without `https://` |
| `domains` | `["burrencrafts.example"]` | The domains this record claims, including the one that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, the record must also contain `business-key` and `registration-number`, and `k` must equal `business-key`.

In Ireland the key is `ie-` followed by the registration number. Ireland uses no subdivision, so a key with a middle part, such as `ie-xx-…`, is invalid.

- **Register:** [Companies Registration Office (CRO)](https://cro.ie/)
- **Number to use:** the CRO company number, digits only
- **How to write it:** start from the number as the register issues it, apply Unicode NFKC normalisation, remove spaces, `-`, `.`, `/` and other dash characters, then write letters in uppercase. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits.

Worked example (invented number): `123456` is already in canonical form. The record then has `"registration-number": "123456"` and `"business-key": "ie-123456"`, and DNS carries `k=ie-123456`. Business names registered with the CRO have their own numbers; use the company number of the company.

Keys are compared case-insensitively, but publish the canonical form: lowercase country code, uppercase number.

### DNS TXT record

Publish exactly one ABIZ TXT record at `_abiz` on your domain. Use the compact form, with no spaces:

```dns
_abiz.burrencrafts.example. 300 IN TXT "v=abiz1;k=ie-123456;h=burrencrafts.ie.to.co;p=95yUstKB852We7rkPiYVI/dfEosGGiQbevR99/EGuV4="
```

- `v=abiz1` must come first. `h` is required; `k` and `p` are optional.
- Tag names are lowercase and case-sensitive. A tag must not appear twice.
- A TTL of 300 seconds is recommended.

The `p` value above is a throwaway example key. Never copy it: publish your own key or leave `p` out.

### Business record (JSON)

The record served at `https://burrencrafts.ie.to.co`, as `application/json`:

```json
{
  "record-version": "abiz1",
  "business-name": "Burren Crafts Limited",
  "country": "ie",
  "business-key": "ie-123456",
  "registration-number": "123456",
  "identity-host": "burrencrafts.ie.to.co",
  "domains": [
    "burrencrafts.example"
  ],
  "description": "Handmade crafts from County Clare and Galway.",
  "website": "https://burrencrafts.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Galway",
      "country": "ie",
      "public": true
    }
  ]
}
```

You can check a record and its DNS value locally with the reference validator:

```sh
python scripts/validate.py record.json --domain burrencrafts.example --dns-value 'v=abiz1;k=ie-123456;h=burrencrafts.ie.to.co;p=95yUstKB852We7rkPiYVI/dfEosGGiQbevR99/EGuV4='
```

### Self-hosted or through a provider

You can serve the record yourself on any HTTPS host you control, or use any compatible provider. ABIZ does not require a particular provider or hostname scheme. Either way, the record must be served over HTTPS, and you must control the domain where `_abiz` is published.

## 3. Using a provider and MCP

MCP (Model Context Protocol) is an open protocol that lets AI assistants call tools and read data from external servers. A provider can run an MCP server so that an assistant can request your public record directly. You can list one in the optional `mcp-server-url` field. ABIZ does not require an MCP server, and a tool should not call one automatically just because a record lists it.

For example, a provider might serve your record at `burrencrafts.ie.to.co` and run an MCP server. An assistant connected to that server could then ask for the opening hours or services of Burren Crafts Limited and receive the facts from your record, not from a guess. to.co, one provider, has an [ABIZ overview](https://to.co/en-ie/abiz) written for readers in Ireland.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 lets a business publish an Ed25519 public key in the DNS `p` tag. `p` is optional. When present, it must be the standard base64 encoding of the 32-byte public key: 44 characters ending in one `=`, in a single DNS string. Any other value, such as an ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid.

The matching private key belongs to the business. It is never published. A provider that holds it for you must let you export it. Software can check a signature made with the private key against the key in DNS. ABIZ 1.1 does not yet define which bytes a signature over the business record covers.

To rotate, publish a new key in `p`. To revoke, remove `p`. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record. A key shows which key the domain's controller published; it does not prove legal identity.

## 5. What AI tools will see

With a valid record, a compatible assistant can answer questions such as:

- "Is Burren Crafts Limited a business in Galway?"
- "What does Burren Crafts Limited offer, and when is it open?"
- "Is burrencrafts.example the official website of Burren Crafts Limited?"
- "Which registration number does Burren Crafts Limited publish for itself?"

The limits matter. ABIZ shows that a domain and a record point to each other. It does not prove that a business is legally registered, that a registration number is genuine, or that anyone endorses the business. A tool that has not checked the CRO register itself must not describe the business as verified. ABIZ does not guarantee that any AI service will find, rank or recommend a business.

## 6. Local practical notes

### Finding the registration number

The company number is on the certificate of incorporation and on the company's letterhead, and can be searched on [CORE](https://cro.ie/), the CRO's online system.

### Adding the TXT record

Add the record wherever your domain's DNS is managed, usually at your domain registrar or web host. The registry for `.ie` domains is [.IE](https://www.weare.ie/), but you add the record at your registrar or DNS host; any that supports TXT records will do. Create a record of type TXT with the name `_abiz` (some control panels want the full name, `_abiz.burrencrafts.example`), the value exactly as above and a TTL of 300. Do not add spaces inside the value, and remove any older ABIZ record so that only one remains.

### Privacy and publishing data

Ireland is in the European Union, so the GDPR applies to personal data in your record, for example the name of a sole trader or a named contact. The [European Data Protection Board](https://www.edpb.europa.eu/) links to each national data protection authority. Everything in an ABIZ record is public, so publish only facts you mean to make public. A sole trader should not publish a home address: the specification requires private personal addresses to be left out, not marked as private. A role address such as `info@` is better than a personal email address.

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md): DNS syntax (section 3.1.1), the `p` key (section 3.3), business keys (section 4.2)
- [Normative JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Reference validator, scripts/validate.py](../../../scripts/validate.py)
- [All European guides](index.md)
