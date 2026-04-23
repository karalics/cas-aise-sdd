# Schritt 4 – Requirements Quality Check

**Ziel:** Konsistenz, Eindeutigkeit, Notwendigkeit und Vollständigkeit der Spezifikation (Schritte 1–3) durch eine unabhängige KI-Instanz beurteilen lassen und die Ergebnisse manuell kuratieren. Änderungen fliessen direkt in die Anforderungsliste in `03-use-cases.md` zurück.

---

## Teil A – KI-Review (unabhängiger Subagent, unverändert)

> Prompt-Kern: *"Du bist unabhängiger Reviewer. Bewerte die Spezifikation nach Konsistenz, Eindeutigkeit, Notwendigkeit, Vollständigkeit für ein MVP. Keine Datei verändern, nur Bericht liefern."*

### Zusammenfassung des Subagenten

Die Anforderungsliste ist insgesamt konsistent mit Domänenmodell und Feature-Katalog und zeigt gute Use-Case-Traceability. Sie ist jedoch für ein produktionsreifes MVP unvollständig: Es fehlen kritische Sicherheits- und Deployment-Spezifikationen (Cookie-Attribute, XSS-Schutz, Encoding, Deployment-Artefakte). Einige Anforderungen sind mehrdeutig formuliert (Zeitzone, Enter-Verhalten, Cookie-Lebensdauer). Die Notwendigkeit der Anforderungen ist gut kalibriert, wenige über-engineered.

### Befunde des Subagenten

**Konsistenz:** Keine Widersprüche gefunden. Domänenmodell, Features, Use Cases und Anforderungsliste sind durchgängig ableitbar.

**Eindeutigkeit:**

- *R11 / R17 – Zeitzone:* Format `hh:mm` ist spezifiziert, Zeitzone nicht. UTC oder Serverzeit?
- *R14 – Enter-Verhalten:* Nicht spezifiziert, ob Shift+Enter eine neue Zeile erzeugt.
- *R03 – Cookie-Attribute:* `HttpOnly`, `SameSite`, `Path`, `Max-Age` / `Expires`, `Secure` sind nicht genannt.
- *R10 – Zeichenzählung & Encoding:* Zählt raw input oder nach Escaping? HTML-Injection?
- *R18a – Platzhaltertext:* Exakte deutsche Zeichenkette nicht formal Teil der Anforderung (nur via N04).

**Notwendigkeit:** Die vorhandenen Anforderungen sind proportional; nichts offensichtlich über-engineered.

**Vollständigkeit – kritische Lücken:**

- *Deployment-Artefakte:* `requirements.txt`, `Procfile` / `render.yaml`, `PORT`-Env-Variable, Startkommando.
- *Character Encoding:* UTF-8-Deklaration im HTML.
- *XSS-Schutz:* Benutzereingaben müssen HTML-escaped gerendert werden.
- *Initialer Zustand:* Leere Nachrichtenliste beim Start ist implizit, nicht explizit.
- *Request-Grössen-Limit:* Keine Obergrenze für POST-Payloads.
- *Cookie-Scope:* Path/Domain nicht geregelt.
- *HTTP-Methoden:* N03 spricht von "einem Endpoint", aber die Anforderungen nennen GET und POST nicht explizit.
- *Logging / Observability:* Nicht geregelt.

**Explizit zu benennende Risiken/Annahmen:**

- Datenverlust bei Restart / Redeployment ist akzeptiert (In-Memory).
- Multi-Worker: In-Memory funktioniert nur mit **einem** Worker-Prozess.
- Browser-Kompatibilität von `<meta refresh>`.
- Zeitstempel-Granularität `hh:mm` kann bei schneller Abfolge mehrdeutig werden.
- Unbegrenztes Wachstum der In-Memory-Liste (Speicher-Leak).
- Auto-Linking von URLs/Mailto – nicht geregelt.

---

## Teil B – Manuelle Kuration (Entscheidungen)

Leitlinie: **MVP / TRL4, so einfach wie möglich.** Jeden Befund daraufhin prüfen, ob er für die MVP-Qualität notwendig ist oder in eine spätere Iteration verschoben werden kann.

### Akzeptierte Änderungen (führen zu Anpassungen in `03-use-cases.md`)

