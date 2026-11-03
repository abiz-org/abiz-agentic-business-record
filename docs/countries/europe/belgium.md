# Een agentisch bedrijf worden met ABIZ in België

*Een handleiding bij ABIZ 1.1 (voorstel). De [specificatie (SPEC.md, Engelstalig)](../../../SPEC.md) is leidend: als deze handleiding en de specificatie verschillen, geldt de specificatie.* België heeft drie officiële talen; deze handleiding is in het Nederlands, de meest gebruikte taal. Versies in het Frans en het Duits zijn er nog niet.

## 1. Wat dit betekent voor een bedrijf in België

Steeds meer mensen vragen AI-assistenten naar bedrijven: wie ze zijn, wat ze aanbieden, waar ze te vinden zijn. Met ABIZ (Agentic Business Record) publiceert een bedrijf één openbaar, machineleesbaar record met zijn eigen gegevens, zoals naam, land, website, diensten en openingstijden, en op zijn eigen domein een DNS-record dat naar dat record verwijst.

Alleen het bedrijf, of iemand die het daartoe machtigt, kan de DNS van zijn domein wijzigen. Compatibele software kan het record dus via het domein vinden en controleren of domein en record naar elkaar verwijzen, in plaats van gegevens bij elkaar te zoeken op losse webpagina's. ABIZ is open en onafhankelijk van aanbieders: lidmaatschap, kosten of een bepaalde aanbieder zijn niet nodig.

## 2. Een ABIZ-record publiceren

### Verplichte velden

Het bedrijfsrecord is een JSON-document dat moet voldoen aan het [normatieve schema](../../../schemas/abiz-business-record-v1.1.schema.json). Vijf velden zijn verplicht:

| Veld | Voorbeeld | Toelichting |
| --- | --- | --- |
| `record_version` | `abiz1` | Altijd deze waarde |
| `business_name` | `Bakkerij Peeters BV` | De openbare naam, meestal zoals in het register, met rechtsvorm als u die gebruikt |
| `country` | `be` | Landcode volgens ISO 3166-1 alfa-2; de canonieke vorm is in kleine letters |
| `identity_host` | `bakkerijpeeters.be.to.co` | Precies de DNS-waarde `h`: een hostnaam met optioneel pad, zonder `https://` |
| `domains` | `["bakkerijpeeters.example"]` | De domeinen die dit record claimt, inclusief het domein met `_abiz` |

### Optionele bedrijfssleutel `k`

`k` is voor elk bedrijf optioneel, ingeschreven of niet. Als u `k` publiceert, moet het record ook `business_key` en `registration_number` bevatten, en moet `k` gelijk zijn aan `business_key`.

In België bestaat de sleutel uit `be-` gevolgd door het inschrijvingsnummer, zonder onderverdeling: een sleutel met een middendeel, zoals `be-xx-…`, is ongeldig.

- **Register:** [Kruispuntbank van Ondernemingen (KBO)](https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html) van de FOD Economie
- **Te gebruiken nummer:** het ondernemingsnummer van 10 cijfers, geschreven als `0123.456.789`. Niet het vestigingseenheidsnummer
- **Schrijfwijze:** begin bij het nummer zoals het register het toekent, pas Unicode-normalisatie NFKC toe, verwijder spaties, `-`, `.`, `/` en andere streepjes en zet letters in hoofdletters. Voorloopnullen en lettervoorvoegsels blijven staan. Het resultaat mag alleen ASCII-letters en -cijfers bevatten.

Voorbeeld (verzonnen nummer): `0123.456.789` wordt `0123456789`. Het record bevat dan `"registration_number": "0123456789"` en `"business_key": "be-0123456789"`, en in de DNS staat `k=be-0123456789`. Het eerste cijfer (`0` of `1`) hoort bij het nummer en blijft staan.

Sleutels worden zonder onderscheid tussen hoofd- en kleine letters vergeleken, maar publiceer de canonieke vorm: landcode in kleine letters, nummer in hoofdletters.

### DNS-TXT-record

Publiceer precies één ABIZ-TXT-record onder `_abiz` op uw domein, in de compacte vorm zonder spaties:

