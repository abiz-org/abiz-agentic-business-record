# Becoming an Agentic Business using ABIZ in Malawi

*A guide to published ABIZ 1.1. The [specification (SPEC.md)](../../../SPEC.md) is authoritative: if this guide and the specification differ, the specification applies.* English is the official language of government and business; Chichewa is the national language.

## 1. What this means for a business in Malawi

AI assistants are now often asked questions such as ‘what is this company’s real website?’ or ‘who runs this shop?’. ABIZ (Agentic Business Record) is an open standard that lets a business in Malawi publish its public facts once, in a form those tools can read: a short DNS TXT record on a domain the business controls, pointing to a JSON business record served over HTTPS. Because the pointer sits in the business’s own DNS, a tool can tell that the record was published by whoever controls that domain, instead of relying on an unofficial directory or a guess.

## 2. How to publish an ABIZ record

### Required fields

Every business record needs these five fields (SPEC section 4.1):

| Field | Example and rule |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | the public name customers know, for example `Lake Shore Joinery` |
| `country` | `mw`, the ISO 3166-1 alpha-2 code, in lowercase |
| `identity_host` | `lakeshorejoinery.mw.to.co`, which must match `h` in DNS exactly |
| `domains` | `["lakeshorejoinery.example"]`, which must include the domain that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, it must equal `business_key` in the record, and the record must then also contain `registration_number`. For Malawi the form is:

```text
mw-<registration-number>
```

Malawi uses no subdivision: do not add a region, province or city code. SPEC section 4.2.2 requires a subdivision only for the United States, Canadian provincial corporations and the United Arab Emirates, and forbids it everywhere else.

**Which number:** the registration number on your certificate of incorporation or business name registration, exactly as issued.

**Normalisation (SPEC section 4.2.3):** start from the number exactly as the register issues it, apply Unicode NFKC, remove spaces, `-`, `.`, `/` and the dash characters, then uppercase any letters. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits. If it does not, you cannot publish a business key: leave out `k`, `business_key` and `registration_number`.

**Worked example (fictional):** `COY-ABC1234` becomes `COYABC1234`, so `k=mw-COYABC1234`. In the record: `"business_key": "mw-COYABC1234"` and `"registration_number": "COYABC1234"`. Keys are compared case-insensitively; the canonical form has a lowercase country code and an uppercase number.

**Please check:** we could not confirm the exact format of this number from an official source, so the example is illustrative only. Use the number exactly as it appears on your official registration document. If it is not clear which number identifies your business nationally, leave `k` out until you are sure.

**Sole traders:** if the only number you have is a personal one, such as a national identity number or a personal tax number, do not publish `k`. Leave out `k`, `business_key` and `registration_number`; the record is still valid.

### DNS TXT record

Publish exactly one TXT record at `_abiz` under your domain, in the compact form with no spaces and `v=abiz1` first:

```dns
_abiz.lakeshorejoinery.example. 300 IN TXT "v=abiz1;k=mw-COYABC1234;h=lakeshorejoinery.mw.to.co;p=EW3qVKb9+gzEt8y2lPP/NoHXpnY5ZGVinAMOxPE1j9c="
```

The `p` value above is a throwaway example key generated for this page. Never copy it: publish your own key. An ABIZ 1.1 assertion must include `p`. All names, numbers and domains on this page are fictional.

Without the optional `k` tag, this is also valid:

```dns
_abiz.lakeshorejoinery.example. 300 IN TXT "v=abiz1;h=lakeshorejoinery.mw.to.co;p=EW3qVKb9+gzEt8y2lPP/NoHXpnY5ZGVinAMOxPE1j9c="
```

The business record served as `application/json` at `https://lakeshorejoinery.mw.to.co`:

