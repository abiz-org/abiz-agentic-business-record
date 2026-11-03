# ABIZ country guides — North America

[← All regions](../README.md)

Find out how to become an agentic business with ABIZ. Choose your country below for local guidance on business registration details, publishing your ABIZ record and connecting your domain.

## About these guides

Country guides for businesses in North America, Central America and the Caribbean that want to publish an ABIZ (Agentic Business Record): a public JSON business record, and a DNS TXT record at `_abiz` on a domain the business controls that points to it. Every guide follows ABIZ 1.1 as merged in [SPEC.md](../../../SPEC.md); where a guide and the specification differ, the specification wins.

About the optional business key `k`:

- **United States:** the state of formation is required, for example `us-de-7654321`; use `dc` for the District of Columbia. Puerto Rico, Guam, the US Virgin Islands, American Samoa and the Northern Mariana Islands use their own country codes (`pr`, `gu`, `vi`, `as`, `mp`), never `us-pr`.
- **Canada:** provincial and territorial corporations include the province, for example `ca-on-…`, `ca-bc-BC…` or `ca-qc-<NEQ>`; federal corporations use `ca-` and the Corporations Canada number with its check digit, not the CRA Business Number.
- **Mexico:** the 12-character RFC of the legal person, as the specification says.
- **Everywhere else** there is no subdivision code, and the number comes from the national company register. Where company registers are only local or regional (the Dominican Republic, Honduras, Nicaragua, and Saint Kitts and Nevis with its separate Nevis register), the specification says the country cannot yet carry a business key, so those guides tell businesses to leave `k` out. Tax numbers are not used outside Mexico.

`k` is always optional, and every business can publish a record without it. Each guide is written in the country's main business language.

## Country guides

| Country | Language | Guide |
|---|---|---|
| Antigua and Barbuda | English | [Read guide](antigua-and-barbuda.md) |
| Bahamas | English | [Read guide](bahamas.md) |
| Barbados | English | [Read guide](barbados.md) |
| Belize | English | [Read guide](belize.md) |
| Canada | English (Canadian spelling) | [Read guide](canada-en.md) |
| Canada | Français (Québec) | [Lire le guide](canada-fr.md) |
| Costa Rica | Español | [Leer la guía](costa-rica.md) |
| Cuba | Español | [Leer la guía](cuba.md) |
| Dominica | English | [Read guide](dominica.md) |
| Dominican Republic | Español | [Leer la guía](dominican-republic.md) |
| El Salvador | Español | [Leer la guía](el-salvador.md) |
| Grenada | English | [Read guide](grenada.md) |
| Guatemala | Español | [Leer la guía](guatemala.md) |
| Haiti | Français | [Lire le guide](haiti.md) |
| Honduras | Español | [Leer la guía](honduras.md) |
| Jamaica | English | [Read guide](jamaica.md) |
| Mexico | Español | [Leer la guía](mexico.md) |
| Nicaragua | Español | [Leer la guía](nicaragua.md) |
| Panama | Español | [Leer la guía](panama.md) |
| Saint Kitts and Nevis | English | [Read guide](saint-kitts-and-nevis.md) |
| Saint Lucia | English | [Read guide](saint-lucia.md) |
| Saint Vincent and the Grenadines | English | [Read guide](saint-vincent-and-the-grenadines.md) |
| Trinidad and Tobago | English | [Read guide](trinidad-and-tobago.md) |
| United States | English (American spelling) | [Read guide](united-states.md) |

English guides use British spelling, except the United States guide (American spelling) and the English Canada guide (Canadian spelling).

All examples are fictional. Hostnames ending in `.to.co` illustrate one provider's naming scheme; ABIZ does not require any provider.

See also: [SPEC.md](../../../SPEC.md), [JSON Schema](../../../schemas/abiz-business-record-v1.schema.json), [validator](../../../scripts/validate.py).

## Other regions

- [Africa](../africa/index.md)
- [Asia](../asia/index.md)
- [Europe](../europe/index.md)
- [Oceania](../oceania/index.md)
- [South America](../south-america/index.md)

---

[← Back to all regions](../README.md)
