# Becoming an Agentic Business using ABIZ in South Africa

*A guide to ABIZ 1.1 (proposed). The [specification (SPEC.md)](../../../SPEC.md) is authoritative: if this guide and the specification differ, the specification applies.* South Africa has 12 official languages; English is the main language of business and of the CIPC.

## 1. What this means for a business in South Africa

AI assistants are now often asked questions such as ‘what is this company’s real website?’ or ‘who runs this shop?’. ABIZ (Agentic Business Record) is an open standard that lets a business in South Africa publish its public facts once, in a form those tools can read: a short DNS TXT record on a domain the business controls, pointing to a JSON business record served over HTTPS. Because the pointer sits in the business’s own DNS, a tool can tell that the record was published by whoever controls that domain, instead of relying on an unofficial directory or a guess.

## 2. How to publish an ABIZ record

### Required fields

Every business record needs these five fields (SPEC section 4.1):

| Field | Example and rule |
|---|---|
| `record-version` | `abiz1` |
| `business-name` | the public name customers know, for example `Karoo Leather Goods` |
| `country` | `za`, the ISO 3166-1 alpha-2 code, in lowercase |
| `identity-host` | `karooleather.za.to.co`, which must match `h` in DNS exactly |
| `domains` | `["karooleather.example"]`, which must include the domain that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, it must equal `business-key` in the record, and the record must then also contain `registration-number`. For South Africa the form is:

```text
za-<registration-number>
```

South Africa uses no subdivision: do not add a region, province or city code. SPEC section 4.2.2 requires a subdivision only for the United States, Canadian provincial corporations and the United Arab Emirates, and forbids it everywhere else.

**Which number:** the enterprise registration number issued by the CIPC, in the form year/sequence/type, for example `2023/123456/07` for a private company.

**Normalisation (SPEC section 4.2.3):** start from the number exactly as the register issues it, apply Unicode NFKC, remove spaces, `-`, `.`, `/` and the dash characters, then uppercase any letters. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits. If it does not, you cannot publish a business key: leave out `k`, `business-key` and `registration-number`.

**Worked example (fictional):** `2023/123456/07` becomes `202312345607`, so `k=za-202312345607`. In the record: `"business-key": "za-202312345607"` and `"registration-number": "202312345607"`. Keys are compared case-insensitively; the canonical form has a lowercase country code and an uppercase number.

**Sole traders:** if the only number you have is a personal one, such as a national identity number or a personal tax number, do not publish `k`. Leave out `k`, `business-key` and `registration-number`; the record is still valid.

### DNS TXT record

Publish exactly one TXT record at `_abiz` under your domain, in the compact form with no spaces and `v=abiz1` first:

```dns
_abiz.karooleather.example. 300 IN TXT "v=abiz1;k=za-202312345607;h=karooleather.za.to.co;p=QNMuqI4/2VCDC4ienpfDUKa9mKk79XwZGTaMfu0DrtM="
```

The `p` value above is a throwaway example key generated for this page. Never copy it: publish your own key or leave `p` out. All names, numbers and domains on this page are fictional.

Without the optional `k` and `p` tags, this is also valid:

```dns
_abiz.karooleather.example. 300 IN TXT "v=abiz1;h=karooleather.za.to.co"
```

The business record served as `application/json` at `https://karooleather.za.to.co`:

```json
{
  "record-version": "abiz1",
  "business-name": "Karoo Leather Goods",
  "country": "za",
  "business-key": "za-202312345607",
  "registration-number": "202312345607",
  "identity-host": "karooleather.za.to.co",
  "domains": [
    "karooleather.example"
  ]
}
```

To check a record before you publish it, run the reference validator from a copy of this repository:

```sh
python scripts/validate.py record.json --domain karooleather.example --dns-value 'v=abiz1;k=za-202312345607;h=karooleather.za.to.co;p=QNMuqI4/2VCDC4ienpfDUKa9mKk79XwZGTaMfu0DrtM='
```

You can host the JSON record yourself on any HTTPS server, or use any compatible provider. ABIZ does not require a particular provider.

## 3. Using a provider and MCP

The Model Context Protocol (MCP) is an open protocol that lets AI assistants call tools and read data from outside servers in a standard way. A business record may include an optional `mcp-server-url`, the HTTPS address of an MCP server for the business, for example for bookings or product information. ABIZ does not vouch for that server; tools must apply their own access controls (SPEC section 4.2.6).

A provider can host the record and publish the DNS pointer for you. For example, a registered business in South Africa with a record hosted by to.co might use the host `karooleather.za.to.co`, giving the DNS value `v=abiz1;k=za-202312345607;h=karooleather.za.to.co`. An unregistered business might use a town-based host such as `karooleather-graaffreinet.biz.to.co`. Any compatible provider, or your own server, works in the same way.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 adds an optional signing key. The DNS `p` tag can carry an Ed25519 public key: 44 characters of standard base64 ending in one `=` (SPEC section 3.3.2). The business, or a provider acting for it, keeps the matching private key and can sign material that others check against the published key. The private key always belongs to the business, and a hosting provider must let the business export it.

- `p` is optional. If it is present it must be a valid key: any other value, such as an old ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid.
- Only the current key is published. To rotate, publish the new key in `p`; to revoke, remove `p`. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record.
- A key shows who controls the domain’s DNS. It does not prove legal identity.

## 5. What AI tools will see

A compatible tool that reads your record can answer questions such as:

1. What is the official website of Karoo Leather Goods?
2. Which domains belong to this business?
3. Which registration number does the business give, and in which country?
4. What does it offer, and when is it open?

**Limits:** ABIZ shows what the controller of a domain has published. It does not prove that the business is legally registered, that its number is genuine, or that any AI service, government or provider endorses it. Where it matters, tools and people should check the official register.

## 6. Local practical notes

- **Register:** Companies and Intellectual Property Commission (CIPC). Official website: <https://www.cipc.co.za>.
- **Adding the TXT record:** in the DNS settings of your registrar or DNS host, add a TXT record with the name `_abiz` (some panels want the full name, `_abiz.yourdomain.co.za`), the value shown above and a TTL of 300 seconds. Domains under `.co.za` work in the same way as `.com` or any other domain. Keep the value in one piece where possible, and never split `p`.
- **Privacy:** Protection of Personal Information Act, 2013 (POPIA), overseen by the Information Regulator. An ABIZ record is public. Publish only business facts you are happy to share, and leave out private home addresses and personal phone numbers (SPEC section 4.3).

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md)
- [Business record JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Reference validator](../../../scripts/validate.py)
- [ABIZ country guides: Africa](index.md)
