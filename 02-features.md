# Schritt 2 – Funktionale Anforderungen als Feature-Katalog (MVP)

**Ziel:** Die für ein Minimum Viable Product (MVP) notwendigen Features des Classroom-Messengers identifizieren und je Feature *Zweck*, *Anforderungen* und *Umsetzungsidee* festhalten.

**Status:** finalisiert nach Peer-Review (siehe Abschnitt am Ende).

**Leitprinzipien aus der Spezifikation (`README.md` / `specification.md`):**

- So einfach und grundlegend wie möglich.
- Einfacher, gängiger Cloud-Dienst (render.com).
- Umsetzung mit einfachem Python-Code (Flask + Gunicorn).
- Kein eigenes Datenbanksystem, In-Memory-Haltung im Python-Prozess (nicht persistent).
- Wenige Endpunkte – idealerweise ein einziger.

**Bezug zu Schritt 1 (DDD):** Feature-Ideen referenzieren die Klassen `User`, `Classroom`, `Message`, `Membership` aus dem Domänenmodell. *Nach Peer-Review entfällt `Role`/`Membership`-Rolle im MVP (siehe unten); das Domänenmodell wird in einer kleinen Revision nachgezogen.*

---

## Brainstorming – Was muss ein MVP-Classroom-Messenger können?

Gesammelte Funktions­kandidaten aus Nutzendensicht:

- sich mit einem Anzeigenamen zu erkennen geben,
- ein gemeinsames Klassenzimmer betreten,
- eine Textnachricht senden,
- die bisherigen Nachrichten des Klassenzimmers lesen,
- neue Nachrichten anderer Teilnehmender sehen, ohne die Seite manuell neu zu laden,
- den Absender jeder Nachricht erkennen.

Bewusst **nicht** im MVP (siehe Abschnitt *Abgrenzung*):
Rollen (Lehrperson/Lernende), Persistenz, Authentifizierung, mehrere Klassenzimmer, Direktnachrichten, Anhänge, Bearbeiten/Löschen, Reaktionen, Threads, Erwähnungen, Benachrichtigungen, Lesebestätigungen, Moderation.

---

## Feature-Katalog

### F1 – Selbst­identifikation (Anzeigename)

- **Zweck:** Jede Nachricht wird einem Absender zugeordnet, damit der Gesprächsverlauf nachvollziehbar ist.
- **Bezug DDD:** `User(username)`.
- **Anforderungen:**
  - Nutzer/in gibt einen Anzeigenamen ein (nicht leer, max. 40 Zeichen).
  - Der Name **bleibt beim Neuladen erhalten** (Cookie im Browser).
  - Der Name kann vom Nutzer jederzeit geändert werden (kleines „Name ändern“-Element im UI).
  - Keine Registrierung, kein Passwort, keine Rolle.
- **Umsetzungsidee:** Einfaches HTML-Formular auf der Startseite; der Name wird in einem **Cookie** gespeichert und bei jeder Aktion automatisch mitgeschickt.

### F2 – Gemeinsames Klassenzimmer betreten

- **Zweck:** Alle Teilnehmenden sehen denselben Nachrichtenstrom.
- **Bezug DDD:** `Classroom` + `Membership`.
- **Anforderungen:**
  - Im MVP existiert **genau ein** globales Klassenzimmer (Default-Raum). *(Peer-Review bestätigt.)*
  - Nach F1 landet die Nutzer/in unmittelbar in diesem Raum.
  - Kein separater Beitritts­schritt notwendig.
- **Umsetzungsidee:** Hart­kodierter Single-Room im Python-Prozess; `Membership` wird implizit durch einen geöffneten Client hergestellt. Erweiterung „mehrere Räume“ ist für eine spätere Iteration vorgesehen.

### F3 – Nachricht senden

- **Zweck:** Text­beitrag für alle im Klassenzimmer sichtbar machen.
- **Bezug DDD:** `Message(content, created_at)` verfasst von `User`, enthalten in `Classroom`.
- **Anforderungen:**
  - Eingabefeld für Text (nicht leer, **max. 500 Zeichen** – Peer-Review bestätigt).
  - Absenden per Button oder *Enter*.
  - System ergänzt Absender (aus F1) und Zeitstempel automatisch.
  - Nachricht erscheint im Chatverlauf (F4) aller Teilnehmenden nach spätestens einem Aktualisierungs­intervall (F5).
- **Umsetzungsidee:** HTML-Formular via `POST` an den gemeinsamen Endpoint; Server hängt die Nachricht an eine In-Memory-Liste an.

### F4 – Nachrichten lesen

- **Zweck:** Laufendes Gespräch verfolgen.
- **Bezug DDD:** `Classroom.history() : list<Message>`.
- **Anforderungen:**
  - Chronologische Darstellung, **neueste Nachricht unten** *(Peer-Review bestätigt, Chat-übliche Sortierung)*.
  - Je Nachricht werden **Absender, Uhrzeit und Text** angezeigt.
  - Alle Teilnehmenden sehen denselben Verlauf.
  - Ansicht funktioniert ohne JavaScript-Framework (reines HTML).
