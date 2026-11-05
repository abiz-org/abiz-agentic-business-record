# Een agentisch bedrijf worden met ABIZ in Suriname

*Gids voor de gepubliceerde specificatie ABIZ 1.1. [SPEC.md](../../../SPEC.md) is de gezaghebbende tekst: als deze gids en de specificatie verschillen, geldt de specificatie.*

## 1. Wat dit betekent voor een bedrijf in Suriname

Steeds meer mensen stellen AI-assistenten vragen als ‘welke bakker bij mij in de buurt is zondag open?’ of ‘is deze website echt van dit bedrijf?’. ABIZ (Agentic Business Record) is een open standaard waarmee een bedrijf zijn openbare gegevens zo publiceert dat compatibele software ze kan vinden en controleren: een klein JSON-document met die gegevens, en een DNS TXT-record op het eigen domein van het bedrijf dat ernaar verwijst.

Met ABIZ kan een compatibele assistent vanaf uw domein uw record vinden, het valideren met het gepubliceerde JSON Schema en bevestigen dat domein en record naar elkaar verwijzen. Het werkt voor ingeschreven bedrijven en voor bedrijven zonder inschrijving. ABIZ garandeert niet dat een assistent u vindt, hoog plaatst of aanbeveelt, en het is geen officieel keurmerk.

In Suriname kan een bedrijf dat in het Handelsregister staat zijn KKF-nummer als bedrijfssleutel opnemen; een bedrijf zonder inschrijving kan zijn record zonder sleutel publiceren.

## 2. Een ABIZ-record publiceren

### Verplichte velden

| Veld | Wat u invult | Voorbeeld |
| --- | --- | --- |
| `record_version` | Altijd `abiz1` | `abiz1` |
| `business_name` | De openbare naam van het bedrijf | `Bakkerij Paramaribo N.V.` |
| `country` | De ISO 3166-1 alpha-2-landcode, in kleine letters | `sr` |
| `identity_host` | De host, met optioneel pad, waar het record staat; moet gelijk zijn aan `h` in de DNS | `bakkerijparamaribo.sr.to.co` |
| `domains` | De domeinen die u beheert en die het record claimt | `["bakkerijparamaribo.example"]` |

### De optionele bedrijfssleutel `k`

`k` is voor elk bedrijf optioneel. Als u hem publiceert, moet hij voldoen aan sectie 4.2 van de specificatie en gelijk zijn aan de `business_key` in het record. Bij het vergelijken van sleutels telt hoofdletter of kleine letter niet, maar de canonieke vorm heeft de landcode in kleine letters en het inschrijvingsnummer in hoofdletters.

Vorm: `sr-` gevolgd door het inschrijvingsnummer in het Handelsregister van de Kamer van Koophandel en Fabrieken (KKF). Sectie 4.2.2 van de specificatie noemt Suriname niet, dus de sleutel krijgt geen subdivisiecode. Het Handelsregister is landelijk.

**Het nummer normaliseren (sectie 4.2.3).** Ga uit van het nummer precies zoals het register het uitgeeft. Pas Unicode-NFKC-normalisatie toe; verwijder spaties, koppeltekens, punten en schuine strepen; zet letters om in hoofdletters; behoud voorloopnullen en lettervoorvoegsels. Blijft er een ander teken over, zoals haakjes, `&` of een letter met accent, dan kan het nummer niet worden uitgedrukt en kunt u geen bedrijfssleutel publiceren: laat `k`, `business_key` en `registration_number` weg.

**Voorbeeld (fictief):** KKF-nummer `12345` geeft de sleutel `sr-12345`.

Neemt u `business_key` en `registration_number` op in het record, neem dan beide op; het nummerdeel van de sleutel moet gelijk zijn aan `registration_number`. Ze opnemen verplicht u niet om `k` in de DNS te publiceren. Publiceert u `k` wel, dan moet het record de bijbehorende `business_key` bevatten.

### Het DNS TXT-record

Publiceer precies één TXT-record dat begint met `v=abiz1` op `_abiz.` gevolgd door uw domein. Gebruik de compacte vorm zonder spaties (sectie 3.1.1) en een TTL van 300 seconden:

```dns
_abiz.bakkerijparamaribo.example. 300 IN TXT "v=abiz1;k=sr-12345;h=bakkerijparamaribo.sr.to.co;p=33/gd4VA9zbCRCRSULT3AGtJGtoiHlB1VY8QBQlMRTc="
```

