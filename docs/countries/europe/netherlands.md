# Een agentisch bedrijf worden met ABIZ in Nederland

*Een handleiding bij ABIZ 1.1 (voorstel). De [specificatie (SPEC.md, Engelstalig)](../../../SPEC.md) is leidend: als deze handleiding en de specificatie verschillen, geldt de specificatie.*

## 1. Wat dit betekent voor een bedrijf in Nederland

Steeds meer mensen vragen AI-assistenten naar bedrijven: wie ze zijn, wat ze aanbieden, waar ze te vinden zijn. Met ABIZ (Agentic Business Record) publiceert een bedrijf één openbaar, machineleesbaar record met zijn eigen gegevens, zoals naam, land, website, diensten en openingstijden, en op zijn eigen domein een DNS-record dat naar dat record verwijst.

Alleen het bedrijf, of iemand die het daartoe machtigt, kan de DNS van zijn domein wijzigen. Compatibele software kan het record dus via het domein vinden en controleren of domein en record naar elkaar verwijzen, in plaats van gegevens bij elkaar te zoeken op losse webpagina's. ABIZ is open en onafhankelijk van aanbieders: lidmaatschap, kosten of een bepaalde aanbieder zijn niet nodig.

## 2. Een ABIZ-record publiceren

### Verplichte velden

Het bedrijfsrecord is een JSON-document dat moet voldoen aan het [normatieve schema](../../../schemas/abiz-business-record-v1.schema.json). Vijf velden zijn verplicht:

| Veld | Voorbeeld | Toelichting |
| --- | --- | --- |
| `record_version` | `abiz1` | Altijd deze waarde |
| `business_name` | `Fietsenmaker De Vries B.V.` | De openbare naam, meestal zoals in het register, met rechtsvorm als u die gebruikt |
| `country` | `nl` | Landcode volgens ISO 3166-1 alfa-2; de canonieke vorm is in kleine letters |
| `identity_host` | `fietsenmakerdevries.nl.to.co` | Precies de DNS-waarde `h`: een hostnaam met optioneel pad, zonder `https://` |
| `domains` | `["fietsenmakerdevries.example"]` | De domeinen die dit record claimt, inclusief het domein met `_abiz` |

### Optionele bedrijfssleutel `k`

`k` is voor elk bedrijf optioneel, ingeschreven of niet. Als u `k` publiceert, moet het record ook `business_key` en `registration_number` bevatten, en moet `k` gelijk zijn aan `business_key`.

In Nederland bestaat de sleutel uit `nl-` gevolgd door het inschrijvingsnummer, zonder onderverdeling: een sleutel met een middendeel, zoals `nl-xx-…`, is ongeldig.

