# Becoming an Agentic Business using ABIZ in Nepal

*A guide to published ABIZ 1.1. The [specification (SPEC.md)](../../../SPEC.md) is authoritative: if this guide and the specification differ, the specification applies.* Nepali is the official language. This guide is in English.

## 1. What this means for a business in Nepal

AI assistants are now often asked questions such as ‘what is this company’s real website?’ or ‘who runs this shop?’. ABIZ (Agentic Business Record) is an open standard that lets a business in Nepal publish its public facts once, in a form those tools can read: a short DNS TXT record on a domain the business controls, pointing to a JSON business record served over HTTPS. Because the pointer sits in the business’s own DNS, a tool can tell that the record was published by whoever controls that domain, instead of relying on an unofficial directory or a guess.

## 2. How to publish an ABIZ record

### Required fields

Every business record needs these five fields (SPEC section 4.1):

| Field | Example and rule |
|---|---|
| `record_version` | `abiz1` |
| `business_name` | the public name customers know, for example `Kathmandu Pashmina` |
| `country` | `np`, the ISO 3166-1 alpha-2 code, in lowercase |
| `identity_host` | `kathmandupashmina.np.to.co`, which must match `h` in DNS exactly |
| `domains` | `["kathmandupashmina.example"]`, which must include the domain that carries `_abiz` |

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, it must equal `business_key` in the record, and the record must then also contain `registration_number`. For Nepal the form is:

```text
np-<registration-number>
```

Nepal uses no subdivision: do not add a region, province or city code. SPEC section 4.2.2 requires a subdivision only for the United States, Canadian provincial corporations and the United Arab Emirates, and forbids it everywhere else.

**Which number:** the company registration number, often written with the Nepali fiscal year, for example `123456/080/081`, using the digits 0–9.

**Normalisation (SPEC section 4.2.3):** start from the number exactly as the register issues it, apply Unicode NFKC, remove spaces, `-`, `.`, `/` and the dash characters, then uppercase any letters. Keep leading zeros and letter prefixes. The result must contain only ASCII letters and digits. If it does not, you cannot publish a business key: leave out `k`, `business_key` and `registration_number`.

**Worked example (fictional):** `123456/080/081` becomes `123456080081`, so `k=np-123456080081`. In the record: `"business_key": "np-123456080081"` and `"registration_number": "123456080081"`. Keys are compared case-insensitively; the canonical form has a lowercase country code and an uppercase number.

**Please check:** we could not confirm the exact format of this number from an official source, so the example is illustrative only. Use the number exactly as it appears on your official registration document. If it is not clear which number identifies your business nationally, leave `k` out until you are sure.

**Non-Latin digits:** NFKC does not turn digits such as १२३ into 0–9. If your number exists only in that form, the result is not ASCII and no business key is possible. ABIZ 1.1 defines no digit conversion, so use the number only if the register also issues it with the digits 0–9.

**Sole traders:** if the only number you have is a personal one, such as a national identity number or a personal tax number, do not publish `k`. Leave out `k`, `business_key` and `registration_number`; the record is still valid.

### DNS TXT record

Publish exactly one TXT record at `_abiz` under your domain, in the compact form with no spaces and `v=abiz1` first:

```dns
_abiz.kathmandupashmina.example. 300 IN TXT "v=abiz1;k=np-123456080081;h=kathmandupashmina.np.to.co;p=mQ8PVn/G+osH+aXat89uROz3KHVcXk009SjPrtoe9YI="
```

The `p` value above is a throwaway example key generated for this page. Never copy it: publish your own key. An ABIZ 1.1 assertion must include `p`. All names, numbers and domains on this page are fictional.

Without the optional `k` tag, this is also valid:

```dns
_abiz.kathmandupashmina.example. 300 IN TXT "v=abiz1;h=kathmandupashmina.np.to.co;p=mQ8PVn/G+osH+aXat89uROz3KHVcXk009SjPrtoe9YI="
```

The business record served as `application/json` at `https://kathmandupashmina.np.to.co`:

```json
{
  "record_version": "abiz1",
  "business_name": "Kathmandu Pashmina",
  "country": "np",
  "business_key": "np-123456080081",
  "registration_number": "123456080081",
  "identity_host": "kathmandupashmina.np.to.co",
  "domains": [
    "kathmandupashmina.example"
  ],
  "public_key": "mQ8PVn/G+osH+aXat89uROz3KHVcXk009SjPrtoe9YI=",
  "signature": "lGjcHcZURKF2KdQLJnJtzZmVPF9L575WwO5KDkE3JOP6mMAvdogl1a7dDv03t+Gdkyr830OkjsjlCSg0sz/8DA=="
}
```

To check a record before you publish it, run the reference validator from a copy of this repository:

```sh
python scripts/validate.py record.json --domain kathmandupashmina.example --dns-value 'v=abiz1;k=np-123456080081;h=kathmandupashmina.np.to.co;p=mQ8PVn/G+osH+aXat89uROz3KHVcXk009SjPrtoe9YI='
```

You can host the JSON record yourself on any HTTPS server, or use any compatible provider. ABIZ does not require a particular provider.

## 3. Using a provider and MCP

The Model Context Protocol (MCP) is an open protocol that lets AI assistants call tools and read data from outside servers in a standard way. A business record may include an optional `mcp_server_url`, the HTTPS address of an MCP server for the business, for example for bookings or product information. ABIZ does not vouch for that server; tools must apply their own access controls (SPEC section 4.2.6).

A provider can host the record and publish the DNS pointer for you. For example, a registered business in Nepal with a record hosted by to.co might use the host `kathmandupashmina.np.to.co`, giving the DNS value `v=abiz1;k=np-123456080081;h=kathmandupashmina.np.to.co;p=mQ8PVn/G+osH+aXat89uROz3KHVcXk009SjPrtoe9YI=`. An unregistered business might use a town-based host such as `kathmandupashmina-kathmandu.biz.to.co`. Any compatible provider, or your own server, works in the same way.

## 4. Keys and signatures (ABIZ 1.1)

ABIZ 1.1 requires a signing key. The DNS `p` tag carries an Ed25519 public key: 32 raw bytes, standard base64, 44 characters, one trailing `=` (SPEC section 3.3.2). Base64url is not accepted. The business, or a provider acting for it, keeps the matching private key and signs the business record with it. The private key always belongs to the business, and a hosting provider must let the business export it.

- `v` and `h` are required. `p` is required. `k` is optional. `p` must be a valid key: any other value, such as a hexadecimal string or a base64url key, makes the whole assertion invalid.
- Only the current key is published. To rotate, generate a new Ed25519 keypair, publish the new public key in the DNS or well-known assertion, re-sign the business record with the new private key, and set `public_key` to that same `p`. Allow for DNS caching and propagation. Removing only `p` is not valid revocation while an ABIZ 1.1 assertion remains: to withdraw it, remove the complete DNS TXT record or well-known declaration. Retired keys are not published in ABIZ 1.1, neither in DNS nor in the business record.
- A key shows who controls the domain’s DNS. It does not prove legal identity.

## 5. What AI tools will see

A compatible tool that reads your record can answer questions such as:

1. What is the official website of Kathmandu Pashmina?
2. Which domains belong to this business?
3. Which registration number does the business give, and in which country?
4. What does it offer, and when is it open?

**Limits:** ABIZ shows what the controller of a domain has published. It does not prove that the business is legally registered, that its number is genuine, or that any AI service, government or provider endorses it. Where it matters, tools and people should check the official register.

## 6. Local practical notes

- **Register:** Office of the Company Registrar (OCR). Official website: <https://ocr.gov.np>.
- **Adding the TXT record:** in the DNS settings of your registrar or DNS host, add a TXT record with the name `_abiz` (some panels want the full name, `_abiz.yourdomain.com.np`), the value shown above and a TTL of 300 seconds. Domains under `.com.np` work in the same way as `.com` or any other domain. Keep the value in one piece where possible, and never split `p`.
- **Privacy:** Individual Privacy Act, 2075 (2018). An ABIZ record is public. Publish only business facts you are happy to share, and leave out private home addresses and personal phone numbers (SPEC section 4.3).

## 7. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md)
- [Business record JSON Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Reference validator](../../../scripts/validate.py)
- [ABIZ country guides: Asia](index.md)