Een bedrijf zonder inschrijvingsnummer, of dat het liever niet publiceert, laat `k` gewoon weg:

```dns
_abiz.marktkraam.example. 300 IN TXT "v=abiz1;h=marktkraam.biz.to.co;p=Q2rO0Sv8OykxFAPGtdVBjF3COBG3aGUGBcK7cnKrDTg="
```

### Voorbeeldrecord (JSON)

Dit voorbeeld is fictief. Het slaagt voor de referentievalidator.

```json
{
  "record_version": "abiz1",
  "business_name": "Bakkerij Paramaribo N.V.",
  "country": {
    "code": "SR",
    "name": "Suriname"
  },
  "business_key": "sr-12345",
  "registration_number": "12345",
  "identity_host": "bakkerijparamaribo.sr.to.co",
  "domains": [
    "bakkerijparamaribo.example"
  ],
  "public_key": "33/gd4VA9zbCRCRSULT3AGtJGtoiHlB1VY8QBQlMRTc=",
  "description": "Ambachtelijke bakkerij in het centrum van Paramaribo.",
  "website": "https://bakkerijparamaribo.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Paramaribo",
        "country": {
          "code": "SR"
        }
      },
      "opening_hours": {
        "time_zone": "America/Paramaribo",
        "weekly": [
          {
            "day": "monday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "tuesday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "wednesday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "thursday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "friday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "saturday",
            "periods": [
              {
                "opens": "06:00",
                "closes": "18:00"
              }
            ]
          },
          {
            "day": "sunday",
            "periods": []
          }
        ]
      },
      "public": true
    }
  ],
  "signature": "DCmJEDxe7gU9DiQ/QUTFbXe6JQ59bE/9Piwk6adcvbILbe5cu6xhLSeg3MIDcTlxvzlKiRNTW0iW4+EcPD3dAA=="
}
```

### Waar het record staat

U kunt het record zelf aanbieden vanaf elke HTTPS-URL die het JSON-document teruggeeft, bijvoorbeeld `h=www.bakkerijparamaribo.example`, of elke compatibele aanbieder gebruiken. ABIZ schrijft geen bepaalde aanbieder of naamgeving voor. Wat u ook kiest: `identity_host` in het record moet gelijk zijn aan `h`, en `domains` moet het domein bevatten waarop u het TXT-record publiceert.

Controleer het record en de DNS-waarde vóór publicatie met de referentievalidator:

```sh
python scripts/validate.py record.json \
  --domain bakkerijparamaribo.example \
  --dns-value 'v=abiz1;k=sr-12345;h=bakkerijparamaribo.sr.to.co;p=33/gd4VA9zbCRCRSULT3AGtJGtoiHlB1VY8QBQlMRTc='
```

## 3. Aanbieders en MCP

Het Model Context Protocol (MCP) is een open protocol waarmee AI-assistenten op een standaardmanier tools van externe diensten kunnen gebruiken en gegevens kunnen lezen. Een ABIZ-record kan een optionele `mcp_server_url` bevatten: het HTTPS-adres van een MCP-server die vragen over het bedrijf beantwoordt, zoals openingstijden, diensten of beschikbaarheid. ABIZ vereist geen MCP-server, en een vermelde server wordt daarmee niet gegarandeerd: compatibele software mag hem niet automatisch aanroepen alleen omdat hij in een record staat, en moet eigen toegangscontroles toepassen.

Een aanbieder kan bijvoorbeeld het record van Bakkerij Paramaribo hosten op `bakkerijparamaribo.sr.to.co`, het DNS TXT-record via zijn eigen instelproces publiceren en zijn MCP-server vermelden in `mcp_server_url`. U kunt overstappen naar een andere aanbieder, of het record zelf gaan hosten, door `h` en de `identity_host` van het record te wijzigen.

## 4. Sleutels en handtekeningen (ABIZ 1.1)

- **`p` is verplicht.** `v` en `h` zijn verplicht; `k` is optioneel. `p` moet een openbare Ed25519-sleutel zijn: 32 ruwe bytes, standaard-base64, precies 44 tekens, eindigend op één `=`. Base64url wordt niet aanvaard (sectie 3.3.2). Elke andere waarde, zoals een hexadecimale tekenreeks of een base64url-sleutel, maakt de hele bewering ongeldig.
- **Voorbeeld** (voorbeeldsleutel voor eenmalig gebruik; de private sleutel is vernietigd). Kopieer hem nooit: publiceer uw eigen sleutel. Een ABIZ 1.1-assertie moet `p` bevatten.

  ```dns
  _abiz.bakkerijparamaribo.example. 300 IN TXT "v=abiz1;k=sr-12345;h=bakkerijparamaribo.sr.to.co;p=33/gd4VA9zbCRCRSULT3AGtJGtoiHlB1VY8QBQlMRTc="
  ```

