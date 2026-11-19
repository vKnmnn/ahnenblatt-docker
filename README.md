# Ahnenblatt im Browser

Ahnenblatt mit Wine 11 und Selkies: Komplett im Browser, mit Uploader
für Dateien und mit Zwischenablage.

**Image:** `ghcr.io/vknmnn/ahnenblatt-docker` · **Architektur:** `linux/amd64`

## Unterstützte Versionen

| Tags | Ahnenblatt |
| --- | --- |
| `5`, `latest`, `5-wine11`, `5.02`, `5.02-wine11` | 5.02 – Standard |
| `4`, `4-wine11`, `4.55`, `4.55-wine11` | 4.55 |
| `3`, `3-wine11`, `3.60`, `3.60-wine11` | 3.60 |
| `2.99`, `2.99-wine11`, `2.99p`, `2.99p-wine11` | 2.99p – kostenlos |

Alle gepflegten Tags verwenden Wine 11. Die Versionen 3, 4 und 5 starten als
Demo und können mit einer passenden [Ahnenblatt-Lizenz](https://www.ahnenblatt.de/shop/) freigeschaltet werden.

## Schnellstart mit Docker Compose

Diese Konfiguration als `docker-compose.yaml` speichern. Die Host-Verzeichnisse und
Benutzer-IDs an die eigene Installation anpassen:

```yaml
services:
  ahnenblatt:
    image: ghcr.io/vknmnn/ahnenblatt-docker:5
    environment:
      PUID: "1000"
      PGID: "1000"
      TZ: Europe/Berlin
      LC_ALL: en_US.UTF-8
    volumes:
      - ./config:/config
      - ./files:/config/files
    ports:
      - "3001:3001"
      # Optional für einen HTTPS-Reverse-Proxy:
      # - "3000:3000"
    shm_size: 1gb
    restart: unless-stopped
```

```sh
docker compose up -d
```

Die Oberfläche unter **`https://<Docker-Host>:3001`** öffnen.

### Ports

| Container-Port | Protokoll | Zweck |
| --- | --- | --- |
| `3001` | TCP / HTTPS | Direkter Browserzugriff |
| `3000` | TCP / HTTP | Optional für einen HTTPS-Reverse-Proxy |

## Daten und Einstellungen

| Container-Pfad | Inhalt |
| --- | --- |
| `/config` | Wine-Profil, Einstellungen und Freischaltung; dauerhaft speichern |
| `/config/files` | Eigene Ahnendateien, Medien und Ausgaben; in Ahnenblatt Laufwerk `D:` |

Ein bestehender Datenordner kann direkt nach `/config/files` eingebunden werden:

```text
files/
├── Familie.ahn
└── Familie Media/
```

Neue Profile verwenden `D:\` als Dateiablage.

## Laufzeitvariablen

| Variable | Standard | Bedeutung |
| --- | --- | --- |
| `PUID` | `911` | Benutzer-ID für Schreibrechte auf den eingebundenen Ordnern |
| `PGID` | `911` | Gruppen-ID für Schreibrechte |
| `LC_ALL` | `en_US.UTF-8` | Systemsprache sowie Datums- und Zahlenformate; Deutsch: `de_DE.UTF-8` |
| `TZ` | `Europe/Berlin` | Zeitzone; für den optionalen Host-Mount: `:/etc/localtime` |
| `CUSTOM_USER` | `abc` | Benutzername für optionale HTTP-Basisauthentifizierung; zusammen mit `PASSWORD` setzen |
| `PASSWORD` | leer | Passwort für die optionale HTTP-Basisauthentifizierung |

Die Ahnenblatt-Sprache kann zusätzlich in der Anwendung unter **Extras → Sprache**
gewählt werden.

### Selkies-Seitenleiste

Dateimanager, Zwischenablage und Vollbild stehen direkt zur Verfügung.
Statistik-, Video- und Bildschirmeinstellungen sowie Teilen sind standardmäßig
ausgeschaltet. Folgende **Laufzeitvariablen** blenden sie mit `true` wieder ein:

| Variable | Standard | Funktion bei `true` |
| --- | --- | --- |
| `SELKIES_UI_SIDEBAR_SHOW_STATS` | `false` | Statistiken anzeigen |
| `SELKIES_UI_SIDEBAR_SHOW_VIDEO_SETTINGS` | `false` | Videoeinstellungen anzeigen |
| `SELKIES_UI_SIDEBAR_SHOW_SCREEN_SETTINGS` | `false` | Bildschirmeinstellungen anzeigen |
| `SELKIES_UI_SIDEBAR_SHOW_SHARING` | `false` | Menü zum Teilen anzeigen |
| `SELKIES_ENABLE_SHARING` | deaktiviert und gesperrt | Teilen der Sitzung erlauben |

Zum Aktivieren des Teilens **beide** Sharing-Variablen auf `true` setzen.

### Variablen der mitgelieferten Compose-Datei

Wer die `docker-compose.yml` aus diesem Repository nutzt, kann `.env.example`
nach `.env` kopieren. Zusätzlich zu den Laufzeitvariablen gelten diese Werte nur
für **Compose auf dem Host**; sie sind keine Einstellungen innerhalb des Containers:

| Variable | Standard auf `main` | Bedeutung |
| --- | --- | --- |
| `IMAGE` | `ghcr.io/vknmnn/ahnenblatt-docker` | Image-Repository |
| `SERIES` | `5` | Ahnenblatt-Tag: `2.99`, `3`, `4`, `5` oder `latest` |
| `CONFIG_DIR` | `./data/5` | Host-Verzeichnis für `/config` |
| `DATA_DIR` | `CONFIG_DIR/files` | Host-Verzeichnis für `/config/files` |
| `HTTPS_PORT` | `3001` | Veröffentlichter HTTPS-Host-Port |
| `HTTP_PORT` | `3000` | Veröffentlichter HTTP-Host-Port |

## Aktualisieren und Hilfe

```sh
docker compose pull
docker compose up -d
docker compose logs --tail=100 ahnenblatt
```

Die Anleitung für eigene Builds und Entwicklung steht in [BUILD.md](BUILD.md).

## Projekt und Lizenzen

Ein unabhängiges Community-Image, basierend auf
[LinuxServer.io Selkies](https://github.com/linuxserver/docker-baseimage-selkies).
_Kein_ offizielles LinuxServer.io- oder [Ahnenblatt](https://www.ahnenblatt.de/)-Image.
Ahnenblatt und die enthaltenen Schriftarten unterliegen ihren jeweiligen Lizenzen.
