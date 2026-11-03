# Becoming an Agentic Business using ABIZ in the United Kingdom

*A guide to ABIZ 1.1 (proposed). [SPEC.md](../../../SPEC.md) is the authoritative text: if this guide and the specification differ, the specification applies.*

**On this page:** 1. What this means · 2. Publishing the DNS record · 3. Serving the business record: the `format` parameter · 4. Without DNS: the well-known file · 5. Full UK examples · 6. The JSON schema and field reference · 7. Business units, groups and brands · 8. Using a provider and MCP · 9. Keys and record signatures · 10. What AI tools will see · 11. Local practical notes · 12. Further reading

All businesses, people, numbers and addresses on this page are invented. Domains end in `.example`, telephone numbers come from the ranges Ofcom reserves for drama, and company numbers are illustrative only.

## 1. What this means for a business in the United Kingdom

People increasingly ask AI assistants about businesses: who they are, what they offer, where to find them. ABIZ (Agentic Business Record) lets a business publish one public, machine-readable record of its own facts, such as its name, country, website, services and opening hours, and a DNS record on its own domain that points to that record.

Only the business, or someone it authorises, can change the DNS of its domain. So compatible software can find the record from the domain and check that the domain and the record refer to each other, instead of piecing facts together from scattered web pages. ABIZ is open and provider-independent: no membership, fee or particular provider is required.

An ABIZ record has two parts:

1. **A DNS TXT record** at `_abiz.<your domain>`, which says where the business record lives and carries your public key (section 2). If you cannot edit DNS, a small file at `https://<your domain>/.well-known/abiz.json` can carry the same values instead (section 4).
2. **The business record**, served over HTTPS at that address as HTML, Markdown and JSON, chosen with a `format` parameter. The JSON validates against the ABIZ schema, repeats your public key as `public_key` and is signed with your private key in `signature` (sections 3, 5, 6 and 9).

All field names in the JSON record use snake_case, such as `business_name` and `identity_host`. The hyphenated names of ABIZ 1.0, such as `business-name`, are no longer accepted.

## 2. Publishing the DNS record

Publish exactly one ABIZ TXT record at `_abiz` on your domain. Use the compact form, with no spaces:

```dns
_abiz.hartleysbakery.example. 300 IN TXT "v=abiz1;h=www.hartleysbakery.example;p=9qb9yCmLPLK6afOLw2opb+3lz7Rm1SQugvNM9lWSgM4="
```

| Tag | Required | What it holds |
| --- | --- | --- |
| `v=abiz1` | Yes, always first | The protocol version |
| `h` | Yes | The HTTPS hostname of your business record, without `https://`; a path only for a business unit or division (section 7) |
| `k` | No | Your business key, if you choose to publish one (see below) |
| `p` | Yes | Your Ed25519 public key in standard base64, 44 characters (section 9). A record without `p` is invalid |

- Tag names are lowercase and case-sensitive. A tag must not appear twice. Two or more `v=abiz1` records at the same name make the assertion invalid.
- `p` is required for every business, registered or not (SPEC section 3.3). Section 9 explains how to get a key.
- A TTL of 300 seconds is recommended.
- `h` for your main record **should be a bare host**, such as `www.hartleysbakery.example` or `hartleysbakery.uk.to.co` (SPEC sections 3.2 and 8). Software fetches `https://` followed by `h`, so the record is served at the root of that host. A path, such as `h=www.severnsideleisure.example/events`, is for a business unit or division with its own record (section 7).
- `h` may point to a host you run yourself or to a provider's host. You must control the domain where `_abiz` is published, and have permission for the record at `h`.

### Optional business key `k`

`k` is optional for every business, registered or not. If you publish it, the record must also contain `business_key` and `registration_number`, and `k` must equal `business_key`. You may include the two record fields without publishing `k`.

In the United Kingdom the key is `gb-` followed by the Companies House number. The United Kingdom uses no subdivision, so a key with a middle part, such as `gb-xx-…`, is invalid.