```dns
_abiz.bakkerijpeeters.example. 300 IN TXT "v=abiz1;k=be-0123456789;h=bakkerijpeeters.be.to.co;p=tzht7C39KDuSrkNsoZPU9SXxgeqK3GOWv2UvFpU4IFU="
```

- `v=abiz1` moet vooraan staan. `h` en `p` zijn verplicht; `k` is optioneel.
- Tagnamen zijn kleine letters en hoofdlettergevoelig. Een tag mag niet twee keer voorkomen.
- Een TTL van 300 seconden wordt aanbevolen.

De `p`-waarde hierboven is een wegwerpsleutel als voorbeeld. Neem die nooit over: publiceer uw eigen sleutel. Een ABIZ 1.1-assertie moet `p` bevatten.

### Bedrijfsrecord (JSON)

Het record dat op `https://bakkerijpeeters.be.to.co` als `application/json` wordt geleverd:

```json
{
  "record_version": "abiz1",
  "business_name": "Bakkerij Peeters BV",
  "country": "be",
  "business_key": "be-0123456789",
  "registration_number": "0123456789",
  "identity_host": "bakkerijpeeters.be.to.co",
  "domains": [
    "bakkerijpeeters.example"
  ],
  "public_key": "tzht7C39KDuSrkNsoZPU9SXxgeqK3GOWv2UvFpU4IFU=",
  "description": "Ambachtelijke bakkerij in Gent.",
  "website": "https://bakkerijpeeters.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Gent",
        "country": {
          "code": "BE"
        }
      },
      "public": true
    }
  ],
  "signature": "WRrXAMfnSKhdgW91i6Ct7wptPc7hv7/mZg9OhZdd1bRbZthcq8HOJFHmgO1o7cxQvc0QXphdT6M8yglAtMHJDw=="
}
```

Met de referentievalidator controleert u record en DNS-waarde lokaal:

```sh
python scripts/validate.py record.json --domain bakkerijpeeters.example --dns-value 'v=abiz1;k=be-0123456789;h=bakkerijpeeters.be.to.co;p=tzht7C39KDuSrkNsoZPU9SXxgeqK3GOWv2UvFpU4IFU='
```

### Zelf hosten of via een aanbieder

U kunt het record zelf leveren op elke HTTPS-host die u beheert, of een compatibele aanbieder naar keuze gebruiken. ABIZ schrijft geen aanbieder of naamschema voor hostnamen voor. Hoe dan ook moet het record via HTTPS worden geleverd en moet u het domein met `_abiz` beheren.

## 3. Aanbieders en MCP

MCP (Model Context Protocol) is een open protocol waarmee AI-assistenten hulpmiddelen aanroepen en gegevens van externe servers lezen. Een aanbieder kan een MCP-server draaien waarmee een assistent uw openbare record rechtstreeks opvraagt. U kunt die server vermelden in het optionele veld `mcp_server_url`. ABIZ vereist geen MCP-server, en een hulpmiddel hoort een server niet automatisch aan te roepen alleen omdat die in een record staat.

Een voorbeeld: een aanbieder publiceert uw record op `bakkerijpeeters.be.to.co` en draait een MCP-server. Een assistent die met die server verbonden is, kan dan naar de openingstijden of diensten van Bakkerij Peeters BV vragen en krijgt de gegevens uit uw record, in plaats van te gokken.

## 4. Sleutels en handtekeningen (ABIZ 1.1)

ABIZ 1.1 vereist een openbare Ed25519-sleutel in de DNS-tag `p`. `v` en `h` zijn verplicht. `p` is verplicht. `k` is optioneel. `p` moet 32 ruwe bytes in standaard-base64 zijn: 44 tekens die eindigen op precies één `=`, in één DNS-string. Base64url wordt niet aanvaard. Elke andere waarde, zoals een hexadecimaal ABIZ 1.0-token, maakt het hele record ongeldig.

