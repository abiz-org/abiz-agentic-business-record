# Bli en agentisk virksomhet med ABIZ i Norge

*En veiledning til den publiserte spesifikasjonen ABIZ 1.1. [Spesifikasjonen (SPEC.md, på engelsk)](../../../SPEC.md) gjelder: hvis veiledningen og spesifikasjonen er uenige, gjelder spesifikasjonen.* Veiledningen er på bokmål.

## 1. Hva dette betyr for en virksomhet i Norge

Stadig flere spør KI-assistenter om virksomheter: hvem de er, hva de tilbyr og hvor de finnes. Med ABIZ (Agentic Business Record) publiserer en virksomhet én åpen, maskinlesbar post med egne opplysninger, for eksempel navn, land, nettsted, tjenester og åpningstider, og på sitt eget domene en DNS-post som peker til den.

Bare virksomheten, eller noen som handler på dens vegne, kan endre DNS for domenet. Kompatibel programvare kan derfor finne posten ut fra domenet og kontrollere at domene og post peker på hverandre, i stedet for å sette sammen opplysninger fra spredte nettsider. ABIZ er åpent og leverandøruavhengig: Det kreves verken medlemskap, gebyrer eller en bestemt leverandør.

## 2. Slik publiserer dere en ABIZ-post

### Obligatoriske felt

Virksomhetsposten er et JSON-dokument som må følge det [normative skjemaet](../../../schemas/abiz-business-record-v1.1.schema.json). Fem felt er obligatoriske:

| Felt | Eksempel | Merknad |
| --- | --- | --- |
| `record_version` | `abiz1` | Alltid denne verdien |
| `business_name` | `Nordlys Fisk AS` | Det offentlige navnet, vanligvis som i registeret, med selskapsform hvis dere bruker den |
| `country` | `no` | Landkode etter ISO 3166-1 alpha-2; kanonisk form er små bokstaver |
| `identity_host` | `nordlysfisk.no.to.co` | Nøyaktig DNS-verdien `h`: et vertsnavn med valgfri sti, uten `https://` |
| `domains` | `["nordlysfisk.example"]` | Domenene posten gjelder, inkludert domenet med `_abiz` |

### Valgfri virksomhetsnøkkel `k`

`k` er valgfri for alle virksomheter, registrerte eller ikke. Hvis dere publiserer `k`, må posten også inneholde `business_key` og `registration_number`, og `k` må være lik `business_key`.

I Norge er nøkkelen `no-` etterfulgt av registreringsnummeret, uten regionsdel: en nøkkel med en mellomdel, for eksempel `no-xx-…`, er ugyldig.

