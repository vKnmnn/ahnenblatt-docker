# Ahnenblatt mit Wine und KasmVNC

Repository: <https://github.com/vKnmnn/ahnenblatt-docker>

Image: `ghcr.io/vknmnn/ahnenblatt-docker`

`main` enthält die gemeinsame Codebasis und verwendet standardmäßig Serie 4.
Die Branches `release/2.99`, `release/3`, `release/4` und `release/5` setzen
die jeweilige Serie als Standard. Alle Branches können über `SERIES=…` auch
die anderen Varianten bauen. Änderungen an gemeinsamen Skripten werden auf
`main` entwickelt und anschließend in die Release-Branches übernommen.
Die unten aufgeführten Image-Tags entstehen erst beim erfolgreichen Publishing;
sie sind keine bereits veröffentlichten Git-Release-Tags.

Container für die **normale Windows-Installation** von Ahnenblatt. Bedienung im
Browser über KasmVNC, einschließlich des LinuxServer-Webdateimanagers zum Hoch-
und Herunterladen von Dateien. Die portable Ahnenblatt-Version wird nicht benutzt.

| Tag | Geplanter Versionsstand | Anwendung |
| --- | --- | --- |
| `2.99`, `2.99p` | 2.99p | kostenlose Version |
| `3`, `3.60` | 3.60 | Demo, mit passender Lizenz freischaltbar |
| `4`, `4.55` | 4.55 | Demo, mit passender Lizenz freischaltbar |
| `5`, `5.02` | 5.02 | Demo, mit passender Lizenz freischaltbar |

Die kurzen Tags verfolgen die jeweilige Versionslinie. Es gibt bewusst keinen
`latest`-Tag, der unbemerkt auf eine andere Hauptversion wechseln könnte.
Unterstützte Containerplattform: **linux/amd64**. Wine enthält auch die
32-Bit-Laufzeit für ältere Ahnenblatt-Versionen und die Installer.

## Aktueller Prüfstand

Die Dateien sind vorbereitet und statisch geprüft. **Ein Docker-Build und die
Starttests stehen noch aus**, da Docker auf dem Entwicklungsrechner erst nach
dem Reboot nach einem Kernelupgrade wieder verfügbar ist. Insbesondere sind
der Start aus den extrahierten Programmdateien, die Einstellungen der älteren
Versionen und die Freischaltung noch nicht funktional bestätigt.

Die Installer-Prüfsummen in `versions/versions.json` sind zunächst `null`:
Downloads waren in der Entwicklungsumgebung wegen fehlender DNS-Auflösung
nicht möglich. Sie werden mit `make lock-all` ermittelt; es sind keine
erfundenen oder ungeprüften Hashes hinterlegt. Ein Build ohne Lock bricht ab.

## Nach dem Reboot

Voraussetzungen: Docker mit Compose und Buildx, GNU Make, Python 3 und ExifTool
(`libimage-exiftool-perl` unter Debian/Ubuntu). ShellCheck ist für das Linting
empfohlen. Für die Downloads wird Internetzugang benötigt.

```sh
make check
make lock-all
# Die angezeigten Versionen prüfen und versions/versions.json committen.
make build SERIES=4
make smoke SERIES=4
make up SERIES=4
```

Danach: <http://localhost:3000>. Für alle vier Varianten:

```sh
make build-all
make smoke-all
```

`make lock-all` lädt die offiziellen Standard-Installer, kontrolliert ihre
PE-Versionsangaben und schreibt SHA-256-Werte ins Manifest. Bei 2.99 kann die
numerische PE-Version den Buchstabenzusatz auslassen: die Zuordnung zu 2.99p
stammt zusätzlich von der Hersteller-Downloadseite. Bereits gesperrte Downloads
mit verändertem Inhalt werden abgewiesen.

Die Hersteller-URLs sind veränderlich. Falls eine neuere Version angeboten wird,
müssen Versionsangabe und Lock bewusst aktualisiert werden. Der Build prüft den
Hash **vor** dem Ausführen des Installers und zusätzlich die installierte EXE.

