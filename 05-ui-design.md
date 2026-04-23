# Schritt 5 – Minimales UI-Design

**Ziel:** Ein lauffähiges HTML mit simuliertem Verhalten, das alle Anforderungen aus Schritt 3/4 abdeckt, minimal bleibt und die wichtigsten Nielsen-Usability-Heuristiken einhält. Grundlage für den Nutzertest vor Schritt 6 (Code-Generierung).

**Deliverable:** [`05-ui-mockup.html`](05-ui-mockup.html) – eine einzige Datei, kein Framework, keine externen Abhängigkeiten. Kann per Doppelklick im Browser geöffnet werden.

---

## Abdeckung der Anforderungen

| Anforderung                           | Umsetzung im Mockup |
|---------------------------------------|---------------------|
| UC1 / R01 Name erfragen               | Startansicht „Willkommen im Classroom Messenger“ mit Eingabefeld. |
| R02 / R14b Name 1–40 Zeichen, `maxlength=40` | `<input maxlength="40" required>` + Live-Zähler. |
| R03 Name persistiert                  | `localStorage` simuliert das Cookie (Wiedereintritt ohne erneute Eingabe). |
| R04 / UC5 „Name ändern“               | Link im Kopf der Chat-Ansicht führt auf das Namensformular (mit vorbelegtem Wert). |
| R05 Fallback bei fehlendem Namen       | Beim Start prüft `start()`; ohne Name → Namensformular. |
| UC2 / R07 Einziges Klassenzimmer       | Chat-Ansicht ohne Raumwahl, ein globaler Nachrichtenstrom. |
| R10 / R14a Nachricht 1–500 Zeichen     | `<input maxlength="500" required>` + Live-Zähler. |
| R11 / R17 Absender + UTC `HH:MM`       | Beim Senden erzeugt der Client `ts = new Date().toISOString()`; Anzeige via `fmtTime()` in UTC. |
| R12 Leere Nachrichten ignorieren       | Submit mit leerem Text löscht stillschweigend, keine Fehlermeldung. |
| R13 Append-only                       | Kein Edit/Delete im UI vorhanden. |
| R14 Enter oder Klick, einzeilig        | `<form>` mit `<input type="text">` (einzeilig); Enter submitted. |
| R15 / R16 Verlauf chronologisch, neueste unten | Liste wird in Einfügereihenfolge gerendert; Auto-Scroll nach unten. |
| R18 Kein JS-Framework                  | Reines Vanilla-JS, nur Standard-DOM. |
| R18a „Noch keine Nachrichten“          | Platzhalter-Element bei leerer Liste. |
| R18b Keine Beitritts-Meldungen         | Beim Betreten wird nichts in den Stream geschrieben. |
| R19 Auto-Refresh 3 s                   | `setInterval(renderMessages, 3000)` simuliert `<meta refresh>`. |
| R20 Kein WebSocket/Push                | Nur Polling/Re-Render, keine Verbindung nach aussen. |
| R21 HTML-Escape                        | `escapeHtml()` auf Namen und Nachrichtentext beim Rendern. |
| R22 UTF-8                              | `<meta charset="utf-8">` gesetzt. |
| R23 Ein Endpoint                       | Mockup simuliert nur Client-Verhalten; die Unterscheidung GET/POST wird in Schritt 6 (Flask) realisiert. Die Struktur des Formulars (`method="post"` sinngemäss, `action="/"`) ist bereits so gewählt, dass sie sich 1:1 auf `/` abbilden lässt. |
| N04 Deutschsprachig                    | Alle Texte und Beschriftungen auf Deutsch. |
| N05 Tastatur-Bedienung                 | Tab-Reihenfolge durchgängig; Enter = Senden; sichtbarer Fokus. |

**Nicht im Mockup (bewusst):** Das simulierte `<meta refresh>` ist durch ein `setInterval` ersetzt, weil ein echtes Reload in einer Mockup-Datei den State löschen würde. Im echten Flask-Deployment (Schritt 6) kommt das originale `<meta http-equiv="refresh" content="3">` zurück.

---

## Orientierung an den 10 Nielsen-Heuristiken

