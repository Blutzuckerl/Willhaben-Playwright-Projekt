# willhabenbot

Automatisierter Playwright-Bot fuer [willhaben.at](https://www.willhaben.at/iad), der den Ablauf Login -> Inserat erstellen -> Inserat wieder loeschen fuer Test- und Lernzwecke abbildet.

## Features

- Login auf Willhaben mit E-Mail/Passwort aus `.env`
- Cookie-Banner automatisch akzeptieren
- Inserat automatisiert erstellen
- Inserat per Titel wieder loeschen
- Screenshot-Debugging bei Fehlern (`debug/`)
- Manueller Schritt fuer CAPTCHA/2FA unterstuetzt

## Projektstruktur

- `automation.py`: Hauptablauf (Login, Erstellen, Loeschen)
- `main.py`: Startpunkt via Uvicorn
- `willhaben_bot/willhaben_bot/config.py`: Laden von Umgebungsvariablen
- `willhaben_bot/willhaben_bot/willhaben_login.py`: Login-Helferklasse

## Voraussetzungen

- Python 3.11+
- Installierte Python-Pakete:
  - `playwright`
  - `python-dotenv`
  - `uvicorn`

Zusaetzlich einmalig:

```bash
playwright install
```

## Konfiguration

In der Datei `.env`:

```env
WILLHABEN_EMAIL=deine_email@example.com
WILLHABEN_PASSWORD=dein_passwort
```

## Start

Direkt ausfuehren:

```bash
python automation.py
```

Oder ueber den Startpunkt:

```bash
python main.py
```

## Hinweis

Die Automatisierung haengt von der aktuellen Willhaben-Oberflaeche ab. Bei UI-Aenderungen muessen Selektoren im Code ggf. angepasst werden.