## Wie das Image gebaut wird

1. Die Ubuntu-Noble-Variante von LinuxServers KasmVNC-Basisimage erhält Wine
   mit 32- und 64-Bit-Unterstützung, Tint2 und die erforderlichen Werkzeuge.
   Diese Basis ersetzt Alpine 3.20 aus dem ursprünglichen Aufbau.
2. Eine separate Build-Stufe initialisiert ein temporäres Wine-Prefix unter
   Xvfb und führt den Standard-Installer unbeaufsichtigt aus. Tahoma und Ubuntu
   Font Family werden wie beim bisherigen Container über Winetricks installiert.
3. Nur das Anwendungsverzeichnis, diese zusätzlichen Schriftarten und
   Versionsmetadaten werden ins finale Image kopiert. Installer, Build-Prefix,
   Build-Registry und Winetricks bleiben in der Build-Stufe.
4. Beim ersten Start initialisiert der Benutzer `abc` ein persönliches Prefix,
   bindet die Programmdateien als `C:\AhnenblattApp` ein und setzt die
   Schriftglättung. Danach startet Ahnenblatt unter s6-Aufsicht. Das Schließen
   der Anwendung führt zu einem erneuten Start.

Es wird weder das bestehende `config/` in den Build übernommen noch beim Start
Ahnenblatt heruntergeladen oder erneut installiert. Die Anwendung unter `/opt`
bleibt für `abc` schreibgeschützt; Updates werden über das Containerimage geliefert.
Die Übernahme weiterer Installer-Registryeinträge ist derzeit nicht vorgesehen
und muss anhand der Funktionstests bewertet werden.

## Dateien, Uploads und Freischaltung

Im Container:

```text
/opt/ahnenblatt/                         Programmdateien aus dem Image
/opt/ahnenblatt-image.json               Version, EXE und Installer-Prüfsumme
/config/versions/<Linie>/wineprefix/     persönliches Wine-Profil
/config/files/                          Webdateimanager und Wine-Laufwerk D:
    Ahnenblatt/                         Ahnendateien
    Bilder/                             hochgeladene Fotos und andere Bilder
    Ausgaben/                           Exporte
```

Die normale Ahnenblatt-Konfiguration wird einmalig in AppData angelegt. Sie
setzt die Verzeichnisse auf `D:\Ahnenblatt`, `D:\Bilder` und `D:\Ausgaben`.
Vorhandene Einstellungen werden nicht überschrieben. Das Prefix und damit
auch dort gespeicherte Freischaltdaten bleiben im Volume. Persönliche Lizenzen
gehören nicht in Dockerfile, Git, Build-Argumente oder Image-Layer.

Zum Einfügen eines Bildes: im Webdateimanager nach `Bilder` hochladen und in
Ahnenblatt über den Dateiauswahldialog `D:\Bilder` öffnen. Ein Browserupload
ist kein automatisches Drag-and-drop in ein Windows-Programm. Ahnenblatt-Dateien
können entsprechend nach `Ahnenblatt` hochgeladen und über `D:\Ahnenblatt`
geöffnet werden.

Die Compose-Datei lässt sich über `.env` anpassen; `.env.example` enthält die
Variablen. `make` liest diese ebenfalls. Wichtige Optionen:

- `IMAGE=ghcr.io/<owner>/<repository>` und `SERIES=4`
- `CONFIG_DIR=./data/4`, `HTTP_PORT=3000`, `PUID=1000`, `PGID=1000`
- `CUSTOM_USER` und `PASSWORD` für die optionale HTTP-Basisauthentifizierung

Ohne `.env` verwendet `make up SERIES=3` automatisch `./data/3` als Configordner.
Bei direktem `docker compose` gilt der Standardpfad der Compose-Datei. Für mehrere
gleichzeitig laufende Instanzen unterschiedliche Compose-Projektnamen, Ports und
Configordner verwenden. Eine Sperre verhindert, dass zwei Container dasselbe
Wine-Profil gleichzeitig öffnen.

