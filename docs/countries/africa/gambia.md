# Becoming an Agentic Business using ABIZ in The Gambia

*A guide to published ABIZ 1.1. The [specification (SPEC.md)](../../../SPEC.md) is authoritative: if this guide and the specification differ, the specification applies.* English is the official language and the language of registration.

## 1. What this means for a business in The Gambia

AI assistants are now often asked questions such as ‘what is this company’s real website?’ or ‘who runs this shop?’. ABIZ (Agentic Business Record) is an open standard that lets a business in The Gambia publish its public facts once, in a form those tools can read: a short DNS TXT record on a domain the business controls, pointing to a JSON business record served over HTTPS. Because the pointer sits in the business’s own DNS, a tool can tell that the record was published by whoever controls that domain, instead of relying on an unofficial directory or a guess.

## 2. How to publish an ABIZ record

### Required fields

Every business record needs these five fields (SPEC section 4.1):

| Field | Example and rule |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | the public name customers know, for example `Banjul Fabrics` |
| `country` | `gm`, the ISO 3166-1 alpha-2 code, in lowercase |
| `identity_host` | `banjulfabrics.gm.to.co`, which must match `h` in DNS exactly |
| `domains` | `["banjulfabrics.example"]`, which must include the domain that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, it must equal `business_key` in the record, and the record must then also contain `registration_number`. For The Gambia the form is:

```text
gm-<registration-number>
```

The Gambia uses no subdivision: do not add a region, province or city code. SPEC section 4.2.2 requires a subdivision only for the United States, Canadian provincial corporations and the United Arab Emirates, and forbids it everywhere else.

**Which number:** the registration number on your certificate of incorporation or business name registration, exactly as issued.

**Normalisation (SPEC section 4.2.3):** start from the number exactly as the register issues it, apply Unicode NFKC, remove spaces, `-`, `.`, `/` and the dash characters, then uppercase any letters. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits. If it does not, you cannot publish a business key: leave out `k`, `business_key` and `registration_number`.

**Worked example (fictional):** `C/2023/12345` becomes `C202312345`, so `k=gm-C202312345`. In the record: `"business_key": "gm-C202312345"` and `"registration_number": "C202312345"`. Keys are compared case-insensitively; the canonical form has a lowercase country code and an uppercase number.

**Please check:** we could not confirm the exact format of this number from an official source, so the example is illustrative only. Use the number exactly as it appears on your official registration document. If it is not clear which number identifies your business nationally, leave `k` out until you are sure.

**Sole traders:** if the only number you have is a personal one, such as a national identity number or a personal tax number, do not publish `k`. Leave out `k`, `business_key` and `registration_number`; the record is still valid.

### DNS TXT record

Publish exactly one TXT record at `_abiz` under your domain, in the compact form with no spaces and `v=abiz1` first:

```dns
_abiz.banjulfabrics.example. 300 IN TXT "v=abiz1;k=gm-C202312345;h=banjulfabrics.gm.to.co;p=uKverb1sGlqHa0IUxm98h1pwL3pBxNrV2z13mumoHio="
```

The `p` value above is a throwaway example key generated for this page. Never copy it: publish your own key. An ABIZ 1.1 assertion must include `p`. All names, numbers and domains on this page are fictional.

Without the optional `k` tag, this is also valid:

```dns
_abiz.banjulfabrics.example. 300 IN TXT "v=abiz1;h=banjulfabrics.gm.to.co;p=uKverb1sGlqHa0IUxm98h1pwL3pBxNrV2z13mumoHio="
```

The business record served as `application/json` at `https://banjulfabrics.gm.to.co`:

