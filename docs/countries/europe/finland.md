# Agenttiseksi yritykseksi ABIZin avulla Suomessa

*Opas ABIZ 1.1:een (ehdotus). Velvoittava teksti on [määrittely (SPEC.md, englanniksi)](../../../SPEC.md): jos tämä opas ja määrittely eroavat, määrittely on ratkaiseva.* Suomessa on kaksi kansalliskieltä; tämä opas on suomeksi. Ruotsinkielistä versiota ei vielä ole.

## 1. Mitä tämä tarkoittaa yritykselle Suomessa

Yhä useampi kysyy tekoälyavustajilta yrityksistä: keitä ne ovat, mitä ne tarjoavat ja mistä ne löytää. ABIZin (Agentic Business Record) avulla yritys julkaisee yhden avoimen, koneluettavan tietueen omista tiedoistaan, kuten nimestä, maasta, verkkosivustosta, palveluista ja aukioloajoista, sekä omaan verkkotunnukseensa DNS-tietueen, joka osoittaa tähän tietueeseen.

Vain yritys tai sen puolesta toimiva taho voi muuttaa verkkotunnuksensa DNS-asetuksia. Siksi yhteensopiva ohjelmisto voi löytää tietueen verkkotunnuksen perusteella ja tarkistaa, että verkkotunnus ja tietue viittaavat toisiinsa, sen sijaan että se kokoaisi tietoja hajanaisilta verkkosivuilta. ABIZ on avoin ja palveluntarjoajista riippumaton: jäsenyyttä, maksuja tai tiettyä palveluntarjoajaa ei tarvita.

## 2. ABIZ-tietueen julkaiseminen

### Pakolliset kentät

Yritystietue on JSON-asiakirja, jonka on noudatettava [normatiivista skeemaa](../../../schemas/abiz-business-record-v1.schema.json). Pakollisia kenttiä on viisi:

| Kenttä | Esimerkki | Huomautus |
| --- | --- | --- |
| `record_version` | `abiz1` | Aina tämä arvo |
| `business_name` | `Koivu Design Oy` | Julkinen nimi, yleensä kuten rekisterissä, yhtiömuodon kanssa, jos käytätte sitä |
| `country` | `fi` | ISO 3166-1 alpha-2 -maatunnus; kanoninen muoto on pienin kirjaimin |
| `identity_host` | `koivudesign.fi.to.co` | Täsmälleen DNS-arvo `h`: isäntänimi ja mahdollinen polku ilman `https://`-alkua |
| `domains` | `["koivudesign.example"]` | Verkkotunnukset, joita tietue koskee, mukaan lukien se, jossa `_abiz` on |

### Vapaaehtoinen yritysavain `k`

`k` on vapaaehtoinen kaikille yrityksille, olivat ne rekisteröityjä tai eivät. Jos julkaisette `k`:n, tietueessa on oltava myös `business_key` ja `registration_number`, ja `k`:n on oltava sama kuin `business_key`.

Suomessa avain on `fi-` ja sen perässä rekisterinumero ilman alueosaa: avain, jossa on keskiosa, kuten `fi-xx-…`, on virheellinen.

