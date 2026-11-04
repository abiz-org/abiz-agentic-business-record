# Cum deveniți o afacere agentică cu ABIZ în Republica Moldova

*Ghid pentru ABIZ 1.1 (specificația publicată). Textul de referință este [specificația (SPEC.md, în engleză)](../../../SPEC.md): dacă acest ghid și specificația diferă, prevalează specificația.*

## 1. Ce înseamnă pentru o firmă în Republica Moldova

Tot mai mulți oameni întreabă asistenții AI despre firme: cine sunt, ce oferă, unde le găsesc. Cu ABIZ (Agentic Business Record), o firmă publică o singură înregistrare publică, ușor de citit de mașini, cu propriile date, precum denumire, țară, site, servicii și program, iar pe propriul domeniu o înregistrare DNS care trimite la ea.

Doar firma, sau cine acționează în numele ei, poate modifica DNS-ul domeniului. Astfel, un software compatibil poate găsi înregistrarea pornind de la domeniu și poate verifica dacă domeniul și înregistrarea trimit unul la celălalt, în loc să adune date de pe pagini web disparate. ABIZ este deschis și independent de furnizori: nu cere calitate de membru, taxe sau un anumit furnizor.

## 2. Cum publicați o înregistrare ABIZ

### Câmpuri obligatorii

Înregistrarea firmei este un document JSON care trebuie să respecte [schema normativă](../../../schemas/abiz-business-record-v1.1.schema.json). Există cinci câmpuri obligatorii:

| Câmp | Exemplu | Observații |
| --- | --- | --- |
| `record_version` | `abiz1` | Întotdeauna această valoare |
| `business_name` | `Codru Vin SRL` | Denumirea publică, de obicei ca în registru, cu forma juridică dacă o folosiți |
| `country` | `md` | Codul țării ISO 3166-1 alpha-2; forma canonică este cu litere mici |
| `identity_host` | `codruvin.md.to.co` | Exact valoarea DNS `h`: un nume de gazdă cu cale opțională, fără `https://` |
| `domains` | `["codruvin.example"]` | Domeniile revendicate de înregistrare, inclusiv cel care conține `_abiz` |

### Cheia opțională a firmei `k`

`k` este opțional pentru orice firmă, înregistrată sau nu. Dacă îl publicați, înregistrarea trebuie să conțină și `business_key` și `registration_number`, iar `k` trebuie să fie egal cu `business_key`.

În Republica Moldova cheia este `md-` urmat de numărul de înregistrare, fără subdiviziune teritorială: o cheie cu o parte intermediară, cum ar fi `md-xx-…`, este invalidă.