| Heuristik (NN/g) | Umsetzung |
|---|---|
| 1. Sichtbarkeit des Systemstatus | Zeichenzähler, Footer-Hinweis „simuliert Refresh alle 3 s“, fokussiertes Eingabefeld nach Eintritt. |
| 2. Übereinstimmung mit der realen Welt | Vertraute Chat-Metapher: Eingabe unten, Verlauf oben, eigene Nachrichten rechts bündig in hellblauer Blase. |
| 3. Nutzerkontrolle und -freiheit | „Name ändern“ jederzeit erreichbar; keine irreversiblen Aktionen. |
| 4. Konsistenz & Standards | Einheitliche Primärbutton-Farbe, einheitliche Formularhöhen, konsistente Fehleranzeige unter den Feldern. |
| 5. Fehlervermeidung | `required`, `maxlength`, `trim()` vor Validierung, Server-Validierung als zweite Stufe (in Schritt 6). |
| 6. Wiedererkennen statt Erinnern | Labels sichtbar (nicht nur Placeholder), vorbelegter Name bei UC5. |
| 7. Flexibilität & Effizienz | Enter zum Senden, Auto-Fokus, Auto-Scroll. |
| 8. Ästhetik & minimalistisches Design | Kein Logo, kein Avatar, keine Icons; einfarbige Primärfarbe, viel Weissraum. |
| 9. Fehler erkennen & beheben | ARIA-Live-Region `role="alert"` für Validierungsmeldungen; leere Nachrichten lautlos verworfen. |
| 10. Hilfe & Dokumentation | Kurze Inline-Hinweise („1–40 Zeichen“, „Enter zum Senden · max. 500 Zeichen“) direkt am Feld. |

---

## Ablaufpfade (kurz)

1. **Erster Besuch (UC1):** `localStorage` leer → Namensformular. Eingabe „Anna“ → Chat-Ansicht, Eingabefeld fokussiert.
2. **Wiederkehr (UC2):** `localStorage` enthält Namen → direkt Chat-Ansicht.
3. **Nachricht senden (UC3):** Text eingeben → Enter → Nachricht rechts bündig mit UTC-Zeit erscheint; Eingabe leert sich.
4. **Fremde Nachrichten mitverfolgen (UC4):** Der Button „Testnachricht eines anderen Teilnehmers“ simuliert eine fremde Einlieferung; Auto-Scroll nach unten.
5. **Name ändern (UC5):** Klick auf „Name ändern“ → Namensformular mit vorbelegtem Wert → Bestätigen → Chat-Ansicht.
6. **Zustand zurücksetzen:** Debug-Button im Footer löscht `localStorage` und die In-Memory-Liste.

---

## Nutzertest – Leitfaden

**Setup:** `05-ui-mockup.html` lokal im Browser öffnen (Doppelklick).

**Tasks für Testperson (ca. 5 Min.):**

1. „Stell dir vor, du öffnest die Anwendung zum ersten Mal und willst unter deinem Vornamen mitschreiben. Bitte lege los.“
2. „Schreibe eine kurze Nachricht an die Klasse und schicke sie ab.“
3. „Warte einige Sekunden und drücke dann ‚Testnachricht eines anderen Teilnehmers‘. Was beobachtest du?“
4. „Stelle dir vor, du willst dich anders nennen. Finde heraus, wie das geht.“
5. „Versuche, eine leere Nachricht zu senden. Was passiert? Versuche, 501 Zeichen einzugeben. Was passiert?“

**Beobachtungsfokus:**

- Wie schnell erkennt die Testperson, wo sie schreiben soll?
- Ist die Rolle der „Testnachricht“-Schaltfläche klar als Simulations­hilfe erkennbar (soll sie sein)?
- Funktioniert das Senden per Enter intuitiv?
- Werden Zeichenzähler beachtet? Sind sie hilfreich oder ablenkend?
- Ist die UTC-Zeit verständlich oder verwirrend?

**Erwartete Findings, die in Schritt 6 einfliessen:**

- Ggf. Zeitzone auf Browser-Zeit umstellen (falls UTC regelmässig irritiert).
- Ggf. Platzhalter im Eingabefeld („Nachricht schreiben …“) prägnanter formulieren.
- Ggf. den „Testnachricht“-Knopf optisch stärker als Dev-Element markieren (aktuell: gestrichelter Rahmen im Footer).

---

Mit diesem lauffähigen Mockup ist Schritt 5 abgeschlossen; Schritt 6 (Flask-Code + Deployment) kann direkt darauf aufsetzen, indem das Markup in ein Jinja-Template umgezogen und die In-Memory-Liste serverseitig gehalten wird.