- **Register:** Handelsregister van de [Kamer van Koophandel (KVK)](https://www.kvk.nl/)
- **Te gebruiken nummer:** het KVK-nummer van 8 cijfers. Niet het vestigingsnummer (12 cijfers) en niet het btw-identificatienummer
- **Schrijfwijze:** begin bij het nummer zoals het register het toekent, pas Unicode-normalisatie NFKC toe, verwijder spaties, `-`, `.`, `/` en andere streepjes en zet letters in hoofdletters. Voorloopnullen en lettervoorvoegsels blijven staan. Het resultaat mag alleen ASCII-letters en -cijfers bevatten.

Voorbeeld (verzonnen nummer): `12345678` staat al in de canonieke vorm. Het record bevat dan `"registration_number": "12345678"` en `"business_key": "nl-12345678"`, en in de DNS staat `k=nl-12345678`.

Sleutels worden zonder onderscheid tussen hoofd- en kleine letters vergeleken, maar publiceer de canonieke vorm: landcode in kleine letters, nummer in hoofdletters.

### DNS-TXT-record

Publiceer precies één ABIZ-TXT-record onder `_abiz` op uw domein, in de compacte vorm zonder spaties:

```dns
_abiz.fietsenmakerdevries.example. 300 IN TXT "v=abiz1;k=nl-12345678;h=fietsenmakerdevries.nl.to.co;p=j4I88ldun0pst/oOl5WF+uIVP2hX4szG4S55bSJO8Ug="
```

- `v=abiz1` moet vooraan staan. `h` is verplicht; `k` en `p` zijn optioneel.
- Tagnamen zijn kleine letters en hoofdlettergevoelig. Een tag mag niet twee keer voorkomen.
- Een TTL van 300 seconden wordt aanbevolen.

De `p`-waarde hierboven is een wegwerpsleutel als voorbeeld. Neem die nooit over: publiceer uw eigen sleutel of laat `p` weg.

### Bedrijfsrecord (JSON)

Het record dat op `https://fietsenmakerdevries.nl.to.co` als `application/json` wordt geleverd:

```json
{
  "record_version": "abiz1",
  "business_name": "Fietsenmaker De Vries B.V.",
  "country": "nl",
  "business_key": "nl-12345678",
  "registration_number": "12345678",
  "identity_host": "fietsenmakerdevries.nl.to.co",
  "domains": [
    "fietsenmakerdevries.example"
  ],
  "public_key": "j4I88ldun0pst/oOl5WF+uIVP2hX4szG4S55bSJO8Ug=",
  "description": "Fietsenmaker in Utrecht.",
  "website": "https://fietsenmakerdevries.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Utrecht",
      "country": "nl",
      "public": true
    }
  ],
  "signature": "TVF7OIemkJHIt3a0U8ye6riP7nNiJ2Su6oN02fGIxS4Bvbf1jeGSzSrtwrvEDUeujj92+7WX9WohryZTNEC2Aw=="
}
```

Met de referentievalidator controleert u record en DNS-waarde lokaal:

```sh
python scripts/validate.py record.json --domain fietsenmakerdevries.example --dns-value 'v=abiz1;k=nl-12345678;h=fietsenmakerdevries.nl.to.co;p=j4I88ldun0pst/oOl5WF+uIVP2hX4szG4S55bSJO8Ug='
```

### Zelf hosten of via een aanbieder

U kunt het record zelf leveren op elke HTTPS-host die u beheert, of een compatibele aanbieder naar keuze gebruiken. ABIZ schrijft geen aanbieder of naamschema voor hostnamen voor. Hoe dan ook moet het record via HTTPS worden geleverd en moet u het domein met `_abiz` beheren.

## 3. Aanbieders en MCP

MCP (Model Context Protocol) is een open protocol waarmee AI-assistenten hulpmiddelen aanroepen en gegevens van externe servers lezen. Een aanbieder kan een MCP-server draaien waarmee een assistent uw openbare record rechtstreeks opvraagt. U kunt die server vermelden in het optionele veld `mcp_server_url`. ABIZ vereist geen MCP-server, en een hulpmiddel hoort een server niet automatisch aan te roepen alleen omdat die in een record staat.

Een voorbeeld: een aanbieder publiceert uw record op `fietsenmakerdevries.nl.to.co` en draait een MCP-server. Een assistent die met die server verbonden is, kan dan naar de openingstijden of diensten van Fietsenmaker De Vries B.V. vragen en krijgt de gegevens uit uw record, in plaats van te gokken. to.co, een van die aanbieders, legt ABIZ uit op een [Nederlandstalige pagina](https://to.co/nl-nl/abiz).

## 4. Sleutels en handtekeningen (ABIZ 1.1)

Met ABIZ 1.1 kan een bedrijf een openbare Ed25519-sleutel publiceren in de DNS-tag `p`. `p` is optioneel. Als de tag er staat, moet de waarde de standaard-base64-codering van de sleutel van 32 bytes zijn: 44 tekens die eindigen op precies één `=`, in één DNS-string. Elke andere waarde, zoals een hexadecimaal ABIZ 1.0-token of een base64url-sleutel, maakt het hele record ongeldig.

De bijbehorende privésleutel is van het bedrijf en wordt nooit gepubliceerd. Bewaart een aanbieder hem voor u, dan moet die u de sleutel laten exporteren. Software kan een handtekening die met de privésleutel is gemaakt, controleren met de sleutel in de DNS. Welke bytes een handtekening over het bedrijfsrecord dekt, legt ABIZ 1.1 nog niet vast.

Om te wisselen publiceert u een nieuwe sleutel in `p`; om in te trekken verwijdert u `p`. Afgedankte sleutels worden in ABIZ 1.1 niet gepubliceerd, niet in de DNS en niet in het bedrijfsrecord. De sleutel laat zien welke sleutel de beheerder van het domein heeft gepubliceerd; hij bewijst geen juridische identiteit.

## 5. Wat AI-hulpmiddelen zien

Met een geldig record kan een compatibele assistent vragen beantwoorden zoals:

- ‘Is Fietsenmaker De Vries B.V. een bedrijf in Utrecht?’
- ‘Wat biedt Fietsenmaker De Vries B.V. aan, en wanneer is het open?’
- ‘Is fietsenmakerdevries.example de officiële website van Fietsenmaker De Vries B.V.?’
- ‘Welk inschrijvingsnummer geeft Fietsenmaker De Vries B.V. zelf op?’

De grenzen zijn belangrijk. ABIZ laat zien dat een domein en een record naar elkaar verwijzen. Het bewijst niet dat een bedrijf wettelijk is ingeschreven, dat een inschrijvingsnummer echt is of dat iemand het bedrijf aanbeveelt. Een hulpmiddel dat het Handelsregister niet zelf heeft geraadpleegd, mag het bedrijf niet als geverifieerd voorstellen. ABIZ garandeert niet dat een AI-dienst een bedrijf vindt, rangschikt of aanbeveelt.

## 6. Praktische informatie

### Het inschrijvingsnummer vinden

Het KVK-nummer staat op het uittreksel uit het Handelsregister, op facturen en op uw website. U zoekt het op via de [KVK](https://www.kvk.nl/). Ook een eenmanszaak heeft een KVK-nummer en kan de sleutel publiceren, maar geen woonadres.

### Het TXT-record toevoegen

Voeg het record toe waar de DNS van uw domein wordt beheerd, meestal bij uw domeinregistrar of webhoster. De registry voor `.nl`-domeinen is [SIDN](https://www.sidn.nl/), maar het record voegt u toe bij uw registrar of DNS-aanbieder; elke aanbieder die TXT-records ondersteunt, volstaat. Maak een record van het type TXT met de naam `_abiz` (sommige beheerpanelen willen de volledige naam, `_abiz.fietsenmakerdevries.example`), de waarde precies zoals hierboven en een TTL van 300. Zet geen spaties in de waarde en verwijder oudere ABIZ-records, zodat er maar één overblijft.

### Privacy en publicatie

De AVG geldt voor persoonsgegevens in uw record, zoals de naam van een eenmanszaak of een contactpersoon. Het [Europees Comité voor gegevensbescherming](https://www.edpb.europa.eu/) verwijst naar de nationale toezichthouders. In Nederland is de Autoriteit Persoonsgegevens de toezichthouder. Alles in een ABIZ-record is openbaar; publiceer alleen gegevens die openbaar mogen zijn. Een eenmanszaak publiceert beter geen woonadres: de specificatie vereist dat privé-adressen worden weggelaten, niet als privé gemarkeerd. Een algemeen adres zoals `info@` is beter dan een persoonlijk e-mailadres.

## 7. Meer informatie

- [ABIZ-specificatie (SPEC.md, Engelstalig)](../../../SPEC.md): DNS-syntaxis (sectie 3.1.1), de sleutel `p` (sectie 3.3), bedrijfssleutels (sectie 4.2)
- [Normatief JSON-schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Referentievalidator, scripts/validate.py](../../../scripts/validate.py)
- [Alle Europese handleidingen](index.md)
