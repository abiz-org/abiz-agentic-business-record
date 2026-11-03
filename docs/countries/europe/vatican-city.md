# Diventare un'impresa agentica con ABIZ nella Città del Vaticano

*Una guida ad ABIZ 1.1 (proposta). Il testo di riferimento è la [specifica (SPEC.md, in inglese)](../../../SPEC.md): se questa guida e la specifica non coincidono, vale la specifica.*

## 1. Che cosa significa per un'impresa nella Città del Vaticano

Sempre più persone chiedono agli assistenti di IA informazioni sulle imprese: chi sono, che cosa offrono, dove trovarle. Con ABIZ (Agentic Business Record) un'impresa pubblica una scheda pubblica e leggibile dalle macchine con i propri dati, come nome, paese, sito web, servizi e orari, e sul proprio dominio un record DNS che rimanda a quella scheda.

Solo l'impresa, o chi agisce per suo conto, può modificare il DNS del suo dominio. Un software compatibile può quindi trovare la scheda partendo dal dominio e verificare che dominio e scheda si richiamino a vicenda, invece di ricostruire i dati da pagine web sparse. ABIZ è aperto e indipendente dai fornitori: non servono iscrizioni, costi o un fornitore particolare.

## 2. Come pubblicare una scheda ABIZ

### Campi obbligatori

La scheda dell'impresa è un documento JSON che deve rispettare lo [schema normativo](../../../schemas/abiz-business-record-v1.schema.json). I campi obbligatori sono cinque:

| Campo | Esempio | Note |
| --- | --- | --- |
| `record_version` | `abiz1` | Sempre questo valore |
| `business_name` | `Libreria del Borgo` | Il nome pubblico, di solito come risulta dal registro, con la forma giuridica se la usate |
| `country` | `va` | Codice paese ISO 3166-1 alpha-2; la forma canonica è in minuscolo |
| `identity_host` | `www.libreriadelborgo.example/abiz.json` | Esattamente il valore DNS `h`: un nome host con percorso facoltativo, senza `https://` |
| `domains` | `["libreriadelborgo.example"]` | I domini rivendicati dalla scheda, compreso quello che contiene `_abiz` |

### Chiave d'impresa `k` (facoltativa)

`k` è facoltativa per ogni impresa; una scheda senza `k` è pienamente valida.

Nella Città del Vaticano non esiste un registro pubblico nazionale delle imprese da cui ricavare un numero di iscrizione: le attività economiche sono svolte in gran parte da enti della Santa Sede e del Governatorato. Non c'è quindi un numero da cui ricavare una chiave ABIZ. Omettete `k`, `business_key` e `registration_number`; il codice paese `va` è comunque valido per il campo `country`.

### Record DNS TXT

Pubblicate un solo record TXT ABIZ in `_abiz` sul vostro dominio, nella forma compatta senza spazi:

```dns
_abiz.libreriadelborgo.example. 300 IN TXT "v=abiz1;h=www.libreriadelborgo.example/abiz.json;p=MrwcHkVFm/CET4gGNBY+rz9bpRGUQrpGYQzQf7zcu+o="
```

- `v=abiz1` deve venire per primo. `h` è obbligatorio; `k` e `p` sono facoltativi.
- I nomi dei tag sono in minuscolo e distinguono maiuscole e minuscole. Nessun tag può comparire due volte.
- Si raccomanda un TTL di 300 secondi.

Il valore `p` qui sopra è una chiave d'esempio usa e getta. Non copiatelo mai: pubblicate la vostra chiave oppure omettete `p`.

### Scheda dell'impresa (JSON)