```json
{
  "record_version": "abiz1",
  "business_name": "Lake Shore Joinery",
  "country": "mw",
  "business_key": "mw-COYABC1234",
  "registration_number": "COYABC1234",
  "identity_host": "lakeshorejoinery.mw.to.co",
  "domains": [
    "lakeshorejoinery.example"
  ],
  "public_key": "EW3qVKb9+gzEt8y2lPP/NoHXpnY5ZGVinAMOxPE1j9c=",
  "signature": "2aG+Cn4Vrntl8XHQ2ES220gKDUR5qPgz3LHAiI5Q3aB6LFYMqf4+PGeU3jcnE6d7oWOzDQf/tge9wSQBkuWDDQ=="
}
```

To check a record before you publish it, run the reference validator from a copy of this repository:

```sh
python scripts/validate.py record.json --domain lakeshorejoinery.example --dns-value 'v=abiz1;k=mw-COYABC1234;h=lakeshorejoinery.mw.to.co;p=EW3qVKb9+gzEt8y2lPP/NoHXpnY5ZGVinAMOxPE1j9c='
```

You can host the JSON record yourself on any HTTPS server, or use any compatible provider. ABIZ does not require a particular provider.

## 3. Using a provider and MCP

The Model Context Protocol (MCP) is an open protocol that lets AI assistants call tools and read data from outside servers in a standard way. A business record may include an optional `mcp_server_url`, the HTTPS address of an MCP server for the business, for example for bookings or product information. ABIZ does not vouch for that server; tools must apply their own access controls (SPEC section 4.2.6).

A provider can host the record and publish the DNS pointer for you. For example, a registered business in Malawi with a record hosted by to.co might use the host `lakeshorejoinery.mw.to.co`, giving the DNS value `v=abiz1;k=mw-COYABC1234;h=lakeshorejoinery.mw.to.co;p=EW3qVKb9+gzEt8y2lPP/NoHXpnY5ZGVinAMOxPE1j9c=`. An unregistered business might use a town-based host such as `lakeshorejoinery-mangochi.biz.to.co`. Any compatible provider, or your own server, works in the same way.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 requires a signing key. The DNS `p` tag carries an Ed25519 public key: 32 raw bytes, standard base64, 44 characters, one trailing `=` (SPEC section 3.3.2). Base64url is not accepted. The business, or a provider acting for it, keeps the matching private key and signs the business record with it. The private key always belongs to the business, and a hosting provider must let the business export it.

- `v` and `h` are required. `p` is required. `k` is optional. `p` must be a valid key: any other value, such as a hexadecimal string or a base64url key, makes the whole assertion invalid.
- Only the current key is published. To rotate, generate a new Ed25519 keypair, publish the new public key in the DNS or well-known assertion, re-sign the business record with the new private key, and set `public_key` to that same `p`. Allow for DNS caching and propagation. Removing only `p` is not valid revocation while an ABIZ 1.1 assertion remains: to withdraw it, remove the complete DNS TXT record or well-known declaration. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record.
- A key shows who controls the domain’s DNS. It does not prove legal identity.

## 5. What AI tools will see

A compatible tool that reads your record can answer questions such as:

1. What is the official website of Lake Shore Joinery?
2. Which domains belong to this business?
3. Which registration number does the business give, and in which country?
4. What does it offer, and when is it open?

**Limits:** ABIZ shows what the controller of a domain has published. It does not prove that the business is legally registered, that its number is genuine, or that any AI service, government or provider endorses it. Where it matters, tools and people should check the official register.

## 6. Local practical notes

- **Register:** Department of the Registrar General. Official website: <https://registrargeneral.gov.mw>.
- **Adding the TXT record:** in the DNS settings of your registrar or DNS host, add a TXT record with the name `_abiz` (some panels want the full name, `_abiz.yourdomain.mw`), the value shown above and a TTL of 300 seconds. Domains under `.mw` work in the same way as `.com` or any other domain. Keep the value in one piece where possible, and never split `p`.
- **Privacy:** Check the data-protection rules that apply in Malawi before you publish personal data. An ABIZ record is public. Publish only business facts you are happy to share, and leave out private home addresses and personal phone numbers (SPEC section 4.3).

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md)
- [Business record JSON Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Reference validator](../../../scripts/validate.py)
- [ABIZ country guides: Africa](index.md)
