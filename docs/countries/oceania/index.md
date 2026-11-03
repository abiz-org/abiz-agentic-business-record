# Agentic business records in Oceania

Country guides for businesses in Oceania that want to publish an ABIZ (Agentic Business Record): a public JSON business record, and a DNS TXT record at `_abiz` on a domain the business controls that points to it. Every guide follows ABIZ 1.1 as merged in [SPEC.md](../../../SPEC.md); where a guide and the specification differ, the specification wins.

About the optional business key `k`: no country in Oceania uses a subdivision code. Australia uses the 9-digit ACN, or the 11-digit ABN for an entity with no ACN, as the specification says. Elsewhere the number comes from the national company register; New Zealand uses the company number, not the NZBN. The Marshall Islands and Tuvalu guides recommend leaving `k` out until it is clear that numbers from their separate domestic and international registers cannot collide, and Micronesia's guide does the same for state-chartered corporations. `k` is always optional, and every business can publish a record without it.

All guides are in English (British spelling), the common language of business registration in the region; each notes the country's other official languages.

| Country | Code | Language | Guide |
| --- | --- | --- | --- |
| Australia | `au` | English | [australia.md](australia.md) |
| Fiji | `fj` | English | [fiji.md](fiji.md) |
| Kiribati | `ki` | English | [kiribati.md](kiribati.md) |
| Marshall Islands | `mh` | English | [marshall-islands.md](marshall-islands.md) |
| Micronesia | `fm` | English | [micronesia.md](micronesia.md) |
| Nauru | `nr` | English | [nauru.md](nauru.md) |
| New Zealand | `nz` | English | [new-zealand.md](new-zealand.md) |
| Palau | `pw` | English | [palau.md](palau.md) |
| Papua New Guinea | `pg` | English | [papua-new-guinea.md](papua-new-guinea.md) |
| Samoa | `ws` | English | [samoa.md](samoa.md) |
| Solomon Islands | `sb` | English | [solomon-islands.md](solomon-islands.md) |
| Tonga | `to` | English | [tonga.md](tonga.md) |
| Tuvalu | `tv` | English | [tuvalu.md](tuvalu.md) |
| Vanuatu | `vu` | English | [vanuatu.md](vanuatu.md) |

All examples are fictional. Hostnames ending in `.to.co` illustrate one provider's naming scheme; ABIZ does not require any provider.

See also: [SPEC.md](../../../SPEC.md), [JSON Schema](../../../schemas/abiz-business-record-v1.schema.json), [validator](../../../scripts/validate.py).
