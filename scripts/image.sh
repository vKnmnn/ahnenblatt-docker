#!/usr/bin/env bash
set -euo pipefail
action=${1:?build or publish required}
case "$action" in build|publish) ;; *) exit 2 ;; esac
series=${SERIES:-3}
wine_version=${WINE_VERSION:-10}
image=${IMAGE:-ghcr.io/vknmnn/ahnenblatt-docker}
base=${BASE_IMAGE:-ghcr.io/linuxserver/baseimage-selkies:debiantrixie}
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
tag_list=$(python3 scripts/image-tags.py "$series" "$wine_version" "$image")
mapfile -t tags <<< "$tag_list"
tag_args=()
for tag in "${tags[@]}"; do tag_args+=(--tag "$tag"); done
docker buildx build --platform linux/amd64 --load \
    --build-arg "WINE_VERSION=$wine_version" --build-arg "BASE_IMAGE=$base" --build-arg "SERIES=$series" \
    --build-arg "VERSION=$version" --build-arg "SOURCE_URL=${SOURCE_URL:-}" \
    --build-arg "REVISION=${REVISION:-unknown}" \
    "${tag_args[@]}" .
if [[ "$action" == publish ]]; then
    bash scripts/smoke.sh "${tags[0]}"
    for tag in "${tags[@]}"; do docker push "$tag"; done
fi
