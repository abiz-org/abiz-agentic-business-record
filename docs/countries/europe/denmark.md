# Bliv en agentisk virksomhed med ABIZ i Danmark

*En vejledning i den offentliggjorte specifikation ABIZ 1.1. [Specifikationen (SPEC.md, på engelsk)](../../../SPEC.md) er gældende: hvis vejledningen og specifikationen er uenige, gælder specifikationen.*

## 1. Hvad det betyder for en virksomhed i Danmark

Flere og flere spørger AI-assistenter om virksomheder: hvem de er, hvad de tilbyder, og hvor de findes. Med ABIZ (Agentic Business Record) offentliggør en virksomhed én åben, maskinlæsbar post med sine egne oplysninger, fx navn, land, website, ydelser og åbningstider, og på sit eget domæne en DNS-post, der peger på den.

Kun virksomheden, eller nogen der handler på dens vegne, kan ændre DNS for dens domæne. Kompatibel software kan derfor finde posten ud fra domænet og kontrollere, at domæne og post peger på hinanden, i stedet for at stykke oplysninger sammen fra spredte websider. ABIZ er åbent og uafhængigt af udbydere: Der kræves hverken medlemskab, gebyrer eller en bestemt udbyder.

## 2. Sådan offentliggør I en ABIZ-post

### Obligatoriske felter

Virksomhedsposten er et JSON-dokument, der skal overholde det [normative skema](../../../schemas/abiz-business-record-v1.1.schema.json). Fem felter er obligatoriske:

| Felt | Eksempel | Bemærkning |
| --- | --- | --- |
| `record_version` | `abiz1` | Altid denne værdi |
| `business_name` | `Fiskehuset Holm ApS` | Det offentlige navn, normalt som i registret, med selskabsform hvis I bruger den |
| `country` | `dk` | Landekode efter ISO 3166-1 alpha-2; kanonisk form er små bogstaver |
| `identity_host` | `fiskehusetholm.dk.to.co` | Præcis DNS-værdien `h`: et værtsnavn med valgfri sti, uden `https://` |
| `domains` | `["fiskehusetholm.example"]` | De domæner, posten gælder, inklusive domænet med `_abiz` |

### Frivillig virksomhedsnøgle `k`

`k` er frivillig for alle virksomheder, registrerede eller ej. Hvis I offentliggør `k`, skal posten også indeholde `business_key` og `registration_number`, og `k` skal være lig med `business_key`.

I Danmark er nøglen `dk-` efterfulgt af registreringsnummeret, uden regionsdel: en nøgle med en mellemdel, fx `dk-xx-…`, er ugyldig.