- **Umsetzungsidee:** Server-gerendertes HTML; dieselbe Seite zeigt Eingabe (F3) und Verlauf (F4).

### F5 – Automatische Aktualisierung

- **Zweck:** Neue Beiträge werden sichtbar, ohne manuell neu zu laden.
- **Anforderungen:**
  - Die Chat-Seite aktualisiert sich eigenständig **alle 3 Sekunden** *(Peer-Review: `<meta refresh>` akzeptabel)*.
  - Funktioniert in allen gängigen Browsern ohne zusätzliche Installation.
- **Umsetzungsidee:** `<meta http-equiv="refresh" content="3">` im HTML-Header. Kein WebSocket, kein Push, kein JS nötig.

### ~~F6 – Absender und Rolle sichtbar~~ *(gestrichen im Peer-Review)*

Rollen (Lehrperson/Lernende) sind im MVP **nicht erforderlich**. Der Absendername aus F1 reicht; die Differenzierung nach Rolle fällt weg und mit ihr der Enum `Role`.

---

## Abgrenzung – nicht im MVP

| Bereich | Bewusst ausgeschlossen | Begründung |
|---|---|---|
| Rollen (Lehrperson/Lernende) | Kein `Role`-Enum, keine Unterscheidung im UI | Peer-Review-Entscheidung; maximal einfach. |
| Persistenz | Keine Datenbank, Nachrichten nur im Prozess­speicher | Drastisch einfacher; passt zum render.com Free-Tier. |
| Auth | Keine Passwörter / Tokens | MVP im Schul-/Unterrichts­kontext mit vertrauens­würdigen Teilnehmenden. |
| Mehrere Räume | Nur ein globales Klassenzimmer | Reduziert UI und State. |
| Anhänge, Bilder | Nur Text | Minimaler Scope. |
| Bearbeiten/Löschen | Append-only | Einfachste Semantik. |
| Reaktionen, Threads, Mentions | Nicht enthalten | Nicht MVP-kritisch. |
| Benachrichtigungen, Lesebestätigungen | Nicht enthalten | Nicht MVP-kritisch. |
| Moderation | Nicht enthalten | Nicht MVP-kritisch. |

---

## Nicht-funktionale Randbedingungen (kurz)

- **Einfachheit:** Gesamter Applikations­code soll in einer einzelnen Python-Datei (z. B. `app.py`) lesbar bleiben.
- **Deployment:** Lauffähig auf render.com mit `gunicorn app:app`.
- **Ressourcen:** Ein einzelner Web-Worker-Prozess reicht für den MVP (alle Teilnehmenden sehen dieselbe In-Memory-Liste).
- **Sprache/i18n:** Deutschsprachiges UI, keine Übersetzungs­schicht.
- **Barrierefreiheit:** Standard-HTML-Formular­elemente, Tastatur­bedienung möglich.

---

## Rückverfolgbarkeit Features ↔ Domänenmodell

| Feature | Beteiligte DDD-Klassen |
|---|---|
| F1 Selbstidentifikation | `User` |
| F2 Klassenzimmer betreten | `Classroom`, `Membership` |
| F3 Nachricht senden | `User`, `Classroom`, `Message` |
| F4 Nachrichten lesen | `Classroom`, `Message` |
| F5 Automatische Aktualisierung | (technisch, kein fachliches Konzept) |

**Konsequenz für Schritt 1 (Domänenmodell):**
Der Enum `Role` und die Assoziation `User — Role` werden in einer Mini-Revision des Domänenmodells entfernt. Die übrigen Klassen (`User`, `Classroom`, `Message`, `Membership`) bleiben unverändert. Anpassung erfolgt in `domain-model.puml` / `domain-model.md` im Repo `classroom-chat`.

---

## Peer-Review – Ergebnisse (✓ = erledigt)

1. ✓ **Single-Room vs. Multi-Room** → Single-Room (ein globales Klassenzimmer).
2. ✓ **Sitzung vs. Cookie** → Name bleibt bei Neuladen erhalten (Cookie).
3. ✓ **Refresh-Strategie** → `<meta refresh>` ist akzeptabel (3 s).
4. ✓ **Zeichenlimit** → 500 Zeichen pro Nachricht.
5. ✓ **Sortierung** → Neueste Nachrichten **unten** (Chat-üblich).
6. ✓ **Sichtbarkeit der Rolle** → *Rollen werden nicht benötigt*; F6 gestrichen, `Role` aus dem Domänenmodell entfernt.

Mit diesen Festlegungen ist Schritt 2 abgeschlossen und Schritt 3 (Use Cases & vollständige Anforderungsliste) kann beginnen.
