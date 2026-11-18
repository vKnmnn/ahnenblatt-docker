#!/usr/bin/env bash
set -euo pipefail
image=${1:?image tag required}
# Include the actual daemon version when diagnosing Wine socket failures.
docker version --format 'Docker server: {{.Server.Version}}'
name="ahnenblatt-smoke-$$-$RANDOM"
volume="$name-config"
created_volume=false
created_container=false
cleanup() {
    local status=$?
    if [[ "$created_container" == true ]]; then
        if ((status != 0)); then docker logs "$name" >&2 || true; fi
        docker rm -f "$name" >/dev/null || true
    fi
    if [[ "$created_volume" == true ]]; then docker volume rm "$volume" >/dev/null || true; fi
}
trap cleanup EXIT
docker volume create "$volume" >/dev/null
created_volume=true
# No network: first startup must work entirely from the image.
docker create --name "$name" --network none --shm-size 1g \
    --mount "type=volume,source=$volume,target=/config" "$image" >/dev/null
created_container=true
docker start "$name" >/dev/null
wait_for_window() {
    for ((attempt=0; attempt<120; attempt++)); do
        if docker exec "$name" /usr/local/bin/ahnenblatt-healthcheck >/dev/null 2>&1; then
            return 0
        fi
        sleep 2
    done
    echo 'No visible Ahnenblatt window within 240 seconds' >&2
    return 1
}
wait_for_window
# Check the Selkies frontend as well as the Wine window.
docker exec "$name" curl --fail --silent --show-error --insecure \
    --retry 30 --retry-connrefused --retry-delay 1 --max-time 5 \
    https://localhost:3001/api/health >/dev/null
docker exec "$name" curl --fail --silent --show-error --insecure https://localhost:3001/ >/dev/null
docker exec "$name" bash -c 'test "$FILE_MANAGER_PATH" = /config/files'
# Exercise the same upload/download API as the browser, then read through Wine.
docker exec "$name" curl --fail --silent --show-error --insecure \
    -H 'Origin: https://localhost:3001' -H 'X-Upload-Path: upload-smoke.txt' \
    --data-binary 'upload-smoke-ok' https://localhost:3001/api/upload >/dev/null
download=$(docker exec "$name" curl --fail --silent --show-error --insecure \
    https://localhost:3001/api/files/upload-smoke.txt)
[[ "$download" == upload-smoke-ok ]]
docker exec -u abc "$name" bash -c '
    set -euo pipefail
    series=$(python3 -c '\''import json; print(json.load(open("/opt/ahnenblatt-image.json"))["series"])'\'')
    export WINEPREFIX="/config/versions/$series/wineprefix" DISPLAY=:1 WINEDEBUG=-all
    wine cmd /c type "D:\\upload-smoke.txt" | tr -d "\r" | grep -qx upload-smoke-ok
    echo persisted > "$WINEPREFIX/smoke-sentinel"
    test ! -d /tmp/build-prefix
    test ! -f /tmp/ahnenblatt-setup.exe
'
docker restart "$name" >/dev/null
wait_for_window
docker exec -u abc "$name" bash -c '
    set -euo pipefail
    series=$(python3 -c '\''import json; print(json.load(open("/opt/ahnenblatt-image.json"))["series"])'\'')
    grep -qx persisted "/config/versions/$series/wineprefix/smoke-sentinel"
    grep -qx upload-smoke-ok /config/files/upload-smoke.txt
'
echo "Smoke test passed: $image (window, offline startup, Selkies upload/download, D: mapping, persistence)"
