# Bli ett agentiskt företag med ABIZ i Sverige

*En guide till ABIZ 1.1 (förslag). [Specifikationen (SPEC.md, på engelska)](../../../SPEC.md) gäller: om guiden och specifikationen skiljer sig åt gäller specifikationen.*

## 1. Vad det betyder för ett företag i Sverige

Allt fler frågar AI-assistenter om företag: vilka de är, vad de erbjuder och var de finns. Med ABIZ (Agentic Business Record) publicerar ett företag en öppen, maskinläsbar post med sina egna uppgifter, till exempel namn, land, webbplats, tjänster och öppettider, och på sin egen domän en DNS-post som pekar på den.

Bara företaget, eller någon som agerar för det, kan ändra DNS för dess domän. Kompatibel programvara kan därför hitta posten utifrån domänen och kontrollera att domän och post pekar på varandra, i stället för att pussla ihop uppgifter från spridda webbsidor. ABIZ är öppet och leverantörsoberoende: inget medlemskap, inga avgifter och ingen särskild leverantör krävs.

## 2. Så publicerar ni en ABIZ-post

### Obligatoriska fält

Företagsposten är ett JSON-dokument som måste följa det [normativa schemat](../../../schemas/abiz-business-record-v1.schema.json). Fem fält är obligatoriska:

| Fält | Exempel | Kommentar |
| --- | --- | --- |
| `record-version` | `abiz1` | Alltid detta värde |
| `business-name` | `Norrland Snickeri AB` | Det offentliga namnet, oftast som i registret, med bolagsform om ni använder den |
| `country` | `se` | Landskod enligt ISO 3166-1 alpha-2; kanonisk form är gemener |
| `identity-host` | `norrlandsnickeri.se.to.co` | Exakt DNS-värdet `h`: ett värdnamn med valfri sökväg, utan `https://` |
| `domains` | `["norrlandsnickeri.example"]` | Domänerna som posten gäller, inklusive domänen med `_abiz` |

### Frivillig företagsnyckel `k`

`k` är frivilligt för alla företag, registrerade eller inte. Om ni publicerar `k` måste posten också innehålla `business-key` och `registration-number`, och `k` måste vara lika med `business-key`.

I Sverige är nyckeln `se-` följt av registreringsnumret, utan regionsdel: en nyckel med en mittdel, till exempel `se-xx-…`, är ogiltig.

