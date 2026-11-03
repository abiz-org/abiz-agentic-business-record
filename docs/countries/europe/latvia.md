# Becoming an Agentic Business using ABIZ in Latvia

*A guide to ABIZ 1.1 (proposed). [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.* This first draft is in English; a version in Latvian has not been written yet.

## 1. What this means for a business in Latvia

People increasingly ask AI assistants about businesses: who they are, what they offer, where to find them. ABIZ (Agentic Business Record) lets a business publish one public, machine-readable record of its own facts, such as its name, country, website, services and opening hours, and a DNS record on its own domain that points to that record.

Only the business, or someone it authorises, can change the DNS of its domain. So compatible software can find the record from the domain and check that the domain and the record refer to each other, instead of piecing facts together from scattered web pages. ABIZ is open and provider-independent: no membership, fee or particular provider is required.

## 2. How to publish an ABIZ record

### Required fields

The business record is a JSON document that must validate against the [normative schema](../../../schemas/abiz-business-record-v1.schema.json). Five fields are required:

| Field | Example for Latvia | Notes |
| --- | --- | --- |
| `record_version` | `abiz1` | Always this value |
| `business_name` | `Daugava Koks SIA` | The public name, usually as it appears on the register, with the legal form if you use it |
| `country` | `lv` | ISO 3166-1 alpha-2 code; lowercase is the canonical form |
| `identity_host` | `daugavakoks.lv.to.co` | Exactly the DNS `h` value: a hostname with an optional path, without `https://` |
| `domains` | `["daugavakoks.example"]` | The domains this record claims, including the one that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, the record must also contain `business_key` and `registration_number`, and `k` must equal `business_key`.

In Latvia the key is `lv-` followed by the registration number. Latvia uses no subdivision, so a key with a middle part, such as `lv-xx-…`, is invalid.

- **Register:** [Register of Enterprises of the Republic of Latvia (Uzņēmumu reģistrs)](https://www.ur.gov.lv/)
- **Number to use:** the 11-digit registration number (reģistrācijas numurs)
- **How to write it:** start from the number as the register issues it, apply Unicode NFKC normalisation, remove spaces, `-`, `.`, `/` and other dash characters, then write letters in uppercase. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits.

Worked example (invented number): `40001234567` is already in canonical form. The record then has `"registration_number": "40001234567"` and `"business_key": "lv-40001234567"`, and DNS carries `k=lv-40001234567`.

Keys are compared case-insensitively, but publish the canonical form: lowercase country code, uppercase number.

### DNS TXT record

Publish exactly one ABIZ TXT record at `_abiz` on your domain. Use the compact form, with no spaces:

```dns
_abiz.daugavakoks.example. 300 IN TXT "v=abiz1;k=lv-40001234567;h=daugavakoks.lv.to.co;p=c3/ZkSLzm1EwRlkhpMmb8JONcp1BlVGTZ571imFVE38="
```

- `v=abiz1` must come first. `h` is required; `k` and `p` are optional.
- Tag names are lowercase and case-sensitive. A tag must not appear twice.
- A TTL of 300 seconds is recommended.

The `p` value above is a throwaway example key. Never copy it: publish your own key or leave `p` out.

### Business record (JSON)

The record served at `https://daugavakoks.lv.to.co`, as `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Daugava Koks SIA",
  "country": "lv",
  "business_key": "lv-40001234567",
  "registration_number": "40001234567",
  "identity_host": "daugavakoks.lv.to.co",
  "domains": [
    "daugavakoks.example"
  ],
  "public_key": "c3/ZkSLzm1EwRlkhpMmb8JONcp1BlVGTZ571imFVE38=",
  "description": "Timber merchant in Riga.",
  "website": "https://daugavakoks.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Riga",
        "country": {
          "code": "LV"
        }
      },
      "public": true
    }
  ],
  "signature": "tN0eWKEdyzVm4YpaTaAGLXV4Bjlv2AP8IRi5xGWK1w04JHpadv+m/fQfZpT8rIY9MXEBKJLIxw/g/x6sgqkfDw=="
}
```

You can check a record and its DNS value locally with the reference validator:

```sh
python scripts/validate.py record.json --domain daugavakoks.example --dns-value 'v=abiz1;k=lv-40001234567;h=daugavakoks.lv.to.co;p=c3/ZkSLzm1EwRlkhpMmb8JONcp1BlVGTZ571imFVE38='
```

### Self-hosted or through a provider

You can serve the record yourself on any HTTPS host you control, or use any compatible provider. ABIZ does not require a particular provider or hostname scheme. Either way, the record must be served over HTTPS, and you must control the domain where `_abiz` is published.

## 3. Using a provider and MCP

MCP (Model Context Protocol) is an open protocol that lets AI assistants call tools and read data from external servers. A provider can run an MCP server so that an assistant can request your public record directly. You can list one in the optional `mcp_server_url` field. ABIZ does not require an MCP server, and a tool should not call one automatically just because a record lists it.

For example, a provider might serve your record at `daugavakoks.lv.to.co` and run an MCP server. An assistant connected to that server could then ask for the opening hours or services of Daugava Koks SIA and receive the facts from your record, not from a guess.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 lets a business publish an Ed25519 public key in the DNS `p` tag. `p` is optional. When present, it must be the standard base64 encoding of the 32-byte public key: 44 characters ending in one `=`, in a single DNS string. Any other value, such as an ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid.

The matching private key belongs to the business. It is never published. A provider that holds it for you must let you export it. Software can check a signature made with the private key against the key in DNS. The business record repeats the key as `public_key` and carries a `signature` over the whole record, made with the private key (SPEC section 4.6). Software verifies the signature and checks that `public_key` equals `p`; a record that fails either check is not verified.

To rotate, publish a new key in `p`. To revoke, remove `p`. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record. A key shows which key the domain's controller published; it does not prove legal identity.

## 5. What AI tools will see

With a valid record, a compatible assistant can answer questions such as:

- "Is Daugava Koks SIA a business in Riga?"
- "What does Daugava Koks SIA offer, and when is it open?"
- "Is daugavakoks.example the official website of Daugava Koks SIA?"
- "Which registration number does Daugava Koks SIA publish for itself?"

The limits matter. ABIZ shows that a domain and a record point to each other. It does not prove that a business is legally registered, that a registration number is genuine, or that anyone endorses the business. A tool that has not checked the Register of Enterprises itself must not describe the business as verified. ABIZ does not guarantee that any AI service will find, rank or recommend a business.

## 6. Local practical notes

### Finding the registration number

The registration number is on the registration certificate and can be searched on the [Register of Enterprises](https://www.ur.gov.lv/) website.

### Adding the TXT record

Add the record wherever your domain's DNS is managed, usually at your domain registrar or web host. The registry for `.lv` domains is [NIC.LV](https://www.nic.lv/), but you add the record at your registrar or DNS host; any that supports TXT records will do. Create a record of type TXT with the name `_abiz` (some control panels want the full name, `_abiz.daugavakoks.example`), the value exactly as above and a TTL of 300. Do not add spaces inside the value, and remove any older ABIZ record so that only one remains.

### Privacy and publishing data

Latvia is in the European Union, so the GDPR applies to personal data in your record, for example the name of a sole trader or a named contact. The [European Data Protection Board](https://www.edpb.europa.eu/) links to each national data protection authority. Everything in an ABIZ record is public, so publish only facts you mean to make public. A sole trader should not publish a home address: the specification requires private personal addresses to be left out, not marked as private. A role address such as `info@` is better than a personal email address.

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md): DNS syntax (section 3.1.1), the `p` key (section 3.3), business keys (section 4.2)
- [Normative JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Reference validator, scripts/validate.py](../../../scripts/validate.py)
- [All European guides](index.md)
