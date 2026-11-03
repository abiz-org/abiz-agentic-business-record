# Agentic business records in South America

Country guides for businesses in South America that want to publish an ABIZ (Agentic Business Record): a public JSON business record, and a DNS TXT record at `_abiz` on a domain the business controls that points to it. Every guide follows ABIZ 1.1 as merged in [SPEC.md](../../../SPEC.md); where a guide and the specification differ, the specification wins.

The optional business key `k` never has a subdivision code in South America: section 4.2.2 of the specification requires one only for the United States, Canada (provincial corporations) and the United Arab Emirates. Brazil's key uses the CNPJ, as the specification says. For every other country the specification says the number comes from the national company register. Where a country's company registers are only local or regional (Argentina, Chile, Colombia, Peru and Venezuela), the specification says the country cannot yet carry a business key, so those guides tell businesses to leave `k` out; tax numbers such as the CUIT, RUT, NIT, RUC or RIF are not used, because the specification accepts a tax number only where it names one (Mexico and Brazil). `k` is always optional, and every business can publish a record without it.

Each guide is written in the country's main business language.

| Country | Code | Language | Guide |
| --- | --- | --- | --- |
| Argentina | `ar` | Spanish | [argentina.md](argentina.md) |
| Bolivia | `bo` | Spanish | [bolivia.md](bolivia.md) |
| Brazil | `br` | Portuguese (Brazil) | [brazil.md](brazil.md) |
| Chile | `cl` | Spanish | [chile.md](chile.md) |
| Colombia | `co` | Spanish | [colombia.md](colombia.md) |
| Ecuador | `ec` | Spanish | [ecuador.md](ecuador.md) |
| Guyana | `gy` | English | [guyana.md](guyana.md) |
| Paraguay | `py` | Spanish | [paraguay.md](paraguay.md) |
| Peru | `pe` | Spanish | [peru.md](peru.md) |
| Suriname | `sr` | Dutch | [suriname.md](suriname.md) |
| Uruguay | `uy` | Spanish | [uruguay.md](uruguay.md) |
| Venezuela | `ve` | Spanish | [venezuela.md](venezuela.md) |

All examples are fictional. Hostnames ending in `.to.co` illustrate one provider's naming scheme; ABIZ does not require any provider.

See also: [SPEC.md](../../../SPEC.md), [JSON Schema](../../../schemas/abiz-business-record-v1.schema.json), [validator](../../../scripts/validate.py).
