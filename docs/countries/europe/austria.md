# Mit ABIZ zum Agentic Business in Österreich

*Ein Leitfaden zu ABIZ 1.1 (Entwurf). Maßgeblich ist die [Spezifikation (SPEC.md, Englisch)](../../../SPEC.md): Weichen dieser Leitfaden und die Spezifikation voneinander ab, gilt die Spezifikation.*

## 1. Was das für ein Unternehmen in Österreich bedeutet

Immer mehr Menschen fragen KI-Assistenten nach Unternehmen: wer sie sind, was sie anbieten, wo man sie findet. Mit ABIZ (Agentic Business Record) veröffentlicht ein Unternehmen einen öffentlichen, maschinenlesbaren Eintrag mit seinen eigenen Angaben, etwa Name, Land, Website, Leistungen und Öffnungszeiten, und auf seiner eigenen Domain einen DNS-Eintrag, der auf diesen Eintrag verweist.

Nur das Unternehmen oder jemand in seinem Auftrag kann das DNS seiner Domain ändern. Deshalb kann kompatible Software den Eintrag über die Domain finden und prüfen, ob Domain und Eintrag aufeinander verweisen, statt Angaben aus verstreuten Webseiten zusammenzusuchen. ABIZ ist offen und anbieterunabhängig: Es braucht weder eine Mitgliedschaft noch Gebühren noch einen bestimmten Anbieter.

## 2. So veröffentlichen Sie einen ABIZ-Eintrag

### Pflichtfelder

Der Unternehmenseintrag ist ein JSON-Dokument, das dem [normativen Schema](../../../schemas/abiz-business-record-v1.1.schema.json) entsprechen muss. Fünf Felder sind Pflicht:

| Feld | Beispiel | Hinweise |
| --- | --- | --- |
| `record_version` | `abiz1` | Immer dieser Wert |
| `business_name` | `Tischlerei Gruber GmbH` | Der öffentliche Name, meist wie im Register, mit Rechtsform, wenn Sie sie verwenden |
| `country` | `at` | Ländercode nach ISO 3166-1 Alpha-2; kanonisch in Kleinbuchstaben |
| `identity_host` | `tischlereigruber.at.to.co` | Genau der DNS-Wert `h`: Hostname mit optionalem Pfad, ohne `https://` |
| `domains` | `["tischlereigruber.example"]` | Die Domains, die dieser Eintrag beansprucht, einschließlich der Domain mit `_abiz` |

### Optionaler Unternehmensschlüssel `k`

`k` ist für jedes Unternehmen optional, ob eingetragen oder nicht. Wenn Sie `k` veröffentlichen, muss der Eintrag auch `business_key` und `registration_number` enthalten, und `k` muss `business_key` entsprechen.

In Österreich lautet der Schlüssel `at-`, gefolgt von der Registernummer. Eine Untergliederung wie Bundesland oder Kanton kommt im Schlüssel nicht vor; ein Schlüssel mit Mittelteil wie `at-xx-…` ist ungültig.

