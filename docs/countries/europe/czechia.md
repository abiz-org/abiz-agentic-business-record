# Jak se stát agentní firmou s ABIZ v Česku

*Průvodce zveřejněnou specifikací ABIZ 1.1. Závazná je [specifikace (SPEC.md, anglicky)](../../../SPEC.md): pokud se tento průvodce a specifikace liší, platí specifikace.*

## 1. Co to znamená pro firmu v Česku

Stále více lidí se ptá asistentů umělé inteligence na firmy: kdo jsou, co nabízejí a kde je najít. Díky ABIZ (Agentic Business Record) firma zveřejní jeden veřejný, strojově čitelný záznam s vlastními údaji, jako je název, země, web, služby a otevírací doba, a na své doméně záznam DNS, který na něj odkazuje.

Jen firma, nebo ten, kdo jedná jejím jménem, může měnit DNS své domény. Kompatibilní software proto může záznam najít podle domény a ověřit, že doména a záznam odkazují jeden na druhý, místo aby skládal údaje z roztroušených webových stránek. ABIZ je otevřený a nezávislý na poskytovatelích: nevyžaduje členství, poplatky ani konkrétního poskytovatele.

## 2. Jak zveřejnit záznam ABIZ

### Povinná pole

Záznam firmy je dokument JSON, který musí odpovídat [normativnímu schématu](../../../schemas/abiz-business-record-v1.1.schema.json). Povinných polí je pět:

| Pole | Příklad | Poznámka |
| --- | --- | --- |
| `record_version` | `abiz1` | Vždy tato hodnota |
| `business_name` | `Pekárna Novák s.r.o.` | Veřejný název, obvykle jako v rejstříku, s právní formou, pokud ji používáte |
| `country` | `cz` | Kód země podle ISO 3166-1 alpha-2; kanonický tvar je malými písmeny |
| `identity_host` | `pekarnanovak.cz.to.co` | Přesně hodnota DNS `h`: název hostitele s volitelnou cestou, bez `https://` |
| `domains` | `["pekarnanovak.example"]` | Domény, kterých se záznam týká, včetně domény se záznamem `_abiz` |

### Nepovinný klíč firmy `k`

`k` je nepovinný pro každou firmu, zapsanou i nezapsanou. Pokud `k` zveřejníte, musí záznam obsahovat také `business_key` a `registration_number` a `k` se musí rovnat `business_key`.

V Česku je klíč `cz-` a za ním registrační číslo, bez územní části: klíč se střední částí, například `cz-xx-…`, je neplatný.

