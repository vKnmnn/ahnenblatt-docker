#!/usr/bin/env bash
set -euo pipefail
action=${1:?build or publish required}
case "$action" in build|publish) ;; *) exit 2 ;; esac
series=${SERIES:-5}
image=${IMAGE:-ghcr.io/vknmnn/ahnenblatt-docker}
base=${BASE_IMAGE:-ghcr.io/linuxserver/baseimage-kasmvnc:ubuntunoble}
version=$(python3 scripts/versions.py get "$series" version)
checksum=$(python3 scripts/versions.py get "$series" sha256)
if [[ -z "$checksum" ]]; then
    echo "Installer not locked. Run: make lock SERIES=$series" >&2
    exit 1
fi
if [[ "$action" == publish && "$image" != ghcr.io/*/* ]]; then
    echo 'Publishing requires IMAGE=ghcr.io/<owner>/<repository>' >&2
    exit 1
fi
docker buildx build --platform linux/amd64 --load \
    --build-arg "BASE_IMAGE=$base" --build-arg "SERIES=$series" \
    --build-arg "VERSION=$version" --build-arg "SOURCE_URL=${SOURCE_URL:-}" \
    --build-arg "REVISION=${REVISION:-unknown}" \
    --tag "$image:$series" --tag "$image:$version" .
if [[ "$action" == publish ]]; then
    bash scripts/smoke.sh "$image:$series"
    docker push "$image:$version"
    docker push "$image:$series"
fi
