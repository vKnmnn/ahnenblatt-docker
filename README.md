# Ahnenblatt mit Wine und Selkies

Ahnenblatt im Browser, mit Wine und Selkies. Das Image enthält die normale
Windows-Installation und einen Webdateimanager für Uploads und Downloads.

**Image:** `ghcr.io/vknmnn/ahnenblatt-docker` · **Plattform:** `linux/amd64`

## Versionen

Beim Veröffentlichen werden folgende Tags erzeugt:

| Tags | Anwendung |
| --- | --- |
| `2.99`, `2.99p` | kostenlose Version 2.99p |
| `3`, `3.60` | Version 3.60, Demo mit optionaler Freischaltung |
| `4`, `4.55` | Version 4.55, Demo mit optionaler Freischaltung |
| `5`, `5.02` | Version 5.02, Demo mit optionaler Freischaltung |

Die kurzen Tags verfolgen die jeweilige Versionslinie. Es gibt keinen
`latest`-Tag. Für die Freischaltung ist eine passende Ahnenblatt-Lizenz nötig.

## Starten

Voraussetzungen: eine aktuelle Docker Engine mit Compose und GNU Make.

```sh
git clone https://github.com/vKnmnn/ahnenblatt-docker.git
cd ahnenblatt-docker
make up SERIES=4
```

Nach erfolgreicher Veröffentlichung kann das Image direkt aus GHCR bezogen
werden; alternativ lässt es sich selbst bauen. Die Oberfläche ist unter
<https://localhost:3001> erreichbar (mit selbstsigniertem Zertifikat). HTTP auf Port 3000 steht für einen
HTTPS-Reverse-Proxy weiterhin zur Verfügung.

```sh
make logs
make down
```

Optional `.env.example` nach `.env` kopieren und anpassen:

| Variable | Bedeutung |
| --- | --- |
| `SERIES` | Ahnenblatt-Versionslinie, standardmäßig `4` |
| `CONFIG_DIR` | Persistente Wine-Profile und Containereinstellungen |
| `DATA_DIR` | Ahnenblatt-Datenordner auf dem Host; standardmäßig `CONFIG_DIR/files` |
| `HTTPS_PORT` | HTTPS-Port der Weboberfläche, standardmäßig `3001` |
| `HTTP_PORT` | HTTP-Port für einen Reverse-Proxy, standardmäßig `3000` |
| `APP_LOCALE` | Wine-/Desktop-Locale, standardmäßig `en_US.UTF-8` |
| `PUID`, `PGID` | Benutzer- und Gruppen-ID für Dateirechte |
| `CUSTOM_USER`, `PASSWORD` | Optionale HTTP-Basisauthentifizierung |

Ohne `.env` verwendet `make up SERIES=3` den Datenordner `./data/3`.
Bei einer eigenen `.env` den `CONFIG_DIR` passend zur Serie setzen.
Mehrere Instanzen benötigen unterschiedliche Compose-Projektnamen, Ports und
Datenordner.

## Oberfläche

Die Selkies-Seitenleiste konzentriert sich auf Bildschirm, Dateien und
Zwischenablage; Audio, Mikrofon, Webcam und Gamepad sind standardmäßig deaktiviert.
Das Ahnenblatt-Hauptfenster öffnet maximiert ohne zusätzliche Titelleiste,
Dialoge werden zentriert. Ein Hinweis auf dem Desktop erklärt den automatischen
Neustart nach dem Schließen. Minimierte Fenster lassen sich über die Taskleiste
wieder öffnen.

## Dateien und Einstellungen

Der eigene Datenordner wird nach `/config/files` gemountet und erscheint in
Ahnenblatt direkt als Laufwerk `D:`. In `.env` beispielsweise:

```dotenv
CONFIG_DIR=./data/4
DATA_DIR=/srv/genealogie
```

Die vorhandene Ordnerstruktur kann so bleiben:

```text
/srv/genealogie/
├── Familie.ahn
└── Familie Media/
```

Ein zusätzlicher Unterordner `Ahnenblatt` ist nicht erforderlich. Bereits
vorhandene Unterordner bleiben nutzbar. Relative Verweise auf Medien bleiben
beim gemeinsamen Mount der `.ahn`-Datei und ihrer Medienordner erhalten.

