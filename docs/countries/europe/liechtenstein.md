# Mit ABIZ zum Agentic Business in Liechtenstein

*Ein Leitfaden zu ABIZ 1.1 (veröffentlichte Spezifikation). Maßgeblich ist die [Spezifikation (SPEC.md, Englisch)](../../../SPEC.md): Weichen dieser Leitfaden und die Spezifikation voneinander ab, gilt die Spezifikation.*

## 1. Was das für ein Unternehmen in Liechtenstein bedeutet

Immer mehr Menschen fragen KI-Assistenten nach Unternehmen: wer sie sind, was sie anbieten, wo man sie findet. Mit ABIZ (Agentic Business Record) veröffentlicht ein Unternehmen einen öffentlichen, maschinenlesbaren Eintrag mit seinen eigenen Angaben, etwa Name, Land, Website, Leistungen und Öffnungszeiten, und auf seiner eigenen Domain einen DNS-Eintrag, der auf diesen Eintrag verweist.

Nur das Unternehmen oder jemand in seinem Auftrag kann das DNS seiner Domain ändern. Deshalb kann kompatible Software den Eintrag über die Domain finden und prüfen, ob Domain und Eintrag aufeinander verweisen, statt Angaben aus verstreuten Webseiten zusammenzusuchen. ABIZ ist offen und anbieterunabhängig: Es braucht weder eine Mitgliedschaft noch Gebühren noch einen bestimmten Anbieter.

## 2. So veröffentlichen Sie einen ABIZ-Eintrag

### Pflichtfelder

Der Unternehmenseintrag ist ein JSON-Dokument, das dem [normativen Schema](../../../schemas/abiz-business-record-v1.1.schema.json) entsprechen muss. Fünf Felder sind Pflicht:

| Feld | Beispiel | Hinweise |
| --- | --- | --- |
| `record_version` | `abiz1` | Immer dieser Wert |
| `business_name` | `Rheintal Treuhand AG` | Der öffentliche Name, meist wie im Register, mit Rechtsform, wenn Sie sie verwenden |
| `country` | `li` | Ländercode nach ISO 3166-1 Alpha-2; kanonisch in Kleinbuchstaben |
| `identity_host` | `rheintaltreuhand.li.to.co` | Genau der DNS-Wert `h`: Hostname mit optionalem Pfad, ohne `https://` |
| `domains` | `["rheintaltreuhand.example"]` | Die Domains, die dieser Eintrag beansprucht, einschließlich der Domain mit `_abiz` |

### Optionaler Unternehmensschlüssel `k`

`k` ist für jedes Unternehmen optional, ob eingetragen oder nicht. Wenn Sie `k` veröffentlichen, muss der Eintrag auch `business_key` und `registration_number` enthalten, und `k` muss `business_key` entsprechen.

In Liechtenstein lautet der Schlüssel `li-`, gefolgt von der Registernummer. Eine Untergliederung wie Bundesland oder Kanton kommt im Schlüssel nicht vor; ein Schlüssel mit Mittelteil wie `li-xx-…` ist ungültig.

