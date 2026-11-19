# Ahnenblatt im Browser

Ahnenblatt mit Wine 11 und Selkies: Genealogie im Browser, einschließlich
Datei-Upload, Download und Zwischenablage. Die Windows-Anwendung ist
vorinstalliert; auf dem eigenen Rechner wird nur ein Browser benötigt.

**Image:** `ghcr.io/vknmnn/ahnenblatt-docker` · **Architektur:** `linux/amd64`

## Unterstützte Versionen

| Tags | Ahnenblatt |
| --- | --- |
| `5`, `latest`, `5-wine11`, `5.02`, `5.02-wine11` | 5.02 – Standard |
| `4`, `4-wine11`, `4.55`, `4.55-wine11` | 4.55 |
| `3`, `3-wine11`, `3.60`, `3.60-wine11` | 3.60 |
| `2.99`, `2.99-wine11`, `2.99p`, `2.99p-wine11` | 2.99p – kostenlos |

Alle gepflegten Tags verwenden Wine 11. Die Versionen 3, 4 und 5 starten als
Demo und können mit einer passenden Ahnenblatt-Lizenz freigeschaltet werden.
`5` bleibt bei Ahnenblatt 5; `latest` folgt der empfohlenen Version.
Alte `-wine10`-Tags werden nicht mehr aktualisiert.

## Schnellstart mit Docker Compose

Diese Konfiguration als `compose.yaml` speichern. Die Host-Verzeichnisse und
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
      # Optional: Host-Zeitzone nutzen und TZ oben auf :/etc/localtime setzen.
      # - /etc/localtime:/etc/localtime:ro
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

Die Oberfläche unter **`https://<Docker-Host>:3001`** öffnen und das
selbstsignierte Zertifikat bestätigen. Beim ersten Start wird das persönliche
Wine-Profil angelegt; das kann etwas dauern. Ahnenblatt öffnet sich automatisch
und wird nach dem Schließen wieder gestartet.

### Ports und Unraid

| Container-Port | Protokoll | Zweck |
| --- | --- | --- |
| `3001` | TCP / HTTPS | Direkter Browserzugriff |
| `3000` | TCP / HTTP | Optional für einen HTTPS-Reverse-Proxy |

In Unraid den Netzwerkmodus **Bridge**, eine TCP-Portzuordnung auf Container-Port
`3001` und die beiden unten beschriebenen Verzeichniszuordnungen verwenden.
Unter „Extra Parameters“ `--shm-size=1gb` eintragen. Die Variablen aus der
Laufzeit-Tabelle lassen sich als zusätzliche Container-Variablen hinterlegen.

Der Host-Port darf abweichen, etwa `3301:3001`; die Browseradresse lautet dann
`https://<Docker-Host>:3301`. Die im Image deklarierten Ports werden erst durch
diese Zuordnung erreichbar. Zusätzliche VNC- oder UDP-Ports sind nicht nötig.

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

Ein zusätzlicher Unterordner `Ahnenblatt` ist nicht erforderlich. Ahnendatei und
zugehörige Medienordner gemeinsam einhängen, damit relative Dateiverweise erhalten
bleiben. Der Webdateimanager verwendet denselben Ordner für Uploads und Downloads.

Neue Profile verwenden `D:\` als Dateiablage. Je nach Containersprache werden
`Bilder` und `Ausgabe` oder `Pictures` und `Output` angelegt. Vorhandene Dateien,
Ordnernamen und Ahnenblatt-Einstellungen bleiben erhalten.

Beide Verzeichnisse regelmäßig sichern. Pro Instanz ein eigenes `/config`
verwenden und Ahnendateien nicht gleichzeitig in mehreren Instanzen bearbeiten.

## Laufzeitvariablen

Diese Variablen werden beim **Starten des Containers** gesetzt, in Compose unter
`environment`, in Unraid als Variable oder bei `docker run` mit `-e`.
Sie benötigen keinen Image-Neubau. Nach einer Änderung den Container neu erstellen.

| Variable | Standard | Bedeutung |
| --- | --- | --- |
| `PUID` | `911` (`1000` im Compose-Beispiel) | Benutzer-ID für Schreibrechte auf den eingebundenen Ordnern |
| `PGID` | `911` (`1000` im Compose-Beispiel) | Gruppen-ID für Schreibrechte |
| `LC_ALL` | `en_US.UTF-8` | Systemsprache sowie Datums- und Zahlenformate; Deutsch: `de_DE.UTF-8` |
| `TZ` | `Europe/Berlin` | Zeitzone; für den optionalen Host-Mount: `:/etc/localtime` |
| `CUSTOM_USER` | `abc` | Benutzername für optionale HTTP-Basisauthentifizierung; zusammen mit `PASSWORD` setzen |
| `PASSWORD` | leer | Passwort für die optionale HTTP-Basisauthentifizierung |

Die Ahnenblatt-Sprache kann zusätzlich in der Anwendung unter **Extras → Sprache**
gewählt werden. Alle Sprachdateien des jeweiligen Installers sind enthalten.
Der Desktop-Hinweis und neu angelegte Datenordner sind bei deutscher Locale auf
Deutsch, ansonsten auf Englisch. Bestehende Ahnendateien werden nicht umformatiert.

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

Zum Aktivieren des Teilens **beide** Sharing-Variablen auf `true` setzen, etwa:

```yaml
environment:
  SELKIES_UI_SIDEBAR_SHOW_SHARING: "true"
  SELKIES_ENABLE_SHARING: "true"
```

Die ausgeblendeten Video- und Bildschirmeinstellungen beeinträchtigen die
Bildübertragung nicht. Audio, Mikrofon, Webcam und Gamepad sind ebenfalls
standardmäßig deaktiviert. Weitere Optionen beschreibt die
[Selkies-Konfigurationsreferenz](https://docs.linuxserver.io/selkies/user-guide/configuration/).

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

Die eingebundenen Verzeichnisse beim Aktualisieren beibehalten. Falls ein altes
Wine-Profil nicht mehr startet, den Container stoppen und das Profil unter
`/config/versions/<Serie>/wineprefix` sichern und entfernen. Beim nächsten Start
wird es neu angelegt; Einstellungen und Freischaltung müssen dann erneut gesetzt
werden. Die Ahnendaten unter `/config/files` behalten.

Fehler bitte mit Image-Tag und relevanten Logs in den
[Issues](https://github.com/vKnmnn/ahnenblatt-docker/issues) melden; keine
Lizenzschlüssel oder persönlichen Ahnendaten beifügen.
Die Anleitung für eigene Builds und Entwicklung steht in [BUILD.md](BUILD.md).

## Projekt und Lizenzen

Ein unabhängiges Community-Image von vKnmnn, basierend auf
[LinuxServer.io Selkies](https://github.com/linuxserver/docker-baseimage-selkies).
Kein offizielles LinuxServer.io- oder [Ahnenblatt](https://www.ahnenblatt.de/)-Image.
Ahnenblatt und die enthaltenen Schriftarten unterliegen ihren jeweiligen Lizenzen.