- **Register:** Enhetsregisteret hos [Brønnøysundregistrene](https://www.brreg.no/)
- **Nummer:** organisasjonsnummeret, 9 sifre. Ikke MVA-nummeret (`NO … MVA`)
- **Skrivemåte:** ta utgangspunkt i nummeret slik registeret tildeler det, bruk Unicode-normalisering NFKC, fjern mellomrom, `-`, `.`, `/` og andre bindestreker, og skriv bokstaver som store bokstaver. Innledende nuller og bokstavprefikser beholdes. Resultatet kan bare inneholde ASCII-bokstaver og -sifre.

Eksempel (oppdiktet nummer): `123 456 789` blir `123456789`. Posten inneholder da `"registration_number": "123456789"` og `"business_key": "no-123456789"`, og i DNS står `k=no-123456789`.

Nøkler sammenlignes uten forskjell på store og små bokstaver, men publiser den kanoniske formen: landkode med små bokstaver, nummer med store.

### DNS TXT-post

Publiser nøyaktig én ABIZ TXT-post under `_abiz` på domenet deres, i kompakt form uten mellomrom:

```dns
_abiz.nordlysfisk.example. 300 IN TXT "v=abiz1;k=no-123456789;h=nordlysfisk.no.to.co;p=Wt0P6JI6+3SdOmOHUo9hg9jRWv34mi0FCDLz5bizg2k="
```

- `v=abiz1` må stå først. `h` og `p` er obligatoriske; `k` er valgfri.
- Tagnavn skrives med små bokstaver og skiller mellom store og små bokstaver. Ingen tagg kan forekomme to ganger.
- En TTL på 300 sekunder anbefales.

`p`-verdien ovenfor er en engangsnøkkel for eksempelet. Kopier den aldri: publiser deres egen nøkkel. En ABIZ 1.1-påstand må inneholde `p`.

### Virksomhetspost (JSON)

Posten som leveres på `https://nordlysfisk.no.to.co` som `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Nordlys Fisk AS",
  "country": {
    "code": "NO",
    "name": "Norway"
  },
  "business_key": "no-123456789",
  "registration_number": "123456789",
  "identity_host": "nordlysfisk.no.to.co",
  "domains": [
    "nordlysfisk.example"
  ],
  "public_key": "Wt0P6JI6+3SdOmOHUo9hg9jRWv34mi0FCDLz5bizg2k=",
  "description": "Fiskeforretning i Bergen.",
  "website": "https://nordlysfisk.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Bergen",
        "country": {
          "code": "NO"
        }
      },
      "public": true
    }
  ],
  "signature": "7LB9XzNJTqMtdYGvn5CSgWennXvi4V/P8mbAQAs1QyX+cAG7mKWMxlkLtv5Qr8yPR6+0hXf5MSUcH2PcSUdFBA=="
}
```

Med referansevalidatoren kan dere kontrollere posten og DNS-verdien lokalt:

```sh
python scripts/validate.py record.json --domain nordlysfisk.example --dns-value 'v=abiz1;k=no-123456789;h=nordlysfisk.no.to.co;p=Wt0P6JI6+3SdOmOHUo9hg9jRWv34mi0FCDLz5bizg2k='
```

### Selv eller via en leverandør

Dere kan selv levere posten fra en hvilken som helst HTTPS-vert dere kontrollerer, eller bruke en hvilken som helst kompatibel leverandør. ABIZ krever ingen bestemt leverandør eller navnestruktur for vertsnavn. Posten må alltid leveres over HTTPS, og dere må kontrollere domenet med `_abiz`.

## 3. Leverandører og MCP

MCP (Model Context Protocol) er en åpen protokoll som lar KI-assistenter kalle verktøy og lese data fra eksterne servere. En leverandør kan drifte en MCP-server der en assistent henter den offentlige posten deres direkte. Serveren kan oppgis i det valgfrie feltet `mcp_server_url`. ABIZ krever ingen MCP-server, og et verktøy bør ikke kalle den automatisk bare fordi den står i en post.

Et eksempel: en leverandør publiserer posten deres på `nordlysfisk.no.to.co` og drifter en MCP-server. En assistent som er koblet til serveren, kan da spørre om åpningstider eller tjenester hos Nordlys Fisk AS og få opplysningene fra posten i stedet for å gjette.

## 4. Nøkler og signaturer (ABIZ 1.1)

ABIZ 1.1 krever en offentlig Ed25519-nøkkel i DNS-taggen `p`. `v` og `h` er obligatoriske. `p` er obligatorisk. `k` er valgfri. `p` må være 32 råbyte i standard base64: 44 tegn som slutter med nøyaktig ett `=`, i én DNS-streng. Base64url godtas ikke. Alle andre verdier, for eksempel en heksadesimal streng, gjør hele posten ugyldig.

Den tilhørende private nøkkelen tilhører virksomheten og publiseres aldri. Hvis en leverandør oppbevarer den for dere, må dere kunne eksportere den. Programvare kan kontrollere en signatur laget med den private nøkkelen mot nøkkelen i DNS. Signaturen dekker den RFC 8785-kanoniske formen av posten uten medlemmet `signature` og kontrolleres med `public_key`, som må være lik `p` (SPEC avsnitt 4.6).

For å bytte nøkkel lager dere et nytt Ed25519-nøkkelpar, publiserer den nye offentlige nøkkelen i DNS- eller well-known-påstanden, signerer posten på nytt med den nye private nøkkelen og setter `public_key` til samme `p`. Ta hensyn til DNS-hurtiglager. Å fjerne bare `p` er ikke gyldig tilbakekalling så lenge ABIZ 1.1-påstanden står: for å trekke den tilbake fjerner dere hele erklæringen. Utfasede nøkler publiseres ikke i ABIZ 1.1, verken i DNS eller i posten. Nøkkelen viser hvilken nøkkel domeneinnehaveren har publisert; den beviser ikke juridisk identitet.

## 5. Hva KI-verktøy ser

Med en gyldig post kan en kompatibel assistent svare på spørsmål som:

- «Er Nordlys Fisk AS en virksomhet i Bergen?»
- «Hva tilbyr Nordlys Fisk AS, og når har de åpent?»
- «Er nordlysfisk.example det offisielle nettstedet til Nordlys Fisk AS?»
- «Hvilket organisasjonsnummer oppgir Nordlys Fisk AS?»

Begrensningene er viktige. ABIZ viser at et domene og en post peker på hverandre. Det beviser ikke at virksomheten er lovlig registrert, at et registreringsnummer er ekte, eller at noen anbefaler virksomheten. Et verktøy som ikke selv har sjekket Enhetsregisteret, bør ikke presentere virksomheten som verifisert. ABIZ garanterer ikke at en KI-tjeneste finner, rangerer eller anbefaler en virksomhet.

## 6. Praktiske råd

### Hvor dere finner nummeret

Organisasjonsnummeret står på fakturaer, på nettstedet og i firmaattesten og kan søkes opp hos [Brønnøysundregistrene](https://www.brreg.no/). Også enkeltpersonforetak har organisasjonsnummer og kan bruke nøkkelen, men bør ikke publisere hjemmeadressen.

### Legg til TXT-posten

Legg til posten der domenets DNS administreres, vanligvis hos registraren eller webhotellet. Registeret for `.no`-domener er [Norid](https://www.norid.no/), men TXT-posten legges inn hos registraren eller DNS-leverandøren; alle som støtter TXT-poster, kan brukes. Opprett en post av typen TXT med navnet `_abiz` (noen kontrollpaneler vil ha hele navnet, `_abiz.nordlysfisk.example`), verdien nøyaktig som ovenfor og TTL 300. Ikke legg inn mellomrom i verdien, og slett eldre ABIZ-poster slik at bare én står igjen.

### Personvern og publisering

Personvernforordningen (GDPR) gjelder i Norge gjennom EØS-avtalen og omfatter personopplysninger i posten, for eksempel navnet på innehaveren av et enkeltpersonforetak eller en kontaktperson. Tilsynsmyndigheten er Datatilsynet; [Det europeiske personvernrådet](https://www.edpb.europa.eu/) viser til de nasjonale myndighetene. Alt i en ABIZ-post er offentlig; publiser bare opplysninger som kan være offentlige. Et enkeltpersonforetak bør ikke publisere hjemmeadressen: Spesifikasjonen krever at private adresser utelates, ikke merkes som private. En generell adresse som `post@` er bedre enn en personlig e-postadresse.

## 7. Les mer

- [ABIZ-spesifikasjonen (SPEC.md, på engelsk)](../../../SPEC.md): DNS-syntaks (avsnitt 3.1.1), nøkkelen `p` (avsnitt 3.3), virksomhetsnøkler (avsnitt 4.2)
- [Normativt JSON-skjema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Referansevalidator, scripts/validate.py](../../../scripts/validate.py)
- [Alle veiledninger for Europa](index.md)