- **Register:** Det Centrale Virksomhedsregister (CVR) hos Erhvervsstyrelsen, tilgængeligt via [Virk](https://www.virk.dk/)
- **Nummer:** CVR-nummeret, 8 cifre. Ikke P-nummeret (produktionsenhed) og ikke momsnummeret med præfikset `DK`
- **Skrivemåde:** tag udgangspunkt i nummeret, som registret udsteder det, anvend Unicode-normalisering NFKC, fjern mellemrum, `-`, `.`, `/` og andre bindestreger, og skriv bogstaver med versaler. Foranstillede nuller og bogstavpræfikser bevares. Resultatet må kun indeholde ASCII-bogstaver og -cifre.

Eksempel (opdigtet nummer): `12 34 56 78` bliver til `12345678`. Posten indeholder så `"registration_number": "12345678"` og `"business_key": "dk-12345678"`, og i DNS står `k=dk-12345678`.

Nøgler sammenlignes uden forskel på store og små bogstaver, men offentliggør den kanoniske form: landekode med små bogstaver, nummer med store.

### DNS TXT-post

Offentliggør præcis én ABIZ TXT-post under `_abiz` på jeres domæne, i kompakt form uden mellemrum:

```dns
_abiz.fiskehusetholm.example. 300 IN TXT "v=abiz1;k=dk-12345678;h=fiskehusetholm.dk.to.co;p=aspCxrnYr9RiTS7T/cVsOjbL87o1Qy7Nr0VZzsddZLA="
```

- `v=abiz1` skal stå først. `h` og `p` er obligatoriske; `k` er frivillig.
- Tagnavne skrives med små bogstaver og skelner mellem store og små bogstaver. Intet tag må forekomme to gange.
- En TTL på 300 sekunder anbefales.

`p`-værdien ovenfor er en engangsnøgle til eksemplet. Kopiér den aldrig: offentliggør jeres egen nøgle. En ABIZ 1.1-påstand skal indeholde `p`.

### Virksomhedspost (JSON)

Posten, der leveres på `https://fiskehusetholm.dk.to.co` som `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Fiskehuset Holm ApS",
  "country": "dk",
  "business_key": "dk-12345678",
  "registration_number": "12345678",
  "identity_host": "fiskehusetholm.dk.to.co",
  "domains": [
    "fiskehusetholm.example"
  ],
  "public_key": "aspCxrnYr9RiTS7T/cVsOjbL87o1Qy7Nr0VZzsddZLA=",
  "description": "Fiskehandel i Aarhus.",
  "website": "https://fiskehusetholm.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Aarhus",
        "country": {
          "code": "DK"
        }
      },
      "public": true
    }
  ],
  "signature": "/Y9vJkI8MGhCM0fRksIdaihskxrXsE4KDiYD2IecIAD9pBxC56Q/f6Y/EpUOeulqlJa0u1rFKslXgHd7c9ylAQ=="
}
```

Med referencevalidatoren kan I kontrollere posten og DNS-værdien lokalt:

```sh
python scripts/validate.py record.json --domain fiskehusetholm.example --dns-value 'v=abiz1;k=dk-12345678;h=fiskehusetholm.dk.to.co;p=aspCxrnYr9RiTS7T/cVsOjbL87o1Qy7Nr0VZzsddZLA='
```

### Selv eller via en udbyder

I kan selv levere posten fra enhver HTTPS-vært, I kontrollerer, eller bruge en hvilken som helst kompatibel udbyder. ABIZ kræver ingen bestemt udbyder eller navngivning af værtsnavne. Posten skal altid leveres over HTTPS, og I skal kontrollere domænet med `_abiz`.

## 3. Udbydere og MCP

MCP (Model Context Protocol) er en åben protokol, som lader AI-assistenter kalde værktøjer og læse data fra eksterne servere. En udbyder kan drive en MCP-server, hvor en assistent henter jeres offentlige post direkte. Serveren kan angives i det frivillige felt `mcp_server_url`. ABIZ kræver ingen MCP-server, og et værktøj bør ikke kalde den automatisk, bare fordi den står i en post.

Et eksempel: en udbyder offentliggør jeres post på `fiskehusetholm.dk.to.co` og driver en MCP-server. En assistent, der er forbundet til serveren, kan så spørge om åbningstider eller ydelser hos Fiskehuset Holm ApS og få oplysningerne fra jeres post i stedet for at gætte.

## 4. Nøgler og signaturer (ABIZ 1.1)

ABIZ 1.1 kræver en offentlig Ed25519-nøgle i DNS-tagget `p`. `v` og `h` er obligatoriske. `p` er obligatorisk. `k` er frivillig. `p` skal være 32 rå byte i standard-base64: 44 tegn, der slutter med præcis ét `=`, i én DNS-streng. Base64url accepteres ikke. Alle andre værdier, fx en hexadecimal streng, gør hele posten ugyldig.

Den tilhørende private nøgle tilhører virksomheden og offentliggøres aldrig. Opbevarer en udbyder den for jer, skal I kunne eksportere den. Software kan kontrollere en signatur, der er lavet med den private nøgle, mod nøglen i DNS. Signaturen dækker den RFC 8785-kanoniske form af posten uden medlemmet `signature` og kontrolleres med `public_key`, som skal være lig med `p` (SPEC afsnit 4.6).

For at skifte nøgle genererer I et nyt Ed25519-nøglepar, offentliggør den nye offentlige nøgle i DNS- eller well-known-påstanden, underskriver posten igen med den nye private nøgle og sætter `public_key` til samme `p`. Tag højde for DNS-cache. At fjerne kun `p` er ikke en gyldig tilbagekaldelse, så længe ABIZ 1.1-påstanden bliver stående: for at trække den tilbage fjerner I hele erklæringen. Udfasede nøgler offentliggøres ikke i ABIZ 1.1, hverken i DNS eller i posten. Nøglen viser, hvilken nøgle domænets indehaver har offentliggjort; den beviser ikke juridisk identitet.

## 5. Hvad AI-værktøjer ser

Med en gyldig post kan en kompatibel assistent svare på spørgsmål som:

- »Er Fiskehuset Holm ApS en virksomhed i Aarhus?«
- »Hvad tilbyder Fiskehuset Holm ApS, og hvornår har de åbent?«
- »Er fiskehusetholm.example det officielle website for Fiskehuset Holm ApS?«
- »Hvilket CVR-nummer oplyser Fiskehuset Holm ApS?«

Begrænsningerne er vigtige. ABIZ viser, at et domæne og en post peger på hinanden. Det beviser ikke, at virksomheden er lovligt registreret, at et registreringsnummer er ægte, eller at nogen anbefaler virksomheden. Et værktøj, der ikke selv har slået op i CVR, bør ikke præsentere virksomheden som verificeret. ABIZ garanterer ikke, at en AI-tjeneste finder, rangerer eller anbefaler en virksomhed.

## 6. Praktiske råd

### Hvor I finder nummeret

CVR-nummeret står på fakturaer, på jeres website og i registreringsbeviset og kan slås op via [Virk](https://www.virk.dk/). Også enkeltmandsvirksomheder har et CVR-nummer og kan bruge nøglen, men bør ikke offentliggøre deres privatadresse.

### Tilføj TXT-posten

Tilføj posten dér, hvor domænets DNS administreres, typisk hos jeres registrator eller webhotel. Registret for `.dk`-domæner er [Punktum dk](https://punktum.dk/), men TXT-posten oprettes hos jeres registrator eller DNS-udbyder; alle, der understøtter TXT-poster, kan bruges. Opret en post af typen TXT med navnet `_abiz` (nogle kontrolpaneler vil have hele navnet, `_abiz.fiskehusetholm.example`), værdien præcis som ovenfor og TTL 300. Sæt ikke mellemrum ind i værdien, og slet ældre ABIZ-poster, så der kun er én tilbage.

### Privatliv og offentliggørelse

GDPR (databeskyttelsesforordningen) gælder for personoplysninger i posten, fx navnet på en enkeltmandsvirksomheds ejer eller en kontaktperson. [Det Europæiske Databeskyttelsesråd](https://www.edpb.europa.eu/) henviser til de nationale tilsynsmyndigheder; i Danmark er det Datatilsynet. Alt i en ABIZ-post er offentligt; offentliggør kun oplysninger, der må være offentlige. En enkeltmandsvirksomhed bør ikke offentliggøre sin private adresse: Specifikationen kræver, at private adresser udelades, ikke markeres som private. En generel adresse som `info@` er bedre end en personlig e-mailadresse.

## 7. Læs mere

- [ABIZ-specifikationen (SPEC.md, på engelsk)](../../../SPEC.md): DNS-syntaks (afsnit 3.1.1), nøglen `p` (afsnit 3.3), virksomhedsnøgler (afsnit 4.2)
- [Normativt JSON-skema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Referencevalidator, scripts/validate.py](../../../scripts/validate.py)
- [Alle vejledninger for Europa](index.md)