| Nr. | Befund | Entscheidung | Nachzug |
|-----|--------|--------------|---------|
| A1 | Zeitzone unspezifiziert (R11/R17) | Annehmen. Serverzeit in UTC, Anzeige `HH:MM` (2 Ziffern, 24 h). | R11/R17 präzisieren |
| A2 | Enter-Verhalten (R14) | Annehmen. MVP-Nachrichten sind **einzeilig**; `<input type="text">` statt `<textarea>` – damit erledigt sich das Shift+Enter-Thema. | R14 präzisieren |
| A3 | Cookie-Attribute (R03) | Teilweise annehmen. Für MVP genügt `Path=/` und `SameSite=Lax`. `HttpOnly` setzen (wir lesen den Cookie nur serverseitig). `Secure` nur in Produktion (render.com liefert HTTPS). Lebensdauer: 30 Tage. | R03 präzisieren |
| A4 | XSS-Schutz fehlt | Annehmen. Neue Anforderung R21. Flask/Jinja2 autoescaped standardmässig – wir verlangen, dass dies aktiv bleibt. | R21 (neu) |
| A5 | UTF-8-Encoding fehlt | Annehmen. Neue Anforderung R22: HTML-Header `<meta charset="utf-8">`, Response-Header `Content-Type: text/html; charset=utf-8`. | R22 (neu) |
| A6 | HTTP-Methoden explizit | Annehmen. Neue Anforderung R23: Ein einziger HTTP-Endpoint `/` beantwortet `GET` (Seite anzeigen) und `POST` (Nachricht entgegennehmen). | R23 (neu) |
| A7 | Initialer leerer Zustand | Annehmen. Neue Anforderung N06: System startet mit leerer Nachrichtenliste; Zustand geht mit Prozess verloren (bekannte Eigenschaft des MVP). | N06 (neu) |
| A8 | Deployment-Artefakte | Annehmen. Neue nicht-funktionale Anforderungen N07–N09: `requirements.txt` mit Pin-Versionen (Flask, Gunicorn); `Procfile` **oder** `render.yaml`; `PORT`-Env-Variable lesen (Fallback 5000). | N07, N08, N09 (neu) |
| A9 | Singleton-Worker | Annehmen. Neue Anforderung N10: Bereitstellung mit **genau einem** Gunicorn-Worker (`--workers 1`), weil die In-Memory-Liste sonst nicht geteilt würde. | N10 (neu) |

### Abgelehnt / verschoben (dokumentiert, aber nicht in Anforderungen übernommen)

| Nr. | Befund | Entscheidung | Begründung |
|-----|--------|--------------|------------|
| R1 | Request-Grössen-Limit | Ablehnen (für MVP). | Flask-Default `MAX_CONTENT_LENGTH=None`; in Kombination mit `maxlength`-Attributen (R14a/R14b) und Server-Validierung (R10, R02) reicht es für ein vertrauenswürdiges Unterrichtsszenario. |
| R2 | Formaler Wortlaut Platzhaltertext | Ablehnen. | R18a nennt die Zeichenfolge bereits explizit in Anführungszeichen, N04 legt Deutsch fest. Ausreichend. |
| R3 | Logging / Observability | Ablehnen (für MVP). | Render.com erfasst `stdout`/`stderr` automatisch. Flask-Default-Logging reicht. |
| R4 | Auto-Linking von URLs | Ablehnen. | Über Scope eines MVP hinaus. |
| R5 | Speicher-Leak der Nachrichtenliste | Als *Risiko* dokumentieren, aber keine Hard-Cap-Anforderung setzen. | Unterrichts­dauer << kritische Laufzeit; Restart setzt Liste ohnehin zurück. Kann in späterer Iteration adressiert werden. |
| R6 | Browser-Kompatibilität `<meta refresh>` | Als Risiko dokumentieren. | In allen gängigen Browsern funktional. Escape-Hatch wäre manuelles Reload. |
| R7 | Unterscheidung Schritt 1 (`Membership`-Klasse im Diagramm, aber ohne UI-Manifestation) | Als Hinweis dokumentieren, kein Handlungsbedarf. | Modellentscheidung aus Schritt 1 bleibt gültig; R18b stellt klar, dass *keine* UI-Meldung beim Beitritt erzeugt wird. |

---

## Teil C – Verbleibende Risiken (werden in die Architekturdoku / das Deployment-Dokument übernommen)

1. **Persistenz:** Alle Nachrichten gehen bei Prozess-Neustart (inkl. render.com Free-Tier Sleep) verloren – *akzeptiert für TRL4*.
2. **Skalierung:** In-Memory-State ist nicht prozess-übergreifend – *N10 erzwingt genau einen Worker*.
3. **Speicherwachstum:** Liste kann über die Laufzeit wachsen; für Unterrichtssitzungen unkritisch.
4. **Sichtbarkeit:** Keine Auth – jeder mit der URL kann mitlesen/schreiben. *Bewusste MVP-Entscheidung* (R06).
5. **Zeitstempel-Granularität:** `HH:MM` in UTC; bei mehreren Nachrichten derselben Minute bleibt die Reihenfolge durch die Liste erhalten, die Anzeige kann aber gleich aussehen – akzeptabel.

---

Mit dem Abschluss dieses Quality Checks und der Nachführung der Anforderungen in `03-use-cases.md` ist Schritt 4 abgeschlossen. Als Nächstes folgt Schritt 5 (minimales UI-Design als lauffähiges HTML).
