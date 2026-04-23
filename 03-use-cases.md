# Schritt 3 – Use Cases & vollständige Anforderungsliste

**Ziel:** Interaktionsszenarien zwischen Nutzenden und System als Use Cases beschreiben und daraus eine konsolidierte, vollständige Liste funktionaler Anforderungen ableiten.

**Grundlagen:**

- Spezifikation (`specification.md` im Repo `classroom-chat`)
- Domänenmodell Schritt 1 (`domain-model.puml` / `domain-model.md`, Revision *ohne `Role`*)
- Feature-Katalog Schritt 2 (`02-features.md`, finalisiert nach Peer-Review)

**Methodik:** UML-Use-Case-Ansatz (Akteur, Auslöser, Vorbedingungen, Hauptablauf, Alternativen/Ausnahmen, Nachbedingungen); Anforderungen werden direkt aus den Schritten abgeleitet und mit einer stabilen ID versehen.

---

## Akteure

| Akteur | Beschreibung |
|---|---|
| **Teilnehmer/in** | Jede Person, die den Classroom-Messenger im Browser nutzt. Im MVP gibt es keine Rollenunterscheidung; Lehrpersonen und Lernende sind aus Systemsicht identisch. |
| **System (Classroom Messenger)** | Die Flask-Anwendung mit In-Memory-Haltung. Rendert HTML, nimmt Nachrichten entgegen, liefert den Verlauf aus. |

*Kein externer Systemakteur (keine Datenbank, kein Auth-Provider, kein Push-Dienst).*

---

## Use-Case-Übersicht

| ID  | Name                                | Primärer Akteur      | Bezug Features     |
|-----|-------------------------------------|----------------------|--------------------|
| UC1 | Anzeigenamen festlegen              | Teilnehmer/in        | F1                 |
| UC2 | Klassenzimmer öffnen                | Teilnehmer/in        | F2, F4, F5         |
| UC3 | Nachricht senden                    | Teilnehmer/in        | F3, F4             |
| UC4 | Neue Nachrichten mitverfolgen       | Teilnehmer/in        | F4, F5             |
| UC5 | Anzeigenamen ändern                 | Teilnehmer/in        | F1                 |

```
     ┌────────────────────────────────────────┐
     │         Classroom Messenger            │
     │                                        │
     │   (UC1) Anzeigenamen festlegen         │
     │   (UC2) Klassenzimmer öffnen           │
  ●──┤   (UC3) Nachricht senden               │
 /|\ │   (UC4) Neue Nachrichten mitverfolgen  │
  │  │   (UC5) Anzeigenamen ändern            │
 / \ │                                        │
     └────────────────────────────────────────┘
  Teilnehmer/in
```

---

## UC1 – Anzeigenamen festlegen

- **Primärer Akteur:** Teilnehmer/in
- **Auslöser:** Erster Aufruf der Applikation im Browser (kein Namens-Cookie vorhanden).
- **Vorbedingung:** Applikation ist über ihre URL erreichbar.
- **Nachbedingung (Erfolg):** Anzeigename ist im Browser gespeichert (Cookie); Teilnehmer/in sieht den Chatverlauf.
- **Hauptablauf:**
  1. System zeigt eine Seite mit einem Eingabefeld „Anzeigename“ und Button „Betreten“.
  2. Teilnehmer/in gibt einen Namen ein (1–40 Zeichen).
  3. Teilnehmer/in klickt *Betreten* (oder drückt *Enter*).
  4. System validiert den Namen (nicht leer, Längenbegrenzung).
  5. System speichert den Namen als Cookie im Browser.
  6. System leitet weiter auf die Chat-Ansicht (UC2).
- **Alternativabläufe:**
  - *A1 – Cookie vorhanden:* Bei Schritt 1 erkennt das System den bestehenden Cookie und überspringt direkt zu UC2.
- **Ausnahmen:**
  - *E1 – Name leer:* System zeigt die Seite erneut mit Hinweis „Name darf nicht leer sein“.
  - *E2 – Name zu lang:* System kürzt oder weist zurück mit Hinweis „max. 40 Zeichen“.

---

## UC2 – Klassenzimmer öffnen