```json
{
  "record_version": "abiz1",
  "business_name": "Banjul Fabrics",
  "country": {
    "code": "GM",
    "name": "Gambia"
  },
  "business_key": "gm-C202312345",
  "registration_number": "C202312345",
  "identity_host": "banjulfabrics.gm.to.co",
  "domains": [
    "banjulfabrics.example"
  ],
  "public_key": "uKverb1sGlqHa0IUxm98h1pwL3pBxNrV2z13mumoHio=",
  "signature": "P36HSEJ7QnKp7yYNFg89W82YJgTD+KPIW3l8PLQNWOuVyfJRnfRd7STnZryKrt6wpWkyTRLsITB7F+xk0vtyBQ=="
}
```

To check a record before you publish it, run the reference validator from a copy of this repository:

```sh
python scripts/validate.py record.json --domain banjulfabrics.example --dns-value 'v=abiz1;k=gm-C202312345;h=banjulfabrics.gm.to.co;p=uKverb1sGlqHa0IUxm98h1pwL3pBxNrV2z13mumoHio='
```

You can host the JSON record yourself on any HTTPS server, or use any compatible provider. ABIZ does not require a particular provider.

## 3. Using a provider and MCP

The Model Context Protocol (MCP) is an open protocol that lets AI assistants call tools and read data from outside servers in a standard way. A business record may include an optional `mcp_server_url`, the HTTPS address of an MCP server for the business, for example for bookings or product information. ABIZ does not vouch for that server; tools must apply their own access controls (SPEC section 4.2.6).

A provider can host the record and publish the DNS pointer for you. For example, a registered business in The Gambia with a record hosted by to.co might use the host `banjulfabrics.gm.to.co`, giving the DNS value `v=abiz1;k=gm-C202312345;h=banjulfabrics.gm.to.co;p=uKverb1sGlqHa0IUxm98h1pwL3pBxNrV2z13mumoHio=`. An unregistered business might use a town-based host such as `banjulfabrics-banjul.biz.to.co`. Any compatible provider, or your own server, works in the same way.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 requires a signing key. The DNS `p` tag carries an Ed25519 public key: 32 raw bytes, standard base64, 44 characters, one trailing `=` (SPEC section 3.3.2). Base64url is not accepted. The business, or a provider acting for it, keeps the matching private key and signs the business record with it. The private key always belongs to the business, and a hosting provider must let the business export it.

- `v` and `h` are required. `p` is required. `k` is optional. `p` must be a valid key: any other value, such as a hexadecimal string or a base64url key, makes the whole assertion invalid.
- Only the current key is published. To rotate, generate a new Ed25519 keypair, publish the new public key in the DNS or well-known assertion, re-sign the business record with the new private key, and set `public_key` to that same `p`. Allow for DNS caching and propagation. Removing only `p` is not valid revocation while an ABIZ 1.1 assertion remains: to withdraw it, remove the complete DNS TXT record or well-known declaration. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record.
- A key shows who controls the domain’s DNS. It does not prove legal identity.

## 5. What AI tools will see

A compatible tool that reads your record can answer questions such as:

1. What is the official website of Banjul Fabrics?
2. Which domains belong to this business?
3. Which registration number does the business give, and in which country?
4. What does it offer, and when is it open?

**Limits:** ABIZ shows what the controller of a domain has published. It does not prove that the business is legally registered, that its number is genuine, or that any AI service, government or provider endorses it. Where it matters, tools and people should check the official register.

## 6. Local practical notes

- **Register:** Registrar of Companies, through the Single Window Business Registration office. We have not listed a website because we could not confirm an official address that loads.
- **Adding the TXT record:** in the DNS settings of your registrar or DNS host, add a TXT record with the name `_abiz` (some panels want the full name, `_abiz.yourdomain.gm`), the value shown above and a TTL of 300 seconds. Domains under `.gm` work in the same way as `.com` or any other domain. Keep the value in one piece where possible, and never split `p`.
- **Privacy:** Check the data-protection rules that apply in The Gambia before you publish personal data. An ABIZ record is public. Publish only business facts you are happy to share, and leave out private home addresses and personal phone numbers (SPEC section 4.3).

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md)
- [Business record JSON Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Reference validator](../../../scripts/validate.py)
- [ABIZ country guides: Africa](index.md)
