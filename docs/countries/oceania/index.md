# ABIZ country guides — Oceania

[← All regions](../README.md)

Find out how to become an agentic business with ABIZ. Choose your country below for local guidance on business registration details, publishing your ABIZ record and connecting your domain.

## About these guides

Country guides for businesses in Oceania that want to publish an ABIZ (Agentic Business Record): a public JSON business record, and a DNS TXT record at `_abiz` on a domain the business controls that points to it. Every guide follows ABIZ 1.1 as merged in [SPEC.md](../../../SPEC.md); where a guide and the specification differ, the specification wins.

About the optional business key `k`: no country in Oceania uses a subdivision code. Australia uses the 9-digit ACN, or the 11-digit ABN for an entity with no ACN, as the specification says. Elsewhere the number comes from the national company register; New Zealand uses the company number, not the NZBN. The Marshall Islands and Tuvalu guides recommend leaving `k` out until it is clear that numbers from their separate domestic and international registers cannot collide, and Micronesia's guide does the same for state-chartered corporations. `k` is always optional, and every business can publish a record without it.

All guides are in English (British spelling), the common language of business registration in the region; each notes the country's other official languages.

## Country guides

| Country | Language | Guide |
|---|---|---|
| Australia | English | [Read guide](australia.md) |
| Fiji | English | [Read guide](fiji.md) |
| Kiribati | English | [Read guide](kiribati.md) |
| Marshall Islands | English | [Read guide](marshall-islands.md) |
| Micronesia | English | [Read guide](micronesia.md) |
| Nauru | English | [Read guide](nauru.md) |
| New Zealand | English | [Read guide](new-zealand.md) |
| Palau | English | [Read guide](palau.md) |
| Papua New Guinea | English | [Read guide](papua-new-guinea.md) |
| Samoa | English | [Read guide](samoa.md) |
| Solomon Islands | English | [Read guide](solomon-islands.md) |
| Tonga | English | [Read guide](tonga.md) |
| Tuvalu | English | [Read guide](tuvalu.md) |
| Vanuatu | English | [Read guide](vanuatu.md) |

All examples are fictional. Hostnames ending in `.to.co` illustrate one provider's naming scheme; ABIZ does not require any provider.

See also: [SPEC.md](../../../SPEC.md), [JSON Schema](../../../schemas/abiz-business-record-v1.1.schema.json), [validator](../../../scripts/validate.py).

## Other regions

- [Africa](../africa/index.md)
- [Asia](../asia/index.md)
- [Europe](../europe/index.md)
- [North America](../north-america/index.md)
- [South America](../south-america/index.md)

---

[← Back to all regions](../README.md)
