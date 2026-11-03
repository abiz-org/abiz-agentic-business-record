# Jak zostać firmą agentową dzięki ABIZ w Polsce

*Przewodnik po ABIZ 1.1 (propozycja). Wiążąca jest [specyfikacja (SPEC.md, po angielsku)](../../../SPEC.md): jeśli ten przewodnik różni się od specyfikacji, obowiązuje specyfikacja.*

## 1. Co to oznacza dla firmy w Polsce

Coraz więcej osób pyta asystentów AI o firmy: kim są, co oferują, gdzie je znaleźć. Dzięki ABIZ (Agentic Business Record) firma publikuje jeden publiczny, czytelny maszynowo rekord z własnymi danymi, takimi jak nazwa, kraj, strona internetowa, usługi i godziny otwarcia, a w swojej domenie rekord DNS, który na ten rekord wskazuje.

Tylko firma, albo ktoś działający w jej imieniu, może zmienić DNS swojej domeny. Zgodne oprogramowanie może więc znaleźć rekord, zaczynając od domeny, i sprawdzić, że domena i rekord wskazują na siebie nawzajem, zamiast składać dane z rozproszonych stron. ABIZ jest otwarty i niezależny od dostawców: nie wymaga członkostwa, opłat ani konkretnego dostawcy.

## 2. Jak opublikować rekord ABIZ

### Pola wymagane

Rekord firmy to dokument JSON zgodny z [normatywnym schematem](../../../schemas/abiz-business-record-v1.schema.json). Wymaganych jest pięć pól:

| Pole | Przykład | Uwagi |
| --- | --- | --- |
| `record_version` | `abiz1` | Zawsze ta wartość |
| `business_name` | `Piekarnia Kowalski sp. z o.o.` | Nazwa publiczna, zwykle jak w rejestrze, z formą prawną, jeśli jej Państwo używają |
| `country` | `pl` | Kod kraju ISO 3166-1 alfa-2; postać kanoniczna to małe litery |
| `identity_host` | `piekarniakowalski.pl.to.co` | Dokładnie wartość DNS `h`: nazwa hosta z opcjonalną ścieżką, bez `https://` |
| `domains` | `["piekarniakowalski.example"]` | Domeny, których dotyczy rekord, w tym domena z `_abiz` |

### Opcjonalny klucz firmy `k`

`k` jest opcjonalny dla każdej firmy, zarejestrowanej czy nie. Jeśli go Państwo publikują, rekord musi zawierać również `business_key` i `registration_number`, a `k` musi być równy `business_key`.

W Polsce klucz to `pl-` i numer rejestrowy, bez jednostki terytorialnej: klucz z częścią środkową, np. `pl-xx-…`, jest nieprawidłowy.