- **Registru:** Registrul de stat al persoanelor juridice, ținut de [Agenția Servicii Publice (ASP)](https://www.asp.gov.md/)
- **Ce număr folosiți:** numărul de identificare de stat (IDNO), 13 cifre
- **Cum îl scrieți:** porniți de la numărul așa cum îl atribuie registrul, aplicați normalizarea Unicode NFKC, eliminați spațiile, `-`, `.`, `/` și alte liniuțe, apoi scrieți literele cu majuscule. Zerourile de la început și prefixele din litere se păstrează. Rezultatul poate conține doar litere și cifre ASCII.

Exemplu (număr inventat): `1012345678901` este deja în formă canonică. Înregistrarea conține atunci `"registration_number": "1012345678901"` și `"business_key": "md-1012345678901"`, iar în DNS apare `k=md-1012345678901`.

Cheile se compară fără a ține cont de majuscule, dar publicați forma canonică: codul țării cu litere mici, numărul cu majuscule.

### Înregistrarea DNS TXT

Publicați exact o înregistrare TXT ABIZ la `_abiz` pe domeniul dumneavoastră, în forma compactă, fără spații:

```dns
_abiz.codruvin.example. 300 IN TXT "v=abiz1;k=md-1012345678901;h=codruvin.md.to.co;p=6k1pJUgnF6IiBcYWtRXawfW0QYRop5RvFxVxToHKMqs="
```

- `v=abiz1` trebuie să fie primul. `h` și `p` sunt obligatorii; `k` este opțional.
- Numele etichetelor se scriu cu litere mici și țin cont de majuscule. Nicio etichetă nu se poate repeta.
- Se recomandă un TTL de 300 de secunde.

Valoarea `p` de mai sus este o cheie de exemplu, de unică folosință. Nu o copiați niciodată: publicați propria cheie. O aserțiune ABIZ 1.1 trebuie să conțină `p`.

### Înregistrarea firmei (JSON)

Înregistrarea servită la `https://codruvin.md.to.co` ca `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Codru Vin SRL",
  "country": "md",
  "business_key": "md-1012345678901",
  "registration_number": "1012345678901",
  "identity_host": "codruvin.md.to.co",
  "domains": [
    "codruvin.example"
  ],
  "public_key": "6k1pJUgnF6IiBcYWtRXawfW0QYRop5RvFxVxToHKMqs=",
  "description": "Cramă din Chișinău.",
  "website": "https://codruvin.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Chișinău",
        "country": {
          "code": "MD"
        }
      },
      "public": true
    }
  ],
  "signature": "ClygB5+TbQd5IkcgQJQf4WGTxm8sZidp9/qHtysfgykwvv6Aep4L6w6ewLNzuPYBF+Kh8uJCzWlHurS80ftqBw=="
}
```

Cu validatorul de referință puteți verifica local înregistrarea și valoarea DNS:

```sh
python scripts/validate.py record.json --domain codruvin.example --dns-value 'v=abiz1;k=md-1012345678901;h=codruvin.md.to.co;p=6k1pJUgnF6IiBcYWtRXawfW0QYRop5RvFxVxToHKMqs='
```

### Găzduire proprie sau printr-un furnizor

Puteți servi înregistrarea chiar dumneavoastră, de pe orice gazdă HTTPS pe care o controlați, sau puteți folosi orice furnizor compatibil. ABIZ nu impune un furnizor și nici o schemă pentru numele de gazdă. În orice caz, înregistrarea trebuie servită prin HTTPS, iar domeniul care conține `_abiz` trebuie să fie sub controlul dumneavoastră.

## 3. Furnizori și MCP

MCP (Model Context Protocol) este un protocol deschis prin care asistenții AI apelează instrumente și citesc date de pe servere externe. Un furnizor poate opera un server MCP prin care un asistent obține direct înregistrarea dumneavoastră publică. Îl puteți indica în câmpul opțional `mcp_server_url`. ABIZ nu cere un server MCP, iar un instrument nu ar trebui să-l apeleze automat doar pentru că apare într-o înregistrare.

De exemplu, un furnizor vă publică înregistrarea la `codruvin.md.to.co` și operează un server MCP. Un asistent conectat la acel server poate întreba apoi de programul sau serviciile Codru Vin SRL și primește datele din înregistrarea dumneavoastră, în loc să ghicească.

## 4. Chei și semnături (ABIZ 1.1)

ABIZ 1.1 cere o cheie publică Ed25519 în eticheta DNS `p`. `v` și `h` sunt obligatorii. `p` este obligatorie. `k` este opțional. `p` trebuie să fie codificarea base64 standard a cheii de 32 de octeți: 44 de caractere care se termină cu exact un `=`, într-un singur șir DNS. Base64url nu este acceptat. Orice altă valoare, de exemplu un șir hexazecimal, invalidează întreaga înregistrare.

Cheia privată corespunzătoare aparține firmei și nu se publică niciodată. Dacă un furnizor o păstrează pentru dumneavoastră, trebuie să vă permită să o exportați. Un software poate verifica o semnătură făcută cu cheia privată folosind cheia publicată în DNS. Semnătura acoperă forma canonică RFC 8785 a înregistrării fără membrul `signature` și se verifică cu `public_key`, care trebuie să fie egal cu `p` (SPEC, secțiunea 4.6).

Pentru a schimba cheia, generați o nouă pereche Ed25519, publicați noua cheie publică în aserțiunea DNS sau well-known, semnați din nou înregistrarea cu noua cheie privată și setați `public_key` la același `p`. Țineți cont de memoria cache DNS. Eliminarea doar a lui `p` nu este o revocare validă cât timp aserțiunea ABIZ 1.1 rămâne: pentru a o retrage, eliminați întreaga declarație. În ABIZ 1.1 cheile retrase nu se publică, nici în DNS, nici în înregistrare. Cheia arată ce cheie a publicat cel care controlează domeniul; nu dovedește identitatea juridică.

## 5. Ce văd instrumentele AI

Cu o înregistrare validă, un asistent compatibil poate răspunde la întrebări precum:

- „Este Codru Vin SRL o firmă din Chișinău?”
- „Ce oferă Codru Vin SRL și care este programul?”
- „Este codruvin.example site-ul oficial al Codru Vin SRL?”
- „Ce număr de înregistrare declară Codru Vin SRL?”

Limitele contează. ABIZ arată că un domeniu și o înregistrare trimit unul la celălalt. Nu dovedește că firma este înregistrată legal, că un număr de înregistrare este autentic sau că cineva o recomandă. Un instrument care nu a verificat el însuși registrul de stat nu ar trebui să prezinte firma ca verificată. ABIZ nu garantează că vreun serviciu AI va găsi, clasa sau recomanda o firmă.

## 6. Note practice

### Unde găsiți numărul

IDNO-ul apare pe extrasul din registru, pe facturi și pe site-ul firmei. Serviciile de înregistrare sunt descrise de [ASP](https://www.asp.gov.md/).

### Adăugarea înregistrării TXT

Adăugați înregistrarea acolo unde se administrează DNS-ul domeniului, de obicei la registrar sau la furnizorul de găzduire. Înregistrarea TXT se adaugă la registrarul sau furnizorul DNS; merge orice furnizor care acceptă înregistrări TXT. Creați o înregistrare de tip TXT cu numele `_abiz` (unele panouri cer numele complet, `_abiz.codruvin.example`), cu valoarea exact ca mai sus și TTL 300. Nu adăugați spații în valoare și ștergeți înregistrările ABIZ mai vechi, astfel încât să rămână una singură.

### Datele personale

Datelor personale din înregistrare, de exemplu numelui unui întreprinzător individual sau al unei persoane de contact, li se aplică legislația Republicii Moldova privind protecția datelor cu caracter personal. Tot ce se află într-o înregistrare ABIZ este public; publicați doar date care pot fi publice. O persoană fizică ce lucrează pe cont propriu nu ar trebui să-și publice adresa de domiciliu: specificația cere ca adresele private să fie omise, nu marcate ca private. O adresă generală precum `contact@` este mai bună decât un e-mail personal.

## 7. Mai multe informații

- [Specificația ABIZ (SPEC.md, în engleză)](../../../SPEC.md): sintaxa DNS (secțiunea 3.1.1), cheia `p` (secțiunea 3.3), cheile firmelor (secțiunea 4.2)
- [Schema JSON normativă](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Validatorul de referință, scripts/validate.py](../../../scripts/validate.py)
- [Toate ghidurile pentru Europa](index.md)
