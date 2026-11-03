# Becoming an Agentic Business using ABIZ in Somalia

## 1. What this means for a business in Somalia

AI assistants are now often asked questions such as ‘what is this company’s real website?’ or ‘who runs this shop?’. ABIZ (Agentic Business Record) is an open standard that lets a business in Somalia publish its public facts once, in a form those tools can read: a short DNS TXT record on a domain the business controls, pointing to a JSON business record served over HTTPS. Because the pointer sits in the business’s own DNS, a tool can tell that the record was published by whoever controls that domain, instead of relying on an unofficial directory or a guess.

## 2. How to publish an ABIZ record

### Required fields

Every business record needs these five fields (SPEC section 4.1):

| Field | Example and rule |
|---|---|
| `record-version` | `abiz1` |
| `business-name` | the public name customers know, for example `Hodan Trading` |
| `country` | `so`, the ISO 3166-1 alpha-2 code, in lowercase |
| `identity-host` | `www.hodantrading.example/abiz`, which must match `h` in DNS exactly |
| `domains` | `["hodantrading.example"]`, which must include the domain that carries `_abiz` |

A minimal record:

```json
{
  "record-version": "abiz1",
  "business-name": "Hodan Trading",
  "country": "so",
  "identity-host": "www.hodantrading.example/abiz",
  "domains": [
    "hodantrading.example"
  ]
}
```

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, it must equal `business-key` in the record, and the record must then also contain `registration-number`. For Somalia the form is:

```text
so-<registration-number>
```

Somalia uses no subdivision: do not add a region, province or city code. SPEC section 4.2.2 requires a subdivision only for the United States, Canadian provincial corporations and the United Arab Emirates, and forbids it everywhere else.

**Which number:** we could not confirm a single national register whose numbers identify businesses uniquely across Somalia.

**Normalisation (SPEC section 4.2.3):** start from the number exactly as the register issues it, apply Unicode NFKC, remove spaces, `-`, `.`, `/` and the dash characters, then uppercase any letters. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits. If it does not, you cannot publish a business key: leave out `k`, `business-key` and `registration-number`.

**No business key for now:** because registrations may sit with different authorities and SPEC section 4.2.2 allows no subdivision for `so`, we cannot confirm that any number gives a valid national key. Leave out `k`, `business-key` and `registration-number`. The rest of the record works as shown.

### DNS TXT record

Publish exactly one TXT record at `_abiz` under your domain, in the compact form with no spaces and `v=abiz1` first:

```dns
_abiz.hodantrading.example. 300 IN TXT "v=abiz1;h=www.hodantrading.example/abiz;p=oS5YhE6Qz35Id1hMp3XOI3eQWW03DVgY3kU6rEdlodQ="
```

Without the optional `k` and `p` tags, this is also valid:

```dns
_abiz.hodantrading.example. 300 IN TXT "v=abiz1;h=www.hodantrading.example/abiz"
```

All names and numbers on this page are fictional. The `p` value is the throwaway example key from the specification, not a real key.

You can host the JSON record yourself on any HTTPS server, or use any compatible provider. ABIZ does not require a particular provider.

To check a record before you publish it, run the reference validator from a copy of this repository:

```sh
python scripts/validate.py record.json --domain hodantrading.example --dns-value "v=abiz1;h=www.hodantrading.example/abiz;p=oS5YhE6Qz35Id1hMp3XOI3eQWW03DVgY3kU6rEdlodQ="
```

## 3. Using a provider and MCP

The Model Context Protocol (MCP) is an open protocol that lets AI assistants call tools and read data from outside servers in a standard way. A business record may include an optional `mcp-server-url`, the HTTPS address of an MCP server for the business, for example for bookings or product information. ABIZ does not vouch for that server; tools must apply their own access controls (SPEC section 4.2.6).

Your own server or any compatible provider can host the record. This guide gives no provider example for Somalia; check that any provider you choose can lawfully serve businesses there.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 adds an optional signing key. The DNS `p` tag can carry an Ed25519 public key: 44 characters of standard base64 ending in one `=` (SPEC section 3.3.2). The business, or a provider acting for it, keeps the matching private key and can sign material that others check against the published key. The private key always belongs to the business, and a hosting provider must let the business export it.

- `p` is optional. If it is present it must be a valid key: any other value, such as an old ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid.
- Only the current key is published. To rotate, publish the new key in `p`; to revoke, remove `p`. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record.
- A key shows who controls the domain’s DNS. It does not prove legal identity.

## 5. What AI tools will see

A compatible tool that reads your record can answer questions such as:

1. What is the official website of Hodan Trading?
2. Which domains belong to this business?
3. Which registration number does the business give, and in which country?
4. What does it offer, and when is it open?

**Limits:** ABIZ shows what the controller of a domain has published. It does not prove that the business is legally registered, that its number is genuine, or that any AI service, government or provider endorses it. Where it matters, tools and people should check the official register.

## 6. Local practical notes

- **Register:** the federal Ministry of Commerce and Industry; some federal member states and Somaliland also register businesses themselves. We have not listed a website because we could not confirm an official address that loads.
- **Adding the TXT record:** in the DNS settings of your registrar or DNS host, add a TXT record with the name `_abiz` (some panels want the full name, `_abiz.yourdomain.so`), the value shown above and a TTL of 300 seconds. Domains under `.so` work in the same way as `.com` or any other domain. Keep the value in one piece where possible, and never split `p`.
- **Privacy:** Check the data-protection rules that apply in Somalia before you publish personal data. An ABIZ record is public. Publish only business facts you are happy to share, and leave out private home addresses and personal phone numbers (SPEC section 4.3).
- **Languages:** Somali and Arabic are official. This guide is in English.

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md)
- [Business record JSON Schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Reference validator](../../../scripts/validate.py)
- [ABIZ country guides: Africa](index.md)
