# Becoming an Agentic Business using ABIZ in Hungary

*A guide to ABIZ 1.1 (proposed). [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.* This first draft is in English; a version in Hungarian has not been written yet.

## 1. What this means for a business in Hungary

People increasingly ask AI assistants about businesses: who they are, what they offer, where to find them. ABIZ (Agentic Business Record) lets a business publish one public, machine-readable record of its own facts, such as its name, country, website, services and opening hours, and a DNS record on its own domain that points to that record.

Only the business, or someone it authorises, can change the DNS of its domain. So compatible software can find the record from the domain and check that the domain and the record refer to each other, instead of piecing facts together from scattered web pages. ABIZ is open and provider-independent: no membership, fee or particular provider is required.

## 2. How to publish an ABIZ record

### Required fields

The business record is a JSON document that must validate against the [normative schema](../../../schemas/abiz-business-record-v1.schema.json). Five fields are required:

| Field | Example for Hungary | Notes |
| --- | --- | --- |
| `record-version` | `abiz1` | Always this value |
| `business-name` | `Balaton Bor Kft.` | The public name, usually as it appears on the register, with the legal form if you use it |
| `country` | `hu` | ISO 3166-1 alpha-2 code; lowercase is the canonical form |
| `identity-host` | `balatonbor.hu.to.co` | Exactly the DNS `h` value: a hostname with an optional path, without `https://` |
| `domains` | `["balatonbor.example"]` | The domains this record claims, including the one that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, the record must also contain `business-key` and `registration-number`, and `k` must equal `business-key`.

In Hungary the key is `hu-` followed by the registration number. Hungary uses no subdivision, so a key with a middle part, such as `hu-xx-…`, is invalid.

- **Register:** Company Register (cégjegyzék), kept by the registry courts and published through [e-cegjegyzek.hu](https://www.e-cegjegyzek.hu/)
- **Number to use:** the company registration number (cégjegyzékszám), written `01-09-123456`: court code, company form and serial number. It is unique nationally. Not the tax number (adószám)
- **How to write it:** start from the number as the register issues it, apply Unicode NFKC normalisation, remove spaces, `-`, `.`, `/` and other dash characters, then write letters in uppercase. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits.

Worked example (invented number): `01-09-123456` becomes `0109123456`. The record then has `"registration-number": "0109123456"` and `"business-key": "hu-0109123456"`, and DNS carries `k=hu-0109123456`. Removing the hyphens keeps all ten digits, including the court code.

Keys are compared case-insensitively, but publish the canonical form: lowercase country code, uppercase number.

### DNS TXT record

Publish exactly one ABIZ TXT record at `_abiz` on your domain. Use the compact form, with no spaces:

```dns
_abiz.balatonbor.example. 300 IN TXT "v=abiz1;k=hu-0109123456;h=balatonbor.hu.to.co;p=avSSK7n+iET9jOB28I8xJnEtwSRMkBqIYB+V9gKLhEU="
```

- `v=abiz1` must come first. `h` is required; `k` and `p` are optional.
- Tag names are lowercase and case-sensitive. A tag must not appear twice.
- A TTL of 300 seconds is recommended.

The `p` value above is a throwaway example key. Never copy it: publish your own key or leave `p` out.

### Business record (JSON)

The record served at `https://balatonbor.hu.to.co`, as `application/json`:

```json
{
  "record-version": "abiz1",
  "business-name": "Balaton Bor Kft.",
  "country": "hu",
  "business-key": "hu-0109123456",
  "registration-number": "0109123456",
  "identity-host": "balatonbor.hu.to.co",
  "domains": [
    "balatonbor.example"
  ],
  "description": "Winery near Lake Balaton.",
  "website": "https://balatonbor.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Keszthely",
      "country": "hu",
      "public": true
    }
  ]
}
```

You can check a record and its DNS value locally with the reference validator:

```sh
python scripts/validate.py record.json --domain balatonbor.example --dns-value 'v=abiz1;k=hu-0109123456;h=balatonbor.hu.to.co;p=avSSK7n+iET9jOB28I8xJnEtwSRMkBqIYB+V9gKLhEU='
```

### Self-hosted or through a provider

You can serve the record yourself on any HTTPS host you control, or use any compatible provider. ABIZ does not require a particular provider or hostname scheme. Either way, the record must be served over HTTPS, and you must control the domain where `_abiz` is published.

## 3. Using a provider and MCP

MCP (Model Context Protocol) is an open protocol that lets AI assistants call tools and read data from external servers. A provider can run an MCP server so that an assistant can request your public record directly. You can list one in the optional `mcp-server-url` field. ABIZ does not require an MCP server, and a tool should not call one automatically just because a record lists it.

For example, a provider might serve your record at `balatonbor.hu.to.co` and run an MCP server. An assistant connected to that server could then ask for the opening hours or services of Balaton Bor Kft. and receive the facts from your record, not from a guess.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 lets a business publish an Ed25519 public key in the DNS `p` tag. `p` is optional. When present, it must be the standard base64 encoding of the 32-byte public key: 44 characters ending in one `=`, in a single DNS string. Any other value, such as an ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid.

The matching private key belongs to the business. It is never published. A provider that holds it for you must let you export it. Software can check a signature made with the private key against the key in DNS. ABIZ 1.1 does not yet define which bytes a signature over the business record covers.

To rotate, publish a new key in `p`. To revoke, remove `p`. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record. A key shows which key the domain's controller published; it does not prove legal identity.

## 5. What AI tools will see

With a valid record, a compatible assistant can answer questions such as:

- "Is Balaton Bor Kft. a business in Keszthely?"
- "What does Balaton Bor Kft. offer, and when is it open?"
- "Is balatonbor.example the official website of Balaton Bor Kft.?"
- "Which registration number does Balaton Bor Kft. publish for itself?"

The limits matter. ABIZ shows that a domain and a record point to each other. It does not prove that a business is legally registered, that a registration number is genuine, or that anyone endorses the business. A tool that has not checked the Company Register itself must not describe the business as verified. ABIZ does not guarantee that any AI service will find, rank or recommend a business.

## 6. Local practical notes

### Finding the registration number

The cégjegyzékszám is on the company extract (cégkivonat) and can be searched free of charge at [e-cegjegyzek.hu](https://www.e-cegjegyzek.hu/). Sole entrepreneurs (egyéni vállalkozó) are not in the Company Register and omit the key.

### Adding the TXT record

Add the record wherever your domain's DNS is managed, usually at your domain registrar or web host. The registry for `.hu` domains is [the Council of Hungarian Internet Providers](https://www.domain.hu/), but you add the record at your registrar or DNS host; any that supports TXT records will do. Create a record of type TXT with the name `_abiz` (some control panels want the full name, `_abiz.balatonbor.example`), the value exactly as above and a TTL of 300. Do not add spaces inside the value, and remove any older ABIZ record so that only one remains.

### Privacy and publishing data

Hungary is in the European Union, so the GDPR applies to personal data in your record, for example the name of a sole trader or a named contact. The [European Data Protection Board](https://www.edpb.europa.eu/) links to each national data protection authority. Everything in an ABIZ record is public, so publish only facts you mean to make public. A sole trader should not publish a home address: the specification requires private personal addresses to be left out, not marked as private. A role address such as `info@` is better than a personal email address.

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md): DNS syntax (section 3.1.1), the `p` key (section 3.3), business keys (section 4.2)
- [Normative JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Reference validator, scripts/validate.py](../../../scripts/validate.py)
- [All European guides](index.md)
