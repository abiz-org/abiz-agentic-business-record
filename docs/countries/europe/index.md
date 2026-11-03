# Agentic business records in Europe

These guides explain how a business in each European country can publish an ABIZ record: the required fields, the optional business key `k` and where its number comes from, the DNS TXT record, Ed25519 keys in `p`, and local notes on registers, domains and privacy. They follow ABIZ 1.1 (proposed). The [specification (SPEC.md)](../../../SPEC.md) is the authoritative text: if a guide and the specification differ, the specification applies.

Pages are written in the country's main business language where we could do so to a good standard; the others are in English for now. All example businesses, numbers, domains and keys are fictional. Never copy an example `p` value.

| Country | Language |
| --- | --- |
| [Albania](albania.md) | English |
| [Andorra](andorra.md) | English |
| [Austria](austria.md) | Deutsch |
| [Belarus](belarus.md) | Русский |
| [Belgium](belgium.md) | Nederlands |
| [Bosnia and Herzegovina](bosnia-and-herzegovina.md) | English |
| [Bulgaria](bulgaria.md) | English |
| [Croatia](croatia.md) | English |
| [Czechia](czechia.md) | Čeština |
| [Denmark](denmark.md) | Dansk |
| [Estonia](estonia.md) | English |
| [Finland](finland.md) | Suomi |
| [France](france.md) | Français |
| [Germany](germany.md) | Deutsch |
| [Greece](greece.md) | English |
| [Hungary](hungary.md) | English |
| [Iceland](iceland.md) | English |
| [Ireland](ireland.md) | English |
| [Italy](italy.md) | Italiano |
| [Kosovo](kosovo.md) | English |
| [Latvia](latvia.md) | English |
| [Liechtenstein](liechtenstein.md) | Deutsch |
| [Lithuania](lithuania.md) | English |
| [Luxembourg](luxembourg.md) | Français |
| [Malta](malta.md) | English |
| [Moldova](moldova.md) | Română |
| [Monaco](monaco.md) | Français |
| [Montenegro](montenegro.md) | English |
| [Netherlands](netherlands.md) | Nederlands |
| [North Macedonia](north-macedonia.md) | English |
| [Norway](norway.md) | Norsk bokmål |
| [Poland](poland.md) | Polski |
| [Portugal](portugal.md) | Português |
| [Romania](romania.md) | Română |
| [Russia](russia.md) | Русский |
| [San Marino](san-marino.md) | Italiano |
| [Serbia](serbia.md) | English |
| [Slovakia](slovakia.md) | English |
| [Slovenia](slovenia.md) | English |
| [Spain](spain.md) | Español |
| [Sweden](sweden.md) | Svenska |
| [Switzerland](switzerland.md) | Deutsch |
| [Ukraine](ukraine.md) | Українська |
| [United Kingdom](united-kingdom.md) | English |
| [Vatican City](vatican-city.md) | Italiano |

A few countries need care:

- **Bosnia and Herzegovina** has no single national company register, so no business key is possible under ABIZ 1.1.
- **Kosovo** uses `XK`, a user-assigned code, so a conformant ABIZ 1.1 record is not yet possible.
- **Vatican City** has no public business register, so records there omit `k`.

See also the [reference validator](../../../scripts/validate.py) and the [normative JSON Schema](../../../schemas/abiz-business-record-v1.schema.json).
