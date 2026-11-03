# Becoming an Agentic Business using ABIZ in the United Kingdom

*A guide to ABIZ 1.1 (proposed). [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.*

## 1. What this means for a business in the United Kingdom

People increasingly ask AI assistants about businesses: who they are, what they offer, where to find them. ABIZ (Agentic Business Record) lets a business publish one public, machine-readable record of its own facts, such as its name, country, website, services and opening hours, and a DNS record on its own domain that points to that record.

Only the business, or someone it authorises, can change the DNS of its domain. So compatible software can find the record from the domain and check that the domain and the record refer to each other, instead of piecing facts together from scattered web pages. ABIZ is open and provider-independent: no membership, fee or particular provider is required.

## 2. How to publish an ABIZ record

### Required fields

The business record is a JSON document that must validate against the [normative schema](../../../schemas/abiz-business-record-v1.schema.json). Five fields are required:

| Field | Example for the United Kingdom | Notes |
| --- | --- | --- |
| `record-version` | `abiz1` | Always this value |
| `business-name` | `Hartley Joinery Ltd` | The public name, usually as it appears on the register, with the legal form if you use it |
| `country` | `gb` | ISO 3166-1 alpha-2 code; lowercase is the canonical form; the United Kingdom is `gb`, not `uk`, because `uk` is not an assigned ISO 3166-1 code |
| `identity-host` | `hartleyjoinery.uk.to.co` | Exactly the DNS `h` value: a hostname with an optional path, without `https://` |
| `domains` | `["hartleyjoinery.example"]` | The domains this record claims, including the one that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, the record must also contain `business-key` and `registration-number`, and `k` must equal `business-key`.

In the United Kingdom the key is `gb-` followed by the registration number. The United Kingdom uses no subdivision, so a key with a middle part, such as `gb-xx-…`, is invalid.

- **Register:** [Companies House](https://www.gov.uk/government/organisations/companies-house), which keeps one register for England and Wales, Scotland and Northern Ireland
- **Number to use:** the 8-character company number, with its letter prefix and leading zeros
- **How to write it:** start from the number as the register issues it, apply Unicode NFKC normalisation, remove spaces, `-`, `.`, `/` and other dash characters, then write letters in uppercase. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits.

Worked example (invented number): `01234567` is already in canonical form. The record then has `"registration-number": "01234567"` and `"business-key": "gb-01234567"`, and DNS carries `k=gb-01234567`. A Scottish company keeps its prefix, for example `gb-SC123456`; a Northern Irish one, for example `gb-NI123456`. The hostname uses `uk` (`.uk.to.co`) but the key and the `country` field always use `gb`.

Keys are compared case-insensitively, but publish the canonical form: lowercase country code, uppercase number.

### DNS TXT record

Publish exactly one ABIZ TXT record at `_abiz` on your domain. Use the compact form, with no spaces:

```dns
_abiz.hartleyjoinery.example. 300 IN TXT "v=abiz1;k=gb-01234567;h=hartleyjoinery.uk.to.co;p=2TRRkJCho2AP333NPQfUiONoL+GgMM+kaq5v3oYMCYI="
```

- `v=abiz1` must come first. `h` is required; `k` and `p` are optional.
- Tag names are lowercase and case-sensitive. A tag must not appear twice.
- A TTL of 300 seconds is recommended.

The `p` value above is a throwaway example key. Never copy it: publish your own key or leave `p` out.

### Business record (JSON)

The record served at `https://hartleyjoinery.uk.to.co`, as `application/json`:

```json
{
  "record-version": "abiz1",
  "business-name": "Hartley Joinery Ltd",
  "country": "gb",
  "business-key": "gb-01234567",
  "registration-number": "01234567",
  "identity-host": "hartleyjoinery.uk.to.co",
  "domains": [
    "hartleyjoinery.example"
  ],
  "description": "Bespoke joinery in Leeds.",
  "website": "https://hartleyjoinery.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Leeds",
      "country": "gb",
      "public": true
    }
  ]
}
```

You can check a record and its DNS value locally with the reference validator:

```sh
python scripts/validate.py record.json --domain hartleyjoinery.example --dns-value 'v=abiz1;k=gb-01234567;h=hartleyjoinery.uk.to.co;p=2TRRkJCho2AP333NPQfUiONoL+GgMM+kaq5v3oYMCYI='
```

### Self-hosted or through a provider

You can serve the record yourself on any HTTPS host you control, or use any compatible provider. ABIZ does not require a particular provider or hostname scheme. Either way, the record must be served over HTTPS, and you must control the domain where `_abiz` is published.

## 3. Using a provider and MCP

MCP (Model Context Protocol) is an open protocol that lets AI assistants call tools and read data from external servers. A provider can run an MCP server so that an assistant can request your public record directly. You can list one in the optional `mcp-server-url` field. ABIZ does not require an MCP server, and a tool should not call one automatically just because a record lists it.

For example, a provider might serve your record at `hartleyjoinery.uk.to.co` and run an MCP server. An assistant connected to that server could then ask for the opening hours or services of Hartley Joinery Ltd and receive the facts from your record, not from a guess. to.co, one provider, has an [ABIZ overview](https://to.co/en-gb/abiz) written for readers in the United Kingdom.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 lets a business publish an Ed25519 public key in the DNS `p` tag. `p` is optional. When present, it must be the standard base64 encoding of the 32-byte public key: 44 characters ending in one `=`, in a single DNS string. Any other value, such as an ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid.

The matching private key belongs to the business. It is never published. A provider that holds it for you must let you export it. Software can check a signature made with the private key against the key in DNS. ABIZ 1.1 does not yet define which bytes a signature over the business record covers.

To rotate, publish a new key in `p`. To revoke, remove `p`. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record. A key shows which key the domain's controller published; it does not prove legal identity.

## 5. What AI tools will see

With a valid record, a compatible assistant can answer questions such as:

- "Is Hartley Joinery Ltd a business in Leeds?"
- "What does Hartley Joinery Ltd offer, and when is it open?"
- "Is hartleyjoinery.example the official website of Hartley Joinery Ltd?"
- "Which registration number does Hartley Joinery Ltd publish for itself?"

The limits matter. ABIZ shows that a domain and a record point to each other. It does not prove that a business is legally registered, that a registration number is genuine, or that anyone endorses the business. A tool that has not checked the Companies House register itself must not describe the business as verified. ABIZ does not guarantee that any AI service will find, rank or recommend a business.

## 6. Local practical notes

### Finding the registration number

The company number is on the certificate of incorporation and can be searched free of charge on [Find and update company information](https://find-and-update.company-information.service.gov.uk/). Sole traders and ordinary partnerships are not on the Companies House register, so they omit the key.

### Adding the TXT record

Add the record wherever your domain's DNS is managed, usually at your domain registrar or web host. The registry for `.uk` domains is [Nominet](https://www.nominet.uk/), but you add the record at your registrar or DNS host; any that supports TXT records will do. Create a record of type TXT with the name `_abiz` (some control panels want the full name, `_abiz.hartleyjoinery.example`), the value exactly as above and a TTL of 300. Do not add spaces inside the value, and remove any older ABIZ record so that only one remains.

### Privacy and publishing data

UK GDPR and the Data Protection Act 2018 apply to personal data in your record, for example the name of a sole trader or a named contact. The [Information Commissioner's Office](https://www.ico.org.uk/) has guidance. Everything in an ABIZ record is public, so publish only facts you mean to make public. A sole trader should not publish a home address: the specification requires private personal addresses to be left out, not marked as private. A role address such as `info@` is better than a personal email address.

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md): DNS syntax (section 3.1.1), the `p` key (section 3.3), business keys (section 4.2)
- [Normative JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Reference validator, scripts/validate.py](../../../scripts/validate.py)
- [All European guides](index.md)