- **Rejestr:** Krajowy Rejestr Sądowy (KRS), prowadzony przez Ministerstwo Sprawiedliwości: [eKRS](https://ekrs.ms.gov.pl/)
- **Który numer:** numer KRS: 10 cyfr, z zerami wiodącymi. Nie NIP ani REGON
- **Jak go zapisać:** proszę wyjść od numeru w postaci nadanej przez rejestr, zastosować normalizację Unicode NFKC, usunąć spacje, `-`, `.`, `/` i inne myślniki, a litery zapisać wielkimi literami. Zera wiodące i prefiksy literowe pozostają. Wynik może zawierać tylko litery i cyfry ASCII.

Przykład (numer zmyślony): `0000123456` jest już w postaci kanonicznej. Rekord zawiera wtedy `"registration_number": "0000123456"` i `"business_key": "pl-0000123456"`, a w DNS jest `k=pl-0000123456`. Zera wiodące są częścią numeru i muszą zostać.

Klucze porównuje się bez rozróżniania wielkości liter, ale proszę publikować postać kanoniczną: kod kraju małymi literami, numer wielkimi.

### Rekord DNS TXT

Proszę opublikować dokładnie jeden rekord TXT ABIZ pod `_abiz` w swojej domenie, w postaci zwartej, bez spacji:

```dns
_abiz.piekarniakowalski.example. 300 IN TXT "v=abiz1;k=pl-0000123456;h=piekarniakowalski.pl.to.co;p=zRHp+btvHFPfD7ODoyqksta+TYe59LzCpE7TZmqbLu0="
```

- `v=abiz1` musi być pierwsze. `h` jest wymagane; `k` i `p` są opcjonalne.
- Nazwy znaczników pisze się małymi literami i wielkość liter ma znaczenie. Żaden znacznik nie może się powtórzyć.
- Zalecany TTL to 300 sekund.

Wartość `p` powyżej to jednorazowy klucz przykładowy. Proszę go nie kopiować: należy opublikować własny klucz albo pominąć `p`.

### Rekord firmy (JSON)

Rekord udostępniany pod `https://piekarniakowalski.pl.to.co` jako `application/json`:

```json
{
  "record_version": "abiz1",
  "business_name": "Piekarnia Kowalski sp. z o.o.",
  "country": "pl",
  "business_key": "pl-0000123456",
  "registration_number": "0000123456",
  "identity_host": "piekarniakowalski.pl.to.co",
  "domains": [
    "piekarniakowalski.example"
  ],
  "public_key": "zRHp+btvHFPfD7ODoyqksta+TYe59LzCpE7TZmqbLu0=",
  "description": "Rzemieślnicza piekarnia w Krakowie.",
  "website": "https://piekarniakowalski.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Kraków",
        "country": {
          "code": "PL"
        }
      },
      "public": true
    }
  ],
  "signature": "04T24v6SiCOskvxyktUNTYy3lpfBqyuqonfiuC5EhOo0KmsB37FNS8l8/fA44M8puFMuP4Jifo9dSr/pFt4dCA=="
}
```

Walidatorem referencyjnym można lokalnie sprawdzić rekord i wartość DNS:

```sh
python scripts/validate.py record.json --domain piekarniakowalski.example --dns-value 'v=abiz1;k=pl-0000123456;h=piekarniakowalski.pl.to.co;p=zRHp+btvHFPfD7ODoyqksta+TYe59LzCpE7TZmqbLu0='
```

### Samodzielnie lub przez dostawcę

Rekord można udostępniać samodzielnie na dowolnym kontrolowanym hoście HTTPS albo skorzystać z dowolnego zgodnego dostawcy. ABIZ nie narzuca dostawcy ani schematu nazw hostów. W każdym przypadku rekord musi być serwowany przez HTTPS, a domena z `_abiz` musi być pod Państwa kontrolą.

## 3. Dostawcy i MCP

MCP (Model Context Protocol) to otwarty protokół, dzięki któremu asystenci AI wywołują narzędzia i odczytują dane z zewnętrznych serwerów. Dostawca może prowadzić serwer MCP, przez który asystent pobiera bezpośrednio Państwa publiczny rekord. Można go wskazać w opcjonalnym polu `mcp_server_url`. ABIZ nie wymaga serwera MCP, a narzędzie nie powinno wywoływać go automatycznie tylko dlatego, że figuruje w rekordzie.

Przykład: dostawca publikuje Państwa rekord pod adresem `piekarniakowalski.pl.to.co` i prowadzi serwer MCP. Asystent połączony z tym serwerem może zapytać o godziny otwarcia lub usługi firmy Piekarnia Kowalski sp. z o.o. i otrzymać dane z rekordu, zamiast zgadywać. to.co, jeden z takich dostawców, opisuje ABIZ na [stronie w języku polskim](https://to.co/pl-pl/abiz).

## 4. Klucze i podpisy (ABIZ 1.1)

ABIZ 1.1 pozwala opublikować klucz publiczny Ed25519 w znaczniku DNS `p`. `p` jest opcjonalne. Jeśli występuje, musi być standardowym kodowaniem base64 klucza o długości 32 bajtów: 44 znaki zakończone dokładnie jednym `=`, w jednym ciągu DNS. Każda inna wartość, np. szesnastkowy token z ABIZ 1.0 albo klucz w base64url, unieważnia cały rekord.

Odpowiadający mu klucz prywatny należy do firmy i nigdy nie jest publikowany. Jeśli przechowuje go dostawca, musi umożliwić jego eksport. Oprogramowanie może sprawdzić podpis złożony kluczem prywatnym za pomocą klucza opublikowanego w DNS. ABIZ 1.1 nie określa jeszcze, jakie bajty obejmuje podpis rekordu firmy.

Aby wymienić klucz, publikuje się nowy w `p`; aby go unieważnić, usuwa się `p`. W ABIZ 1.1 wycofanych kluczy się nie publikuje, ani w DNS, ani w rekordzie. Klucz pokazuje, jaki klucz opublikował dysponent domeny; nie dowodzi tożsamości prawnej.

## 5. Co widzą narzędzia AI

Przy poprawnym rekordzie zgodny asystent może odpowiedzieć na pytania takie jak:

- „Czy Piekarnia Kowalski sp. z o.o. to firma z Krakowa?”
- „Co oferuje Piekarnia Kowalski sp. z o.o. i w jakich godzinach jest otwarta?”
- „Czy piekarniakowalski.example to oficjalna strona firmy Piekarnia Kowalski sp. z o.o.?”
- „Jaki numer rejestrowy podaje Piekarnia Kowalski sp. z o.o.?”

Granice są ważne. ABIZ pokazuje, że domena i rekord wskazują na siebie nawzajem. Nie dowodzi, że firma jest legalnie zarejestrowana, że numer rejestrowy jest prawdziwy ani że ktokolwiek ją poleca. Narzędzie, które samo nie sprawdziło KRS, nie powinno przedstawiać firmy jako zweryfikowanej. ABIZ nie gwarantuje, że jakakolwiek usługa AI znajdzie, oceni lub poleci firmę.

## 6. Praktyczne wskazówki

### Gdzie znaleźć numer

Numer KRS jest w odpisie z rejestru, na fakturach i na stronie internetowej spółki. Wyszukiwarka: [wyszukiwarka KRS](https://wyszukiwarka-krs.ms.gov.pl/). Osoby prowadzące jednoosobową działalność gospodarczą są wpisane do CEIDG, a nie do KRS, i nie mają numeru KRS. Mogą opublikować rekord bez `k`.

### Dodanie rekordu TXT

Rekord dodaje się tam, gdzie zarządzany jest DNS domeny, zwykle u rejestratora domeny lub w firmie hostingowej. Rejestrem domen `.pl` jest [NASK (dns.pl)](https://www.dns.pl/), ale rekord TXT dodaje się u swojego rejestratora lub dostawcy DNS; wystarczy dowolny, który obsługuje rekordy TXT. Proszę utworzyć rekord typu TXT o nazwie `_abiz` (niektóre panele wymagają pełnej nazwy `_abiz.piekarniakowalski.example`), z wartością dokładnie jak powyżej i TTL 300. Wartość nie może zawierać spacji; starsze rekordy ABIZ należy usunąć, tak aby został tylko jeden.

### Prywatność i publikowane dane

RODO obowiązuje dla danych osobowych w rekordzie, np. imienia i nazwiska przedsiębiorcy lub osoby kontaktowej. [Europejska Rada Ochrony Danych](https://www.edpb.europa.eu/) wskazuje krajowe organy nadzorcze; w Polsce jest to Prezes Urzędu Ochrony Danych Osobowych (UODO). Wszystko w rekordzie ABIZ jest publiczne; proszę publikować tylko dane przeznaczone do upublicznienia. Osoba prowadząca jednoosobową działalność gospodarczą nie powinna publikować adresu domowego: specyfikacja wymaga pominięcia adresów prywatnych, a nie oznaczania ich jako prywatne. Ogólny adres, np. `kontakt@`, jest lepszy niż prywatny e-mail.

## 7. Więcej informacji

- [Specyfikacja ABIZ (SPEC.md, po angielsku)](../../../SPEC.md): składnia DNS (sekcja 3.1.1), klucz `p` (sekcja 3.3), klucze firm (sekcja 4.2)
- [Normatywny schemat JSON](../../../schemas/abiz-business-record-v1.schema.json)
- [Walidator referencyjny, scripts/validate.py](../../../scripts/validate.py)
- [Wszystkie przewodniki dla Europy](index.md)
