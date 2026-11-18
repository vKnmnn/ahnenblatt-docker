# syntax=docker/dockerfile:1
ARG BASE_IMAGE=ghcr.io/linuxserver/baseimage-kasmvnc:ubuntunoble
FROM ${BASE_IMAGE} AS runtime
USER root
# Older releases and the installers require 32-bit Wine as well.
RUN dpkg --add-architecture i386 \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      wine wine64 wine32:i386 fonts-dejavu-core fonts-liberation \
      fontconfig tint2 python3 python3-xdg util-linux xdotool ca-certificates \
 && rm -rf /var/lib/apt/lists/*
ENV LANG=de_DE.UTF-8 LANGUAGE=de_DE:de LC_ALL=de_DE.UTF-8 \
    TZ=Europe/Berlin WINEDEBUG=-all WINEDLLOVERRIDES=mscoree= \
    FM_HOME=/config/files TITLE=Ahnenblatt

FROM runtime AS installer
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      xvfb xauth curl cabextract unzip winetricks libimage-exiftool-perl \
 && rm -rf /var/lib/apt/lists/*
COPY versions/ /build/versions/
COPY scripts/versions.py /build/scripts/versions.py
COPY scripts/install-build.sh /build/scripts/install-build.sh
COPY scripts/build-steps.sh /build/scripts/build-steps.sh
ARG SERIES=4
RUN python3 /build/scripts/versions.py fetch "${SERIES}" /tmp/ahnenblatt-setup.exe \
 && xvfb-run -a bash /build/scripts/install-build.sh "${SERIES}"

FROM runtime AS final
ARG SERIES=4
ARG VERSION
ARG SOURCE_URL
ARG REVISION=unknown
LABEL org.opencontainers.image.title="Ahnenblatt with Wine and KasmVNC" \
      org.opencontainers.image.description="Standard installation; personal Wine prefix created at first start" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.source="${SOURCE_URL}" \
      org.opencontainers.image.revision="${REVISION}"
ENV AHNENBLATT_SERIES=${SERIES}
COPY --from=installer /build-output/app/ /opt/ahnenblatt/
COPY --from=installer /build-output/fonts/ /usr/local/share/fonts/ahnenblatt/
COPY --from=installer /build-output/app.json /opt/ahnenblatt-image.json
COPY root/ /
RUN chmod +x /etc/services.d/ahnenblatt/run /etc/services.d/ahnenblatt/finish \
      /usr/local/bin/ahnenblatt-start /usr/local/bin/ahnenblatt-healthcheck \
 && fc-cache -f
HEALTHCHECK --start-period=180s --interval=30s --timeout=10s --retries=3 \
    CMD /usr/local/bin/ahnenblatt-healthcheck
