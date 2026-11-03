# Mit ABIZ zum Agentic Business in der Schweiz

*Ein Leitfaden zu ABIZ 1.1 (veröffentlichte Spezifikation). Maßgeblich ist die [Spezifikation (SPEC.md, Englisch)](../../../SPEC.md): Weichen dieser Leitfaden und die Spezifikation voneinander ab, gilt die Spezifikation.* Die Schweiz hat vier Landessprachen; dieser Leitfaden ist auf Deutsch, der meistverwendeten Geschäftssprache. Fassungen auf Französisch, Italienisch und Rätoromanisch gibt es noch nicht.

## 1. Was das für ein Unternehmen in der Schweiz bedeutet

Immer mehr Menschen fragen KI-Assistenten nach Unternehmen: wer sie sind, was sie anbieten, wo man sie findet. Mit ABIZ (Agentic Business Record) veröffentlicht ein Unternehmen einen öffentlichen, maschinenlesbaren Eintrag mit seinen eigenen Angaben, etwa Name, Land, Website, Leistungen und Öffnungszeiten, und auf seiner eigenen Domain einen DNS-Eintrag, der auf diesen Eintrag verweist.

Nur das Unternehmen oder jemand in seinem Auftrag kann das DNS seiner Domain ändern. Deshalb kann kompatible Software den Eintrag über die Domain finden und prüfen, ob Domain und Eintrag aufeinander verweisen, statt Angaben aus verstreuten Webseiten zusammenzusuchen. ABIZ ist offen und anbieterunabhängig: Es braucht weder eine Mitgliedschaft noch Gebühren noch einen bestimmten Anbieter.

## 2. So veröffentlichen Sie einen ABIZ-Eintrag

### Pflichtfelder

Der Unternehmenseintrag ist ein JSON-Dokument, das dem [normativen Schema](../../../schemas/abiz-business-record-v1.1.schema.json) entsprechen muss. Fünf Felder sind Pflicht:

| Feld | Beispiel | Hinweise |
| --- | --- | --- |
| `record_version` | `abiz1` | Immer dieser Wert |
| `business_name` | `Uhrenatelier Keller AG` | Der öffentliche Name, meist wie im Register, mit Rechtsform, wenn Sie sie verwenden |
| `country` | `ch` | Ländercode nach ISO 3166-1 Alpha-2; kanonisch in Kleinbuchstaben |
| `identity_host` | `uhrenatelierkeller.ch.to.co` | Genau der DNS-Wert `h`: Hostname mit optionalem Pfad, ohne `https://` |
| `domains` | `["uhrenatelierkeller.example"]` | Die Domains, die dieser Eintrag beansprucht, einschließlich der Domain mit `_abiz` |

### Optionaler Unternehmensschlüssel `k`

`k` ist für jedes Unternehmen optional, ob eingetragen oder nicht. Wenn Sie `k` veröffentlichen, muss der Eintrag auch `business_key` und `registration_number` enthalten, und `k` muss `business_key` entsprechen.

In der Schweiz lautet der Schlüssel `ch-`, gefolgt von der Registernummer. Eine Untergliederung wie Bundesland oder Kanton kommt im Schlüssel nicht vor; ein Schlüssel mit Mittelteil wie `ch-xx-…` ist ungültig.

