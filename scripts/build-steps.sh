#!/usr/bin/env bash
# Sourced by install-build.sh; all diagnostics concern the temporary build prefix.
run_step() {
    local name=$1 limit=$2 started=$SECONDS status
    shift 2
    printf '[build] START %s (limit %ss)\n' "$name" "$limit"
    if timeout --kill-after=10 "$limit" "$@"; then
        printf '[build] OK %s (%ss)\n' "$name" "$((SECONDS - started))"
    else
        status=$?
        printf '[build] FAILED %s: exit %s after %ss\n' \
            "$name" "$status" "$((SECONDS - started))" >&2
        if [[ "$status" == 124 || "$status" == 137 ]]; then
            echo '[build] The step reached its timeout or was killed.' >&2
        fi
        if [[ -f /tmp/ahnenblatt-install.log ]]; then
            tail -n 60 /tmp/ahnenblatt-install.log >&2 || true
        fi
        xdotool search --onlyvisible --name '.*' getwindowname '%@' >&2 2>/dev/null || true
        return "$status"
    fi
}

stop_build_wine() {
    # The installer can launch Ahnenblatt even in silent mode. Do not wait for
    # that GUI to close by itself. This affects only WINEPREFIX, never user data.
    if [[ ${WINEPREFIX:-} != /tmp/build-prefix ]]; then
        echo '[build] Refusing to stop Wine outside the temporary build prefix' >&2
        return 1
    fi
    run_step 'stop temporary Wine processes' 30 wineserver -k
    run_step 'wait for temporary Wine shutdown' 30 wineserver -w
}