- **Rejstřík:** veřejný rejstřík (obchodní rejstřík) vedený krajskými soudy, dostupný na [justice.cz](https://or.justice.cz/)
- **Které číslo:** IČO, osm číslic. Ne DIČ (`CZ…`)
- **Zápis:** vyjděte z čísla tak, jak ho rejstřík přiděluje, použijte normalizaci Unicode NFKC, odstraňte mezery, `-`, `.`, `/` a další pomlčky a písmena převeďte na velká. Úvodní nuly a písmenné předpony zůstávají. Výsledek smí obsahovat jen písmena a číslice ASCII.

Příklad (smyšlené číslo): z `123 45 678` se stane `12345678`. Záznam pak obsahuje `"registration_number": "12345678"` a `"business_key": "cz-12345678"` a v DNS je `k=cz-12345678`. IČO je celostátně jedinečné, i když rejstřík vedou krajské soudy.

Klíče se porovnávají bez ohledu na velikost písmen, ale zveřejňujte kanonický tvar: kód země malými písmeny, číslo velkými.

### Záznam DNS TXT

Na své doméně zveřejněte pod `_abiz` právě jeden záznam TXT ABIZ, v kompaktním tvaru bez mezer:

```dns
_abiz.pekarnanovak.example. 300 IN TXT "v=abiz1;k=cz-12345678;h=pekarnanovak.cz.to.co;p=VKJZd2Cpbs7FmfKMlbOvh2lDfkkkQ1txfD/G5O70ASo="
```

- `v=abiz1` musí být první. `h` a `p` jsou povinné; `k` je nepovinné.
- Názvy značek se píší malými písmeny a rozlišuje se velikost písmen. Žádná značka se nesmí opakovat.
- Doporučené TTL je 300 sekund.

Hodnota `p` výše je jednorázový ukázkový klíč. Nikdy ji nekopírujte: zveřejněte vlastní klíč. Tvrzení ABIZ 1.1 musí obsahovat `p`.

### Záznam firmy (JSON)

Záznam poskytovaný na `https://pekarnanovak.cz.to.co` jako `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Pekárna Novák s.r.o.",
  "country": "cz",
  "business_key": "cz-12345678",
  "registration_number": "12345678",
  "identity_host": "pekarnanovak.cz.to.co",
  "domains": [
    "pekarnanovak.example"
  ],
  "public_key": "VKJZd2Cpbs7FmfKMlbOvh2lDfkkkQ1txfD/G5O70ASo=",
  "description": "Řemeslná pekárna v Brně.",
  "website": "https://pekarnanovak.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Brno",
        "country": {
          "code": "CZ"
        }
      },
      "public": true
    }
  ],
  "signature": "HxSd7EUbC8V5IAtl3w5niFrfBkfhcB7yahS29Syi5Wndnnkfp+ClltXgG2MhJkaX2VyCu+DEwZAkuENI5nGsBw=="
}
```

Referenčním validátorem můžete záznam a hodnotu DNS ověřit lokálně:

```sh
python scripts/validate.py record.json --domain pekarnanovak.example --dns-value 'v=abiz1;k=cz-12345678;h=pekarnanovak.cz.to.co;p=VKJZd2Cpbs7FmfKMlbOvh2lDfkkkQ1txfD/G5O70ASo='
```

### Vlastní hosting, nebo poskytovatel

Záznam můžete poskytovat sami z jakéhokoli hostitele HTTPS, který spravujete, nebo využít libovolného kompatibilního poskytovatele. ABIZ nepředepisuje poskytovatele ani schéma názvů hostitelů. Záznam musí být vždy poskytován přes HTTPS a doménu se záznamem `_abiz` musíte spravovat vy.

## 3. Poskytovatelé a MCP

MCP (Model Context Protocol) je otevřený protokol, díky němuž asistenti umělé inteligence volají nástroje a čtou data z externích serverů. Poskytovatel může provozovat server MCP, přes který asistent získá váš veřejný záznam přímo. Server lze uvést v nepovinném poli `mcp_server_url`. ABIZ server MCP nevyžaduje a nástroj by ho neměl volat automaticky jen proto, že je uveden v záznamu.

Příklad: poskytovatel zveřejní váš záznam na adrese `pekarnanovak.cz.to.co` a provozuje server MCP. Asistent připojený k tomuto serveru se pak může zeptat na otevírací dobu nebo služby firmy Pekárna Novák s.r.o. a dostane údaje z vašeho záznamu, místo aby hádal.

## 4. Klíče a podpisy (ABIZ 1.1)

ABIZ 1.1 vyžaduje veřejný klíč Ed25519 ve značce DNS `p`. `v` a `h` jsou povinné. `p` je povinné. `k` je nepovinné. `p` musí být 32 surových bajtů ve standardním base64: 44 znaků zakončených právě jedním `=`, v jednom řetězci DNS. Base64url se nepřijímá. Jakákoli jiná hodnota, například šestnáctkový řetězec, činí celý záznam neplatným.

Odpovídající soukromý klíč patří firmě a nikdy se nezveřejňuje. Pokud ho za vás uchovává poskytovatel, musí vám umožnit jeho export. Software může ověřit podpis vytvořený soukromým klíčem pomocí klíče zveřejněného v DNS. ABIZ 1.1 zatím nedefinuje, které bajty podpis záznamu firmy pokrývá.

Klíč vyměníte tak, že vygenerujete nový pár Ed25519, zveřejníte nový veřejný klíč v DNS nebo well-known, znovu podepíšete záznam novým soukromým klíčem a nastavíte `public_key` na stejné `p`. Počítejte s mezipamětí DNS. Odstranit pouze `p` není platné odvolání, dokud tvrzení ABIZ 1.1 zůstává: pro jeho stažení odstraňte celé prohlášení. Vyřazené klíče se v ABIZ 1.1 nezveřejňují, ani v DNS, ani v záznamu. Klíč ukazuje, jaký klíč zveřejnil správce domény; neprokazuje právní identitu.

## 5. Co vidí nástroje umělé inteligence

S platným záznamem může kompatibilní asistent odpovídat na otázky jako:

- „Je Pekárna Novák s.r.o. firma z Brna?“
- „Co nabízí Pekárna Novák s.r.o. a kdy má otevřeno?“
- „Je pekarnanovak.example oficiální web firmy Pekárna Novák s.r.o.?“
- „Jaké IČO uvádí Pekárna Novák s.r.o.?“

Na omezeních záleží. ABIZ ukazuje, že doména a záznam odkazují jeden na druhý. Neprokazuje, že je firma právně zapsána, že je registrační číslo pravé, ani že ji někdo doporučuje. Nástroj, který sám neověřil údaje v obchodním rejstříku, by neměl firmu prezentovat jako ověřenou. ABIZ nezaručuje, že ji jakákoli služba umělé inteligence najde, zařadí nebo doporučí.

## 6. Praktické poznámky

### Kde najdete číslo

IČO je na fakturách, na webu a ve výpisu z obchodního rejstříku; vyhledat ho můžete na [justice.cz](https://or.justice.cz/). IČO mají i živnostníci, kteří nejsou v obchodním rejstříku zapsáni; mohou klíč použít, ale neměli by zveřejňovat adresu bydliště.

### Přidání záznamu TXT

Záznam přidejte tam, kde se spravuje DNS vaší domény, obvykle u registrátora nebo poskytovatele hostingu. Registrem domén `.cz` je [CZ.NIC](https://www.nic.cz/), záznam TXT ale přidáte u svého registrátora nebo poskytovatele DNS; stačí kterýkoli, který záznamy TXT podporuje. Vytvořte záznam typu TXT s názvem `_abiz` (některé administrace vyžadují celý název, `_abiz.pekarnanovak.example`), s hodnotou přesně jako výše a TTL 300. Do hodnoty nevkládejte mezery a starší záznamy ABIZ smažte, aby zůstal jen jeden.

### Ochrana osobních údajů

Na osobní údaje v záznamu, například jméno živnostníka nebo kontaktní osoby, se vztahuje GDPR. Dozorovým úřadem je Úřad pro ochranu osobních údajů (ÚOOÚ); [Evropský sbor pro ochranu osobních údajů](https://www.edpb.europa.eu/) odkazuje na národní úřady. Vše v záznamu ABIZ je veřejné; zveřejňujte jen údaje, které veřejné být mohou. Podnikatel, fyzická osoba, by neměl zveřejňovat adresu bydliště: specifikace vyžaduje soukromé adresy vynechat, ne je označit jako soukromé. Obecná adresa jako `info@` je lepší než osobní e-mail.

## 7. Další informace

- [Specifikace ABIZ (SPEC.md, anglicky)](../../../SPEC.md): syntaxe DNS (oddíl 3.1.1), klíč `p` (oddíl 3.3), klíče firem (oddíl 4.2)
- [Normativní schéma JSON](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Referenční validátor, scripts/validate.py](../../../scripts/validate.py)
- [Všechny průvodce pro Evropu](index.md)
