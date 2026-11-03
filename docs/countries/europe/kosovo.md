# Becoming an Agentic Business using ABIZ in Kosovo

*A guide to published ABIZ 1.1. [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.* This page is in English; versions in Albanian and Serbian have not been written yet.

> **Important:** under ABIZ 1.1, a business in Kosovo cannot yet publish a conformant ABIZ record. The required `country` field must be an assigned ISO 3166-1 alpha-2 code, and Kosovo's commonly used code, `XK`, is a user-assigned code, not an assigned one. The specification names `xk` as invalid (section 4.2.1), it is not in the repository's [list of codes](../../../data/iso3166.json), and the reference validator rejects it. No business key `k` is possible either. This page explains what ABIZ is and what would be needed; it does not give a record to copy.

## 1. What this means for a business in Kosovo

People increasingly ask AI assistants about businesses: who they are, what they offer, where to find them. ABIZ (Agentic Business Record) lets a business publish one public, machine-readable record of its own facts, such as its name, country, website, services and opening hours, and a DNS record on its own domain that points to that record.

Only the business, or someone it authorises, can change the DNS of its domain. So compatible software can find the record from the domain and check that the domain and the record refer to each other, instead of piecing facts together from scattered web pages. ABIZ is open and provider-independent: no membership, fee or particular provider is required.

For a business in Kosovo, this is not yet possible in a conformant way, because of the country code described above. A future revision of the specification may address it.

## 2. How to publish an ABIZ record

### Required fields

The business record is a JSON document that must validate against the [normative schema](../../../schemas/abiz-business-record-v1.1.schema.json). Five fields are required:

| Field | Notes |
| --- | --- |
| `record_version` | Always `abiz1` |
| `business_name` | The public name, usually as it appears in the business register |
| `country` | An **assigned** ISO 3166-1 alpha-2 code, in lowercase. `xk` is not accepted under ABIZ 1.1, so a Kosovo business has no valid value here. Do not use another country's code instead: the record would then make a false statement about the business. |
| `identity_host` | Exactly the DNS `h` value: a hostname with an optional path, without `https://` |
| `domains` | The domains the record claims, including the one that carries `_abiz` |

### Optional business key `k`

No business key is possible for Kosovo under ABIZ 1.1. A business key starts with the country code, and `xk` is not a valid one. Leave out `k`, `business_key` and `registration_number`. Do not invent a key.

### DNS TXT record and examples

This page gives no TXT or JSON example, because no example would pass the reference validator. The DNS syntax itself is the same everywhere: exactly one compact record at `_abiz.<your domain>`, starting with `v=abiz1`, with required `h` and `p`, and optional `k`. See section 3.1.1 of the [specification](../../../SPEC.md) and any other country guide in this folder.

### Self-hosted or through a provider

When a conformant record becomes possible, it can be served on any HTTPS host you control or through any compatible provider. ABIZ does not require a particular provider or hostname scheme.

## 3. Using a provider and MCP

MCP (Model Context Protocol) is an open protocol that lets AI assistants call tools and read data from external servers. A provider can run an MCP server so that an assistant can request a business's public record directly, and a record can list one in the optional `mcp_server_url` field. ABIZ does not require an MCP server, and a tool should not call one automatically just because a record lists it. Until a Kosovo business can publish a conformant record, there is nothing for such a server to serve under ABIZ 1.1.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 requires an Ed25519 public key in the DNS `p` tag. `v` and `h` are required. `p` is required. `k` is optional. `p` must be 32 raw bytes in standard base64: 44 characters ending in one `=`, in a single DNS string. Base64url is not accepted. The matching private key belongs to the business and is never published. To rotate, generate a new Ed25519 keypair, publish the new public key, re-sign the business record, and set `public_key` to that same `p`. Allow for DNS caching and propagation. Removing only `p` is not valid revocation while an ABIZ 1.1 assertion remains: to withdraw it, remove the complete declaration. Retired keys are not published in ABIZ 1.1. A key shows which key the domain's controller published; it does not prove legal identity. A key alone does not make a record conformant, so it does not solve the country-code problem.

## 5. What AI tools will see

With a valid record, a compatible assistant could answer questions such as "Is this business in Prishtina?", "What does it offer, and when is it open?" or "Is this its official website?". Because a Kosovo business cannot yet publish a valid record, conforming tools should not rely on one.

Even with a valid record, the limits matter. ABIZ shows that a domain and a record point to each other. It does not prove that a business is legally registered, that a registration number is genuine, or that anyone endorses the business. ABIZ does not guarantee that any AI service will find, rank or recommend a business.

## 6. Local practical notes

### The business register

Businesses in Kosovo are registered with the [Kosovo Business Registration Agency (ARBK)](https://arbk.rks-gov.net/). Your registration certificate shows your business number. It cannot be used in an ABIZ business key under ABIZ 1.1.

### Adding a TXT record

Kosovo does not have its own country-code top-level domain in use, so businesses usually use another domain, such as a `.com` or `.eu` domain. TXT records are added at your registrar or DNS host.

### Privacy and publishing data

Kosovo's law on the protection of personal data applies to personal data you publish. If you serve customers in the EU, the GDPR may apply too. Everything in an ABIZ record is public; a sole trader should not publish a home address.

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md): the `country` field (section 4.1), business keys and the `xk` code (section 4.2.1)
- [Normative JSON Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Reference validator, scripts/validate.py](../../../scripts/validate.py)
- [All European guides](index.md)
