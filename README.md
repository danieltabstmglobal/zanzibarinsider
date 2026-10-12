# Zanzibar Insider

Statische Seite für zanzibarinsider.com (Vercel, Auto-Deploy bei Push auf `main`).

## Bauen
```
python3 tools/build.py
```
Erzeugt alle HTML-Seiten (Deutsch im Wurzelverzeichnis, Englisch unter `/en/`) aus `tools/build.py` und `data/*.json`. Die erzeugten Dateien werden mit eingecheckt.

## Texte und Sprachen
Texte stehen in den Seitenfunktionen als `tx("Deutsch", "English", ru="...", it="...")`. Neue Sprache: Code in `LANGS` (und `LANG_NAMES`, `SLUGS`) eintragen, Übersetzungen als `ru=`/`it=` ergänzen. Fehlt eine Übersetzung, gilt Englisch.

## Verzeichnis
`data/directory.json`: Einträge mit `status` `geprueft` oder `ungeprueft`, `source`, `checked` (Datum). `data/comments.json`: freigegebene Kommentare je Eintrags-ID, Format `{"kibabu-cars": [{"name": "...", "date": "2026-10-12", "text": "..."}]}`.

## Tipps und Kommentare moderieren
Das Formular sendet an `api/submit.js`, das ein GitHub-Issue (Label `tipp` oder `kommentar`, `ungeprueft`) anlegt. Prüfen, dann Eintrag in `data/directory.json` bzw. Kommentar in `data/comments.json` übernehmen, bauen, pushen, Issue schließen.

Vercel-Umgebungsvariable: `GITHUB_TOKEN` (Fine-grained Token nur für dieses Repo, Berechtigung Issues: Read and write). Optional `GITHUB_REPO`.

## Formular per E-Mail
`api/submit.js` verschickt Tipps und Kommentare per SMTP an `FORM_RECIPIENTS` (Standard: office@fumbatown.agency, daniel.taborek@me.com). Vercel-Variablen: `SMTP_USER`, `SMTP_PASS` (Hostinger-Postfach, z. B. redaktion@zanzibarinsider.com). `GITHUB_TOKEN` ist optional und legt zusätzlich ein Issue an.