Der bisherige Ordner `./config` wird nicht automatisch migriert. Er bleibt
unverändert; auch alte Einstellungen und Freischaltungen werden nicht stillschweigend
übernommen. Für den ersten Test neue Datenordner verwenden und Ahnendateien bzw.
Bilder über den Dateimanager importieren. Alte und neue Compose-Instanz dürfen
nicht gleichzeitig denselben Host-Port belegen.

## GHCR veröffentlichen

```sh
make login
make push SERIES=4
# oder alle vier Varianten:
make push-all
```

`push` baut das Image, führt den isolierten Smoke-Test aus und veröffentlicht
erst danach den genauen Versions- und den Versionslinien-Tag. Der Registryname
muss kleingeschrieben sein. `SOURCE_URL=https://github.com/<owner>/<repo>` und
`REVISION=<commit>` können als OCI-Metadaten mitgegeben werden.

Der Workflow `.github/workflows/container.yml` baut und testet alle vier
Varianten bei Pull Requests und Pushes nach `main` oder `release/**`. Veröffentlichung erfolgt
über **Actions → Container → Run workflow → publish**. Die Anmeldung nutzt das
`GITHUB_TOKEN` mit `packages: write`; ein zusätzlicher Registry-Token ist nicht
nötig. Das Versionsmanifest muss vorher gelockt und eingecheckt sein. Das
GHCR-Paket kann anschließend in GitHub nach Wunsch öffentlich geschaltet werden.

## Tests und Updates

`make check` prüft Shell-, Python- und XML-Syntax, führt bei installiertem
ShellCheck das Linting aus und testet insbesondere den Schutz vorhandener
Benutzerdaten sowie das Abweisen veränderter Installer.

`make smoke SERIES=4` startet einen isolierten Container mit einem temporären
Docker-Volume und **ohne Netzwerk**. Es prüft ein sichtbares Ahnenblatt-Fenster,
den Zugriff auf eine hochgeladene Testdatei über `D:` und den Erhalt der Daten
nach einem Neustart. Container und Testvolume werden anschließend entfernt.
Es greift nicht auf die persönlichen Configordner zu.

Zusätzlich vor einer Freigabe je Version manuell prüfen:

- normale Bedienung und tatsächlicher Versionsstand im Infofenster;
- Upload eines Bildes, Einfügen in Ahnenblatt und erneutes Öffnen nach Neustart;
- Öffnen/Speichern einer Ahnendatei und Export nach `D:\Ausgaben`;
- Freischaltung mit einer passenden Lizenz und Erhalt nach Container-Neuerstellung;
- Imageupdate innerhalb einer Versionslinie mit bestehendem Testprofil.

Für eine neue Anwendungsfassung in `versions/versions.json` Version/URL anpassen,
den zugehörigen `sha256` auf `null` setzen, `make lock SERIES=…` ausführen und
anschließend bauen und testen. Ein Versionswechsel darf keine Datenmigration
oder Abwärtskompatibilität von Ahnendateien voraussetzen.

`BASE_IMAGE` kann auf einen Digest fixiert werden. Standardmäßig wird der
Distributions-Tag benutzt; APT-Pakete und zusätzliche Fontdownloads sind nicht
vollständig eingefroren. Die Installer sind nach dem Lock inhaltsgebunden,
der Gesamtbuild ist damit noch nicht bitgenau reproduzierbar.

Ahnenblatt und die enthaltenen Schriftarten behalten ihre jeweiligen
Herstellerlizenzen; dieses Repository enthält keine persönlichen Lizenzschlüssel.

## Quellen

- [Ahnenblatt 2.99](https://www.ahnenblatt.de/ahnenblatt-kostenlos/),
  [3](https://www.ahnenblatt.de/download3/),
  [4](https://www.ahnenblatt.de/download4/),
  [5](https://www.ahnenblatt.de/download/)
- [LinuxServer KasmVNC-Basisimage](https://github.com/linuxserver/docker-baseimage-kasmvnc)
- [GitHub: Docker-Images veröffentlichen](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)