De bijbehorende privésleutel is van het bedrijf en wordt nooit gepubliceerd. Bewaart een aanbieder hem voor u, dan moet die u de sleutel laten exporteren. Software kan een handtekening die met de privésleutel is gemaakt, controleren met de sleutel in de DNS. De handtekening dekt de RFC 8785-canonieke vorm van het record zonder het lid `signature` en wordt gecontroleerd met `public_key`, dat gelijk moet zijn aan `p` (SPEC sectie 4.6).

Om te wisselen maakt u een nieuw Ed25519-sleutelpaar, publiceert u de nieuwe openbare sleutel in de DNS- of well-known-assertie, ondertekent u het record opnieuw met de nieuwe privésleutel en zet u `public_key` op dezelfde `p`. Houd rekening met DNS-cache. Alleen `p` verwijderen is geen geldige intrekking zolang de ABIZ 1.1-assertie blijft staan: om haar in te trekken, verwijdert u de volledige verklaring. Afgedankte sleutels worden in ABIZ 1.1 niet gepubliceerd, niet in de DNS en niet in het bedrijfsrecord. De sleutel laat zien welke sleutel de beheerder van het domein heeft gepubliceerd; hij bewijst geen juridische identiteit.

## 5. Wat AI-hulpmiddelen zien

Met een geldig record kan een compatibele assistent vragen beantwoorden zoals:

- ‘Is Bakkerij Peeters BV een bedrijf in Gent?’
- ‘Wat biedt Bakkerij Peeters BV aan, en wanneer is het open?’
- ‘Is bakkerijpeeters.example de officiële website van Bakkerij Peeters BV?’
- ‘Welk inschrijvingsnummer geeft Bakkerij Peeters BV zelf op?’

De grenzen zijn belangrijk. ABIZ laat zien dat een domein en een record naar elkaar verwijzen. Het bewijst niet dat een bedrijf wettelijk is ingeschreven, dat een inschrijvingsnummer echt is of dat iemand het bedrijf aanbeveelt. Een hulpmiddel dat het KBO-register niet zelf heeft geraadpleegd, mag het bedrijf niet als geverifieerd voorstellen. ABIZ garandeert niet dat een AI-dienst een bedrijf vindt, rangschikt of aanbeveelt.

## 6. Praktische informatie

### Het inschrijvingsnummer vinden

Het ondernemingsnummer staat op uw facturen en briefpapier en is gratis op te zoeken in [KBO Public Search](https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html). Ook zelfstandigen in eenmanszaak hebben een ondernemingsnummer.

### Het TXT-record toevoegen

Voeg het record toe waar de DNS van uw domein wordt beheerd, meestal bij uw domeinregistrar of webhoster. De registry voor `.be`-domeinen is [DNS Belgium](https://www.dnsbelgium.be/), maar het record voegt u toe bij uw registrar of DNS-aanbieder; elke aanbieder die TXT-records ondersteunt, volstaat. Maak een record van het type TXT met de naam `_abiz` (sommige beheerpanelen willen de volledige naam, `_abiz.bakkerijpeeters.example`), de waarde precies zoals hierboven en een TTL van 300. Zet geen spaties in de waarde en verwijder oudere ABIZ-records, zodat er maar één overblijft.

### Privacy en publicatie

De AVG geldt voor persoonsgegevens in uw record, zoals de naam van een eenmanszaak of een contactpersoon. Het [Europees Comité voor gegevensbescherming](https://www.edpb.europa.eu/) verwijst naar de nationale toezichthouders. In België is de Gegevensbeschermingsautoriteit de toezichthouder. Alles in een ABIZ-record is openbaar; publiceer alleen gegevens die openbaar mogen zijn. Een eenmanszaak publiceert beter geen woonadres: de specificatie vereist dat privé-adressen worden weggelaten, niet als privé gemarkeerd. Een algemeen adres zoals `info@` is beter dan een persoonlijk e-mailadres.

## 7. Meer informatie

- [ABIZ-specificatie (SPEC.md, Engelstalig)](../../../SPEC.md): DNS-syntaxis (sectie 3.1.1), de sleutel `p` (sectie 3.3), bedrijfssleutels (sectie 4.2)
- [Normatief JSON-schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Referentievalidator, scripts/validate.py](../../../scripts/validate.py)
- [Alle Europese handleidingen](index.md)
