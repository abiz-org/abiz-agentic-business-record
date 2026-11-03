# Diventare un'impresa agentica con ABIZ a San Marino

*Una guida ad ABIZ 1.1 (proposta). Il testo di riferimento è la [specifica (SPEC.md, in inglese)](../../../SPEC.md): se questa guida e la specifica non coincidono, vale la specifica.*

## 1. Che cosa significa per un'impresa a San Marino

Sempre più persone chiedono agli assistenti di IA informazioni sulle imprese: chi sono, che cosa offrono, dove trovarle. Con ABIZ (Agentic Business Record) un'impresa pubblica una scheda pubblica e leggibile dalle macchine con i propri dati, come nome, paese, sito web, servizi e orari, e sul proprio dominio un record DNS che rimanda a quella scheda.

Solo l'impresa, o chi agisce per suo conto, può modificare il DNS del suo dominio. Un software compatibile può quindi trovare la scheda partendo dal dominio e verificare che dominio e scheda si richiamino a vicenda, invece di ricostruire i dati da pagine web sparse. ABIZ è aperto e indipendente dai fornitori: non servono iscrizioni, costi o un fornitore particolare.

## 2. Come pubblicare una scheda ABIZ

### Campi obbligatori

La scheda dell'impresa è un documento JSON che deve rispettare lo [schema normativo](../../../schemas/abiz-business-record-v1.schema.json). I campi obbligatori sono cinque:

| Campo | Esempio | Note |
| --- | --- | --- |
| `record_version` | `abiz1` | Sempre questo valore |
| `business_name` | `Titano Ceramiche S.r.l.` | Il nome pubblico, di solito come risulta dal registro, con la forma giuridica se la usate |
| `country` | `sm` | Codice paese ISO 3166-1 alpha-2; la forma canonica è in minuscolo |
| `identity_host` | `titanoceramiche.sm.to.co` | Esattamente il valore DNS `h`: un nome host con percorso facoltativo, senza `https://` |
| `domains` | `["titanoceramiche.example"]` | I domini rivendicati dalla scheda, compreso quello che contiene `_abiz` |

### Chiave d'impresa `k` (facoltativa)

`k` è facoltativa per ogni impresa, iscritta o no. Se la pubblicate, la scheda deve contenere anche `business_key` e `registration_number`, e `k` deve essere uguale a `business_key`.

A San Marino la chiave è `sm-` seguito dal numero di iscrizione, senza suddivisione territoriale: una chiave con una parte centrale, come `sm-xx-…`, non è valida.

- **Registro:** Registro delle Società, tenuto dall'[Ufficio Attività Economiche](https://www.gov.sm/pub2/GovSM/Dipartimenti/Dipartimento-Sviluppo-Economico/Ufficio-Attivit--Economiche.html)
- **Numero da usare:** il Codice Operatore Economico (COE): il prefisso `SM` seguito da 5 cifre, l'identificativo che vale per lo stesso operatore in tutti i registri sammarinesi
- **Come scriverlo:** partite dal numero come lo rilascia il registro, applicate la normalizzazione Unicode NFKC, togliete spazi, `-`, `.`, `/` e gli altri trattini, poi scrivete le lettere in maiuscolo. Zeri iniziali e prefissi in lettere restano. Il risultato deve contenere solo lettere e cifre ASCII.

Esempio (numero inventato): `SM01234` è già in forma canonica. La scheda contiene allora `"registration_number": "SM01234"` e `"business_key": "sm-SM01234"`, e nel DNS compare `k=sm-SM01234`. Mantenete il prefisso `SM` e gli zeri iniziali.

Le chiavi si confrontano senza distinguere maiuscole e minuscole, ma pubblicate la forma canonica: codice del paese in minuscolo, numero in maiuscolo.

### Record DNS TXT

Pubblicate un solo record TXT ABIZ in `_abiz` sul vostro dominio, nella forma compatta senza spazi:

```dns
_abiz.titanoceramiche.example. 300 IN TXT "v=abiz1;k=sm-SM01234;h=titanoceramiche.sm.to.co;p=ZkadQfgoS5g6YKYkNavD+5MrKELf9qGUyBsuvfLZ+Tg="
```

- `v=abiz1` deve venire per primo. `h` è obbligatorio; `k` e `p` sono facoltativi.
- I nomi dei tag sono in minuscolo e distinguono maiuscole e minuscole. Nessun tag può comparire due volte.
- Si raccomanda un TTL di 300 secondi.

Il valore `p` qui sopra è una chiave d'esempio usa e getta. Non copiatelo mai: pubblicate la vostra chiave oppure omettete `p`.

### Scheda dell'impresa (JSON)