- **Register:** Handelsregister, geführt vom Amt für Justiz der [Liechtensteinischen Landesverwaltung](https://www.llv.li/)
- **Zu verwendende Nummer:** die Registernummer im Format `FL-0002.123.456-7`, mit dem Präfix `FL`
- **Schreibweise:** Ausgangspunkt ist die Nummer, wie das Register sie vergibt. Wenden Sie die Unicode-Normalisierung NFKC an, entfernen Sie Leerzeichen, `-`, `.`, `/` und andere Bindestriche und schreiben Sie Buchstaben groß. Führende Nullen und Buchstabenpräfixe bleiben erhalten. Das Ergebnis darf nur ASCII-Buchstaben und -Ziffern enthalten.

Beispiel (erfundene Nummer): Aus `FL-0002.123.456-7` wird `FL00021234567`. Der Eintrag enthält dann `"registration_number": "FL00021234567"` und `"business_key": "li-FL00021234567"`, im DNS steht `k=li-FL00021234567`. Das Präfix `FL` gehört zur Nummer und bleibt erhalten.

Schlüssel werden ohne Beachtung der Groß- und Kleinschreibung verglichen. Veröffentlichen Sie dennoch die kanonische Form: Ländercode klein, Nummer groß.

### DNS-TXT-Eintrag

Veröffentlichen Sie genau einen ABIZ-TXT-Eintrag unter `_abiz` auf Ihrer Domain, in der kompakten Form ohne Leerzeichen:

```dns
_abiz.rheintaltreuhand.example. 300 IN TXT "v=abiz1;k=li-FL00021234567;h=rheintaltreuhand.li.to.co;p=DuFRKPJJTmMVtOwMeETxZpK8p13mD6dMOqihbJGQMX8="
```

- `v=abiz1` muss am Anfang stehen. `h` und `p` sind Pflicht, `k` ist optional.
- Tag-Namen werden kleingeschrieben und unterscheiden Groß- und Kleinschreibung. Kein Tag darf doppelt vorkommen.
- Empfohlen wird eine TTL von 300 Sekunden.

Der `p`-Wert oben ist ein Wegwerf-Beispielschlüssel. Übernehmen Sie ihn nie: Veröffentlichen Sie Ihren eigenen Schlüssel. Eine ABIZ-1.1-Assertion muss `p` enthalten.

### Unternehmenseintrag (JSON)

Der Eintrag, der unter `https://rheintaltreuhand.li.to.co` als `application/json` ausgeliefert wird:

```json
{
  "record_version": "abiz1",
  "business_name": "Rheintal Treuhand AG",
  "country": {
    "code": "LI",
    "name": "Liechtenstein"
  },
  "business_key": "li-FL00021234567",
  "registration_number": "FL00021234567",
  "identity_host": "rheintaltreuhand.li.to.co",
  "domains": [
    "rheintaltreuhand.example"
  ],
  "public_key": "DuFRKPJJTmMVtOwMeETxZpK8p13mD6dMOqihbJGQMX8=",
  "description": "Treuhandb\u00fcro in Vaduz.",
  "website": "https://rheintaltreuhand.example",
  "locations": [
    {
      "kind": "trading",
      "address": {
        "locality": "Vaduz",
        "country": {
          "code": "LI"
        }
      },
      "public": true
    }
  ],
  "signature": "h4FJGi4gSxziFDOmY6Fdi/r+cB+df6TSHAAC+6rvWeUpq36KZp/z7m9n46rshWC778rbhtB+Y5N93sOf8N20BQ=="
}
```

Mit dem Referenz-Validator können Sie Eintrag und DNS-Wert lokal prüfen:

```sh
python scripts/validate.py record.json --domain rheintaltreuhand.example --dns-value 'v=abiz1;k=li-FL00021234567;h=rheintaltreuhand.li.to.co;p=DuFRKPJJTmMVtOwMeETxZpK8p13mD6dMOqihbJGQMX8='
```

### Selbst hosten oder über einen Anbieter

Sie können den Eintrag selbst auf einem beliebigen HTTPS-Host bereitstellen, den Sie kontrollieren, oder einen beliebigen kompatiblen Anbieter nutzen. ABIZ schreibt weder einen Anbieter noch ein Namensschema für Hostnamen vor. In jedem Fall muss der Eintrag über HTTPS ausgeliefert werden, und Sie müssen die Domain kontrollieren, auf der `_abiz` steht.

## 3. Anbieter und MCP

MCP (Model Context Protocol) ist ein offenes Protokoll, über das KI-Assistenten Werkzeuge aufrufen und Daten von externen Servern lesen. Ein Anbieter kann einen MCP-Server betreiben, über den ein Assistent Ihren öffentlichen Eintrag direkt abruft. Einen solchen Server können Sie im optionalen Feld `mcp_server_url` angeben. ABIZ verlangt keinen MCP-Server, und ein Werkzeug sollte einen Server nicht automatisch aufrufen, nur weil er in einem Eintrag steht.

Ein Beispiel: Ein Anbieter stellt Ihren Eintrag unter `rheintaltreuhand.li.to.co` bereit und betreibt einen MCP-Server. Ein damit verbundener Assistent kann dann nach den Öffnungszeiten oder Leistungen von Rheintal Treuhand AG fragen und erhält die Angaben aus Ihrem Eintrag, statt sie zu erraten.

## 4. Schlüssel und Signaturen (ABIZ 1.1)

ABIZ 1.1 verlangt einen öffentlichen Ed25519-Schlüssel im DNS-Tag `p`. `v` und `h` sind Pflicht. `p` ist Pflicht. `k` ist optional. `p` muss 32 Rohbytes in Standard-Base64 sein: 44 Zeichen, am Ende genau ein `=`, in einem einzigen DNS-String. Base64url wird nicht akzeptiert. Jeder andere Wert, etwa eine hexadezimale Zeichenkette, macht den ganzen Eintrag ungültig.

Der zugehörige private Schlüssel gehört dem Unternehmen und wird nie veröffentlicht. Verwahrt ein Anbieter ihn für Sie, muss er Ihnen den Export ermöglichen. Software kann eine mit dem privaten Schlüssel erstellte Signatur gegen den Schlüssel im DNS prüfen. Die Signatur deckt die RFC-8785-kanonische Form des Eintrags ohne das Mitglied `signature` ab und wird mit `public_key` geprüft, das gleich `p` sein muss (SPEC Abschnitt 4.6).

Zum Wechseln erzeugen Sie ein neues Ed25519-Schlüsselpaar, veröffentlichen den neuen öffentlichen Schlüssel in der DNS- oder Well-known-Assertion, signieren den Eintrag mit dem neuen privaten Schlüssel neu und setzen `public_key` auf dasselbe `p`. Rechnen Sie mit DNS-Cache und Propagation. Nur `p` zu entfernen ist kein gültiger Widerruf, solange die ABIZ-1.1-Assertion bestehen bleibt: Zum Zurückziehen entfernen Sie die gesamte DNS- oder Well-known-Erklärung. Ausgemusterte Schlüssel werden in ABIZ 1.1 nicht veröffentlicht, weder im DNS noch im Unternehmenseintrag. Der Schlüssel zeigt, welchen Schlüssel der Inhaber der Domain veröffentlicht hat; eine rechtliche Identität belegt er nicht.

## 5. Was KI-Werkzeuge sehen

Mit einem gültigen Eintrag kann ein kompatibler Assistent Fragen wie diese beantworten:

- „Ist Rheintal Treuhand AG ein Unternehmen in Vaduz?“
- „Was bietet Rheintal Treuhand AG an, und wann ist geöffnet?“
- „Ist rheintaltreuhand.example die offizielle Website von Rheintal Treuhand AG?“
- „Welche Registernummer gibt Rheintal Treuhand AG selbst an?“

Die Grenzen sind wichtig. ABIZ zeigt, dass eine Domain und ein Eintrag aufeinander verweisen. Es belegt nicht, dass ein Unternehmen rechtlich eingetragen ist, dass eine Registernummer echt ist oder dass jemand das Unternehmen empfiehlt. Ein Werkzeug, das das Handelsregister nicht selbst geprüft hat, darf das Unternehmen nicht als verifiziert bezeichnen. ABIZ garantiert nicht, dass ein KI-Dienst ein Unternehmen findet, einstuft oder empfiehlt.

## 6. Praktische Hinweise vor Ort

### Registernummer finden

Die Registernummer steht im Handelsregisterauszug. Das Amt für Justiz bietet eine Online-Abfrage des Handelsregisters an.

### TXT-Eintrag anlegen

Legen Sie den Eintrag dort an, wo das DNS Ihrer Domain verwaltet wird, meist bei Ihrem Domain-Registrar oder Webhoster. Die Registrierungsstelle für `.li`-Domains ist [SWITCH](https://www.nic.li/); den Eintrag legen Sie aber bei Ihrem Registrar oder DNS-Anbieter an. Jeder Anbieter, der TXT-Einträge unterstützt, ist geeignet. Erstellen Sie einen Eintrag vom Typ TXT mit dem Namen `_abiz` (manche Oberflächen verlangen den vollen Namen `_abiz.rheintaltreuhand.example`), dem Wert genau wie oben und einer TTL von 300. Fügen Sie innerhalb des Werts keine Leerzeichen ein und entfernen Sie ältere ABIZ-Einträge, sodass nur einer übrig bleibt.

### Datenschutz und Veröffentlichung

Liechtenstein gehört zum Europäischen Wirtschaftsraum; die DSGVO gilt für personenbezogene Daten in Ihrem Eintrag, etwa den Namen einer Kontaktperson. Der [Europäische Datenschutzausschuss](https://www.edpb.europa.eu/) verlinkt die nationalen Datenschutzbehörden. Alles in einem ABIZ-Eintrag ist öffentlich; veröffentlichen Sie nur Angaben, die öffentlich sein sollen. Einzelunternehmer sollten keine Privatadresse angeben: Die Spezifikation verlangt, private Wohnadressen wegzulassen, statt sie als privat zu kennzeichnen. Eine Funktionsadresse wie `info@` ist besser als eine persönliche E-Mail-Adresse.

## 7. Weiterführende Informationen

- [ABIZ-Spezifikation (SPEC.md, Englisch)](../../../SPEC.md): DNS-Syntax (Abschnitt 3.1.1), Schlüssel `p` (Abschnitt 3.3), Unternehmensschlüssel (Abschnitt 4.2)
- [Normatives JSON-Schema](../../../schemas/abiz-business-record-v1.1.schema.json)
- [Referenz-Validator scripts/validate.py](../../../scripts/validate.py)
- [Alle Leitfäden für Europa](index.md)
