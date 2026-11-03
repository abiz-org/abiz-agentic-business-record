# Becoming an Agentic Business using ABIZ in Croatia

*A guide to published ABIZ 1.1. [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.* This first draft is in English; a version in Croatian has not been written yet.

## 1. What this means for a business in Croatia

People increasingly ask AI assistants about businesses: who they are, what they offer, where to find them. ABIZ (Agentic Business Record) lets a business publish one public, machine-readable record of its own facts, such as its name, country, website, services and opening hours, and a DNS record on its own domain that points to that record.

Only the business, or someone it authorises, can change the DNS of its domain. So compatible software can find the record from the domain and check that the domain and the record refer to each other, instead of piecing facts together from scattered web pages. ABIZ is open and provider-independent: no membership, fee or particular provider is required.

## 2. How to publish an ABIZ record

### Required fields

The business record is a JSON document that must validate against the [normative schema](../../../schemas/abiz-business-record-v1.1.schema.json). Five fields are required:

| Field | Example for Croatia | Notes |
| --- | --- | --- |
| `record_version` | `abiz1` | Always this value |
| `business_name` | `Jadranska Ribarnica d.o.o.` | The public name, usually as it appears on the register, with the legal form if you use it |
| `country` | `hr` | ISO 3166-1 alpha-2 code; lowercase is the canonical form |
| `identity_host` | `jadranskaribarnica.hr.to.co` | Exactly the DNS `h` value: a hostname with an optional path, without `https://` |
| `domains` | `["jadranskaribarnica.example"]` | The domains this record claims, including the one that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, the record must also contain `business_key` and `registration_number`, and `k` must equal `business_key`.

In Croatia the key is `hr-` followed by the registration number. Croatia uses no subdivision, so a key with a middle part, such as `hr-xx-…`, is invalid.

- **Register:** [Court Register (Sudski registar)](https://sudreg.pravosudje.hr/), kept by the commercial courts in one national database
- **Number to use:** the MBS (matični broj subjekta), the 9-digit registration number of the court register. Not the OIB, which is the tax number
- **How to write it:** start from the number as the register issues it, apply Unicode NFKC normalisation, remove spaces, `-`, `.`, `/` and other dash characters, then write letters in uppercase. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits.

Worked example (invented number): `080123456` is already in canonical form. The record then has `"registration_number": "080123456"` and `"business_key": "hr-080123456"`, and DNS carries `k=hr-080123456`. Keep the leading zero.

Keys are compared case-insensitively, but publish the canonical form: lowercase country code, uppercase number.

### DNS TXT record

Publish exactly one ABIZ TXT record at `_abiz` on your domain. Use the compact form, with no spaces:

```dns
_abiz.jadranskaribarnica.example. 300 IN TXT "v=abiz1;k=hr-080123456;h=jadranskaribarnica.hr.to.co;p=SK7XK9qcGo0IvRSoLaau7hkLswsXx5Pn8aE3QQoMcUU="
```

- `v=abiz1` must come first. `h` and `p` are required; `k` is optional.
- Tag names are lowercase and case-sensitive. A tag must not appear twice.
- A TTL of 300 seconds is recommended.

The `p` value above is a throwaway example key. Never copy it: publish your own key. An ABIZ 1.1 assertion must include `p`.

### Business record (JSON)

The record served at `https://jadranskaribarnica.hr.to.co`, as `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Jadranska Ribarnica d.o.o.",
  "country": "hr",
  "business_key": "hr-080123456",
  "registration_number": "080123456",
  "identity_host": "jadranskaribarnica.hr.to.co",
  "domains": [
    "jadranskaribarnica.example"
  ],
  "public_key": "SK7XK9qcGo0IvRSoLaau7hkLswsXx5Pn8aE3QQoMcUU=",
  "description": "Fishmonger in Split.",
  "website": "https://jadranskaribarnica.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Split",
        "country": {
          "code": "HR"
        }
      },
      "public": true
    }
  ],
  "signature": "zxf2MmUw/o0bYW2jp4iJHcqV6kRs3KQ5lkJyfCm4/xmvUHzhesvwgBe4w2F9sYxNz026VQeSFgo+Og73m8uGBg=="
}
```

You can check a record and its DNS value locally with the reference validator:

```sh
python scripts/validate.py record.json --domain jadranskaribarnica.example --dns-value 'v=abiz1;k=hr-080123456;h=jadranskaribarnica.hr.to.co;p=SK7XK9qcGo0IvRSoLaau7hkLswsXx5Pn8aE3QQoMcUU='
```

### Self-hosted or through a provider

You can serve the record yourself on any HTTPS host you control, or use any compatible provider. ABIZ does not require a particular provider or hostname scheme. Either way, the record must be served over HTTPS, and you must control the domain where `_abiz` is published.

## 3. Using a provider and MCP

MCP (Model Context Protocol) is an open protocol that lets AI assistants call tools and read data from external servers. A provider can run an MCP server so that an assistant can request your public record directly. You can list one in the optional `mcp_server_url` field. ABIZ does not require an MCP server, and a tool should not call one automatically just because a record lists it.

For example, a provider might serve your record at `jadranskaribarnica.hr.to.co` and run an MCP server. An assistant connected to that server could then ask for the opening hours or services of Jadranska Ribarnica d.o.o. and receive the facts from your record, not from a guess.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 requires an Ed25519 public key in the DNS `p` tag. `v` and `h` are required. `p` is required. `k` is optional. `p` must be 32 raw bytes in standard base64: 44 characters ending in one `=`, in a single DNS string. Base64url is not accepted. Any other value, such as an ABIZ 1.0 hexadecimal token, makes the whole assertion invalid.

The matching private key belongs to the business. It is never published. A provider that holds it for you must let you export it. Software can check a signature made with the private key against the key in DNS. The business record repeats the key as `public_key` and carries a `signature` over the whole record, made with the private key (SPEC section 4.6). Software verifies the signature and checks that `public_key` equals `p`; a record that fails either check is not verified.

To rotate, generate a new Ed25519 keypair, publish the new public key in the DNS or well-known assertion, re-sign the business record with the new private key, and set `public_key` to that same `p`. Allow for DNS caching and propagation. Removing only `p` is not valid revocation while an ABIZ 1.1 assertion remains: to withdraw it, remove the complete DNS TXT record or well-known declaration. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record. A key shows which key the domain's controller published; it does not prove legal identity.

## 5. What AI tools will see

With a valid record, a compatible assistant can answer questions such as:

- "Is Jadranska Ribarnica d.o.o. a business in Split?"
- "What does Jadranska Ribarnica d.o.o. offer, and when is it open?"
- "Is jadranskaribarnica.example the official website of Jadranska Ribarnica d.o.o.?"
- "Which registration number does Jadranska Ribarnica d.o.o. publish for itself?"

The limits matter. ABIZ shows that a domain and a record point to each other. It does not prove that a business is legally registered, that a registration number is genuine, or that anyone endorses the business. A tool that has not checked the Court Register itself must not describe the business as verified. ABIZ does not guarantee that any AI service will find, rank or recommend a business.

## 6. Local practical notes

### Finding the registration number

The MBS is on the court registration decision and can be searched in the public [Sudski registar](https://sudreg.pravosudje.hr/). Crafts (obrt) are in a separate crafts register and have no MBS, so they omit the key.

### Adding the TXT record

Add the record wherever your domain's DNS is managed, usually at your domain registrar or web host. The registry for `.hr` domains is [CARNET](https://domene.hr/), but you add the record at your registrar or DNS host; any that supports TXT records will do. Create a record of type TXT with the name `_abiz` (some control panels want the full name, `_abiz.jadranskaribarnica.example`), the value exactly as above and a TTL of 300. Do not add spaces inside the value, and remove any older ABIZ record so that only one remains.

### Privacy and publishing data

Croatia is in the European Union, so the GDPR applies to personal data in your record, for example the name of a sole trader or a named contact. The [European Data Protection Board](https://www.edpb.europa.eu/) links to each national data protection authority. Everything in an ABIZ record is public, so publish only facts you mean to make public. A sole trader should not publish a home address: the specification requires private personal addresses to be left out, not marked as private. A role address such as `info@` is better than a personal email address.

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md): DNS syntax (section 3.1.1), the `p` key (section 3.3), business keys (section 4.2)
- [Normative JSON Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Reference validator, scripts/validate.py](../../../scripts/validate.py)
- [All European guides](index.md)
