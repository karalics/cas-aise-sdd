"""Classroom Messenger – TRL4-Prototyp.

Komplette Applikation in einer einzigen Python-Datei (vgl. N02). Ein einziger
HTTP-Endpoint `/` (R23) behandelt sowohl `GET` (Seite anzeigen) als auch
`POST` (Namen setzen oder Nachricht senden). Der Zustand wird ausschließlich
im Arbeitsspeicher des Prozesses gehalten und ist nicht persistent (R09, N06).

Für die Abbildung der Anforderungen siehe `03-use-cases.md`.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from flask import (
    Flask,
    make_response,
    redirect,
    render_template_string,
    request,
    url_for,
)

app = Flask(__name__)

# ---------------------------------------------------------------------------
# In-Memory-Zustand: eine globale Nachrichtenliste für das einzige
# Klassenzimmer (R07, R08, R09, N06).
# ---------------------------------------------------------------------------
MESSAGES: list[dict] = []

# Limits (R02 / R14b, R10 / R14a).
MAX_NAME_LEN = 40
MAX_MSG_LEN = 500

# Cookie-Konfiguration (R03).
COOKIE_NAME = "classroom_user"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 Tage
COOKIE_SAMESITE = "Lax"
COOKIE_PATH = "/"


# ---------------------------------------------------------------------------
# HTML-Template (R18: reines HTML ohne JS-Framework; R19: meta-refresh im
# Chat-Modus; R22: UTF-8; R21: Jinja2-Autoescape ist per Default aktiv und
# bleibt aktiv – daher werden `{{ ... }}`-Ausgaben zuverlässig escaped).
# ---------------------------------------------------------------------------
PAGE = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {% if view == "chat" %}<meta http-equiv="refresh" content="3">{% endif %}
  <title>Classroom Messenger</title>
  <style>
    :root {
      --bg:#f7f7f5; --surface:#fff; --border:#e2e2df; --text:#1a1a1a;
      --muted:#6b6b6b; --primary:#1f5fb2; --primary-hover:#174a8c;
      --error:#b91c1c; --own:#eef5ff; --radius:8px; --gap:12px;
    }
    *{box-sizing:border-box}
    html,body{height:100%;margin:0}
    body{font-family:system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
         color:var(--text);background:var(--bg);font-size:16px;line-height:1.45}
    .app{max-width:720px;margin:0 auto;min-height:100vh;display:flex;flex-direction:column}
    header{padding:16px 20px;border-bottom:1px solid var(--border);background:var(--surface);
           display:flex;align-items:center;justify-content:space-between;gap:var(--gap)}
    header h1{font-size:1.125rem;margin:0;font-weight:600}
    .whoami{font-size:.9rem;color:var(--muted)}
    .whoami strong{color:var(--text)}
    .linkbtn{color:var(--primary);text-decoration:underline;margin-left:8px}
    main{flex:1;display:flex;flex-direction:column;padding:20px;gap:var(--gap);min-height:0}
    .name-form,.compose,.messages{background:var(--surface);border:1px solid var(--border);
                                  border-radius:var(--radius);padding:16px}
    .name-form{display:flex;flex-direction:column;gap:12px;padding:24px}
    .name-form h2{margin:0;font-size:1.25rem}
    .name-form p{margin:0;color:var(--muted);font-size:.95rem}
    .name-form label{font-weight:600}
    .row{display:flex;gap:var(--gap);align-items:center}
    .row>input[type=text]{flex:1}
    input[type=text]{padding:10px 12px;border:1px solid var(--border);border-radius:var(--radius);
                     font-size:1rem;font-family:inherit}
    input[type=text]:focus{outline:2px solid var(--primary);outline-offset:1px}
    button.primary{background:var(--primary);color:#fff;border:none;padding:10px 16px;
                   border-radius:var(--radius);font-size:1rem;font-weight:600;cursor:pointer}
    button.primary:hover{background:var(--primary-hover)}
    .error{color:var(--error);font-size:.9rem;min-height:1.2em}
    .messages{flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:8px;min-height:260px;padding:12px}
    .empty{color:var(--muted);font-style:italic;margin:auto}
    .msg{border:1px solid var(--border);border-radius:var(--radius);padding:8px 12px;
         background:#fff;max-width:85%;word-wrap:break-word}
    .msg.own{background:var(--own);align-self:flex-end;border-color:#cfe0f7}
    .meta{font-size:.8rem;color:var(--muted);margin-bottom:2px}
    .meta .author{font-weight:600;color:var(--text)}
    .text{white-space:pre-wrap}
    .compose{display:flex;flex-direction:column;gap:8px;padding:12px}
    .statusline{font-size:.8rem;color:var(--muted)}
  </style>
</head>
<body>
  <div class="app" role="application" aria-label="Classroom Messenger">
  {% if view == "chat" %}
    <header>
      <h1>Klassenzimmer</h1>
      <div>
        <span class="whoami">Angemeldet als <strong>{{ user }}</strong></span>
        <a class="linkbtn" href="{{ url_for('index', rename=1) }}">Name ändern</a>
      </div>
    </header>
    <main>
      <div class="messages" aria-live="polite" aria-relevant="additions">
        {% if messages %}
          {% for m in messages %}
            <div class="msg {% if m.author == user %}own{% endif %}">
              <div class="meta"><span class="author">{{ m.author }}</span> · {{ m.ts }} UTC</div>
              <div class="text">{{ m.text }}</div>
            </div>
          {% endfor %}
        {% else %}
          <div class="empty">Noch keine Nachrichten</div>
        {% endif %}
      </div>
      <form class="compose" method="post" action="{{ url_for('index') }}" autocomplete="off">
        <input type="hidden" name="action" value="send">
        <div class="row">
          <input type="text" name="content" maxlength="500" required
                 placeholder="Nachricht schreiben …" autofocus>
          <button type="submit" class="primary">Senden</button>
        </div>
        <div class="statusline">Enter zum Senden · max. 500 Zeichen</div>
      </form>
    </main>
  {% else %}
    <main>
      <form class="name-form" method="post" action="{{ url_for('index') }}" autocomplete="off">
        <input type="hidden" name="action" value="set_name">
        <h2>Willkommen im Classroom Messenger</h2>
        <p>Bitte gib einen Anzeigenamen ein, unter dem du im Klassenzimmer schreibst.</p>
        <label for="name">Anzeigename</label>
        <div class="row">
          <input type="text" id="name" name="name" maxlength="40" required
                 value="{{ current_name }}" autofocus placeholder="z. B. Anna">
          <button type="submit" class="primary">Betreten</button>
        </div>
        <div class="statusline">1–40 Zeichen</div>
        {% if error %}<div class="error" role="alert">{{ error }}</div>{% endif %}
      </form>
    </main>
  {% endif %}
  </div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def _fmt_ts(dt: datetime) -> str:
    """Zeitstempel als HH:MM UTC (R11, R17)."""
    return dt.strftime("%H:%M")


def _cookie_secure() -> bool:
    """`Secure`-Flag nur ausserhalb der lokalen Entwicklung (R03)."""
    # Lokales `python app.py` setzt FLASK_ENV=development nicht automatisch,
    # daher zusätzlich auf app.debug prüfen.
    if app.debug:
        return False
    if os.environ.get("FLASK_ENV") == "development":
        return False
    return True


def _render_page(view: str, **ctx) -> "flask.Response":
    resp = make_response(render_template_string(PAGE, view=view, **ctx))
    resp.headers["Content-Type"] = "text/html; charset=utf-8"  # R22
    return resp


# ---------------------------------------------------------------------------
# Einziger Endpoint (R23)
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    user = request.cookies.get(COOKIE_NAME, "").strip()

    if request.method == "POST":
        action = request.form.get("action", "send")

        # UC1 / UC5 – Namen setzen oder ändern
        if action == "set_name":
            name = request.form.get("name", "").strip()[:MAX_NAME_LEN]
            if not name:
                return _render_page(
                    view="name",
                    current_name="",
                    error="Bitte einen Namen eingeben.",
                )
            resp = make_response(redirect(url_for("index")))
            resp.set_cookie(
                COOKIE_NAME,
                name,
                max_age=COOKIE_MAX_AGE,
                path=COOKIE_PATH,
                samesite=COOKIE_SAMESITE,
                httponly=True,
                secure=_cookie_secure(),
            )
            return resp

        # UC3 – Nachricht senden
        if not user:
            # R05: ohne Namen zurück auf die Namensseite.
            return redirect(url_for("index", rename=1))
        text = request.form.get("content", "").strip()[:MAX_MSG_LEN]
        if text:  # R12: leere Nachrichten stillschweigend verwerfen.
            MESSAGES.append(
                {
                    "author": user,
                    "text": text,
                    "ts": _fmt_ts(datetime.now(timezone.utc)),
                }
            )
        # Post/Redirect/Get, damit Reloads keine Nachrichten duplizieren.
        return redirect(url_for("index"))

    # GET
    # UC5: Namensseite auf Wunsch explizit anfordern (?rename=1).
    if request.args.get("rename") == "1" or not user:
        return _render_page(view="name", current_name=user, error=None)
    return _render_page(view="chat", user=user, messages=MESSAGES)


# ---------------------------------------------------------------------------
# Lokaler Entwicklungs-Server: `python app.py`  → http://localhost:5000
# Auf render.com wird die App mit Gunicorn gestartet (siehe Procfile /
# render.yaml, N08, N10).
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))  # N09
    app.run(host="0.0.0.0", port=port, debug=False)