- **Register:** Firmenbuch, geführt von den Landesgerichten (in Wien vom Handelsgericht); Abfrage über das [Unternehmensserviceportal](https://www.usp.gv.at/) und [Justiz](https://www.justiz.gv.at/)
- **Zu verwendende Nummer:** die Firmenbuchnummer: Ziffern und der Prüfbuchstabe, ohne die Abkürzung „FN“. Die Nummer ist österreichweit eindeutig
- **Schreibweise:** Ausgangspunkt ist die Nummer, wie das Register sie vergibt. Wenden Sie die Unicode-Normalisierung NFKC an, entfernen Sie Leerzeichen, `-`, `.`, `/` und andere Bindestriche und schreiben Sie Buchstaben groß. Führende Nullen und Buchstabenpräfixe bleiben erhalten. Das Ergebnis darf nur ASCII-Buchstaben und -Ziffern enthalten.

Beispiel (erfundene Nummer): Aus `FN 123456 a` wird `123456A`. Der Eintrag enthält dann `"registration_number": "123456A"` und `"business_key": "at-123456A"`, im DNS steht `k=at-123456A`. „FN“ steht nur für „Firmenbuchnummer“ und ist kein Teil der Nummer; der Prüfbuchstabe gehört dazu und wird großgeschrieben.

Schlüssel werden ohne Beachtung der Groß- und Kleinschreibung verglichen. Veröffentlichen Sie dennoch die kanonische Form: Ländercode klein, Nummer groß.

### DNS-TXT-Eintrag

Veröffentlichen Sie genau einen ABIZ-TXT-Eintrag unter `_abiz` auf Ihrer Domain, in der kompakten Form ohne Leerzeichen:

```dns
_abiz.tischlereigruber.example. 300 IN TXT "v=abiz1;k=at-123456A;h=tischlereigruber.at.to.co;p=aVJPXi80B4ympmTmnEsyjDKiU2NfUOsEDF6IybfUCxs="
```

- `v=abiz1` muss am Anfang stehen. `h` und `p` sind Pflicht, `k` ist optional.
- Tag-Namen werden kleingeschrieben und unterscheiden Groß- und Kleinschreibung. Kein Tag darf doppelt vorkommen.
- Empfohlen wird eine TTL von 300 Sekunden.

Der `p`-Wert oben ist ein Wegwerf-Beispielschlüssel. Übernehmen Sie ihn nie: Veröffentlichen Sie Ihren eigenen Schlüssel oder lassen Sie `p` weg.

### Unternehmenseintrag (JSON)

Der Eintrag, der unter `https://tischlereigruber.at.to.co` als `application/json` ausgeliefert wird:

```json
{
  "record_version": "abiz1",
  "business_name": "Tischlerei Gruber GmbH",
  "country": "at",
  "business_key": "at-123456A",
  "registration_number": "123456A",
  "identity_host": "tischlereigruber.at.to.co",
  "domains": [
    "tischlereigruber.example"
  ],
  "public_key": "aVJPXi80B4ympmTmnEsyjDKiU2NfUOsEDF6IybfUCxs=",
  "description": "Tischlerei in Graz.",
  "website": "https://tischlereigruber.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Graz",
        "country": {
          "code": "AT"
        }
      },
      "public": true
    }
  ],
  "signature": "e+NCmxy6Rju3eRfdx2mQrBktGjWyL0RzTcRqtPSyr742WCNxqTZAmS3c04+d2o4DqmZF7AaLyMKg1rmGUcVLCQ=="
}
```

Mit dem Referenz-Validator können Sie Eintrag und DNS-Wert lokal prüfen:

```sh
python scripts/validate.py record.json --domain tischlereigruber.example --dns-value 'v=abiz1;k=at-123456A;h=tischlereigruber.at.to.co;p=aVJPXi80B4ympmTmnEsyjDKiU2NfUOsEDF6IybfUCxs='
```

### Selbst hosten oder über einen Anbieter

Sie können den Eintrag selbst auf einem beliebigen HTTPS-Host bereitstellen, den Sie kontrollieren, oder einen beliebigen kompatiblen Anbieter nutzen. ABIZ schreibt weder einen Anbieter noch ein Namensschema für Hostnamen vor. In jedem Fall muss der Eintrag über HTTPS ausgeliefert werden, und Sie müssen die Domain kontrollieren, auf der `_abiz` steht.

## 3. Anbieter und MCP

MCP (Model Context Protocol) ist ein offenes Protokoll, über das KI-Assistenten Werkzeuge aufrufen und Daten von externen Servern lesen. Ein Anbieter kann einen MCP-Server betreiben, über den ein Assistent Ihren öffentlichen Eintrag direkt abruft. Einen solchen Server können Sie im optionalen Feld `mcp_server_url` angeben. ABIZ verlangt keinen MCP-Server, und ein Werkzeug sollte einen Server nicht automatisch aufrufen, nur weil er in einem Eintrag steht.

Ein Beispiel: Ein Anbieter stellt Ihren Eintrag unter `tischlereigruber.at.to.co` bereit und betreibt einen MCP-Server. Ein damit verbundener Assistent kann dann nach den Öffnungszeiten oder Leistungen von Tischlerei Gruber GmbH fragen und erhält die Angaben aus Ihrem Eintrag, statt sie zu erraten.

## 4. Schlüssel und Signaturen (ABIZ 1.1)

ABIZ 1.1 verlangt einen öffentlichen Ed25519-Schlüssel im DNS-Tag `p`. `v` und `h` sind Pflicht. `p` ist Pflicht. `k` ist optional. `p` muss 32 Rohbytes in Standard-Base64 sein: 44 Zeichen, am Ende genau ein `=`, in einem einzigen DNS-String. Base64url wird nicht akzeptiert. Jeder andere Wert, etwa ein hexadezimales Token aus ABIZ 1.0, macht den ganzen Eintrag ungültig.

Der zugehörige private Schlüssel gehört dem Unternehmen und wird nie veröffentlicht. Verwahrt ein Anbieter ihn für Sie, muss er Ihnen den Export ermöglichen. Software kann eine mit dem privaten Schlüssel erstellte Signatur gegen den Schlüssel im DNS prüfen. Die Signatur deckt die RFC-8785-kanonische Form des Eintrags ohne das Mitglied `signature` ab und wird mit `public_key` geprüft, das gleich `p` sein muss (SPEC Abschnitt 4.6).

Zum Wechseln erzeugen Sie ein neues Ed25519-Schlüsselpaar, veröffentlichen den neuen öffentlichen Schlüssel in der DNS- oder Well-known-Assertion, signieren den Eintrag mit dem neuen privaten Schlüssel neu und setzen `public_key` auf dasselbe `p`. Rechnen Sie mit DNS-Cache und Propagation. Nur `p` zu entfernen ist kein gültiger Widerruf, solange die ABIZ-1.1-Assertion bestehen bleibt: Zum Zurückziehen entfernen Sie die gesamte DNS- oder Well-known-Erklärung. Ausgemusterte Schlüssel werden in ABIZ 1.1 nicht veröffentlicht, weder im DNS noch im Unternehmenseintrag. Der Schlüssel zeigt, welchen Schlüssel der Inhaber der Domain veröffentlicht hat; eine rechtliche Identität belegt er nicht.

## 5. Was KI-Werkzeuge sehen

Mit einem gültigen Eintrag kann ein kompatibler Assistent Fragen wie diese beantworten:

- „Ist Tischlerei Gruber GmbH ein Unternehmen in Graz?“
- „Was bietet Tischlerei Gruber GmbH an, und wann ist geöffnet?“
- „Ist tischlereigruber.example die offizielle Website von Tischlerei Gruber GmbH?“
- „Welche Registernummer gibt Tischlerei Gruber GmbH selbst an?“

Die Grenzen sind wichtig. ABIZ zeigt, dass eine Domain und ein Eintrag aufeinander verweisen. Es belegt nicht, dass ein Unternehmen rechtlich eingetragen ist, dass eine Registernummer echt ist oder dass jemand das Unternehmen empfiehlt. Ein Werkzeug, das das Firmenbuch nicht selbst geprüft hat, darf das Unternehmen nicht als verifiziert bezeichnen. ABIZ garantiert nicht, dass ein KI-Dienst ein Unternehmen findet, einstuft oder empfiehlt.

## 6. Praktische Hinweise vor Ort

### Registernummer finden

Die Firmenbuchnummer steht im Firmenbuchauszug, auf Geschäftspapieren und im Impressum. Eingetragene Unternehmen sind über das [Unternehmensserviceportal](https://www.usp.gv.at/) abrufbar. Nicht protokollierte Einzelunternehmer haben keine Firmenbuchnummer und lassen den Schlüssel weg.

### TXT-Eintrag anlegen

Legen Sie den Eintrag dort an, wo das DNS Ihrer Domain verwaltet wird, meist bei Ihrem Domain-Registrar oder Webhoster. Die Registrierungsstelle für `.at`-Domains ist [nic.at](https://www.nic.at/); den Eintrag legen Sie aber bei Ihrem Registrar oder DNS-Anbieter an. Jeder Anbieter, der TXT-Einträge unterstützt, ist geeignet. Erstellen Sie einen Eintrag vom Typ TXT mit dem Namen `_abiz` (manche Oberflächen verlangen den vollen Namen `_abiz.tischlereigruber.example`), dem Wert genau wie oben und einer TTL von 300. Fügen Sie innerhalb des Werts keine Leerzeichen ein und entfernen Sie ältere ABIZ-Einträge, sodass nur einer übrig bleibt.

### Datenschutz und Veröffentlichung

In Österreich gilt die DSGVO für personenbezogene Daten in Ihrem Eintrag, etwa den Namen eines Einzelunternehmers oder einer Kontaktperson. Der [Europäische Datenschutzausschuss](https://www.edpb.europa.eu/) verlinkt die nationalen Datenschutzbehörden. Alles in einem ABIZ-Eintrag ist öffentlich; veröffentlichen Sie nur Angaben, die öffentlich sein sollen. Einzelunternehmer sollten keine Privatadresse angeben: Die Spezifikation verlangt, private Wohnadressen wegzulassen, statt sie als privat zu kennzeichnen. Eine Funktionsadresse wie `info@` ist besser als eine persönliche E-Mail-Adresse.

## 7. Weiterführende Informationen

- [ABIZ-Spezifikation (SPEC.md, Englisch)](../../../SPEC.md): DNS-Syntax (Abschnitt 3.1.1), Schlüssel `p` (Abschnitt 3.3), Unternehmensschlüssel (Abschnitt 4.2)
- [Normatives JSON-Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Referenz-Validator scripts/validate.py](../../../scripts/validate.py)
- [Alle Leitfäden für Europa](index.md)