- **Primärer Akteur:** Teilnehmer/in
- **Auslöser:** Aufruf der Chat-URL mit vorhandenem Namens-Cookie, oder Weiterleitung aus UC1.
- **Vorbedingung:** Anzeigename ist festgelegt (Cookie gesetzt).
- **Nachbedingung:** Teilnehmer/in sieht den aktuellen Nachrichtenverlauf des einen globalen Klassenzimmers und ein Eingabeformular.
- **Hauptablauf:**
  1. System liest den Namen aus dem Cookie.
  2. System ruft den aktuellen Nachrichtenverlauf des globalen Klassenzimmers ab (In-Memory-Liste).
  3. System rendert die Chat-Seite: Kopf (Titel, angemeldeter Name, „Name ändern“-Link), Nachrichtenliste (neueste unten), Eingabeformular, Meta-Refresh alle 3 Sekunden.
  4. Browser zeigt die Seite an.
- **Ausnahmen:**
  - *E1 – Kein Name/Cookie:* System leitet auf UC1 (Name festlegen) um.

---

## UC3 – Nachricht senden

- **Primärer Akteur:** Teilnehmer/in
- **Auslöser:** Teilnehmer/in möchte etwas beitragen.
- **Vorbedingung:** UC2 wurde durchlaufen; Chat-Seite ist offen.
- **Nachbedingung:** Die neue Nachricht ist an den Klassenzimmer-Verlauf angehängt und für alle Teilnehmenden beim nächsten Aktualisierungs­intervall sichtbar.
- **Hauptablauf:**
  1. Teilnehmer/in tippt Text (1–500 Zeichen) in das Eingabefeld.
  2. Teilnehmer/in klickt *Senden* (oder drückt *Enter*).
  3. Browser schickt ein `POST` an den Applikations-Endpoint, inklusive Cookie (Name) und Nachrichtentext.
  4. System validiert den Text (nicht leer, max. 500 Zeichen).
  5. System legt ein neues `Message`-Objekt an (Absender aus Cookie, Zeitstempel = Server-UTC-Zeit, angezeigt im Format `hh:mm`) und hängt es an die In-Memory-Liste des Klassenzimmers an.
  6. System antwortet mit einer neu gerenderten Chat-Seite (Redirect/Reload auf dieselbe Route), die die neue Nachricht enthält.
- **Ausnahmen:**
  - *E1 – Leerer Text:* Nachricht wird verworfen; Chat-Seite wird unverändert neu gerendert.
  - *E2 – Text zu lang:* System kürzt auf 500 Zeichen oder weist mit Hinweis ab.
  - *E3 – Kein Name im Cookie:* System leitet auf UC1 um.

---

## UC4 – Neue Nachrichten mitverfolgen

- **Primärer Akteur:** Teilnehmer/in (passiv)
- **Auslöser:** Chat-Seite ist geöffnet; 3-Sekunden-Timer läuft.
- **Vorbedingung:** UC2 wurde durchlaufen.
- **Nachbedingung:** Teilnehmer/in sieht zwischenzeitlich eingetroffene Nachrichten.
- **Hauptablauf:**
  1. Browser interpretiert `<meta http-equiv="refresh" content="3">` und lädt die Seite alle 3 Sekunden neu.
  2. System liefert den aktuellen Verlauf (UC2, Schritte 1–3).
  3. Neue Nachrichten anderer Teilnehmer/innen erscheinen am unteren Ende.
- **Ausnahmen:**
  - *E1 – Netzwerk-/Server-Ausfall:* Browser zeigt eine Fehlerseite; beim nächsten erfolgreichen Reload läuft UC2 wieder normal.

---

## UC5 – Anzeigenamen ändern

- **Primärer Akteur:** Teilnehmer/in
- **Auslöser:** Teilnehmer/in möchte unter einem anderen Namen auftreten.
- **Vorbedingung:** Chat-Seite ist offen (UC2).
- **Nachbedingung:** Der Cookie ist mit dem neuen Namen überschrieben.
- **Hauptablauf:**
  1. Teilnehmer/in klickt im Kopf auf „Name ändern“.
  2. System zeigt die Namensseite aus UC1; das Eingabefeld ist mit dem bisherigen Namen vorbelegt (kein zusätzlicher Hinweistext).
  3. Teilnehmer/in passt den Namen an und bestätigt.
  4. System validiert, setzt den Cookie neu und leitet auf die Chat-Seite zurück.

---

## Konsolidierte Liste funktionaler Anforderungen

*Jede Anforderung ist mit der/den Use-Cases und dem Feature verknüpft. `MUSS` = MVP-kritisch.*

### Identität & Sitzung

