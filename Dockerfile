# syntax=docker/dockerfile:1
ARG BASE_IMAGE=ghcr.io/linuxserver/baseimage-selkies:debiantrixie
FROM ${BASE_IMAGE} AS desktop
USER root
# Desktop dependencies shared by the installer and final runtime.
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      fonts-dejavu-core fonts-liberation fonts-noto-core \
      fontconfig tint2 python3 python3-xdg python3-gi gir1.2-gtk-3.0 x11-xserver-utils util-linux xdotool ca-certificates \
 && rm -rf /var/lib/apt/lists/*
ENV LANG=en_US.UTF-8 \
    TZ=Europe/Berlin WINEDEBUG=-all WINEDLLOVERRIDES=mscoree= \
    FILE_MANAGER_PATH=/config/files TITLE=Ahnenblatt \
    PIXELFLUX_WAYLAND=false LSIO_FIRST_PARTY=false SELKIES_DESKTOP=false \
    NO_GAMEPAD=true NO_WEBCAM=true \
    SELKIES_AUDIO_ENABLED="false|locked" SELKIES_MICROPHONE_ENABLED="false|locked" \
    SELKIES_UI_SHOW_CORE_BUTTONS=false SELKIES_UI_SIDEBAR_SHOW_AUDIO_SETTINGS=false \
    SELKIES_UI_SIDEBAR_SHOW_GAMEPADS=false SELKIES_UI_SIDEBAR_SHOW_GAMING_MODE=false \
    SELKIES_UI_SIDEBAR_SHOW_WEBCAM=false SELKIES_UI_SIDEBAR_SHOW_APPS=false

FROM desktop AS runtime
ARG SERIES=3
# Keep existing win64 profiles for older applications, but omit i386 for 4/5.
RUN set -eu; \
    case "$SERIES" in \
      2.99|3) dpkg --add-architecture i386; wine_packages="wine wine64 wine32:i386" ;; \
      4|5) wine_packages="wine wine64" ;; \
      *) echo "Unsupported Ahnenblatt series: $SERIES" >&2; exit 1 ;; \
    esac; \
    apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends $wine_packages \
 && rm -rf /var/lib/apt/lists/*

# Installers and winetricks may need 32-bit Wine even for a 64-bit application.
# This stage is not inherited by the final image.
FROM desktop AS installer
RUN dpkg --add-architecture i386 \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      wine wine64 wine32:i386 xvfb xauth curl cabextract unzip winetricks libimage-exiftool-perl \
 && rm -rf /var/lib/apt/lists/*
COPY versions/ /build/versions/
COPY scripts/versions.py /build/scripts/versions.py
ARG SERIES=3
RUN python3 /build/scripts/versions.py fetch "${SERIES}" /tmp/ahnenblatt-setup.exe
COPY scripts/install-build.sh /build/scripts/install-build.sh
COPY scripts/build-steps.sh /build/scripts/build-steps.sh
RUN xvfb-run -a bash /build/scripts/install-build.sh "${SERIES}"

FROM runtime AS final
ARG SERIES=3
ARG VERSION
ARG SOURCE_URL
ARG REVISION=unknown
LABEL maintainer="vKnmnn" \
      build_version="Ahnenblatt ${VERSION} (${REVISION})" \
      org.opencontainers.image.title="Ahnenblatt with Wine and Selkies" \
      org.opencontainers.image.description="Standard installation; personal Wine prefix created at first start" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.source="${SOURCE_URL}" \
      org.opencontainers.image.revision="${REVISION}"
ENV AHNENBLATT_SERIES=${SERIES}
COPY --from=installer /build-output/app/ /opt/ahnenblatt/
COPY --from=installer /build-output/fonts/ /usr/local/share/fonts/ahnenblatt/
COPY --from=installer /build-output/app.json /opt/ahnenblatt-image.json
COPY root/ /
RUN /usr/bin/python3 /usr/local/lib/ahnenblatt/configure-openbox.py /etc/xdg/openbox/rc.xml \
 && cp /etc/xdg/openbox/rc.xml /etc/xdg/openbox/rc.xml.bak \
 && chmod +x /etc/services.d/ahnenblatt-desktop/run /etc/services.d/ahnenblatt/run /etc/services.d/ahnenblatt/finish \
      /usr/local/bin/ahnenblatt-start /usr/local/bin/ahnenblatt-healthcheck \
 && fc-cache -f
HEALTHCHECK --start-period=180s --interval=30s --timeout=10s --retries=3 \
    CMD /usr/local/bin/ahnenblatt-healthcheck
