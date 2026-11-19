# Bauen und Entwickeln

Für die Nutzung fertiger Images siehe [README.md](README.md).
Dieses Dokument beschreibt ausschließlich lokale Builds und die Repository-Pflege.

## Voraussetzungen

Docker Engine mit Buildx, GNU Make und Python 3. Für aktualisierte
Installer-Prüfsummen wird ExifTool benötigt. ShellCheck wird empfohlen.
Gebaut wird für `linux/amd64`; Wine 11 ist die einzige gepflegte Laufzeit.

## Build-Variablen

Diese Werte werden an `make` übergeben. Sie sind **keine Laufzeitvariablen**:

| Variable | Standard auf `main` | Zweck |
| --- | --- | --- |
| `SERIES` | `5` | Ahnenblatt-Version: `2.99`, `3`, `4` oder `5` |
| `WINE_VERSION` | `11` | Wine-Hauptversion; nur `11` wird unterstützt |
| `IMAGE` | `ghcr.io/vknmnn/ahnenblatt-docker` | Repository für die erzeugten Image-Tags |
| `BASE_IMAGE` | `ghcr.io/linuxserver/baseimage-selkies:debiantrixie` | Basisimage |
| `SOURCE_URL` | Repository-URL | OCI-Quellenmetadaten |
| `REVISION` | `unknown` | Commit-ID für die Image-Metadaten |

`IMAGE` und `SERIES` werden auch von der mitgelieferten Compose-Datei genutzt.
Eine vorhandene `.env` wird vom Makefile eingelesen; Kommandozeilenwerte haben Vorrang.

```sh
make check
make build SERIES=5 IMAGE=ahnenblatt-local
make smoke SERIES=5 IMAGE=ahnenblatt-local
# Alle vier Ahnenblatt-Versionen:
make build-all IMAGE=ahnenblatt-local
make smoke-all IMAGE=ahnenblatt-local
```

`make check` prüft Manifest, Python-, XML- und Bash-Syntax, ShellCheck sowie
Unit-Tests. Die Smoke-Tests verwenden isolierte Volumes und prüfen Offline-Start,
sichtbares Anwendungsfenster, Selkies-Upload/Download, Laufwerk `D:`, Datumsformat
und Datenerhalt nach einem Neustart. Die Selkies-Vorgaben und ENV-Overrides werden
anhand der tatsächlich an Browser gesendeten Einstellungen geprüft. Container und Testvolumes werden anschließend
entfernt. Build-Cache und Testimages separat gezielt bereinigen.

**Vor jedem Git-Push müssen die betroffenen Images auf dem Docker-Testhost
gebaut werden und die Smoke-Tests bestehen.** Statische Prüfungen allein genügen
nicht. Das vermeidet unnötige GitHub-Actions-Builds. Host-Tests in einer isolierten
Umgebung durchführen; keine bestehenden Container, Images oder Daten verändern.

## Aufbau und Installer

Der Build installiert Ahnenblatt in einem temporären Wine-Profil. Nur die
Anwendungsdateien, zusätzliche Schriftarten und Versionsmetadaten werden in das
fertige Image übernommen. Persönliche Profile entstehen beim ersten Start unter
`/config`. WineHQs Debian-Trixie-Pakete enthalten 32- und 64-Bit-Komponenten.

Installer-Versionen, Downloadadressen und SHA-256-Prüfsummen stehen in
`versions/versions.json`. Für ein Update Version und URL ändern, `sha256` auf
`null` setzen und beispielsweise `make lock SERIES=5` ausführen. Die
Manifeständerung prüfen und die betreffende Version vollständig testen.

Docker und GitHub Actions cachen Build-Schichten einschließlich der verifizierten
Downloads. Installer, Wine-Profile, Lizenzschlüssel und persönliche Daten gehören
nicht ins Repository. Die `.dockerignore`-Allowlist beibehalten.

## Branches, Tags und CI

`main` verwendet Ahnenblatt 5 als Standard. `release/2.99`, `release/3`,
`release/4` und `release/5` setzen die jeweilige Serie als Vorgabe.
Gemeinsamen Code und Dokumentation in alle Release-Branches übernehmen.
Die README bleibt branchübergreifend identisch.

`scripts/image-tags.py` legt die Aliase zentral fest: Serien- und exakte
Versionstags sowie die jeweiligen `-wine11`-Tags. Nur Serie 5 erhält `latest`.
Wine-10-Images werden nicht mehr gebaut; bereits vorhandene Registry-Tags werden
nicht automatisch gelöscht.

Die GitHub-Actions-Matrix prüft die vier Serien mit Wine 11. Registry-Schreibzugriff
bleibt auf den ausdrücklich angeforderten Veröffentlichungslauf beschränkt;
gewöhnliche Pushes und Pull Requests führen Prüfungen aus.

Das Image folgt den [LSIO-Branding-Vorgaben](https://docs.linuxserver.io/general/container-branding/).