| ID   | Anforderung                                                                                                    | Quelle         |
|------|----------------------------------------------------------------------------------------------------------------|----------------|
| R01  | Das System MUSS beim ersten Aufruf einen Anzeigenamen erfragen.                                                | UC1, F1        |
| R02  | Der Anzeigename MUSS zwischen 1 und 40 Zeichen lang sein.                                                       | UC1, F1        |
| R03  | Das System MUSS den Anzeigenamen als Cookie mit `Path=/`, `SameSite=Lax`, `HttpOnly` und einer Lebensdauer von 30 Tagen setzen (`Secure` in der Produktion auf render.com). | UC1, UC2, F1 |
| R04  | Das System MUSS die Änderung des Anzeigenamens über eine sichtbare Aktion („Name ändern“) ermöglichen.          | UC5, F1        |
| R05  | Das System MUSS bei fehlendem Namen auf die Namenseingabe umleiten.                                            | UC2, UC3, F1   |
| R06  | Das System DARF KEINE Registrierung, kein Passwort und keine Rolle verlangen.                                  | F1, Abgrenzung |

### Klassenzimmer

| ID   | Anforderung                                                                                                    | Quelle       |
|------|----------------------------------------------------------------------------------------------------------------|--------------|
| R07  | Das System MUSS genau ein globales Klassenzimmer bereitstellen.                                                | UC2, F2      |
| R08  | Das Klassenzimmer MUSS dieselbe Nachrichtenliste für alle Teilnehmenden führen.                                | UC2–UC4, F2  |
| R09  | Nachrichten MÜSSEN im Prozess-Speicher gehalten werden (keine Datenbank, nicht persistent).                    | F2, NFA      |

### Nachrichten senden

| ID   | Anforderung                                                                                                    | Quelle      |
|------|----------------------------------------------------------------------------------------------------------------|-------------|
| R10  | Das System MUSS Textnachrichten von 1 bis 500 Zeichen annehmen.                                                | UC3, F3     |
| R11  | Das System MUSS zu jeder Nachricht den Absender (aus dem Cookie) und einen Server-Zeitstempel in UTC ergänzen (Anzeige im Format `HH:MM`, 24 h). | UC3, F3 |
| R12  | Leere Nachrichten MÜSSEN ohne Fehler ignoriert werden.                                                         | UC3 E1, F3  |
| R13  | Nachrichten MÜSSEN append-only sein (kein Bearbeiten, kein Löschen im MVP).                                    | F3, Abgrenzung |
| R14  | Das Senden MUSS per Klick auf „Senden“ oder mit *Enter* möglich sein. Nachrichten sind **einzeilig** (`<input type="text">`, keine Zeilenumbrüche). | UC3, F3 |
| R14a | Das Eingabefeld für Nachrichten MUSS clientseitig via `maxlength="500"` begrenzt sein (zusätzlich zur Servervalidierung). | UC3, F3 |
| R14b | Das Eingabefeld für den Anzeigenamen MUSS clientseitig via `maxlength="40"` begrenzt sein (zusätzlich zur Servervalidierung). | UC1, UC5, F1 |

### Nachrichten anzeigen

| ID   | Anforderung                                                                                                    | Quelle   |
|------|----------------------------------------------------------------------------------------------------------------|----------|
| R15  | Das System MUSS den vollständigen Nachrichtenverlauf des Klassenzimmers anzeigen.                              | UC2, F4  |
| R16  | Die Sortierung MUSS chronologisch sein, neueste Nachricht unten.                                               | UC2, F4  |
| R17  | Je Nachricht MÜSSEN Absender, Uhrzeit (Format `HH:MM` UTC) und Text dargestellt werden.                        | UC2, F4  |
| R18  | Die Anzeige MUSS ohne JavaScript-Framework funktionieren (reines HTML).                                         | F4, NFA  |
| R18a | Ist die Nachrichtenliste leer, MUSS der Platzhaltertext „Noch keine Nachrichten“ angezeigt werden.             | UC2, F4  |
| R18b | Das System DARF KEINE Beitritts-/Verlassen-Meldungen („X ist beigetreten“) in den Verlauf einfügen.            | F2, Abgrenzung |

### Aktualisierung

| ID   | Anforderung                                                                                                    | Quelle   |
|------|----------------------------------------------------------------------------------------------------------------|----------|
| R19  | Die Chat-Ansicht MUSS sich ohne Benutzeraktion etwa alle 3 Sekunden mit neuen Nachrichten aktualisieren und dabei **weder Eingabe noch Scroll-Position zurücksetzen**. Implementiert als minimales Vanilla-JS-Polling auf denselben Endpoint `/`; das ursprünglich vorgesehene `<meta http-equiv="refresh">` wurde verworfen, weil es das Eingabefeld während des Tippens löschte (Finding nach Deployment). | UC4, F5 |
| R20  | Die Aktualisierung DARF KEINEN Push-/WebSocket-Dienst voraussetzen und KEIN JavaScript-Framework einbinden (reines Vanilla-JS ist erlaubt). | F5, NFA |