- **Rekisteri:** kaupparekisteri, jota ylläpitää [Patentti- ja rekisterihallitus (PRH)](https://www.prh.fi/), ja yritys- ja yhteisötietojärjestelmä [YTJ](https://www.ytj.fi/)
- **Käytettävä tunnus:** Y-tunnus, seitsemän numeroa, väliviiva ja tarkistusnumero. Ei ALV-numeroa (`FI…`)
- **Kirjoitustapa:** lähtekää tunnuksesta sellaisena kuin rekisteri sen antaa, tehkää Unicode-normalisointi NFKC, poistakaa välilyönnit, `-`, `.`, `/` ja muut viivat ja kirjoittakaa kirjaimet isoina. Alkunollat ja kirjainetuliitteet säilytetään. Tuloksessa saa olla vain ASCII-kirjaimia ja -numeroita.

Esimerkki (keksitty tunnus): `1234567-8` kirjoitetaan muodossa `12345678`. Tietueessa on tällöin `"registration_number": "12345678"` ja `"business_key": "fi-12345678"`, ja DNS:ssä `k=fi-12345678`.

Avaimia verrataan kirjainkoosta riippumatta, mutta julkaiskaa kanoninen muoto: maatunnus pienin kirjaimin, tunnus isoin.

### DNS TXT -tietue

Julkaiskaa verkkotunnukseenne nimen `_abiz` alle täsmälleen yksi ABIZ TXT -tietue tiiviissä muodossa ilman välilyöntejä:

```dns
_abiz.koivudesign.example. 300 IN TXT "v=abiz1;k=fi-12345678;h=koivudesign.fi.to.co;p=WLEcMnRLL8EZvmWmHI3VIOKCAvQUGvIPHgQMklB1oHw="
```

- `v=abiz1` on oltava ensimmäisenä. `h` on pakollinen; `k` ja `p` ovat vapaaehtoisia.
- Tunnisteiden nimet kirjoitetaan pienin kirjaimin, ja kirjainkoolla on merkitystä. Mikään tunniste ei saa esiintyä kahdesti.
- Suositeltu TTL on 300 sekuntia.

Yllä oleva `p`-arvo on kertakäyttöinen esimerkkiavain. Älkää koskaan kopioiko sitä: julkaiskaa oma avaimenne tai jättäkää `p` pois.

### Yritystietue (JSON)

Tietue, joka tarjoillaan osoitteessa `https://koivudesign.fi.to.co` muodossa `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Koivu Design Oy",
  "country": "fi",
  "business_key": "fi-12345678",
  "registration_number": "12345678",
  "identity_host": "koivudesign.fi.to.co",
  "domains": [
    "koivudesign.example"
  ],
  "public_key": "WLEcMnRLL8EZvmWmHI3VIOKCAvQUGvIPHgQMklB1oHw=",
  "description": "Muotoilutoimisto Tampereella.",
  "website": "https://koivudesign.example",
  "locations": [
    {
      "kind": "trading",
      "city": "Tampere",
      "country": "fi",
      "public": true
    }
  ],
  "signature": "5NwMsv53S0wLO+KnmuB/iUC20D4TVS6WYzvpYePQNj5qmGob6KqG/u49uXZYZ2pZexd5TJwOus8So+zoxyLaAg=="
}
```

Viitevalidaattorilla voitte tarkistaa tietueen ja DNS-arvon paikallisesti:

```sh
python scripts/validate.py record.json --domain koivudesign.example --dns-value 'v=abiz1;k=fi-12345678;h=koivudesign.fi.to.co;p=WLEcMnRLL8EZvmWmHI3VIOKCAvQUGvIPHgQMklB1oHw='
```

### Itse tai palveluntarjoajan kautta

Voitte tarjoilla tietueen itse miltä tahansa hallitsemaltanne HTTPS-palvelimelta tai käyttää mitä tahansa yhteensopivaa palveluntarjoajaa. ABIZ ei edellytä tiettyä palveluntarjoajaa eikä isäntänimien nimeämistapaa. Tietue on joka tapauksessa tarjoiltava HTTPS:n kautta, ja verkkotunnuksen, jossa `_abiz` on, on oltava hallinnassanne.

## 3. Palveluntarjoajat ja MCP

MCP (Model Context Protocol) on avoin protokolla, jonka avulla tekoälyavustajat voivat käyttää työkaluja ja lukea tietoja ulkoisilta palvelimilta. Palveluntarjoaja voi ylläpitää MCP-palvelinta, jonka kautta avustaja hakee julkisen tietueenne suoraan. Palvelimen voi ilmoittaa vapaaehtoisessa kentässä `mcp_server_url`. ABIZ ei edellytä MCP-palvelinta, eikä työkalun pitäisi kutsua sitä automaattisesti vain siksi, että se mainitaan tietueessa.

Esimerkki: palveluntarjoaja julkaisee tietueenne osoitteessa `koivudesign.fi.to.co` ja ylläpitää MCP-palvelinta. Palvelimeen yhdistetty avustaja voi tällöin kysyä yrityksen Koivu Design Oy aukioloaikoja tai palveluja ja saada tiedot tietueestanne arvailun sijaan.

## 4. Avaimet ja allekirjoitukset (ABIZ 1.1)

ABIZ 1.1:ssä yritys voi julkaista julkisen Ed25519-avaimen DNS-tunnisteessa `p`. `p` on vapaaehtoinen. Jos se on mukana, arvon on oltava 32-tavuisen avaimen tavallinen base64-koodaus: 44 merkkiä, joista viimeinen on täsmälleen yksi `=`, yhdessä DNS-merkkijonossa. Mikä tahansa muu arvo, kuten ABIZ 1.0:n heksadesimaalinen tunnus tai base64url-avain, tekee koko tietueesta virheellisen.

Vastaava yksityinen avain kuuluu yritykselle, eikä sitä koskaan julkaista. Jos palveluntarjoaja säilyttää sitä puolestanne, sen on annettava teidän viedä avain itsellenne. Ohjelmisto voi tarkistaa yksityisellä avaimella tehdyn allekirjoituksen DNS:ssä julkaistua avainta vasten. ABIZ 1.1 ei vielä määrittele, mitä tavuja yritystietueen allekirjoitus kattaa.

Avaimen vaihtamiseksi julkaistaan uusi avain kenttään `p`; avaimen mitätöimiseksi `p` poistetaan. Käytöstä poistettuja avaimia ei ABIZ 1.1:ssä julkaista, ei DNS:ssä eikä tietueessa. Avain osoittaa, minkä avaimen verkkotunnuksen haltija on julkaissut; se ei todista oikeudellista henkilöllisyyttä.

## 5. Mitä tekoälytyökalut näkevät

Kun tietue on kelvollinen, yhteensopiva avustaja voi vastata esimerkiksi näihin kysymyksiin:

- ”Toimiiko Koivu Design Oy Tampereella?”
- ”Mitä Koivu Design Oy tarjoaa, ja milloin se on auki?”
- ”Onko koivudesign.example yrityksen Koivu Design Oy virallinen verkkosivusto?”
- ”Minkä Y-tunnuksen Koivu Design Oy ilmoittaa?”

Rajoitukset ovat tärkeitä. ABIZ osoittaa, että verkkotunnus ja tietue viittaavat toisiinsa. Se ei todista, että yritys on laillisesti rekisteröity, että rekisterinumero on aito tai että kukaan suosittelee yritystä. Työkalun, joka ei ole itse tarkistanut tietoja kaupparekisteristä, ei pidä esittää yritystä varmennettuna. ABIZ ei takaa, että mikään tekoälypalvelu löytää, asettaa järjestykseen tai suosittelee yritystä.

## 6. Käytännön ohjeita

### Mistä tunnuksen löytää

Y-tunnus on laskuissa, verkkosivustolla ja kaupparekisteriotteessa, ja sen voi hakea [YTJ:stä](https://www.ytj.fi/). Myös toiminimellä toimivalla yrittäjällä on Y-tunnus, ja hän voi käyttää avainta, mutta kotiosoitetta ei pidä julkaista.

### TXT-tietueen lisääminen

Lisätkää tietue siellä, missä verkkotunnuksenne DNS:ää hallitaan, yleensä verkkotunnusvälittäjän tai webhotellin palvelussa. `.fi`-verkkotunnuksia hallinnoi [Traficom](https://www.traficom.fi/), mutta TXT-tietue lisätään verkkotunnusvälittäjän tai DNS-palveluntarjoajan palvelussa; mikä tahansa TXT-tietueita tukeva palvelu käy. Luokaa TXT-tyyppinen tietue, jonka nimi on `_abiz` (jotkin hallintapaneelit vaativat koko nimen, `_abiz.koivudesign.example`), arvo täsmälleen kuten yllä ja TTL 300. Älkää lisätkö arvoon välilyöntejä, ja poistakaa vanhemmat ABIZ-tietueet niin, että jäljelle jää vain yksi.

### Tietosuoja ja julkaiseminen

Yleistä tietosuoja-asetusta (GDPR) sovelletaan tietueen henkilötietoihin, esimerkiksi toiminimiyrittäjän tai yhteyshenkilön nimeen. Valvova viranomainen on tietosuojavaltuutettu; [Euroopan tietosuojaneuvosto](https://www.edpb.europa.eu/) ohjaa kansallisiin viranomaisiin. Kaikki ABIZ-tietueen tiedot ovat julkisia; julkaiskaa vain tietoja, jotka saavat olla julkisia. Toiminimellä toimivan yrittäjän ei pidä julkaista kotiosoitettaan: määrittely edellyttää, että yksityiset osoitteet jätetään pois eikä niitä vain merkitä yksityisiksi. Yleinen osoite, kuten `info@`, on parempi kuin henkilökohtainen sähköpostiosoite.

## 7. Lisätietoa

- [ABIZ-määrittely (SPEC.md, englanniksi)](../../../SPEC.md): DNS-syntaksi (kohta 3.1.1), avain `p` (kohta 3.3), yritysavaimet (kohta 4.2)
- [Normatiivinen JSON-skeema](../../../schemas/abiz-business-record-v1.schema.json)
- [Viitevalidaattori, scripts/validate.py](../../../scripts/validate.py)
- [Kaikki Euroopan oppaat](index.md)
