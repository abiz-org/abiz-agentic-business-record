# Diventare un'impresa agentica con ABIZ in Italia

*Una guida ad ABIZ 1.1 (proposta). Il testo di riferimento è la [specifica (SPEC.md, in inglese)](../../../SPEC.md): se questa guida e la specifica non coincidono, vale la specifica.*

## 1. Che cosa significa per un'impresa in Italia

Sempre più persone chiedono agli assistenti di IA informazioni sulle imprese: chi sono, che cosa offrono, dove trovarle. Con ABIZ (Agentic Business Record) un'impresa pubblica una scheda pubblica e leggibile dalle macchine con i propri dati, come nome, paese, sito web, servizi e orari, e sul proprio dominio un record DNS che rimanda a quella scheda.

Solo l'impresa, o chi agisce per suo conto, può modificare il DNS del suo dominio. Un software compatibile può quindi trovare la scheda partendo dal dominio e verificare che dominio e scheda si richiamino a vicenda, invece di ricostruire i dati da pagine web sparse. ABIZ è aperto e indipendente dai fornitori: non servono iscrizioni, costi o un fornitore particolare.

## 2. Come pubblicare una scheda ABIZ

### Campi obbligatori

La scheda dell'impresa è un documento JSON che deve rispettare lo [schema normativo](../../../schemas/abiz-business-record-v1.schema.json). I campi obbligatori sono cinque:

| Campo | Esempio | Note |
| --- | --- | --- |
| `record-version` | `abiz1` | Sempre questo valore |
| `business-name` | `Pasticceria Rossi S.r.l.` | Il nome pubblico, di solito come risulta dal registro, con la forma giuridica se la usate |
| `country` | `it` | Codice paese ISO 3166-1 alpha-2; la forma canonica è in minuscolo |
| `identity-host` | `pasticceriarossi.it.to.co` | Esattamente il valore DNS `h`: un nome host con percorso facoltativo, senza `https://` |
| `domains` | `["pasticceriarossi.example"]` | I domini rivendicati dalla scheda, compreso quello che contiene `_abiz` |

### Chiave d'impresa `k` (facoltativa)

`k` è facoltativa per ogni impresa, iscritta o no. Se la pubblicate, la scheda deve contenere anche `business-key` e `registration-number`, e `k` deve essere uguale a `business-key`.

In Italia la chiave è `it-` seguito dal numero di iscrizione, senza suddivisione territoriale: una chiave con una parte centrale, come `it-xx-…`, non è valida.

