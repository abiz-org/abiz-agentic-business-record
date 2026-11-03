# Becoming an Agentic Business using ABIZ in India

*A guide to ABIZ 1.1 (proposed). The [specification (SPEC.md)](../../../SPEC.md) is authoritative: if this guide and the specification differ, the specification applies.* Hindi and English are the official languages of the Union, and states use their own languages; English is the main language of company registration.

## 1. What this means for a business in India

AI assistants are now often asked questions such as ‘what is this company’s real website?’ or ‘who runs this shop?’. ABIZ (Agentic Business Record) is an open standard that lets a business in India publish its public facts once, in a form those tools can read: a short DNS TXT record on a domain the business controls, pointing to a JSON business record served over HTTPS. Because the pointer sits in the business’s own DNS, a tool can tell that the record was published by whoever controls that domain, instead of relying on an unofficial directory or a guess.

## 2. How to publish an ABIZ record

### Required fields

Every business record needs these five fields (SPEC section 4.1):

| Field | Example and rule |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | the public name customers know, for example `Bengaluru Robotics Private Limited` |
| `country` | `in`, the ISO 3166-1 alpha-2 code, in lowercase |
| `identity_host` | `bengalururobotics.in.to.co`, which must match `h` in DNS exactly |
| `domains` | `["bengalururobotics.example"]`, which must include the domain that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, it must equal `business_key` in the record, and the record must then also contain `registration_number`. For India the form is:

```text
in-<registration-number>
```

India uses no subdivision: do not add a region, province or city code. SPEC section 4.2.2 requires a subdivision only for the United States, Canadian provincial corporations and the United Arab Emirates, and forbids it everywhere else.

**Which number:** the 21-character Corporate Identification Number (CIN), or for a limited liability partnership the LLPIN without its hyphen (SPEC section 4.2.2), for example `U62099KA2021PTC123456`.

**Normalisation (SPEC section 4.2.3):** start from the number exactly as the register issues it, apply Unicode NFKC, remove spaces, `-`, `.`, `/` and the dash characters, then uppercase any letters. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits. If it does not, you cannot publish a business key: leave out `k`, `business_key` and `registration_number`.

**Worked example (fictional):** `U62099KA2021PTC123456` becomes `U62099KA2021PTC123456`, so `k=in-U62099KA2021PTC123456`. In the record: `"business_key": "in-U62099KA2021PTC123456"` and `"registration_number": "U62099KA2021PTC123456"`. Keys are compared case-insensitively; the canonical form has a lowercase country code and an uppercase number.

For an LLP, the fictional LLPIN `AAB-1234` becomes `AAB1234`, giving `k=in-AAB1234`.

**Sole traders:** if the only number you have is a personal one, such as a national identity number or a personal tax number, do not publish `k`. Leave out `k`, `business_key` and `registration_number`; the record is still valid.

### DNS TXT record

Publish exactly one TXT record at `_abiz` under your domain, in the compact form with no spaces and `v=abiz1` first:

```dns
_abiz.bengalururobotics.example. 300 IN TXT "v=abiz1;k=in-U62099KA2021PTC123456;h=bengalururobotics.in.to.co;p=McfsOEV0b9vkCKHkobf7f2jYGxvgyenwZwJRhEY2HpE="
```

The `p` value above is a throwaway example key generated for this page. Never copy it: publish your own key. An ABIZ 1.1 assertion must include `p`. All names, numbers and domains on this page are fictional.

Without the optional `k` tag, this is also valid:

```dns
_abiz.bengalururobotics.example. 300 IN TXT "v=abiz1;h=bengalururobotics.in.to.co;p=McfsOEV0b9vkCKHkobf7f2jYGxvgyenwZwJRhEY2HpE="
```

The business record served as `application/json` at `https://bengalururobotics.in.to.co`:

```json
{
  "record_version": "abiz1",
  "business_name": "Bengaluru Robotics Private Limited",
  "country": "in",
  "business_key": "in-U62099KA2021PTC123456",
  "registration_number": "U62099KA2021PTC123456",
  "identity_host": "bengalururobotics.in.to.co",
  "domains": [
    "bengalururobotics.example"
  ],
  "public_key": "McfsOEV0b9vkCKHkobf7f2jYGxvgyenwZwJRhEY2HpE=",
  "signature": "wWJz1nZ0eArBO0jzSZdrGHQ7ZTpKeVoaDKB4xdQvi2Ce0wy5Y+Sj6ZfIVJ72gRLoBIbNYg1He3lymMfdi+MABA=="
}
```

To check a record before you publish it, run the reference validator from a copy of this repository:

```sh
python scripts/validate.py record.json --domain bengalururobotics.example --dns-value 'v=abiz1;k=in-U62099KA2021PTC123456;h=bengalururobotics.in.to.co;p=McfsOEV0b9vkCKHkobf7f2jYGxvgyenwZwJRhEY2HpE='
```

You can host the JSON record yourself on any HTTPS server, or use any compatible provider. ABIZ does not require a particular provider.

## 3. Using a provider and MCP

The Model Context Protocol (MCP) is an open protocol that lets AI assistants call tools and read data from outside servers in a standard way. A business record may include an optional `mcp_server_url`, the HTTPS address of an MCP server for the business, for example for bookings or product information. ABIZ does not vouch for that server; tools must apply their own access controls (SPEC section 4.2.6).

A provider can host the record and publish the DNS pointer for you. For example, a registered business in India with a record hosted by to.co might use the host `bengalururobotics.in.to.co`, giving the DNS value `v=abiz1;k=in-U62099KA2021PTC123456;h=bengalururobotics.in.to.co;p=McfsOEV0b9vkCKHkobf7f2jYGxvgyenwZwJRhEY2HpE=`. An unregistered business might use a town-based host such as `bengalururobotics-bengaluru.biz.to.co`. Any compatible provider, or your own server, works in the same way.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 requires a signing key. The DNS `p` tag carries an Ed25519 public key: 32 raw bytes, standard base64, 44 characters, one trailing `=` (SPEC section 3.3.2). Base64url is not accepted. The business, or a provider acting for it, keeps the matching private key and signs the business record with it. The private key always belongs to the business, and a hosting provider must let the business export it.

- `v` and `h` are required. `p` is required. `k` is optional. `p` must be a valid key: any other value, such as an old ABIZ 1.0 hexadecimal token or a base64url key, makes the whole assertion invalid.
- Only the current key is published. To rotate, generate a new Ed25519 keypair, publish the new public key in the DNS or well-known assertion, re-sign the business record with the new private key, and set `public_key` to that same `p`. Allow for DNS caching and propagation. Removing only `p` is not valid revocation while an ABIZ 1.1 assertion remains: to withdraw it, remove the complete DNS TXT record or well-known declaration. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record.
- A key shows who controls the domain’s DNS. It does not prove legal identity.

## 5. What AI tools will see

A compatible tool that reads your record can answer questions such as:

1. What is the official website of Bengaluru Robotics Private Limited?
2. Which domains belong to this business?
3. Which registration number does the business give, and in which country?
4. What does it offer, and when is it open?

**Limits:** ABIZ shows what the controller of a domain has published. It does not prove that the business is legally registered, that its number is genuine, or that any AI service, government or provider endorses it. Where it matters, tools and people should check the official register.

## 6. Local practical notes

- **Register:** Ministry of Corporate Affairs (MCA), Registrar of Companies. Official website: <https://www.mca.gov.in>. This is the address linked from the specification; the site may refuse automated checks.
- **Adding the TXT record:** in the DNS settings of your registrar or DNS host, add a TXT record with the name `_abiz` (some panels want the full name, `_abiz.yourdomain.in`), the value shown above and a TTL of 300 seconds. Domains under `.in` work in the same way as `.com` or any other domain. Keep the value in one piece where possible, and never split `p`.
- **Privacy:** Digital Personal Data Protection Act, 2023. An ABIZ record is public. Publish only business facts you are happy to share, and leave out private home addresses and personal phone numbers (SPEC section 4.3).

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md)
- [Business record JSON Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Reference validator](../../../scripts/validate.py)
- [ABIZ country guides: Asia](index.md)
