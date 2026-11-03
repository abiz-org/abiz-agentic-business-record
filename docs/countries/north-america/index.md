# Agentic business records in North America

Country guides for businesses in North America, Central America and the Caribbean that want to publish an ABIZ (Agentic Business Record): a public JSON business record, and a DNS TXT record at `_abiz` on a domain the business controls that points to it. Every guide follows ABIZ 1.1 as merged in [SPEC.md](../../../SPEC.md); where a guide and the specification differ, the specification wins.

About the optional business key `k`:

- **United States:** the state of formation is required, for example `us-de-7654321`; use `dc` for the District of Columbia. Puerto Rico, Guam, the US Virgin Islands, American Samoa and the Northern Mariana Islands use their own country codes (`pr`, `gu`, `vi`, `as`, `mp`), never `us-pr`.
- **Canada:** provincial and territorial corporations include the province, for example `ca-on-…`, `ca-bc-BC…` or `ca-qc-<NEQ>`; federal corporations use `ca-` and the Corporations Canada number with its check digit, not the CRA Business Number.
- **Mexico:** the 12-character RFC of the legal person, as the specification says.
- **Everywhere else** there is no subdivision code, and the number comes from the national company register. Where company registers are only local or regional (the Dominican Republic, Honduras, Nicaragua, and Saint Kitts and Nevis with its separate Nevis register), the specification says the country cannot yet carry a business key, so those guides tell businesses to leave `k` out. Tax numbers are not used outside Mexico.

`k` is always optional, and every business can publish a record without it. Each guide is written in the country's main business language.

| Country | Code | Language | Guide |
| --- | --- | --- | --- |
| Antigua and Barbuda | `ag` | English | [antigua-and-barbuda.md](antigua-and-barbuda.md) |
| Bahamas | `bs` | English | [bahamas.md](bahamas.md) |
| Barbados | `bb` | English | [barbados.md](barbados.md) |
| Belize | `bz` | English | [belize.md](belize.md) |
| Canada (English) | `ca` | English (Canadian spelling) | [canada-en.md](canada-en.md) |
| Canada (French) | `ca` | French (Quebec) | [canada-fr.md](canada-fr.md) |
| Costa Rica | `cr` | Spanish | [costa-rica.md](costa-rica.md) |
| Cuba | `cu` | Spanish | [cuba.md](cuba.md) |
| Dominica | `dm` | English | [dominica.md](dominica.md) |
| Dominican Republic | `do` | Spanish | [dominican-republic.md](dominican-republic.md) |
| El Salvador | `sv` | Spanish | [el-salvador.md](el-salvador.md) |
| Grenada | `gd` | English | [grenada.md](grenada.md) |
| Guatemala | `gt` | Spanish | [guatemala.md](guatemala.md) |
| Haiti | `ht` | French | [haiti.md](haiti.md) |
| Honduras | `hn` | Spanish | [honduras.md](honduras.md) |
| Jamaica | `jm` | English | [jamaica.md](jamaica.md) |
| Mexico | `mx` | Spanish | [mexico.md](mexico.md) |
| Nicaragua | `ni` | Spanish | [nicaragua.md](nicaragua.md) |
| Panama | `pa` | Spanish | [panama.md](panama.md) |
| Saint Kitts and Nevis | `kn` | English | [saint-kitts-and-nevis.md](saint-kitts-and-nevis.md) |
| Saint Lucia | `lc` | English | [saint-lucia.md](saint-lucia.md) |
| Saint Vincent and the Grenadines | `vc` | English | [saint-vincent-and-the-grenadines.md](saint-vincent-and-the-grenadines.md) |
| Trinidad and Tobago | `tt` | English | [trinidad-and-tobago.md](trinidad-and-tobago.md) |
| United States | `us` | English (American spelling) | [united-states.md](united-states.md) |

English guides use British spelling, except the United States guide (American spelling) and the English Canada guide (Canadian spelling).

All examples are fictional. Hostnames ending in `.to.co` illustrate one provider's naming scheme; ABIZ does not require any provider.

See also: [SPEC.md](../../../SPEC.md), [JSON Schema](../../../schemas/abiz-business-record-v1.schema.json), [validator](../../../scripts/validate.py).
