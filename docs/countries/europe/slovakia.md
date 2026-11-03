# Becoming an Agentic Business using ABIZ in Slovakia

*A guide to ABIZ 1.1 (proposed). [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.* This first draft is in English; a version in Slovak has not been written yet.

## 1. What this means for a business in Slovakia

People increasingly ask AI assistants about businesses: who they are, what they offer, where to find them. ABIZ (Agentic Business Record) lets a business publish one public, machine-readable record of its own facts, such as its name, country, website, services and opening hours, and a DNS record on its own domain that points to that record.

Only the business, or someone it authorises, can change the DNS of its domain. So compatible software can find the record from the domain and check that the domain and the record refer to each other, instead of piecing facts together from scattered web pages. ABIZ is open and provider-independent: no membership, fee or particular provider is required.

## 2. How to publish an ABIZ record

### Required fields

The business record is a JSON document that must validate against the [normative schema](../../../schemas/abiz-business-record-v1.schema.json). Five fields are required:

| Field | Example for Slovakia | Notes |
| --- | --- | --- |
| `record_version` | `abiz1` | Always this value |
| `business_name` | `Tatra Drevo s.r.o.` | The public name, usually as it appears on the register, with the legal form if you use it |
| `country` | `sk` | ISO 3166-1 alpha-2 code; lowercase is the canonical form |
| `identity_host` | `tatradrevo.sk.to.co` | Exactly the DNS `h` value: a hostname with an optional path, without `https://` |
| `domains` | `["tatradrevo.example"]` | The domains this record claims, including the one that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, the record must also contain `business_key` and `registration_number`, and `k` must equal `business_key`.

In Slovakia the key is `sk-` followed by the registration number. Slovakia uses no subdivision, so a key with a middle part, such as `sk-xx-…`, is invalid.

- **Register:** [Commercial Register of the Slovak Republic (Obchodný register)](https://www.orsr.sk/)
- **Number to use:** the 8-digit IČO (identification number of the organisation)
- **How to write it:** start from the number as the register issues it, apply Unicode NFKC normalisation, remove spaces, `-`, `.`, `/` and other dash characters, then write letters in uppercase. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits.

Worked example (invented number): `12 345 678` becomes `12345678`. The record then has `"registration_number": "12345678"` and `"business_key": "sk-12345678"`, and DNS carries `k=sk-12345678`.

Keys are compared case-insensitively, but publish the canonical form: lowercase country code, uppercase number.

### DNS TXT record

Publish exactly one ABIZ TXT record at `_abiz` on your domain. Use the compact form, with no spaces:

```dns
_abiz.tatradrevo.example. 300 IN TXT "v=abiz1;k=sk-12345678;h=tatradrevo.sk.to.co;p=gk1kzli+17o3cpD1rV7KjPtdhLOO3jWgbd8J/e/iFtw="
```

- `v=abiz1` must come first. `h` is required; `k` and `p` are optional.
- Tag names are lowercase and case-sensitive. A tag must not appear twice.
- A TTL of 300 seconds is recommended.

The `p` value above is a throwaway example key. Never copy it: publish your own key or leave `p` out.

### Business record (JSON)

The record served at `https://tatradrevo.sk.to.co`, as `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Tatra Drevo s.r.o.",
  "country": "sk",
  "business_key": "sk-12345678",
  "registration_number": "12345678",
  "identity_host": "tatradrevo.sk.to.co",
  "domains": [
    "tatradrevo.example"
  ],
  "public_key": "gk1kzli+17o3cpD1rV7KjPtdhLOO3jWgbd8J/e/iFtw=",
  "description": "Joinery in Košice.",
  "website": "https://tatradrevo.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Košice",
        "country": {
          "code": "SK"
        }
      },
      "public": true
    }
  ],
  "signature": "taS9NH/EDVpn5cH6NfKuP8I/wnZYtcHSgZJ3rCfH07ULw5oeRvQ7Mv5b7sjqVcRboUUu2Ex+excK7Ro3Ig0LAg=="
}
```

You can check a record and its DNS value locally with the reference validator:

```sh
python scripts/validate.py record.json --domain tatradrevo.example --dns-value 'v=abiz1;k=sk-12345678;h=tatradrevo.sk.to.co;p=gk1kzli+17o3cpD1rV7KjPtdhLOO3jWgbd8J/e/iFtw='
```

### Self-hosted or through a provider

You can serve the record yourself on any HTTPS host you control, or use any compatible provider. ABIZ does not require a particular provider or hostname scheme. Either way, the record must be served over HTTPS, and you must control the domain where `_abiz` is published.

## 3. Using a provider and MCP

MCP (Model Context Protocol) is an open protocol that lets AI assistants call tools and read data from external servers. A provider can run an MCP server so that an assistant can request your public record directly. You can list one in the optional `mcp_server_url` field. ABIZ does not require an MCP server, and a tool should not call one automatically just because a record lists it.

For example, a provider might serve your record at `tatradrevo.sk.to.co` and run an MCP server. An assistant connected to that server could then ask for the opening hours or services of Tatra Drevo s.r.o. and receive the facts from your record, not from a guess.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 lets a business publish an Ed25519 public key in the DNS `p` tag. `p` is optional. When present, it must be the standard base64 encoding of the 32-byte public key: 44 characters ending in one `=`, in a single DNS string. Any other value, such as an ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid.

The matching private key belongs to the business. It is never published. A provider that holds it for you must let you export it. Software can check a signature made with the private key against the key in DNS. The business record repeats the key as `public_key` and carries a `signature` over the whole record, made with the private key (SPEC section 4.6). Software verifies the signature and checks that `public_key` equals `p`; a record that fails either check is not verified.

To rotate, publish a new key in `p`. To revoke, remove `p`. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record. A key shows which key the domain's controller published; it does not prove legal identity.

## 5. What AI tools will see

With a valid record, a compatible assistant can answer questions such as:

- "Is Tatra Drevo s.r.o. a business in Košice?"
- "What does Tatra Drevo s.r.o. offer, and when is it open?"
- "Is tatradrevo.example the official website of Tatra Drevo s.r.o.?"
- "Which registration number does Tatra Drevo s.r.o. publish for itself?"

The limits matter. ABIZ shows that a domain and a record point to each other. It does not prove that a business is legally registered, that a registration number is genuine, or that anyone endorses the business. A tool that has not checked the Commercial Register itself must not describe the business as verified. ABIZ does not guarantee that any AI service will find, rank or recommend a business.

## 6. Local practical notes

### Finding the registration number

The IČO is on the extract from the Commercial Register and can be searched at [orsr.sk](https://www.orsr.sk/). Tradespeople registered only in the trade register also have an IČO, but this guide uses the Commercial Register.

### Adding the TXT record

Add the record wherever your domain's DNS is managed, usually at your domain registrar or web host. The registry for `.sk` domains is [SK-NIC](https://sk-nic.sk/), but you add the record at your registrar or DNS host; any that supports TXT records will do. Create a record of type TXT with the name `_abiz` (some control panels want the full name, `_abiz.tatradrevo.example`), the value exactly as above and a TTL of 300. Do not add spaces inside the value, and remove any older ABIZ record so that only one remains.

### Privacy and publishing data

Slovakia is in the European Union, so the GDPR applies to personal data in your record, for example the name of a sole trader or a named contact. The [European Data Protection Board](https://www.edpb.europa.eu/) links to each national data protection authority. Everything in an ABIZ record is public, so publish only facts you mean to make public. A sole trader should not publish a home address: the specification requires private personal addresses to be left out, not marked as private. A role address such as `info@` is better than a personal email address.

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md): DNS syntax (section 3.1.1), the `p` key (section 3.3), business keys (section 4.2)
- [Normative JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Reference validator, scripts/validate.py](../../../scripts/validate.py)
- [All European guides](index.md)
