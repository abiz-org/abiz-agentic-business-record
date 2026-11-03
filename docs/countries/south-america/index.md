# ABIZ country guides — South America

[← All regions](../README.md)

Find out how to become an agentic business with ABIZ. Choose your country below for local guidance on business registration details, publishing your ABIZ record and connecting your domain.

## About these guides

Country guides for businesses in South America that want to publish an ABIZ (Agentic Business Record): a public JSON business record, and a DNS TXT record at `_abiz` on a domain the business controls that points to it. Every guide follows ABIZ 1.1 as merged in [SPEC.md](../../../SPEC.md); where a guide and the specification differ, the specification wins.

The optional business key `k` never has a subdivision code in South America: section 4.2.2 of the specification requires one only for the United States, Canada (provincial corporations) and the United Arab Emirates. Brazil's key uses the CNPJ, as the specification says. For every other country the specification says the number comes from the national company register. Where a country's company registers are only local or regional (Argentina, Chile, Colombia, Peru and Venezuela), the specification says the country cannot yet carry a business key, so those guides tell businesses to leave `k` out; tax numbers such as the CUIT, RUT, NIT, RUC or RIF are not used, because the specification accepts a tax number only where it names one (Mexico and Brazil). `k` is always optional, and every business can publish a record without it.

Each guide is written in the country's main business language.

## Country guides

| Country | Language | Guide |
|---|---|---|
| Argentina | Español | [Leer la guía](argentina.md) |
| Bolivia | Español | [Leer la guía](bolivia.md) |
| Brazil | Português (Brasil) | [Ler o guia](brazil.md) |
| Chile | Español | [Leer la guía](chile.md) |
| Colombia | Español | [Leer la guía](colombia.md) |
| Ecuador | Español | [Leer la guía](ecuador.md) |
| Guyana | English | [Read guide](guyana.md) |
| Paraguay | Español | [Leer la guía](paraguay.md) |
| Peru | Español | [Leer la guía](peru.md) |
| Suriname | Nederlands | [Lees de gids](suriname.md) |
| Uruguay | Español | [Leer la guía](uruguay.md) |
| Venezuela | Español | [Leer la guía](venezuela.md) |

All examples are fictional. Hostnames ending in `.to.co` illustrate one provider's naming scheme; ABIZ does not require any provider.

See also: [SPEC.md](../../../SPEC.md), [JSON Schema](../../../schemas/abiz-business-record-v1.schema.json), [validator](../../../scripts/validate.py).

## Other regions

- [Africa](../africa/index.md)
- [Asia](../asia/index.md)
- [Europe](../europe/index.md)
- [North America](../north-america/index.md)
- [Oceania](../oceania/index.md)

---

[← Back to all regions](../README.md)