La scheda servita all'indirizzo `https://titanoceramiche.sm.to.co` come `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Titano Ceramiche S.r.l.",
  "country": "sm",
  "business_key": "sm-SM01234",
  "registration_number": "SM01234",
  "identity_host": "titanoceramiche.sm.to.co",
  "domains": [
    "titanoceramiche.example"
  ],
  "public_key": "ZkadQfgoS5g6YKYkNavD+5MrKELf9qGUyBsuvfLZ+Tg=",
  "description": "Laboratorio di ceramica a Borgo Maggiore.",
  "website": "https://titanoceramiche.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Borgo Maggiore",
        "country": {
          "code": "SM"
        }
      },
      "public": true
    }
  ],
  "signature": "EsejFz4qh+JrDQ4+RjEiWOe30e9Mz36Cn37lNnzo1g3XtKDH4S0l2VrhSF4h/5qUGmxQXHPHlYbudzAAtX9OCw=="
}
```

Con il validatore di riferimento potete controllare in locale la scheda e il valore DNS:

```sh
python scripts/validate.py record.json --domain titanoceramiche.example --dns-value 'v=abiz1;k=sm-SM01234;h=titanoceramiche.sm.to.co;p=ZkadQfgoS5g6YKYkNavD+5MrKELf9qGUyBsuvfLZ+Tg='
```

### In proprio o tramite un fornitore

Potete pubblicare la scheda voi stessi su qualsiasi host HTTPS che controllate, oppure usare un qualsiasi fornitore compatibile. ABIZ non impone fornitori né schemi per i nomi host. In ogni caso la scheda deve essere servita in HTTPS e dovete controllare il dominio che contiene `_abiz`.

## 3. Fornitori e MCP

MCP (Model Context Protocol) è un protocollo aperto con cui gli assistenti di IA richiamano strumenti e leggono dati da server esterni. Un fornitore può gestire un server MCP tramite il quale un assistente ottiene direttamente la vostra scheda pubblica. Potete indicarlo nel campo facoltativo `mcp_server_url`. ABIZ non richiede un server MCP, e uno strumento non dovrebbe richiamarlo automaticamente solo perché compare in una scheda.

Per esempio, un fornitore può pubblicare la vostra scheda all'indirizzo `titanoceramiche.sm.to.co` e gestire un server MCP. Un assistente collegato a quel server può allora chiedere gli orari o i servizi di Titano Ceramiche S.r.l. e ricevere i dati dalla vostra scheda, invece di tirare a indovinare.

## 4. Chiavi e firme (ABIZ 1.1)

ABIZ 1.1 consente di pubblicare una chiave pubblica Ed25519 nel tag DNS `p`. `p` è facoltativo. Se presente, deve essere la codifica base64 standard della chiave di 32 byte: 44 caratteri che terminano con un solo `=`, in un'unica stringa DNS. Qualsiasi altro valore, come un token esadecimale di ABIZ 1.0 o una chiave base64url, rende non valido l'intero record.

La chiave privata corrispondente appartiene all'impresa e non viene mai pubblicata. Un fornitore che la custodisce per voi deve permettervi di esportarla. Un software può verificare una firma creata con la chiave privata usando la chiave pubblicata nel DNS. ABIZ 1.1 non stabilisce ancora quali byte copra una firma della scheda.

Per cambiare chiave pubblicatene una nuova in `p`; per revocarla eliminate `p`. In ABIZ 1.1 le chiavi ritirate non vengono pubblicate, né nel DNS né nella scheda. La chiave mostra quale chiave ha pubblicato chi controlla il dominio; non prova l'identità giuridica.

## 5. Che cosa vedono gli strumenti di IA

Con una scheda valida, un assistente compatibile può rispondere a domande come:

- «Titano Ceramiche S.r.l. è un'impresa di Borgo Maggiore?»
- «Che cosa offre Titano Ceramiche S.r.l. e quali sono gli orari?»
- «titanoceramiche.example è il sito ufficiale di Titano Ceramiche S.r.l.?»
- «Quale numero di iscrizione dichiara Titano Ceramiche S.r.l.?»

I limiti contano. ABIZ mostra che un dominio e una scheda si richiamano a vicenda. Non prova che un'impresa sia iscritta legalmente, che un numero di iscrizione sia autentico né che qualcuno la raccomandi. Uno strumento che non ha consultato direttamente il Registro delle Società non deve presentare l'impresa come verificata. ABIZ non garantisce che un servizio di IA trovi, classifichi o raccomandi un'impresa.

## 6. Note pratiche

### Trovare il numero di iscrizione

Il COE compare sulla licenza, sul certificato di iscrizione e sulle fatture. Il Registro delle Società si consulta con l'applicativo REGSOC ON-LINE sul Portale dei Servizi della PA, indicato dall'[Ufficio Attività Economiche](https://www.gov.sm/pub2/GovSM/Dipartimenti/Dipartimento-Sviluppo-Economico/Ufficio-Attivit--Economiche.html).

### Aggiungere il record TXT

Aggiungete il record dove si gestisce il DNS del vostro dominio, di solito presso il registrar o il fornitore di hosting. Il registro dei domini `.sm` è [NIC San Marino](https://www.nic.sm/), ma il record si aggiunge presso il vostro registrar o fornitore DNS; va bene qualsiasi fornitore che supporti i record TXT. Create un record di tipo TXT con nome `_abiz` (alcuni pannelli vogliono il nome completo, `_abiz.titanoceramiche.example`), il valore esattamente come sopra e un TTL di 300. Non inserite spazi nel valore ed eliminate eventuali record ABIZ precedenti, in modo che ne resti uno solo.

### Privacy e pubblicazione dei dati

La legge sammarinese sulla protezione dei dati personali si applica ai dati personali della scheda, per esempio il nome di un referente. Se servite clienti nell'Unione europea, può applicarsi anche il GDPR. Tutto ciò che è in una scheda ABIZ è pubblico: pubblicate solo dati destinati a esserlo. Un imprenditore individuale non dovrebbe pubblicare l'indirizzo di casa: la specifica richiede di omettere gli indirizzi privati, non di contrassegnarli come privati. Un indirizzo generico come `info@` è preferibile a un indirizzo email personale.

## 7. Per approfondire

- [Specifica ABIZ (SPEC.md, in inglese)](../../../SPEC.md): sintassi DNS (sezione 3.1.1), chiave `p` (sezione 3.3), chiavi d'impresa (sezione 4.2)
- [Schema JSON normativo](../../../schemas/abiz-business-record-v1.schema.json)
- [Validatore di riferimento, scripts/validate.py](../../../scripts/validate.py)
- [Tutte le guide per l'Europa](index.md)