- **Registro:** [Registro delle imprese](https://www.registroimprese.it/), tenuto dalle Camere di commercio
- **Numero da usare:** il codice fiscale dell'impresa (11 cifre per le società), che è anche il numero di iscrizione al Registro delle imprese. Non il numero REA, che è attribuito dalla Camera di commercio di ciascuna provincia e quindi non è unico a livello nazionale
- **Come scriverlo:** partite dal numero come lo rilascia il registro, applicate la normalizzazione Unicode NFKC, togliete spazi, `-`, `.`, `/` e gli altri trattini, poi scrivete le lettere in maiuscolo. Zeri iniziali e prefissi in lettere restano. Il risultato deve contenere solo lettere e cifre ASCII.

Esempio (numero inventato): `12345678901` è già in forma canonica. La scheda contiene allora `"registration-number": "12345678901"` e `"business-key": "it-12345678901"`, e nel DNS compare `k=it-12345678901`. Per molte società il codice fiscale coincide con la partita IVA; usate il codice fiscale senza il prefisso `IT`.

Le chiavi si confrontano senza distinguere maiuscole e minuscole, ma pubblicate la forma canonica: codice del paese in minuscolo, numero in maiuscolo.

### Record DNS TXT

Pubblicate un solo record TXT ABIZ in `_abiz` sul vostro dominio, nella forma compatta senza spazi:

```dns
_abiz.pasticceriarossi.example. 300 IN TXT "v=abiz1;k=it-12345678901;h=pasticceriarossi.it.to.co;p=sNpibaetSBfXQQypOYHY4aVjGPnwcS4n5mu4GpluwxA="
```

- `v=abiz1` deve venire per primo. `h` è obbligatorio; `k` e `p` sono facoltativi.
- I nomi dei tag sono in minuscolo e distinguono maiuscole e minuscole. Nessun tag può comparire due volte.
- Si raccomanda un TTL di 300 secondi.

Il valore `p` qui sopra è una chiave d'esempio usa e getta. Non copiatelo mai: pubblicate la vostra chiave oppure omettete `p`.

### Scheda dell'impresa (JSON)

La scheda servita all'indirizzo `https://pasticceriarossi.it.to.co` come `application/json`:

```json
{
  "record-version": "abiz1",
  "business-name": "Pasticceria Rossi S.r.l.",
  "country": "it",
  "business-key": "it-12345678901",
  "registration-number": "12345678901",
  "identity-host": "pasticceriarossi.it.to.co",
  "domains": [
    "pasticceriarossi.example"
  ],
  "description": "Pasticceria artigianale a Bologna.",
  "website": "https://pasticceriarossi.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Bologna",
      "country": "it",
      "public": true
    }
  ]
}
```

Con il validatore di riferimento potete controllare in locale la scheda e il valore DNS:

```sh
python scripts/validate.py record.json --domain pasticceriarossi.example --dns-value 'v=abiz1;k=it-12345678901;h=pasticceriarossi.it.to.co;p=sNpibaetSBfXQQypOYHY4aVjGPnwcS4n5mu4GpluwxA='
```

### In proprio o tramite un fornitore

Potete pubblicare la scheda voi stessi su qualsiasi host HTTPS che controllate, oppure usare un qualsiasi fornitore compatibile. ABIZ non impone fornitori né schemi per i nomi host. In ogni caso la scheda deve essere servita in HTTPS e dovete controllare il dominio che contiene `_abiz`.

## 3. Fornitori e MCP

MCP (Model Context Protocol) è un protocollo aperto con cui gli assistenti di IA richiamano strumenti e leggono dati da server esterni. Un fornitore può gestire un server MCP tramite il quale un assistente ottiene direttamente la vostra scheda pubblica. Potete indicarlo nel campo facoltativo `mcp-server-url`. ABIZ non richiede un server MCP, e uno strumento non dovrebbe richiamarlo automaticamente solo perché compare in una scheda.

Per esempio, un fornitore può pubblicare la vostra scheda all'indirizzo `pasticceriarossi.it.to.co` e gestire un server MCP. Un assistente collegato a quel server può allora chiedere gli orari o i servizi di Pasticceria Rossi S.r.l. e ricevere i dati dalla vostra scheda, invece di tirare a indovinare. to.co, uno di questi fornitori, presenta ABIZ in una [pagina in italiano](https://to.co/it-it/abiz).

## 4. Chiavi e firme (ABIZ 1.1)

ABIZ 1.1 consente di pubblicare una chiave pubblica Ed25519 nel tag DNS `p`. `p` è facoltativo. Se presente, deve essere la codifica base64 standard della chiave di 32 byte: 44 caratteri che terminano con un solo `=`, in un'unica stringa DNS. Qualsiasi altro valore, come un token esadecimale di ABIZ 1.0 o una chiave base64url, rende non valido l'intero record.

La chiave privata corrispondente appartiene all'impresa e non viene mai pubblicata. Un fornitore che la custodisce per voi deve permettervi di esportarla. Un software può verificare una firma creata con la chiave privata usando la chiave pubblicata nel DNS. ABIZ 1.1 non stabilisce ancora quali byte copra una firma della scheda.

Per cambiare chiave pubblicatene una nuova in `p`; per revocarla eliminate `p`. In ABIZ 1.1 le chiavi ritirate non vengono pubblicate, né nel DNS né nella scheda. La chiave mostra quale chiave ha pubblicato chi controlla il dominio; non prova l'identità giuridica.

## 5. Che cosa vedono gli strumenti di IA

Con una scheda valida, un assistente compatibile può rispondere a domande come:

- «Pasticceria Rossi S.r.l. è un'impresa di Bologna?»
- «Che cosa offre Pasticceria Rossi S.r.l. e quali sono gli orari?»
- «pasticceriarossi.example è il sito ufficiale di Pasticceria Rossi S.r.l.?»
- «Quale numero di iscrizione dichiara Pasticceria Rossi S.r.l.?»

I limiti contano. ABIZ mostra che un dominio e una scheda si richiamano a vicenda. Non prova che un'impresa sia iscritta legalmente, che un numero di iscrizione sia autentico né che qualcuno la raccomandi. Uno strumento che non ha consultato direttamente il Registro delle imprese non deve presentare l'impresa come verificata. ABIZ non garantisce che un servizio di IA trovi, classifichi o raccomandi un'impresa.

## 6. Note pratiche

### Trovare il numero di iscrizione

Il codice fiscale e il numero REA compaiono nella visura camerale, sulle fatture e sul sito dell'impresa. La ricerca è disponibile sul portale del [Registro delle imprese](https://www.registroimprese.it/). Per una ditta individuale il codice fiscale è quello personale del titolare: in quel caso non pubblicate la chiave, perché identifica una persona.

### Aggiungere il record TXT

Aggiungete il record dove si gestisce il DNS del vostro dominio, di solito presso il registrar o il fornitore di hosting. Il registro dei domini `.it` è [Registro .it](https://www.nic.it/), ma il record si aggiunge presso il vostro registrar o fornitore DNS; va bene qualsiasi fornitore che supporti i record TXT. Create un record di tipo TXT con nome `_abiz` (alcuni pannelli vogliono il nome completo, `_abiz.pasticceriarossi.example`), il valore esattamente come sopra e un TTL di 300. Non inserite spazi nel valore ed eliminate eventuali record ABIZ precedenti, in modo che ne resti uno solo.

### Privacy e pubblicazione dei dati

Il GDPR si applica ai dati personali della scheda, per esempio il nome di un imprenditore individuale o di un referente. Il [Comitato europeo per la protezione dei dati](https://www.edpb.europa.eu/) rimanda alle autorità nazionali; in Italia è il Garante per la protezione dei dati personali. Tutto ciò che è in una scheda ABIZ è pubblico: pubblicate solo dati destinati a esserlo. Un imprenditore individuale non dovrebbe pubblicare l'indirizzo di casa: la specifica richiede di omettere gli indirizzi privati, non di contrassegnarli come privati. Un indirizzo generico come `info@` è preferibile a un indirizzo email personale.

## 7. Per approfondire

- [Specifica ABIZ (SPEC.md, in inglese)](../../../SPEC.md): sintassi DNS (sezione 3.1.1), chiave `p` (sezione 3.3), chiavi d'impresa (sezione 4.2)
- [Schema JSON normativo](../../../schemas/abiz-business-record-v1.schema.json)
- [Validatore di riferimento, scripts/validate.py](../../../scripts/validate.py)
- [Tutte le guide per l'Europa](index.md)
