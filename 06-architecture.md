# Schritt 6 – Architektur & Deployment (TRL4-Prototyp)

**Ziel:** Lauffähige Applikation inklusive knapper Architekturdokumentation und Deployment-Anleitung auf render.com. Die Architektur ist bewusst minimal und entspricht der Spezifikation „so einfach wie möglich, in-memory, ein Endpoint“.

---

## Zweck

Ein webbasierter Klassenzimmer-Messenger, in dem Teilnehmer/innen kurze Textnachrichten in einem einzigen, gemeinsam genutzten Raum austauschen. Kein Login, keine Datenbank, kein Push-Dienst. Nachrichten gehen mit einem Prozess-Neustart verloren – das ist für den TRL4-Prototyp akzeptiert.

---

## Komponenten

| Komponente            | Rolle                                                                 |
|-----------------------|-----------------------------------------------------------------------|
| Webserver (Gunicorn)  | Produktionsserver auf render.com, startet den Flask-Prozess.          |
| Web-App (`app.py`)    | Einziges Flask-Modul; rendert HTML, nimmt Formular-POSTs an, hält die In-Memory-Liste. |
| Template (inline)     | Jinja2-String im selben File – erzeugt die zwei Ansichten „Name“ und „Chat“. |
| Browser-Client        | Standard-HTML-Formular + ~15-zeiliges Vanilla-JS-Polling (`fetch`/`setInterval` alle 3 s, ersetzt nur den Inhalt der Nachrichten­liste). Kein Framework, keine externen Skripte. |
| Cookie                | Transportiert den Anzeigenamen. `HttpOnly`, `SameSite=Lax`, `Path=/`, 30 Tage. |

```
  Browser            ┌──────────────── Render.com (ein Worker) ────────────────┐
  ┌─────────┐  HTTP  │  Gunicorn (--workers 1)                                 │
  │  HTML   │ <────> │     │                                                   │
  │  Form   │        │     ▼                                                   │
  │  Meta-  │        │  Flask-App (app.py)                                     │
  │  Refresh│        │     │                                                   │
  └─────────┘        │     ▼                                                   │
                     │  MESSAGES: list[dict]  (In-Memory, ein Prozess)         │
                     └─────────────────────────────────────────────────────────┘
```

---

## Notwendige Dateien & Ordner

Das Repository ist flach – alle Dateien liegen im Root.

| Datei              | Zweck                                                       | Anforderung |
|--------------------|-------------------------------------------------------------|-------------|
| `app.py`           | Die komplette Applikation (ein Endpoint `/`, Template inline). | N02, R23    |
| `requirements.txt` | Pinned Abhängigkeiten: `Flask==3.0.3`, `gunicorn==22.0.0`.  | N07         |
| `render.yaml`      | Blueprint für render.com (Build- und Start-Kommando, `--workers 1`). | N08, N10 |
| `Procfile`         | Alternative für Plattformen ohne Blueprint-Support.         | N08         |
| `README.md`        | Kurzbeschreibung und Deployment-Hinweise.                   | –           |

Keine weiteren Ordner (kein `templates/`, kein `static/`) – hält die Spec „alles in einer Datei lesbar“ ein.

---

## Technologie-Stack

- **Sprache:** Python 3.12
- **Web-Framework:** Flask 3.0.3 (Jinja2-Autoescape aktiv → R21)
- **Webserver:** Gunicorn 22.0.0 (`--workers 1`)
- **Hosting:** render.com (Web Service, Free Tier ausreichend)
- **Versionskontrolle:** Git / GitHub (für Auto-Deploy auf render.com)
- **Modellierung:** PlantUML (`domain-model.puml` im Repo `classroom-chat`)

---

## Deployment auf render.com

**Voraussetzung:** Der Code liegt in einem GitHub-Repository (z. B. dem bestehenden `classroom-chat`-Repo).

Ablauf:

1. `app.py`, `requirements.txt`, `render.yaml`, `Procfile` (und optional die Spezifikations­dateien) ins Repo legen, committen, zu GitHub pushen.
2. Auf render.com ein neues *Blueprint*-Deployment anlegen und das GitHub-Repo auswählen. Render liest `render.yaml` und erzeugt den Web Service automatisch.
3. Nach dem ersten erfolgreichen Deploy stellt Render eine öffentliche HTTPS-URL bereit (Form `https://classroom-messenger.onrender.com`).
4. Die App ist sofort nutzbar: URL teilen, Teilnehmer/innen geben einen Namen ein und schreiben los.

Alternativ ohne Blueprint: Auf render.com einen *Web Service* manuell anlegen mit
`Build Command: pip install -r requirements.txt`
`Start Command: gunicorn app:app --workers 1 --bind 0.0.0.0:$PORT`

### Lokales Ausführen

```bash
pip install -r requirements.txt
python app.py            # http://localhost:5000
# oder
gunicorn app:app --workers 1 --bind 0.0.0.0:5000
```

---

## Betriebsbedingungen & Risiken (übernommen aus Schritt 4)

1. **Flüchtigkeit:** Nachrichten gehen bei Prozess-Neustart verloren. render.com Free Tier friert Services nach ca. 15 Min. Inaktivität ein – beim nächsten Aufruf ist der Verlauf leer. *Akzeptiert.*
2. **Ein Worker:** `--workers 1` ist zwingend, damit die In-Memory-Liste konsistent bleibt.
3. **Keine Authentifizierung:** Jede Person mit der URL kann mitlesen und schreiben. *Bewusste MVP-Entscheidung.*
4. **Speicherwachstum:** Die Nachrichtenliste wächst unbegrenzt innerhalb einer Laufzeit. Für typische Unterrichtssitzungen unkritisch.
5. **Aktualisierung:** Ursprünglich `<meta http-equiv="refresh">` – nach einem Deployment-Test verworfen, weil dadurch während des Tippens das Eingabefeld geleert wurde. Ersetzt durch ein kurzes Vanilla-JS-Polling auf `/`, das nur den Inhalt der Nachrichtenliste ersetzt. Eingabe und Scroll-Position bleiben erhalten. Einzelner Endpoint, kein Push/WebSocket, kein Framework.

---

## Verifikation (Smoke-Tests)

Die folgenden Tests wurden gegen die lokal gestartete App ausgeführt und sind alle erfolgreich durchgelaufen (Protokoll: siehe Chatverlauf Schritt 6):

1. `GET /` ohne Cookie → Namensseite.
2. `POST /` mit `action=set_name` → 302-Redirect + `Set-Cookie` mit `HttpOnly`, `SameSite=Lax`, `Path=/`.
3. `GET /` mit Cookie → Chat-Ansicht inkl. `<meta refresh>` und Platzhalter „Noch keine Nachrichten“.
4. `POST /` mit `action=send` → Nachricht erscheint im Verlauf.
5. `<script>`-Injektion im Nachrichtentext wird HTML-escaped ausgeliefert (R21).
6. Leere Nachricht wird stillschweigend verworfen (R12).
7. Text > 500 Zeichen wird serverseitig auf 500 gekürzt (R10).
8. `GET /?rename=1` zeigt die Namensseite mit vorausgefülltem Wert (UC5).
9. `POST /` ohne Cookie → Redirect mit `?rename=1` (R05).
10. Response-Header `Content-Type: text/html; charset=utf-8` (R22).

---

Mit diesem Stand ist der TRL4-Prototyp lauffähig und deploymentreif. Verbleibende Arbeitsresultate aus dem Einstiegsblock: A4 (SWOT-Reflexion) folgt als eigenes Dokument.