- **Register:** [Companies House](https://www.gov.uk/government/organisations/companies-house), which keeps one register for England and Wales, Scotland and Northern Ireland.
- **Number to use:** the 8-character company number, with its letter prefix and leading zeros: for example `01234567` (England and Wales), `SC123456` (Scotland), `NI123456` (Northern Ireland), `OC123456` (a limited liability partnership).
- **How to write it:** start from the number as the register issues it, apply Unicode NFKC normalisation, remove spaces, `-`, `.`, `/` and other dash characters, then write letters in uppercase. Keep leading zeros and letter prefixes.

So `01234567` gives `"registration_number": "01234567"`, `"business_key": "gb-01234567"` and `k=gb-01234567`. The hostname of a provider may use `uk` (as in `.uk.to.co`), but the key and the `country` field always use `gb`, because `uk` is not an assigned ISO 3166-1 code. Keys are compared case-insensitively; publish the canonical form, a lowercase country code and an uppercase number.

Sole traders and ordinary partnerships are not on the Companies House register. They leave out `k`, `business_key` and `registration_number`. Do not use a UTR, a VAT number or a National Insurance number as a business key.

## 3. Serving the business record: the `format` parameter

### What the specification requires

ABIZ 1.1 says (SPEC section 4.5): the record host serves one business in three representations at the same address, `https://<h>`, and **must** support a `format` query parameter that chooses between them.

| Request | Response | `Content-Type` |
| --- | --- | --- |
| `?format=html`, or no `format` and no matching `Accept` (the default) | A human-readable HTML page | `text/html; charset=utf-8` |
| `?format=markdown` | A Markdown version of the same facts (RFC 7763) | `text/markdown; charset=utf-8` |
| `?format=json` | The business record, which validates against the schema | `application/json` |

- A recognised `format` value wins over the `Accept` header. Values are lowercase. A host may also accept `md` for `markdown`, but consumers send `markdown`.
- Without `format`, or with a value the host does not recognise, the host **must** use the `Accept` header instead: `Accept: application/json` gives JSON, `Accept: text/markdown` gives Markdown, and anything else, or no `Accept` at all, gives HTML. A negotiated response should carry `Vary: Accept`.
- The JSON **must be the business record itself**, whichever way it was requested: never a provider's page data or any other JSON.
- The HTML and Markdown should state the same public facts and must not contradict the JSON. Only the JSON is checked for conformance, and only the JSON is signed: software must not treat the HTML or Markdown as verified.
- You may serve the signed JSON re-indented or with its fields in another order, because the signature covers a canonical form (section 9). Changing any value breaks the signature.

ABIZ consumers send `Accept: application/json` and should also add `?format=json`, and they check that the answer is `application/json` before reading it. A host that supports both works for people and software alike.

### Example requests and responses

Request the record as an ABIZ consumer would:

```sh
curl -sS -i -H 'Accept: application/json' 'https://www.hartleysbakery.example/?format=json'
```

```http
HTTP/2 200
content-type: application/json
vary: Accept

{"record_version":"abiz1","business_name":"Hartley’s Bakery","country":"gb","identity_host":"www.hartleysbakery.example", … ,"public_key":"9qb9yCmLPLK6afOLw2opb+3lz7Rm1SQugvNM9lWSgM4=", … ,"signature":"7uM857rD…bv2Ag=="}
```

The same address in a browser, with `?format=html`, or with no `format` at all:

```sh
curl -sS -i 'https://www.hartleysbakery.example/?format=html'
```

```http
HTTP/2 200
content-type: text/html; charset=utf-8
vary: Accept

<!doctype html>
<html lang="en-GB"><head><title>Hartley’s Bakery, Bristol</title> …
```

And as Markdown, with the parameter or with `Accept: text/markdown`:

```sh
curl -sS -i 'https://www.hartleysbakery.example/?format=markdown'
```

```http
HTTP/2 200
content-type: text/markdown; charset=utf-8
vary: Accept

# Hartley’s Bakery

Sourdough, rye and seasonal bakes, made by hand every morning in Bristol. …
```

The content types above are the ones SPEC section 4.5 defines. In addition:

- **`Vary: Accept`.** When one address returns different content depending on `Accept`, send `Vary: Accept` so that caches and CDNs do not give a browser the JSON, or a consumer the HTML.
- **Redirects.** Consumers refuse unsafe redirects and limit response size and time (SPEC section 6). Serve the record directly with status 200, keep it small, and do not rely on scripts: consumers parse JSON without executing anything.
- **Caching and CORS.** ABIZ 1.1 sets no caching or cross-origin (CORS) rules for the record itself. A short cache lifetime keeps changes visible quickly. A browser-based tool on another site can read the JSON only if you send `Access-Control-Allow-Origin`; server-side consumers do not need it.

### Self-hosted or through a provider

You can serve the record yourself on any HTTPS host you control, or use any compatible provider. To self-publish at a bare host such as `www.hartleysbakery.example`, your website's home page must answer `?format=json` and `Accept: application/json` with the record, and `?format=markdown` with Markdown. If your website cannot do that, use a host that can, such as a subdomain (`h=abiz.hartleysbakery.example`) or a provider's host. Keep paths for business units (section 7).

## 4. Without DNS: the well-known file

If you cannot publish a TXT record, for example because a web agency or an IT department manages your DNS, ABIZ 1.1 lets you publish the same values as a file on your website instead (SPEC section 3.4):

```text
https://hartleysbakery.example/.well-known/abiz.json
```

```json
{
  "v": "abiz1",
  "h": "www.hartleysbakery.example",
  "p": "9qb9yCmLPLK6afOLw2opb+3lz7Rm1SQugvNM9lWSgM4="
}
```

- **Location.** The file sits on exactly the domain the TXT record would use (`hartleysbakery.example`, not `www.hartleysbakery.example`), over HTTPS on port 443. The name is `abiz.json`, with no underscore.
- **Content.** A JSON object with the same values as the TXT tags: `v` (always `abiz1`), `h` and `p` are required, `k` is optional and follows the same rules as in section 2. It is a pointer, not the business record; software still fetches the record from `https://<h>`. It validates against [`schemas/abiz-well-known-v1.schema.json`](../../../schemas/abiz-well-known-v1.schema.json).
- **Serving.** Status 200 with no redirect, `Content-Type: application/json`, no larger than 65,536 bytes, and preferably `Cache-Control: max-age=300`. Software will not follow a redirect to the file and caches it for at most 300 seconds.

**DNS wins.** Software looks for the `_abiz` TXT record first. It uses the file only when there is no `v=abiz1` TXT record at all. If the DNS lookup fails, or the TXT record is duplicated or malformed, it does not fall back to the file. If both exist and disagree, it uses DNS and ignores the file. If you publish both, keep them identical, and change the TXT record first.

The file shows that you control the website at your domain, which is weaker than controlling its DNS: a web host can publish a file without touching DNS. Software may treat a TXT record as the stronger evidence and should say which one it used. If you can publish a TXT record, do so.

## 5. Full UK examples

Each example below has been checked with the reference validator, which verifies the record's `signature` and checks that `public_key` equals the `p` in the DNS value:

```sh
python scripts/validate.py record.json --domain hartleysbakery.example --dns-value 'v=abiz1;h=www.hartleysbakery.example;p=9qb9yCmLPLK6afOLw2opb+3lz7Rm1SQugvNM9lWSgM4='
```

or, for a well-known file saved locally as `abiz.json`:

```sh
python scripts/validate.py record.json --domain hartleysbakery.example --well-known abiz.json
```

```text
PASS: schema + record signature + offline DNS/document consistency; public_key matches p (not a live DNS or registry check)
```

The examples follow Hartley’s Bakery, a small invented bakery in Bristol: first as a partnership that publishes its own record, then after it incorporates as a private limited company.

### 5a. An unregistered business: a partnership, self-published

Hartley’s Bakery is run by two partners. An ordinary partnership is not on the Companies House register, so the record has no `k`, `business_key` or `registration_number`. The partners publish the record on their own website, so `h` is their bare `www` host. Like every business, they publish an Ed25519 key in `p`.

DNS:

```dns
_abiz.hartleysbakery.example. 300 IN TXT "v=abiz1;h=www.hartleysbakery.example;p=9qb9yCmLPLK6afOLw2opb+3lz7Rm1SQugvNM9lWSgM4="
```

JSON served at `https://www.hartleysbakery.example/?format=json` (and for `Accept: application/json`):

```json
{
  "record_version": "abiz1",
  "business_name": "Hartley’s Bakery",
  "country": "gb",
  "identity_host": "www.hartleysbakery.example",
  "domains": [
    "hartleysbakery.example"
  ],
  "public_key": "9qb9yCmLPLK6afOLw2opb+3lz7Rm1SQugvNM9lWSgM4=",
  "description": "Sourdough, rye and seasonal bakes, made by hand every morning in Bristol. Order a loaf for collection, or ask us about a celebration cake.",
  "website": "https://www.hartleysbakery.example",
  "contact_email": "hello@hartleysbakery.example",
  "contact_phone": "+44 117 496 0142",
  "logo_url": "https://www.hartleysbakery.example/logo.png",
  "last_updated": "2026-11-03T09:00:00Z",
  "services": [
    {
      "name": "Sourdough and rye loaves",
      "description": "Baked every morning from 7:30. Order by 4pm for collection the next day.",
      "url": "https://www.hartleysbakery.example/order"
    },
    {
      "name": "Celebration cakes",
      "description": "Made to order. Ask for a quote at least a week ahead.",
      "url": "https://www.hartleysbakery.example/cakes"
    },
    {
      "name": "Gift cards",
      "url": "https://www.hartleysbakery.example/gift-cards"
    }
  ],
  "locations": [
    {
      "kind": "trading",
      "name": "Hartley’s Bakery, Bristol",
      "street": "1 Example Street",
      "city": "Bristol",
      "region": "England",
      "postal_code": "BS1 4XX",
      "country": "gb",
      "public": true
    },
    {
      "kind": "trading",
      "name": "Saturday market stall",
      "street": "Example Market, Stall 14",
      "city": "Bristol",
      "region": "England",
      "postal_code": "BS5 0XX",
      "country": "gb",
      "public": true
    }
  ],
  "opening_hours": [
    "Shop: Mo-Sa 07:30-15:00",
    "Market stall: Sa 08:30-13:30",
    "Closed 25 and 26 December"
  ],
  "links": [
    {
      "label": "Menu",
      "url": "https://www.hartleysbakery.example/menu"
    },
    {
      "label": "Order for collection",
      "url": "https://www.hartleysbakery.example/order"
    }
  ],
  "signature": "7uM857rDHehWucIDtpSObjEb/eSHyf6mZ+xqjd6IF7ojPFhL6vDFVM1J0Chd6a79T5W3IqT/1sefoxei9bv2Ag=="
}
```

Notes:

- No partner is named and no home address appears. The shop and the market stall are trading premises, so their addresses are public (`"public": true`). A sole trader who works from home would list only the town, or leave `locations` out: the specification requires private personal addresses to be omitted, not marked as private.
- `contact_email` is a role address, not a partner's personal one.
- `opening_hours` is a list of short text lines. The schema does not fix a format; a familiar notation such as `Mo-Sa 07:30-15:00` is easy for people and software to read.
- If the partners preferred a provider to host the record, only `h` and `identity_host` would change, for example to `hartleysbakery-bristol.biz.to.co`.
- `public_key` is the same value as `p` in DNS, and `signature` is the record's Ed25519 signature (section 9). Both are required. `last_updated` is covered by the signature, so update it whenever you re-sign.
- The `p` value, and the signature made with it, come from a throwaway example key whose private key has been discarded. Never copy them: publish your own key and sign your own record (section 9).

### 5b. A registered company: a private limited company, through a provider

The partners incorporate Hartley’s Bakery Ltd at Companies House, which issues company number `01234567` (invented). They now use a provider to host the record, publish their business key, and move to a new Ed25519 key held by the provider (section 9). The new record replaces the old one; there must only ever be one `_abiz` record on the domain.

DNS:

```dns
_abiz.hartleysbakery.example. 300 IN TXT "v=abiz1;k=gb-01234567;h=hartleysbakery.uk.to.co;p=pRefpOaEPXy40c3SKc4NZge42h38/Su7nyD1aU0o1+8="
```

JSON served at `https://hartleysbakery.uk.to.co/?format=json` (and for `Accept: application/json`):

```json
{
  "record_version": "abiz1",
  "business_name": "Hartley’s Bakery Ltd",
  "country": "gb",
  "business_key": "gb-01234567",
  "registration_number": "01234567",
  "identity_host": "hartleysbakery.uk.to.co",
  "domains": [
    "hartleysbakery.example"
  ],
  "public_key": "pRefpOaEPXy40c3SKc4NZge42h38/Su7nyD1aU0o1+8=",
  "description": "Sourdough, rye and seasonal bakes, made by hand every morning in Bristol. Order a loaf for collection, or ask us about a celebration cake.",
  "website": "https://www.hartleysbakery.example",
  "contact_email": "hello@hartleysbakery.example",
  "contact_phone": "+44 117 496 0142",
  "logo_url": "https://www.hartleysbakery.example/logo.png",
  "last_updated": "2026-11-03T09:00:00Z",
  "mcp_server_url": "https://agents.hartleysbakery.example/mcp",
  "services": [
    {
      "name": "Sourdough and rye loaves",
      "description": "Baked every morning from 7:30. Order by 4pm for collection the next day.",
      "url": "https://www.hartleysbakery.example/order"
    },
    {
      "name": "Celebration cakes",
      "description": "Made to order. Ask for a quote at least a week ahead.",
      "url": "https://www.hartleysbakery.example/cakes"
    },
    {
      "name": "Wholesale bread for cafés",
      "description": "Daily deliveries within Bristol.",
      "url": "https://www.hartleysbakery.example/wholesale"
    },
    {
      "name": "Gift cards",
      "url": "https://www.hartleysbakery.example/gift-cards"
    }
  ],
  "locations": [
    {
      "kind": "registered-office",
      "name": "Registered office",
      "street": "Unit 3, Example Trading Estate",
      "city": "Bristol",
      "region": "England",
      "postal_code": "BS2 0XX",
      "country": "gb",
      "public": true
    },
    {
      "kind": "trading",
      "name": "Hartley’s Bakery, Bristol",
      "street": "1 Example Street",
      "city": "Bristol",
      "region": "England",
      "postal_code": "BS1 4XX",
      "country": "gb",
      "public": true
    },
    {
      "kind": "other",
      "name": "Saturday market stall",
      "street": "Example Market, Stall 14",
      "city": "Bristol",
      "region": "England",
      "postal_code": "BS5 0XX",
      "country": "gb",
      "public": true
    }
  ],
  "opening_hours": [
    "Shop: Mo-Sa 07:30-15:00",
    "Market stall: Sa 08:30-13:30",
    "Closed 25 and 26 December"
  ],
  "links": [
    {
      "label": "Menu",
      "url": "https://www.hartleysbakery.example/menu"
    },
    {
      "label": "Order for collection",
      "url": "https://www.hartleysbakery.example/order"
    },
    {
      "label": "Allergen information",
      "url": "https://www.hartleysbakery.example/allergens"
    }
  ],
  "extensions": {
    "example.hartleysbakery": {
      "food_hygiene_rating_url": "https://www.hartleysbakery.example/hygiene"
    }
  },
  "signature": "oDkZktkx2z2sTzuHg5nnCqAfLvuJTs/mw9WxOPwaAaaLPiAwre8IMAKwyX+faVBf6Udfvp1ILSJ7G446n/4BCw=="
}
```

Notes:

- `business_name` is the name on the register, including `Ltd`.
- `business_key` is `gb-` plus the company number, `registration_number` is the number alone, and DNS `k` equals `business_key`.
- The registered office is already public on the Companies House register, so it is listed with `"kind": "registered-office"`. The shop is a trading address; the market stall uses `other`.
- `mcp_server_url` is optional (section 8). `extensions` holds implementation-specific data under a reverse-domain key; consumers may ignore it, and it must not change the meaning of any standard field.
- The move to a new key held by the provider changes `p`, `public_key` and `signature` together. The provider signs the record for the company with the company's key (hosted mode, section 9).
- The `p` value and the signature are throwaway examples. Never copy them: publish your own key and sign your own record. Neither `p` nor `signature` can be left out.

## 6. The JSON schema and field reference

The normative schema is [`schemas/abiz-business-record-v1.schema.json`](../../../schemas/abiz-business-record-v1.schema.json) in this repository ([raw file](https://raw.githubusercontent.com/abiz-org/abiz-agentic-business-record/main/schemas/abiz-business-record-v1.schema.json)). It uses JSON Schema Draft 2020-12, and its `$id` is:

```text
https://abizrecord.org/schema/abiz-business-record-v1.schema.json
```

Cite that `$id` and the SPEC revision when you claim conformance (SPEC section 7). The `$id` address serves the same file as the repository copy. The well-known file of section 4 has its own schema, [`schemas/abiz-well-known-v1.schema.json`](../../../schemas/abiz-well-known-v1.schema.json) (`$id` `https://abizrecord.org/schema/abiz-well-known-v1.schema.json`).

The schema rejects any top-level field not listed below. Beyond the schema, `scripts/validate.py` checks that `country` and the key's country are assigned codes, that `business_key` matches `country` and `registration_number`, that URLs use HTTPS, that `country` is not `kp` (North Korea is not supported, SPEC section 4.2.7), that `signature` verifies with `public_key` over the record (SPEC section 4.6), and, with `--domain` and `--dns-value` or `--well-known` (or just `--p`), that the record and the assertion agree, including that `p` is present and valid and that `public_key` equals it.

The table is generated from the schema file. Types, constraints and required flags come from the schema; descriptions come from the schema where it has one, and otherwise from SPEC section 4. Examples are from example 5b.

<!-- Generated from schemas/abiz-business-record-v1.schema.json. Regenerate rather than edit by hand. -->
| Field | Type and constraints | Required | Description | UK example |
| --- | --- | --- | --- | --- |
| `record_version` | string, always `abiz1` | Yes | Wire protocol family abiz1. Document revisions, including a proposed 1.1, may advance without changing this value. | `"abiz1"` |
| `business_name` | string (length 1–240) | Yes | Nonempty public name (SPEC 4.1) | `"Hartley’s Bakery Ltd"` |
| `country` | string (pattern `^[A-Za-z]{2}$`) | Yes | Assigned ISO 3166-1 alpha-2 country code. Case-insensitive; canonical form is lowercase. The validator checks it against data/iso3166.json. | `"gb"` |
| `identity_host` | string (pattern `^[A-Za-z0-9][A-Za-z0-9.-]*(?:/[^\s?#]*)?$`; length 4–512) | Yes | DNS h value: lowercase DNS hostname with optional path; never includes https:// | `"hartleysbakery.uk.to.co"` |
| `domains` | array of strings (at least 1; unique; each format `hostname`, length 4–253) | Yes | Business-controlled domain names this record claims. DNS cross-check must confirm control. | `["hartleysbakery.example"]` |
| `public_key` | string (pattern `^[A-Za-z0-9+/]{43}=$`, 44 characters) | Yes | Ed25519 public key, standard base64 of the 32-byte key (SPEC 3.3.2). MUST equal p in the DNS assertion or well-known file; consumers reject the identity claim if it differs (SPEC 4.6). | `"pRefpOaEPXy40c3SKc4NZge42h38/Su7nyD1aU0o1+8="` |
| `signature` | string (pattern `^[A-Za-z0-9+/]{86}==$`, 88 characters) | Yes | Ed25519 signature, standard base64 of the 64 bytes, over the UTF-8 RFC 8785 (JCS) canonical form of the record without signature, verified with public_key (SPEC 4.6). | `"oDkZktkx…"` (88 characters) |
| `business_key` | string (pattern `^[A-Za-z]{2}-(?:[A-Za-z0-9]{1,3}-)?[A-Za-z0-9]+$`; up to 128 characters) | If `registration_number` present | country[-subdivision]-registration-number (SPEC section 4.2.1). Case-insensitive; canonical form has lowercase country and subdivision and an uppercase number. Assigned codes and the subdivision rule (section 4.2.2) are checked by the validator. | `"gb-01234567"` |
| `registration_number` | string (pattern `^[A-Za-z0-9]+$`; length 1–96) | If `business_key` present | Normalised registration number: ASCII letters and digits only (SPEC section 4.2.3). Case-insensitive; canonical form is uppercase. | `"01234567"` |
| `mcp_server_url` | string (format `uri`; pattern `^https://`; up to 2048 characters) | No | Optional. No conformance requirement to operate an MCP server. | `"https://agents.hartleysbakery.example/mcp"` |
| `description` | string (length 1–4000) | No | Short public description of the business (SPEC 4.3) | `"Sourdough, rye and seasonal bakes, made by hand every mo…` |
| `website` | string (format `uri`; pattern `^https://`; up to 2048 characters) | No | Main public website (SPEC 4.3) | `"https://www.hartleysbakery.example"` |
| `contact_email` | string (format `email`; up to 320 characters) | No | Public contact email address; use a role address (SPEC 4.3, 9) | `"hello@hartleysbakery.example"` |
| `contact_phone` | string (up to 64 characters) | No | Public contact telephone number (SPEC 4.3) | `"+44 117 496 0142"` |
| `logo_url` | string (format `uri`; pattern `^https://`; up to 2048 characters) | No | Public logo image (SPEC 4.3) | `"https://www.hartleysbakery.example/logo.png"` |
| `last_updated` | string (format `date-time`) | No | When the record was last updated (SPEC 4.3) | `"2026-11-03T09:00:00Z"` |
| `services` | array of objects (up to 200 items) | No | Services the business offers (SPEC 4.3) | See below |
| `services[].name` | string (length 1–180) | Yes | Service name | `"Sourdough and rye loaves"` |
| `services[].description` | string (up to 2000 characters) | No | Service description | `"Baked every morning from 7:30. Order by 4pm for collecti…` |
| `services[].url` | string (format `uri`; pattern `^https://`) | No | Page for the service | `"https://www.hartleysbakery.example/order"` |
| `locations` | array of objects (up to 100 items) | No | Public places of business; omit private personal addresses (SPEC 4.3) | See below |
| `locations[].kind` | string (one of `registered-office`, `trading`, `other`) | No | Type of location | `"trading"` |
| `locations[].name` | string (up to 180 characters) | No | Location name | `"Hartley’s Bakery, Bristol"` |
| `locations[].city` | string (at least 1 character) | Yes | Town or city | `"Bristol"` |
| `locations[].region` | string | No | Region | `"England"` |
| `locations[].country` | string (pattern `^[A-Za-z]{2}$`) | Yes | Assigned ISO 3166-1 alpha-2 country code, case-insensitive. | `"gb"` |
| `locations[].street` | string | No | Street address | `"1 Example Street"` |
| `locations[].postal_code` | string | No | Postcode | `"BS1 4XX"` |
| `locations[].public` | boolean | No | Whether the location is public | `true` |
| `opening_hours` | array of strings (up to 50 items; each length 1–160) | No | Opening hours as short text lines (SPEC 4.3) | `["Shop: Mo-Sa 07:30-15:00", "Market stall: Sa 08:30-13:30…` |
| `links` | array of objects (up to 100 items) | No | Other public links (SPEC 4.3) | See below |
| `links[].label` | string (length 1–140) | Yes | Link text | `"Menu"` |
| `links[].url` | string (format `uri`; pattern `^https://`) | Yes | Link target | `"https://www.hartleysbakery.example/menu"` |
| `extensions` | object (keys match `^[a-z0-9-]+(?:\.[a-z0-9-]+)+$`) | No | Vendor-namespaced extensions; consumers may ignore unfamiliar extensions. | `{"example.hartleysbakery": {"food_hygiene_rating_url": "h…` |

Notes on the table:

- `business_key` and `registration_number` are optional, but if one is present the other must be too.
- In `locations`, each entry needs `city` and `country`, and accepts no other fields than those listed.
- `locations[].region` for the United Kingdom can be `England`, `Scotland`, `Wales` or `Northern Ireland`, or a county; the schema does not restrict it.
- `contact_phone` is free text. International format (`+44 117 496 0142`) is the clearest for software.
- `public_key` and `signature` are required in every record. Any change to any field, including `extensions` and `last_updated`, needs a new signature.
- Names inside `extensions` are chosen by the extension's owner; snake_case is recommended, as in `food_hygiene_rating_url`.

## 7. Business units, groups and brands

Large organisations rarely map to one name, one domain and one company. ABIZ 1.1 keeps the rule simple: **a business record describes one legal entity, and that entity has exactly one business key.** SPEC section 8 (business units and divisions) adds:

- the main record of a business **should** use a bare host as `h`;
- a unit or division **may** have its own record, and its `h` **may** be a path on the parent's host, such as `www.severnsideleisure.example/events`; its `identity_host` must equal that `h` exactly, path included, and the path must answer `?format=json` with the unit's own record;
- a unit of a registered business may carry the parent's `business_key` and `registration_number` when it has no registration of its own;
- the unit should publish its own ABIZ assertion (TXT record or well-known file) on a domain it uses;
- a parent business **may** list its units and their domains, in an implementation-specific extension, in `links` or as separate business records;
- a consumer **must not** treat the parent's word alone, or a path under the parent's host, as proof that the parent vouches for or controls a unit;
- a stronger claim needs the unit's own ABIZ assertion and a consistent reference back to the parent;
- the base schema does not define relationships between units.

### Choosing a pattern

| You have | Records | `k` |
| --- | --- | --- |
| One company with several websites or trading names | One record, listing every domain in `domains`, and the same TXT record on each domain | The company's number |
| A division of one company that needs its own record | A separate record for the division, served from a path or subdomain of the company's host | The same company number: a division is not a separate legal entity |
| A subsidiary (its own company number) | Its own record, on its own domain | The subsidiary's own number, never the parent's |

**Paths or subdomains?** Both are valid for a unit's `h`.

- A **path** (`h=www.severnsideleisure.example/events`) keeps every record on one website. It suits a group that runs a single website and content system. Each path must still answer `?format=json` and `Accept: application/json` with its own record, for example `https://www.severnsideleisure.example/events?format=json`. A path never contains a query, a fragment, or `.` or `..` segments.
- A **subdomain** (`h=events.severnsideleisure.example`) gives each unit its own host and certificate. It suits units that run their own website or use different providers, and makes it easier to hand a unit over if it is sold.
- A bare host is the rule for a business's main record. Use paths or subdomains only for units and divisions.

### Worked example: a UK group

Severnside Leisure Group plc (company `09876543`, invented) has:

- a trading name, Severnside Hire, with its own website;
- a division, Severnside Events, which is part of the plc;
- a subsidiary, Severnside Cycles Ltd, a Scottish company (`SC123456`, invented).

**The plc and its trading name: one record, two domains.** The same TXT record goes on both domains, and the record lists both:

```dns
_abiz.severnsideleisure.example. 300 IN TXT "v=abiz1;k=gb-09876543;h=www.severnsideleisure.example;p=Qz3VDqaDeVVG8lS1hK6aFp3q43kC8+guAhUAUg+h3+w="
_abiz.severnsidehire.example.    300 IN TXT "v=abiz1;k=gb-09876543;h=www.severnsideleisure.example;p=Qz3VDqaDeVVG8lS1hK6aFp3q43kC8+guAhUAUg+h3+w="
```

```json
{
  "record_version": "abiz1",
  "business_name": "Severnside Leisure Group plc",
  "country": "gb",
  "business_key": "gb-09876543",
  "registration_number": "09876543",
  "identity_host": "www.severnsideleisure.example",
  "domains": [
    "severnsideleisure.example",
    "severnsidehire.example"
  ],
  "public_key": "Qz3VDqaDeVVG8lS1hK6aFp3q43kC8+guAhUAUg+h3+w=",
  "description": "Leisure group in the South West of England. Also trades as Severnside Hire.",
  "website": "https://www.severnsideleisure.example",
  "links": [
    {
      "label": "Severnside Hire (trading name)",
      "url": "https://www.severnsidehire.example"
    },
    {
      "label": "Severnside Events (division)",
      "url": "https://www.severnsideleisure.example/events"
    },
    {
      "label": "Severnside Cycles Ltd (subsidiary)",
      "url": "https://www.severnsidecycles.example"
    }
  ],
  "extensions": {
    "example.severnsideleisure": {
      "units": [
        {
          "name": "Severnside Events",
          "domain": "severnsideevents.example",
          "relationship": "division"
        },
        {
          "name": "Severnside Cycles Ltd",
          "domain": "severnsidecycles.example",
          "relationship": "subsidiary"
        }
      ]
    }
  },
  "signature": "v0COZj9fvGsUapca8zHvclpjyV1PQ7wmLGM+HRnqQ6P1J75PZx6IniW9k++oXMc8nvr9N5znPKbFasZ2cdT3Dg=="
}
```

**The division: its own record, on a path of the parent's website.** The division is the same legal entity, so it uses the plc's number.

```dns
_abiz.severnsideevents.example. 300 IN TXT "v=abiz1;k=gb-09876543;h=www.severnsideleisure.example/events;p=joN8hf8xOeLEizQ3Da/YPzYaaGJimSbt0Tl6Y9Brh2M="
```

```json
{
  "record_version": "abiz1",
  "business_name": "Severnside Events",
  "country": "gb",
  "business_key": "gb-09876543",
  "registration_number": "09876543",
  "identity_host": "www.severnsideleisure.example/events",
  "domains": [
    "severnsideevents.example"
  ],
  "public_key": "joN8hf8xOeLEizQ3Da/YPzYaaGJimSbt0Tl6Y9Brh2M=",
  "description": "Corporate and private events in Bristol. Severnside Events is a division of Severnside Leisure Group plc.",
  "website": "https://www.severnsideevents.example",
  "links": [
    {
      "label": "Parent company: Severnside Leisure Group plc",
      "url": "https://www.severnsideleisure.example"
    }
  ],
  "extensions": {
    "example.severnsideleisure": {
      "parent_domain": "severnsideleisure.example",
      "relationship": "division"
    }
  },
  "signature": "hQW/bESnHUuRPFTk9BXdFh90/4epugoZdsky4Ki+pjwRpg+PS6RCNL5NtDeLpnAy5iFDh5CK3eZfExEktVjnCQ=="
}
```

**The subsidiary: its own record and its own company number.**

```dns
_abiz.severnsidecycles.example. 300 IN TXT "v=abiz1;k=gb-SC123456;h=www.severnsidecycles.example;p=SSSaqOjwr73oB8dBUbWhehK88c9Cb9xp8AxhkixF3aU="
```

```json
{
  "record_version": "abiz1",
  "business_name": "Severnside Cycles Ltd",
  "country": "gb",
  "business_key": "gb-SC123456",
  "registration_number": "SC123456",
  "identity_host": "www.severnsidecycles.example",
  "domains": [
    "severnsidecycles.example"
  ],
  "public_key": "SSSaqOjwr73oB8dBUbWhehK88c9Cb9xp8AxhkixF3aU=",
  "description": "Cycle hire and repairs in Edinburgh. A subsidiary of Severnside Leisure Group plc.",
  "website": "https://www.severnsidecycles.example",
  "locations": [
    {
      "kind": "registered-office",
      "street": "2 Example Lane",
      "city": "Edinburgh",
      "region": "Scotland",
      "postal_code": "EH1 9XX",
      "country": "gb",
      "public": true
    }
  ],
  "links": [
    {
      "label": "Parent company: Severnside Leisure Group plc",
      "url": "https://www.severnsideleisure.example"
    }
  ],
  "extensions": {
    "example.severnsideleisure": {
      "parent_domain": "severnsideleisure.example",
      "relationship": "subsidiary"
    }
  },
  "signature": "8X5o2K9bbnf9B15kxvqEi9hcWQ5qMCN96PkIyfMwjRh6dhmWXY1iIEUOMWNiAKNA8e0WkucO53rzuTF4VFKVBw=="
}
```

How the parts fit together:

- Each record carries its own `p` in DNS, the same value as `public_key`, and is signed with the matching private key; the keys and signatures shown are throwaway examples. The division may use its own key or the plc's, but its `public_key` and signature must match the `p` in its own `_abiz` record.
- Each unit's own DNS record proves control of its own domain. The parent's `extensions` list alone proves nothing about the units.
- The units point back to the parent with `links` (readable by anyone) and with the same extension key the parent uses. The relationship is consistent only when both sides say the same thing.
- The extension key (`example.severnsideleisure`) and its contents are illustrative. ABIZ 1.1 defines no standard schema field for units, parents or relationships; any extension is implementation-specific, and consumers may ignore it.
- A consumer that has not checked Companies House itself must not describe the subsidiary as owned by the plc. That is a legal-registration fact, separate from the domain link.

## 8. Using a provider and MCP

MCP (Model Context Protocol) is an open protocol that lets AI assistants call tools and read data from external servers. A provider can run an MCP server so that an assistant can request your public record directly. You can list one in the optional `mcp_server_url` field. ABIZ does not require an MCP server, does not assert that a listed endpoint is safe or available, and a tool should not call one automatically just because a record lists it.

For example, a provider might serve the record of Hartley’s Bakery Ltd at `hartleysbakery.uk.to.co` and run an MCP server. An assistant connected to that server could then ask for the bakery's opening hours or services and receive the facts from its record, not from a guess. to.co, one provider, has an [ABIZ overview](https://to.co/en-gb/abiz) written for readers in the United Kingdom.

## 9. Keys and record signatures (ABIZ 1.1)

### The key

ABIZ 1.1 requires every business to publish an Ed25519 public key in the DNS `p` tag, or in the `p` member of the well-known file (SPEC section 3.3). It must be the standard base64 encoding of the 32-byte public key: 44 characters ending in one `=`, in a single DNS string. A record without `p`, or with any other value, such as an ABIZ 1.0 hexadecimal token or a base64url key, is invalid.

The business record repeats the same value as `public_key`. `p` is the authoritative copy: if the two differ, software must reject the record's claim to belong to your domain.

The matching private key belongs to the business. It is never published, never appears in the record, and should never be stored anywhere public. You can generate a keypair yourself (SPEC section 3.3.3 shows how with OpenSSL), or a provider can generate and hold it for you (hosted mode). If a provider holds it, it must let you export it.

### The signature

Every business record carries a `signature`. This is an Ed25519 signature, made with your private key, over the whole record except the `signature` field itself (SPEC section 4.6). To make it:

1. Write the complete record, with `public_key` set to your `p` and, preferably, `last_updated` set to now.
2. Convert the record, without `signature`, to its canonical form under RFC 8785, the JSON Canonicalization Scheme. The canonical form has no whitespace, sorted field names and a fixed way of writing strings and numbers. Encode it as UTF-8.
3. Sign those bytes with Ed25519. Add the 64-byte result as `signature`, in standard base64 (88 characters, ending `==`).

The reference validator includes `sign_record()`, which does steps 2 and 3. A provider in hosted mode signs for you. Because the signature covers the canonical form, you may indent or reorder the JSON you serve. Any change to a value, however small, needs a new signature.

Software checks your record in three steps:

1. It parses the JSON, rejecting duplicate field names, and validates it against the schema.
2. It verifies `signature` with `public_key` over the canonical form of the record without `signature`.
3. It checks that `public_key` equals the `p` it found in your `_abiz` TXT record or well-known file.

If step 1 or 2 fails, or `signature` is missing, the record is **not verified**. If step 3 fails, the record is not accepted as yours.

### Rotating and revoking

To rotate:

1. Generate a new keypair.
2. Re-sign the record with the new private key, with the new `public_key` and a new `last_updated`.
3. Publish the new `p` and the re-signed record as close together as possible.

Until the TXT TTL runs out (300 seconds is recommended), some software may still see the old `p` and report a mismatch. It should look again once the TTL has passed.

Because `p` is required, you can't revoke a key by removing it. Rotate to a new key instead, or remove the whole ABIZ record to withdraw from ABIZ. Records signed with an old key stop verifying as soon as `p` changes. ABIZ 1.1 doesn't publish retired keys, either in DNS or in the business record.

### What a signature does and does not show

A valid signature shows two things: whoever holds the key your domain publishes also published this exact record, and nobody has changed it since. It does not prove legal identity, does not make a company number genuine, and does not cover the HTML or Markdown pages. A record you signed in the past stays valid for as long as its key does, so keep `last_updated` current. If you think your private key has been exposed, rotate at once.

## 10. What AI tools will see

With a valid record, a compatible assistant can answer questions such as:

- "Is Hartley’s Bakery Ltd a business in Bristol?"
- "What does Hartley’s Bakery offer, and when is the market stall open?"
- "Is hartleysbakery.example the official website of Hartley’s Bakery Ltd?"
- "Which company number does Hartley’s Bakery Ltd publish for itself?"

Software should only rely on a record whose `signature` verifies and whose `public_key` equals your `p`; a record that fails either check is not verified.

The limits matter. ABIZ shows that a domain and a record point to each other, and that the record was signed with the key your domain publishes. It does not prove that a business is legally registered, that a company number is genuine, or that anyone endorses the business. A tool that has not checked the Companies House register itself must not describe the business as verified. ABIZ does not guarantee that any AI service will find, rank or recommend a business.

## 11. Local practical notes

### Finding the company number

The company number is on the certificate of incorporation and can be searched free of charge on [Find and update company information](https://find-and-update.company-information.service.gov.uk/). Use the registered name exactly as it appears there for `business_name`.

### Adding the TXT record

Add the record wherever your domain's DNS is managed, usually at your domain registrar or web host. The registry for `.uk` domains is [Nominet](https://www.nominet.uk/), but you add the record at your registrar or DNS host; any that supports TXT records will do. Create a record of type TXT with the name `_abiz` (some control panels want the full name, `_abiz.hartleysbakery.example`), the value exactly as in section 2 and a TTL of 300. Do not add spaces inside the value, include `p` (the same value as `public_key` in your record), and remove any older ABIZ record so that only one remains. An ABIZ 1.0 record with no `p`, or a hexadecimal `p`, must be replaced. If you cannot add a TXT record at all, publish the well-known file of section 4 on your website instead.

### Privacy and publishing data

UK GDPR and the Data Protection Act 2018 apply to personal data in your record, for example the name of a sole trader or a named contact. The [Information Commissioner's Office](https://www.ico.org.uk/) has guidance. Everything in an ABIZ record is public, so publish only facts you mean to make public. A sole trader should not publish a home address. A role address such as `hello@` is better than a personal email address.

## 12. Further reading

- [ABIZ specification (SPEC.md)](../../../SPEC.md): DNS syntax (section 3.1.1), the `p` key (section 3.3), the well-known file (section 3.4), the business record (section 4), the `format` parameter (section 4.5), record signing (section 4.6), producer and consumer rules (sections 5 and 6), business units and divisions (section 8)
- [Normative JSON Schema](../../../schemas/abiz-business-record-v1.schema.json) (`$id`: [`https://abizrecord.org/schema/abiz-business-record-v1.schema.json`](https://abizrecord.org/schema/abiz-business-record-v1.schema.json))
- [Well-known file schema](../../../schemas/abiz-well-known-v1.schema.json) (`$id`: `https://abizrecord.org/schema/abiz-well-known-v1.schema.json`)
- [Reference validator, scripts/validate.py](../../../scripts/validate.py)
- [All European guides](index.md)