- **De private sleutel is van het bedrijf.** Hij mag nooit in de DNS, in het record of in een openbare repository staan. Een aanbieder mag hem voor u aanmaken en bewaren (gehoste modus), maar moet u hem altijd laten exporteren, bijvoorbeeld als PKCS#8, en zijn kopie op verzoek verwijderen (sectie 3.3.4).
- **Ondertekenen.** Software kan een losse Ed25519-handtekening controleren met de gepubliceerde sleutel. De handtekening van het record dekt de RFC 8785-canonieke vorm van het record zonder het lid `signature` en wordt gecontroleerd met `public_key`, dat gelijk moet zijn aan `p` (SPEC sectie 4.6). Een handtekening over een ander bericht zegt alleen iets als beide partijen dat bericht hebben afgesproken.
- **Sleutelwissel en intrekking.** Maak een nieuw Ed25519-sleutelpaar, publiceer de nieuwe openbare sleutel in de DNS- of well-known-assertie, onderteken het record opnieuw met de nieuwe privésleutel en zet `public_key` op dezelfde `p`. Houd rekening met DNS-cache en propagatie. Alleen `p` verwijderen is geen geldige intrekking zolang de ABIZ 1.1-assertie blijft staan: om haar in te trekken, verwijdert u de volledige verklaring. ABIZ 1.1 publiceert geen ingetrokken sleutels (een eigenschap `retired_keys` wordt afgewezen).
- **Wat een sleutel bewijst.** Hij laat zien welke sleutel de beheerder van het domein heeft gepubliceerd. Hij ondertekent het TXT-record niet zelf en bewijst geen juridische identiteit. Gebruik DNSSEC als uw DNS-aanbieder dat ondersteunt.

## 5. Wat AI-tools te zien krijgen

Compatibele software die uw record leest, kan vragen beantwoorden zoals:

- ‘Is Bakkerij Paramaribo op zaterdag open?’
- ‘Wat verkoopt Bakkerij Paramaribo?’
- ‘Wat is de officiële website van Bakkerij Paramaribo?’
- ‘Heeft Bakkerij Paramaribo een KKF-nummer gepubliceerd?’

Ook kan zij melden dat domein en record naar elkaar verwijzen, dat het record aan het schema voldoet en of er een geldige `p`-sleutel is gepubliceerd.

**Grenzen.** Een ABIZ-record is geen bewijs van wettelijke inschrijving. Een tool mag een bedrijf alleen als ‘bevestigd in het register’ omschrijven als zij het officiële register apart heeft gecontroleerd en dat ook zo vermeldt. ABIZ is geen aanbeveling, geen kwaliteitskeurmerk en geen belofte van zichtbaarheid in een AI-dienst.

## 6. Praktische lokale informatie

**Inschrijvingsnummer.** Het nummer staat op het uittreksel uit het Handelsregister van de [KKF](https://www.kkf.sr/). Het Handelsregister is openbaar.

**Het TXT-record toevoegen.** Log in waar de DNS van uw domein wordt beheerd: meestal bij de partij waar u het domein hebt geregistreerd, of bij uw webhost. Voeg een record van het type TXT toe met de naam `_abiz` (sommige panelen vragen de volledige naam, `_abiz.bakkerijparamaribo.example`), plak de waarde zonder aanhalingstekens en stel, als het kan, de TTL in op 300 seconden.

**Privacy.** Het record en de TXT-waarde zijn openbaar. Publiceer alleen gegevens die openbaar mogen zijn. Een eenmanszaak publiceert beter geen woonadres of privételefoonnummer; laat een veld liever weg dan het als privé te markeren (sectie 4.3). Ga na welke regels voor persoonsgegevens gelden voordat u gegevens over personen publiceert.

## 7. Meer lezen

- [ABIZ-specificatie](../../../SPEC.md) (Engels): sectie 3.1.1 (TXT-syntaxis), sectie 3.3 (`p`-sleutels), sectie 4.2 (bedrijfssleutels)
- [JSON Schema van het record](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Referentievalidator](../../../scripts/validate.py) en [voorbeelden](../../../examples/)
- [Alle gidsen voor Zuid-Amerika](index.md)
