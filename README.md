# Classroom Messenger – SDD-AISE

Specification-Driven-Development-Lieferobjekte für den Classroom-Messenger (TRL4-Prototyp).

## Artefakte

| Schritt | Datei                                     | Inhalt |
|---------|-------------------------------------------|--------|
| 1       | [`classroom-chat/domain-model.md`](../classroom-chat/domain-model.md) + `.puml` | Domänenmodell (DDD) |
| 2       | [`02-features.md`](02-features.md)        | Feature-Katalog (MVP) |
| 3       | [`03-use-cases.md`](03-use-cases.md)      | Use Cases + konsolidierte Anforderungen R01–R23, N01–N10 |
| 4       | [`04-quality-check.md`](04-quality-check.md) | Requirements Quality Check (KI-Review + manuelle Kuration) |
| 5       | [`05-ui-mockup.html`](05-ui-mockup.html) + [`05-ui-design.md`](05-ui-design.md) | Lauffähiges UI-Mockup + Nutzertest-Leitfaden |
| 6       | [`app.py`](app.py), [`requirements.txt`](requirements.txt), [`render.yaml`](render.yaml), [`Procfile`](Procfile), [`06-architecture.md`](06-architecture.md) | Flask-App + Deployment-Konfiguration |

## Lokal starten

```bash
pip install -r requirements.txt
python app.py            # http://localhost:5000
```

## Deployment

Repository zu GitHub pushen → auf render.com als Blueprint verbinden (`render.yaml` wird automatisch gelesen).
Details in [`06-architecture.md`](06-architecture.md).
