# Becoming an Agentic Business using ABIZ in Albania

*A guide to published ABIZ 1.1. [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.* This first draft is in English; a version in Albanian has not been written yet.

## 1. What this means for a business in Albania

People increasingly ask AI assistants about businesses: who they are, what they offer, where to find them. ABIZ (Agentic Business Record) lets a business publish one public, machine-readable record of its own facts, such as its name, country, website, services and opening hours, and a DNS record on its own domain that points to that record.

Only the business, or someone it authorises, can change the DNS of its domain. So compatible software can find the record from the domain and check that the domain and the record refer to each other, instead of piecing facts together from scattered web pages. ABIZ is open and provider-independent: no membership, fee or particular provider is required.

## 2. How to publish an ABIZ record

### Required fields

The business record is a JSON document that must validate against the [normative schema](../../../schemas/abiz-business-record-v1.1.schema.json). Five fields are required:

| Field | Example for Albania | Notes |
| --- | --- | --- |
| `record_version` | `abiz1` | Always this value |
| `business_name` | `Ulliri Agro sh.p.k.` | The public name, usually as it appears on the register, with the legal form if you use it |
| `country` | `al` | ISO 3166-1 alpha-2 code; lowercase is the canonical form |
| `identity_host` | `ulliriagro.al.to.co` | Exactly the DNS `h` value: a hostname with an optional path, without `https://` |
| `domains` | `["ulliriagro.example"]` | The domains this record claims, including the one that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, the record must also contain `business_key` and `registration_number`, and `k` must equal `business_key`.

In Albania the key is `al-` followed by the registration number. Albania uses no subdivision, so a key with a middle part, such as `al-xx-…`, is invalid.

- **Register:** [National Business Centre (Qendra Kombëtare e Biznesit, QKB)](https://qkb.gov.al/)
- **Number to use:** the NUIS (also called NIPT), the identification number the QKB gives on registration: a letter, eight digits and a letter
- **How to write it:** start from the number as the register issues it, apply Unicode NFKC normalisation, remove spaces, `-`, `.`, `/` and other dash characters, then write letters in uppercase. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits.

Worked example (invented number): `L12345678A` is already in canonical form. The record then has `"registration_number": "L12345678A"` and `"business_key": "al-L12345678A"`, and DNS carries `k=al-L12345678A`.

Keys are compared case-insensitively, but publish the canonical form: lowercase country code, uppercase number.

### DNS TXT record

Publish exactly one ABIZ TXT record at `_abiz` on your domain. Use the compact form, with no spaces:

```dns
_abiz.ulliriagro.example. 300 IN TXT "v=abiz1;k=al-L12345678A;h=ulliriagro.al.to.co;p=3bkn4LMfVUSneY3p2AppPLZfVJb53fMCy6+GnLn9Fo0="
```

- `v=abiz1` must come first. `h` and `p` are required; `k` is optional.
- Tag names are lowercase and case-sensitive. A tag must not appear twice.
- A TTL of 300 seconds is recommended.

The `p` value above is a throwaway example key. Never copy it: publish your own key. An ABIZ 1.1 assertion must include `p`.

### Business record (JSON)

The record served at `https://ulliriagro.al.to.co`, as `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Ulliri Agro sh.p.k.",
  "country": {
    "code": "AL",
    "name": "Albania"
  },
  "business_key": "al-L12345678A",
  "registration_number": "L12345678A",
  "identity_host": "ulliriagro.al.to.co",
  "domains": [
    "ulliriagro.example"
  ],
  "public_key": "3bkn4LMfVUSneY3p2AppPLZfVJb53fMCy6+GnLn9Fo0=",
  "description": "Olive oil producer near Tirana.",
  "website": "https://ulliriagro.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Tirana",
        "country": {
          "code": "AL"
        }
      },
      "public": true
    }
  ],
  "signature": "mkrRsLWC32oxMDFmwBRFEsFqBbq5GUJWJL8QD5oDvCMV4IXlPGO3f8++N4R+v0DcHsiv8kHlADHyjlnCEl39DQ=="
}
```

You can check a record and its DNS value locally with the reference validator:

```sh
python scripts/validate.py record.json --domain ulliriagro.example --dns-value 'v=abiz1;k=al-L12345678A;h=ulliriagro.al.to.co;p=3bkn4LMfVUSneY3p2AppPLZfVJb53fMCy6+GnLn9Fo0='
```

### Self-hosted or through a provider

You can serve the record yourself on any HTTPS host you control, or use any compatible provider. ABIZ does not require a particular provider or hostname scheme. Either way, the record must be served over HTTPS, and you must control the domain where `_abiz` is published.

## 3. Using a provider and MCP

MCP (Model Context Protocol) is an open protocol that lets AI assistants call tools and read data from external servers. A provider can run an MCP server so that an assistant can request your public record directly. You can list one in the optional `mcp_server_url` field. ABIZ does not require an MCP server, and a tool should not call one automatically just because a record lists it.

For example, a provider might serve your record at `ulliriagro.al.to.co` and run an MCP server. An assistant connected to that server could then ask for the opening hours or services of Ulliri Agro sh.p.k. and receive the facts from your record, not from a guess.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 requires an Ed25519 public key in the DNS `p` tag. `v` and `h` are required. `p` is required. `k` is optional. `p` must be 32 raw bytes in standard base64: 44 characters ending in one `=`, in a single DNS string. Base64url is not accepted. Any other value, such as a hexadecimal string, makes the whole assertion invalid.

The matching private key belongs to the business. It is never published. A provider that holds it for you must let you export it. Software can check a signature made with the private key against the key in DNS. The business record repeats the key as `public_key` and carries a `signature` over the whole record, made with the private key (SPEC section 4.6). Software verifies the signature and checks that `public_key` equals `p`; a record that fails either check is not verified.

To rotate, generate a new Ed25519 keypair, publish the new public key in the DNS or well-known assertion, re-sign the business record with the new private key, and set `public_key` to that same `p`. Allow for DNS caching and propagation. Removing only `p` is not valid revocation while an ABIZ 1.1 assertion remains: to withdraw it, remove the complete DNS TXT record or well-known declaration. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record. A key shows which key the domain's controller published; it does not prove legal identity.

## 5. What AI tools will see

With a valid record, a compatible assistant can answer questions such as:

- "Is Ulliri Agro sh.p.k. a business in Tirana?"
- "What does Ulliri Agro sh.p.k. offer, and when is it open?"
- "Is ulliriagro.example the official website of Ulliri Agro sh.p.k.?"
- "Which registration number does Ulliri Agro sh.p.k. publish for itself?"

The limits matter. ABIZ shows that a domain and a record point to each other. It does not prove that a business is legally registered, that a registration number is genuine, or that anyone endorses the business. A tool that has not checked the QKB register itself must not describe the business as verified. ABIZ does not guarantee that any AI service will find, rank or recommend a business.

## 6. Local practical notes

### Finding the registration number

The NUIS is on the registration certificate (ekstrakt) from the QKB and on invoices. You can look it up in the QKB online register. Use the NUIS of the legal entity, with both letters.

### Adding the TXT record

Add the record wherever your domain's DNS is managed, usually at your domain registrar or web host. The registry for `.al` domains is [AKEP](https://www.akep.al/), but you add the record at your registrar or DNS host; any that supports TXT records will do. Create a record of type TXT with the name `_abiz` (some control panels want the full name, `_abiz.ulliriagro.example`), the value exactly as above and a TTL of 300. Do not add spaces inside the value, and remove any older ABIZ record so that only one remains.

### Privacy and publishing data

Albania's own data protection law applies to personal data in your record, for example the name of a sole trader or a named contact. If you also serve customers in the EU, the GDPR may apply too. Everything in an ABIZ record is public, so publish only facts you mean to make public. A sole trader should not publish a home address: the specification requires private personal addresses to be left out, not marked as private. A role address such as `info@` is better than a personal email address.

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md): DNS syntax (section 3.1.1), the `p` key (section 3.3), business keys (section 4.2)
- [Normative JSON Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Reference validator, scripts/validate.py](../../../scripts/validate.py)
- [All European guides](index.md)