- **Register:** [Bolagsverket](https://bolagsverket.se/) (aktiebolagsregistret och handelsregistret)
- **Nummer att använda:** organisationsnumret, 10 siffror, skrivet som `556123-4567`. Inte momsregistreringsnumret (`SE…01`)
- **Skrivsätt:** utgå från numret så som registret anger det, tillämpa Unicode-normalisering NFKC, ta bort mellanslag, `-`, `.`, `/` och andra streck och skriv bokstäver med versaler. Inledande nollor och bokstavsprefix behålls. Resultatet får bara innehålla ASCII-bokstäver och siffror.

Exempel (påhittat nummer): `556123-4567` blir `5561234567`. Posten innehåller då `"registration-number": "5561234567"` och `"business-key": "se-5561234567"`, och i DNS står `k=se-5561234567`.

Nycklar jämförs utan hänsyn till versaler och gemener, men publicera den kanoniska formen: landskod med gemener, nummer med versaler.

### DNS TXT-post

Publicera exakt en ABIZ TXT-post under `_abiz` på er domän, i kompakt form utan mellanslag:

```dns
_abiz.norrlandsnickeri.example. 300 IN TXT "v=abiz1;k=se-5561234567;h=norrlandsnickeri.se.to.co;p=1O7oNocedjwUazsaPPTuF8pGzgzqUWAgy7s8Xr2WF7w="
```

- `v=abiz1` måste stå först. `h` är obligatoriskt; `k` och `p` är frivilliga.
- Taggnamn skrivs med gemener och är skiftlägeskänsliga. Ingen tagg får förekomma två gånger.
- En TTL på 300 sekunder rekommenderas.

`p`-värdet ovan är en engångsnyckel för exemplet. Kopiera den aldrig: publicera er egen nyckel eller utelämna `p`.

### Företagspost (JSON)

Posten som levereras på `https://norrlandsnickeri.se.to.co` som `application/json`:

```json
{
  "record-version": "abiz1",
  "business-name": "Norrland Snickeri AB",
  "country": "se",
  "business-key": "se-5561234567",
  "registration-number": "5561234567",
  "identity-host": "norrlandsnickeri.se.to.co",
  "domains": [
    "norrlandsnickeri.example"
  ],
  "description": "Snickeri i Umeå.",
  "website": "https://norrlandsnickeri.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Umeå",
      "country": "se",
      "public": true
    }
  ]
}
```

Med referensvalideraren kan ni kontrollera posten och DNS-värdet lokalt:

```sh
python scripts/validate.py record.json --domain norrlandsnickeri.example --dns-value 'v=abiz1;k=se-5561234567;h=norrlandsnickeri.se.to.co;p=1O7oNocedjwUazsaPPTuF8pGzgzqUWAgy7s8Xr2WF7w='
```

### Egen drift eller via leverantör

Ni kan själva leverera posten från valfri HTTPS-värd som ni kontrollerar, eller använda valfri kompatibel leverantör. ABIZ kräver ingen viss leverantör eller namnstruktur för värdnamn. Posten måste alltid levereras över HTTPS, och ni måste kontrollera domänen med `_abiz`.

## 3. Leverantörer och MCP

MCP (Model Context Protocol) är ett öppet protokoll som låter AI-assistenter anropa verktyg och läsa data från externa servrar. En leverantör kan driva en MCP-server där en assistent hämtar er offentliga post direkt. Servern kan anges i det frivilliga fältet `mcp-server-url`. ABIZ kräver ingen MCP-server, och ett verktyg bör inte anropa den automatiskt bara för att den står i en post.

Ett exempel: en leverantör publicerar er post på `norrlandsnickeri.se.to.co` och driver en MCP-server. En assistent som är ansluten till servern kan då fråga efter öppettider eller tjänster hos Norrland Snickeri AB och få uppgifterna från er post i stället för att gissa. to.co, en av dessa leverantörer, förklarar ABIZ på en [svenskspråkig sida](https://to.co/sv-se/abiz).

## 4. Nycklar och signaturer (ABIZ 1.1)

ABIZ 1.1 låter ett företag publicera en publik Ed25519-nyckel i DNS-taggen `p`. `p` är frivilligt. Finns taggen måste värdet vara standard-base64 av nyckeln på 32 byte: 44 tecken som slutar med exakt ett `=`, i en enda DNS-sträng. Alla andra värden, till exempel en hexadecimal ABIZ 1.0-token eller en base64url-nyckel, gör hela posten ogiltig.

Den tillhörande privata nyckeln tillhör företaget och publiceras aldrig. Förvarar en leverantör den åt er måste ni kunna exportera den. Programvara kan kontrollera en signatur som gjorts med den privata nyckeln mot nyckeln i DNS. Vilka byte en signatur över företagsposten omfattar definierar ABIZ 1.1 ännu inte.

För att byta nyckel publicerar ni en ny i `p`; för att återkalla den tar ni bort `p`. Pensionerade nycklar publiceras inte i ABIZ 1.1, varken i DNS eller i posten. Nyckeln visar vilken nyckel domänens innehavare har publicerat; den bevisar inte juridisk identitet.

## 5. Vad AI-verktyg ser

Med en giltig post kan en kompatibel assistent svara på frågor som:

- ”Är Norrland Snickeri AB ett företag i Umeå?”
- ”Vad erbjuder Norrland Snickeri AB, och när har de öppet?”
- ”Är norrlandsnickeri.example den officiella webbplatsen för Norrland Snickeri AB?”
- ”Vilket registreringsnummer uppger Norrland Snickeri AB?”

Begränsningarna är viktiga. ABIZ visar att en domän och en post pekar på varandra. Det bevisar inte att företaget är lagligt registrerat, att ett registreringsnummer är äkta eller att någon rekommenderar företaget. Ett verktyg som inte självt har kontrollerat Bolagsverkets register bör inte presentera företaget som verifierat. ABIZ garanterar inte att någon AI-tjänst hittar, rangordnar eller rekommenderar ett företag.

## 6. Praktiska tips

### Var ni hittar numret

Organisationsnumret står på registreringsbeviset, på fakturor och på webbplatsen och kan sökas hos [Bolagsverket](https://bolagsverket.se/). En enskild näringsidkares organisationsnummer är personnumret: publicera då inte nyckeln, eftersom den identifierar en person.

### Lägga till TXT-posten

Lägg till posten där domänens DNS hanteras, oftast hos domänregistraren eller webbhotellet. Registret för `.se`-domäner är [Internetstiftelsen](https://internetstiftelsen.se/), men TXT-posten läggs till hos er registrar eller DNS-leverantör; alla som stöder TXT-poster fungerar. Skapa en post av typen TXT med namnet `_abiz` (vissa kontrollpaneler vill ha hela namnet, `_abiz.norrlandsnickeri.example`), värdet exakt som ovan och TTL 300. Lägg inte in mellanslag i värdet, och ta bort äldre ABIZ-poster så att bara en finns kvar.

### Integritet och publicering

GDPR gäller personuppgifter i posten, till exempel namnet på en enskild näringsidkare eller en kontaktperson. [Europeiska dataskyddsstyrelsen](https://www.edpb.europa.eu/) hänvisar till de nationella tillsynsmyndigheterna; i Sverige är det Integritetsskyddsmyndigheten (IMY). Allt i en ABIZ-post är offentligt; publicera bara uppgifter som får vara offentliga. En enskild näringsidkare bör inte publicera sin hemadress: specifikationen kräver att privata adresser utelämnas, inte markeras som privata. En allmän adress som `info@` är bättre än en personlig e-postadress.

## 7. Läs mer

- [ABIZ-specifikationen (SPEC.md, på engelska)](../../../SPEC.md): DNS-syntax (avsnitt 3.1.1), nyckeln `p` (avsnitt 3.3), företagsnycklar (avsnitt 4.2)
- [Normativt JSON-schema](../../../schemas/abiz-business-record-v1.schema.json)
- [Referensvalidator, scripts/validate.py](../../../scripts/validate.py)
- [Alla guider för Europa](index.md)