La scheda servita all'indirizzo `https://www.libreriadelborgo.example/abiz.json` come `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Libreria del Borgo",
  "country": "va",
  "identity_host": "www.libreriadelborgo.example/abiz.json",
  "domains": [
    "libreriadelborgo.example"
  ],
  "public_key": "MrwcHkVFm/CET4gGNBY+rz9bpRGUQrpGYQzQf7zcu+o=",
  "description": "Libreria nella Città del Vaticano.",
  "website": "https://libreriadelborgo.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Città del Vaticano",
        "country": {
          "code": "VA"
        }
      },
      "public": true
    }
  ],
  "signature": "Djo3OE7peBFn+O+jG6jO1FasDPKJSGrE2E7Idvv6XGMInWlWFkqAlqx6q8yEESg1p5c0g9xB+NdElIocgwHFBw=="
}
```

Con il validatore di riferimento potete controllare in locale la scheda e il valore DNS:

```sh
python scripts/validate.py record.json --domain libreriadelborgo.example --dns-value 'v=abiz1;h=www.libreriadelborgo.example/abiz.json;p=MrwcHkVFm/CET4gGNBY+rz9bpRGUQrpGYQzQf7zcu+o='
```

### In proprio o tramite un fornitore

Potete pubblicare la scheda voi stessi su qualsiasi host HTTPS che controllate, oppure usare un qualsiasi fornitore compatibile. ABIZ non impone fornitori né schemi per i nomi host. In ogni caso la scheda deve essere servita in HTTPS e dovete controllare il dominio che contiene `_abiz`.

## 3. Fornitori e MCP

MCP (Model Context Protocol) è un protocollo aperto con cui gli assistenti di IA richiamano strumenti e leggono dati da server esterni. Un fornitore può gestire un server MCP tramite il quale un assistente ottiene direttamente la vostra scheda pubblica. Potete indicarlo nel campo facoltativo `mcp_server_url`. ABIZ non richiede un server MCP, e uno strumento non dovrebbe richiamarlo automaticamente solo perché compare in una scheda.

Per esempio, se pubblicate voi stessi la scheda all'indirizzo `www.libreriadelborgo.example/abiz.json`, qualsiasi strumento o server MCP compatibile può leggerla come una scheda ospitata da un fornitore.

## 4. Chiavi e firme (ABIZ 1.1)

ABIZ 1.1 consente di pubblicare una chiave pubblica Ed25519 nel tag DNS `p`. `p` è facoltativo. Se presente, deve essere la codifica base64 standard della chiave di 32 byte: 44 caratteri che terminano con un solo `=`, in un'unica stringa DNS. Qualsiasi altro valore, come un token esadecimale di ABIZ 1.0 o una chiave base64url, rende non valido l'intero record.

La chiave privata corrispondente appartiene all'impresa e non viene mai pubblicata. Un fornitore che la custodisce per voi deve permettervi di esportarla. Un software può verificare una firma creata con la chiave privata usando la chiave pubblicata nel DNS. ABIZ 1.1 non stabilisce ancora quali byte copra una firma della scheda.

Per cambiare chiave pubblicatene una nuova in `p`; per revocarla eliminate `p`. In ABIZ 1.1 le chiavi ritirate non vengono pubblicate, né nel DNS né nella scheda. La chiave mostra quale chiave ha pubblicato chi controlla il dominio; non prova l'identità giuridica.

## 5. Che cosa vedono gli strumenti di IA

Con una scheda valida, un assistente compatibile può rispondere a domande come:

- «Libreria del Borgo è un'impresa di Città del Vaticano?»
- «Che cosa offre Libreria del Borgo e quali sono gli orari?»
- «libreriadelborgo.example è il sito ufficiale di Libreria del Borgo?»

I limiti contano. ABIZ mostra che un dominio e una scheda si richiamano a vicenda. Non prova che un'impresa sia iscritta legalmente, che un numero di iscrizione sia autentico né che qualcuno la raccomandi. Uno strumento che non ha consultato direttamente una fonte ufficiale non deve presentare l'impresa come verificata. ABIZ non garantisce che un servizio di IA trovi, classifichi o raccomandi un'impresa.

## 6. Note pratiche

### Trovare il numero di iscrizione

Non c'è un numero di registro nazionale da indicare. Le informazioni ufficiali sullo Stato sono pubblicate dal [Governatorato](https://www.vaticanstate.va/).

### Aggiungere il record TXT

Aggiungete il record dove si gestisce il DNS del vostro dominio, di solito presso il registrar o il fornitore di hosting. Il dominio `.va` non è aperto alla registrazione pubblica: usate un dominio che controllate presso qualsiasi registrar o fornitore DNS che supporti i record TXT. Create un record di tipo TXT con nome `_abiz` (alcuni pannelli vogliono il nome completo, `_abiz.libreriadelborgo.example`), il valore esattamente come sopra e un TTL di 300. Non inserite spazi nel valore ed eliminate eventuali record ABIZ precedenti, in modo che ne resti uno solo.

### Privacy e pubblicazione dei dati

Valutate le norme vaticane applicabili ai dati personali della scheda; se servite persone nell'Unione europea, può applicarsi anche il GDPR. Tutto ciò che è in una scheda ABIZ è pubblico: pubblicate solo dati destinati a esserlo. Un imprenditore individuale non dovrebbe pubblicare l'indirizzo di casa: la specifica richiede di omettere gli indirizzi privati, non di contrassegnarli come privati. Un indirizzo generico come `info@` è preferibile a un indirizzo email personale.

## 7. Per approfondire

- [Specifica ABIZ (SPEC.md, in inglese)](../../../SPEC.md): sintassi DNS (sezione 3.1.1), chiave `p` (sezione 3.3), chiavi d'impresa (sezione 4.2)
- [Schema JSON normativo](../../../schemas/abiz-business-record-v1.schema.json)
- [Validatore di riferimento, scripts/validate.py](../../../scripts/validate.py)
- [Tutte le guide per l'Europa](index.md)