### Sicherheit & Encoding (ergänzt durch Schritt 4)

| ID   | Anforderung                                                                                                    | Quelle   |
|------|----------------------------------------------------------------------------------------------------------------|----------|
| R21  | Das System MUSS alle Benutzereingaben (Anzeigename, Nachrichtentext) beim Rendern HTML-escapen (Jinja2-Autoescape aktiv). | Schritt 4 |
| R22  | Das System MUSS UTF-8 als Zeichenkodierung verwenden (`<meta charset="utf-8">` und `Content-Type: text/html; charset=utf-8`). | Schritt 4 |
| R23  | Das System MUSS einen einzigen HTTP-Endpoint `/` bereitstellen, der `GET` (Seite anzeigen) und `POST` (Nachricht entgegennehmen) verarbeitet. | Schritt 4, N03 |

### Nicht-funktionale Rahmenbedingungen (zur Erinnerung)

| ID   | Anforderung                                                                                                    | Quelle |
|------|----------------------------------------------------------------------------------------------------------------|--------|
| N01  | Die Applikation MUSS auf render.com mit `gunicorn app:app` lauffähig sein.                                     | Spez.  |
| N02  | Der Applikationscode SOLLTE in einer einzelnen Python-Datei (`app.py`) leserlich bleiben.                      | Spez.  |
| N03  | Die Applikation SOLL mit genau einem HTTP-Endpoint auskommen (GET zeigt Seite, POST sendet Nachricht, beide auf `/`). | Spez.  |
| N04  | Das UI MUSS deutschsprachig sein.                                                                              | Spez.  |
| N05  | Die Bedienung MUSS per Tastatur möglich sein (Tab/Enter).                                                      | NFA    |
| N06  | Das System MUSS beim Start mit einer leeren Nachrichtenliste beginnen; der Zustand geht mit dem Prozess verloren. | Schritt 4 |
| N07  | Das Repo MUSS eine `requirements.txt` mit gepinnten Versionen für Flask und Gunicorn enthalten.                | Schritt 4 |
| N08  | Das Repo MUSS eine render.com-konforme Startkonfiguration enthalten (`render.yaml` oder `Procfile` mit `gunicorn app:app`). | Schritt 4 |
| N09  | Die Applikation MUSS den Port aus der Umgebungsvariable `PORT` lesen (Fallback `5000`).                        | Schritt 4 |
| N10  | Das Deployment MUSS mit genau einem Gunicorn-Worker erfolgen (`--workers 1`), weil die In-Memory-Liste sonst nicht geteilt wird. | Schritt 4 |

---

## Rückverfolgbarkeit Use Cases ↔ Anforderungen ↔ DDD

| Use Case | Anforderungen                   | DDD-Klassen                    |
|----------|---------------------------------|--------------------------------|
| UC1      | R01, R02, R03, R14b, R21, R22, R23 | `User`                         |
| UC2      | R05, R07, R08, R15–R18, R18a, R18b, R21, R22, R23 | `User`, `Classroom`, `Message` |
| UC3      | R05, R10–R14, R14a, R21, R23    | `User`, `Classroom`, `Message` |
| UC4      | R19, R20, R23                   | `Classroom`, `Message`         |
| UC5      | R02, R03, R04, R14b, R23        | `User`                         |

---

## Peer-Review – Ergebnisse (✓ = erledigt)

1. ✓ **Anzeige Zeitstempel** → Serverzeit, Format `hh:mm` (R11, R17).
2. ✓ **Name ändern (UC5)** → Eingabefeld mit bisherigem Namen vorbelegt, kein zusätzlicher Hinweistext.
3. ✓ **System-Meldungen** → Keine „X ist beigetreten“-Einträge im Verlauf (R18b).
4. ✓ **Leere Chat-Liste** → Platzhaltertext „Noch keine Nachrichten“ (R18a).
5. ✓ **Längenbegrenzung clientseitig** → `maxlength="500"` für Nachricht (R14a) und `maxlength="40"` für Name (R14b).
6. ✓ **Einheitliches Styling** → Wird erst in Schritt 5 (UI-Design) festgelegt.

Mit diesen Festlegungen ist Schritt 3 abgeschlossen und Schritt 4 (Requirements Quality Check durch KI) kann beginnen.