- **Register:** die kantonalen Handelsregister; jedes Unternehmen hat zusätzlich eine landesweite Unternehmens-Identifikationsnummer (UID), abrufbar über [Zefix](https://www.zefix.admin.ch/) und das [UID-Register](https://www.uid.admin.ch/)
- **Zu verwendende Nummer:** die UID ohne Satzzeichen, mit dem Präfix `CHE`. Kein Kantonskürzel: die UID ist landesweit eindeutig
- **Schreibweise:** Ausgangspunkt ist die Nummer, wie das Register sie vergibt. Wenden Sie die Unicode-Normalisierung NFKC an, entfernen Sie Leerzeichen, `-`, `.`, `/` und andere Bindestriche und schreiben Sie Buchstaben groß. Führende Nullen und Buchstabenpräfixe bleiben erhalten. Das Ergebnis darf nur ASCII-Buchstaben und -Ziffern enthalten.

Beispiel (erfundene Nummer): Aus `CHE-123.456.789` wird `CHE123456789`. Der Eintrag enthält dann `"registration_number": "CHE123456789"` und `"business_key": "ch-CHE123456789"`, im DNS steht `k=ch-CHE123456789`. Lassen Sie Zusätze wie `MWST`, `TVA` oder `IVA` weg; sie gehören zur Mehrwertsteuernummer, nicht zur UID.

Schlüssel werden ohne Beachtung der Groß- und Kleinschreibung verglichen. Veröffentlichen Sie dennoch die kanonische Form: Ländercode klein, Nummer groß.

### DNS-TXT-Eintrag

Veröffentlichen Sie genau einen ABIZ-TXT-Eintrag unter `_abiz` auf Ihrer Domain, in der kompakten Form ohne Leerzeichen:

```dns
_abiz.uhrenatelierkeller.example. 300 IN TXT "v=abiz1;k=ch-CHE123456789;h=uhrenatelierkeller.ch.to.co;p=5NEGT89sUhadAeardUi+JnqvqLgy8M4Q1qffKx4qeUA="
```

- `v=abiz1` muss am Anfang stehen. `h` und `p` sind Pflicht, `k` ist optional.
- Tag-Namen werden kleingeschrieben und unterscheiden Groß- und Kleinschreibung. Kein Tag darf doppelt vorkommen.
- Empfohlen wird eine TTL von 300 Sekunden.

Der `p`-Wert oben ist ein Wegwerf-Beispielschlüssel. Übernehmen Sie ihn nie: Veröffentlichen Sie Ihren eigenen Schlüssel oder lassen Sie `p` weg.

### Unternehmenseintrag (JSON)

Der Eintrag, der unter `https://uhrenatelierkeller.ch.to.co` als `application/json` ausgeliefert wird:

```json
{
  "record_version": "abiz1",
  "business_name": "Uhrenatelier Keller AG",
  "country": "ch",
  "business_key": "ch-CHE123456789",
  "registration_number": "CHE123456789",
  "identity_host": "uhrenatelierkeller.ch.to.co",
  "domains": [
    "uhrenatelierkeller.example"
  ],
  "public_key": "5NEGT89sUhadAeardUi+JnqvqLgy8M4Q1qffKx4qeUA=",
  "description": "Uhrenatelier in Zürich.",
  "website": "https://uhrenatelierkeller.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Zürich",
        "country": {
          "code": "CH"
        }
      },
      "public": true
    }
  ],
  "signature": "gF0uF8DE2IALxhYQi2KDGzHj0FIbhXhHoyDL3C6g5YwN036RhJRGUfi+y7898+La5tz6/63bMj9XhG86GRDmBw=="
}
```

Mit dem Referenz-Validator können Sie Eintrag und DNS-Wert lokal prüfen:

```sh
python scripts/validate.py record.json --domain uhrenatelierkeller.example --dns-value 'v=abiz1;k=ch-CHE123456789;h=uhrenatelierkeller.ch.to.co;p=5NEGT89sUhadAeardUi+JnqvqLgy8M4Q1qffKx4qeUA='
```

### Selbst hosten oder über einen Anbieter

Sie können den Eintrag selbst auf einem beliebigen HTTPS-Host bereitstellen, den Sie kontrollieren, oder einen beliebigen kompatiblen Anbieter nutzen. ABIZ schreibt weder einen Anbieter noch ein Namensschema für Hostnamen vor. In jedem Fall muss der Eintrag über HTTPS ausgeliefert werden, und Sie müssen die Domain kontrollieren, auf der `_abiz` steht.

## 3. Anbieter und MCP

MCP (Model Context Protocol) ist ein offenes Protokoll, über das KI-Assistenten Werkzeuge aufrufen und Daten von externen Servern lesen. Ein Anbieter kann einen MCP-Server betreiben, über den ein Assistent Ihren öffentlichen Eintrag direkt abruft. Einen solchen Server können Sie im optionalen Feld `mcp_server_url` angeben. ABIZ verlangt keinen MCP-Server, und ein Werkzeug sollte einen Server nicht automatisch aufrufen, nur weil er in einem Eintrag steht.

Ein Beispiel: Ein Anbieter stellt Ihren Eintrag unter `uhrenatelierkeller.ch.to.co` bereit und betreibt einen MCP-Server. Ein damit verbundener Assistent kann dann nach den Öffnungszeiten oder Leistungen von Uhrenatelier Keller AG fragen und erhält die Angaben aus Ihrem Eintrag, statt sie zu erraten.

## 4. Schlüssel und Signaturen (ABIZ 1.1)

ABIZ 1.1 verlangt einen öffentlichen Ed25519-Schlüssel im DNS-Tag `p`. `v` und `h` sind Pflicht. `p` ist Pflicht. `k` ist optional. `p` muss 32 Rohbytes in Standard-Base64 sein: 44 Zeichen, am Ende genau ein `=`, in einem einzigen DNS-String. Base64url wird nicht akzeptiert. Jeder andere Wert, etwa ein hexadezimales Token aus ABIZ 1.0, macht den ganzen Eintrag ungültig.

Der zugehörige private Schlüssel gehört dem Unternehmen und wird nie veröffentlicht. Verwahrt ein Anbieter ihn für Sie, muss er Ihnen den Export ermöglichen. Software kann eine mit dem privaten Schlüssel erstellte Signatur gegen den Schlüssel im DNS prüfen. Die Signatur deckt die RFC-8785-kanonische Form des Eintrags ohne das Mitglied `signature` ab und wird mit `public_key` geprüft, das gleich `p` sein muss (SPEC Abschnitt 4.6).

Zum Wechseln erzeugen Sie ein neues Ed25519-Schlüsselpaar, veröffentlichen den neuen öffentlichen Schlüssel in der DNS- oder Well-known-Assertion, signieren den Eintrag mit dem neuen privaten Schlüssel neu und setzen `public_key` auf dasselbe `p`. Rechnen Sie mit DNS-Cache und Propagation. Nur `p` zu entfernen ist kein gültiger Widerruf, solange die ABIZ-1.1-Assertion bestehen bleibt: Zum Zurückziehen entfernen Sie die gesamte DNS- oder Well-known-Erklärung. Ausgemusterte Schlüssel werden in ABIZ 1.1 nicht veröffentlicht, weder im DNS noch im Unternehmenseintrag. Der Schlüssel zeigt, welchen Schlüssel der Inhaber der Domain veröffentlicht hat; eine rechtliche Identität belegt er nicht.

## 5. Was KI-Werkzeuge sehen

Mit einem gültigen Eintrag kann ein kompatibler Assistent Fragen wie diese beantworten:

- „Ist Uhrenatelier Keller AG ein Unternehmen in Zürich?“
- „Was bietet Uhrenatelier Keller AG an, und wann ist geöffnet?“
- „Ist uhrenatelierkeller.example die offizielle Website von Uhrenatelier Keller AG?“
- „Welche Registernummer gibt Uhrenatelier Keller AG selbst an?“

Die Grenzen sind wichtig. ABIZ zeigt, dass eine Domain und ein Eintrag aufeinander verweisen. Es belegt nicht, dass ein Unternehmen rechtlich eingetragen ist, dass eine Registernummer echt ist oder dass jemand das Unternehmen empfiehlt. Ein Werkzeug, das das Handelsregister nicht selbst geprüft hat, darf das Unternehmen nicht als verifiziert bezeichnen. ABIZ garantiert nicht, dass ein KI-Dienst ein Unternehmen findet, einstuft oder empfiehlt.

## 6. Praktische Hinweise vor Ort

### Registernummer finden

Die UID steht im Handelsregisterauszug, auf Rechnungen und im Impressum. Sie können sie über [Zefix](https://www.zefix.admin.ch/) oder das [UID-Register](https://www.uid.admin.ch/) suchen.

### TXT-Eintrag anlegen

Legen Sie den Eintrag dort an, wo das DNS Ihrer Domain verwaltet wird, meist bei Ihrem Domain-Registrar oder Webhoster. Die Registrierungsstelle für `.ch`-Domains ist [SWITCH](https://www.nic.ch/); den Eintrag legen Sie aber bei Ihrem Registrar oder DNS-Anbieter an. Jeder Anbieter, der TXT-Einträge unterstützt, ist geeignet. Erstellen Sie einen Eintrag vom Typ TXT mit dem Namen `_abiz` (manche Oberflächen verlangen den vollen Namen `_abiz.uhrenatelierkeller.example`), dem Wert genau wie oben und einer TTL von 300. Fügen Sie innerhalb des Werts keine Leerzeichen ein und entfernen Sie ältere ABIZ-Einträge, sodass nur einer übrig bleibt.

### Datenschutz und Veröffentlichung

In der Schweiz gilt das Datenschutzgesetz (DSG) für personenbezogene Daten in Ihrem Eintrag, etwa den Namen einer Kontaktperson. Der [Eidgenössische Datenschutz- und Öffentlichkeitsbeauftragte](https://www.edoeb.admin.ch/) bietet Informationen. Bedienen Sie Kundschaft in der EU, kann zusätzlich die DSGVO gelten. Alles in einem ABIZ-Eintrag ist öffentlich; veröffentlichen Sie nur Angaben, die öffentlich sein sollen. Einzelunternehmer sollten keine Privatadresse angeben: Die Spezifikation verlangt, private Wohnadressen wegzulassen, statt sie als privat zu kennzeichnen. Eine Funktionsadresse wie `info@` ist besser als eine persönliche E-Mail-Adresse.

## 7. Weiterführende Informationen

- [ABIZ-Spezifikation (SPEC.md, Englisch)](../../../SPEC.md): DNS-Syntax (Abschnitt 3.1.1), Schlüssel `p` (Abschnitt 3.3), Unternehmensschlüssel (Abschnitt 4.2)
- [Normatives JSON-Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Referenz-Validator scripts/validate.py](../../../scripts/validate.py)
- [Alle Leitfäden für Europa](index.md)