Neue Profile verwenden `D:\` als Vorgabe für Ahnendateien und Suchbegriffe.
Für Bilder wird bei deutscher Containersprache `D:\Bilder`, sonst
`D:\Pictures` angelegt (Vorrang: `LC_ALL`, `LC_MESSAGES`, `LANG`). Eine
Ausgabeordner-Vorgabe wird nicht gesetzt. Vorhandene INI-Einstellungen und
Ordner werden nicht überschrieben, umbenannt oder gelöscht; bei bestehenden
Profilen die gewünschten Pfade direkt in Ahnenblatt einstellen.

Selkies verwendet denselben Datenordner für Uploads und Downloads. Ohne
`DATA_DIR` bleibt der bisherige Speicherort unter `CONFIG_DIR/files` erhalten.
Bei direktem `docker run` den Datenordner zusätzlich mit
`-v /srv/genealogie:/config/files` einhängen. `PUID` und `PGID` müssen zum
Schreibzugriff auf den eingehängten Ordner passen.

Wine-Profile und Einstellungen liegen getrennt unter
`/config/versions/<Serie>/wineprefix/`.

Einstellungen und im Wine-Profil gespeicherte Freischaltdaten bleiben im
Datenordner erhalten. Diesen Ordner regelmäßig sichern und bei Imageupdates
weiterverwenden. Für jede Hauptversion ein eigenes Profil verwenden.
Lizenzschlüssel und persönliche Daten gehören weder ins Repository noch ins Image.

## Sprachen

Alle mit dem jeweiligen Installer gelieferten Sprachdateien sind enthalten.
Die Sprache wird in Ahnenblatt unter **Extras → Sprache** gewählt und im
persönlichen Profil gespeichert. Je nach Version unterscheiden sich die
verfügbaren Übersetzungen; unvollständige Texte können auf Englisch erscheinen.

Englisch ist die Standard-Locale. Mit `APP_LOCALE=de_DE.UTF-8` in `.env`
setzt Compose `LANG=de_DE.UTF-8` im Container. Bei direktem `docker run` genügt
`-e LANG=de_DE.UTF-8`. Der Desktop-Hinweis verwendet `LC_ALL`, `LC_MESSAGES`
oder `LANG` (in dieser Reihenfolge): Deutsch für `de`, sonst Englisch.
Die Locale ersetzt nicht die Sprachauswahl in Ahnenblatt und setzt bestehende
Einstellungen nicht zurück. Noto-Schriftarten ergänzen die Zeichenabdeckung.

## Selbst bauen und testen

Zusätzlich benötigt: Docker Buildx und Python 3; für das Aktualisieren der
Installer-Prüfsummen ExifTool. ShellCheck wird für das Linting empfohlen.

```sh
make check
make build SERIES=4
make smoke SERIES=4
make up SERIES=4
```

`make check` führt statische Prüfungen und Unit-Tests aus. `make smoke` prüft
in einem isolierten Container ohne Netzwerk den Anwendungsstart, Selkies-Uploads und -Downloads, den Dateizugriff
über `D:` und den Erhalt der Daten nach einem Neustart. Für alle Varianten gibt
es `make build-all` und `make smoke-all`.

Der Build installiert Ahnenblatt in einem temporären Wine-Profil. Nur
Programmdateien, zusätzliche Schriftarten und Versionsmetadaten gelangen ins
finale Image. Das persönliche Wine-Profil wird beim ersten Containerstart erzeugt.
Anwendungsupdates erfolgen über neue Images. Version 4/5 enthalten nur die
64-Bit-Wine-Laufzeit. Version 2.99/3 behalten beide Wine-Architekturen für ihre
32-Bit-Anwendung und bestehende 64-Bit-Profile. Die separate Installationsstufe
verwendet für alle Versionen beide Architekturen.

Installer-Versionen und SHA-256-Prüfsummen stehen in `versions/versions.json`.
Für ein Update Version und URL anpassen, `sha256` auf `null` setzen und
`make lock SERIES=4` ausführen. Anschließend die Manifeständerung prüfen,
einchecken und die betreffende Variante bauen und testen.

## Auf GHCR veröffentlichen

In GitHub **Actions → Container → Run workflow** öffnen und `publish` aktivieren.
Der Workflow baut und testet alle vier Varianten und veröffentlicht sie mit dem
`GITHUB_TOKEN`. Das Paket kann anschließend in den GitHub-Paketeinstellungen
öffentlich geschaltet werden.

Alternativ lokal:

```sh
make login
make push SERIES=4
# Alle Varianten:
make push-all
```

Veröffentlicht wird erst nach bestandenem Smoke-Test. Pushes und Pull Requests
starten die CI-Prüfungen; die Veröffentlichung wird separat ausgelöst.

`main` enthält die gemeinsame Codebasis mit Serie 4 als Standard.
Die Branches `release/2.99`, `release/3`, `release/4` und `release/5` setzen jeweils
die passende Serie als Standard. Gemeinsame Änderungen werden von `main` in die
Release-Branches übernommen.

## Weitere Informationen

- [Ahnenblatt](https://www.ahnenblatt.de/)
- [LinuxServer Selkies-Basisimage](https://github.com/linuxserver/docker-baseimage-selkies)

Dieses Image wird unabhängig von vKnmnn gepflegt. Es ist kein offizielles
LinuxServer.io- oder Ahnenblatt-Image. Support und Fehlerberichte gehören in die
[Issues dieses Repositorys](https://github.com/vKnmnn/ahnenblatt-docker/issues).
Das Startbanner folgt den [LSIO-Branding-Vorgaben](https://docs.linuxserver.io/general/container-branding/).

Ahnenblatt und die enthaltenen Schriftarten behalten ihre jeweiligen Herstellerlizenzen.

GitHub Actions speichert Build-Schichten je Serie im Cache, einschließlich des
verifizierten Installer-Downloads und der Installation. Bei unveränderten Eingaben
werden sie wiederverwendet; Installer gehören nicht ins Git-Repository.
