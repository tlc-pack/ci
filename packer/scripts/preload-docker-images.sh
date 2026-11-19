#!/usr/bin/env bash
set -euo pipefail

# Pull the native platform; ECR pulls can reuse these layers.
read -r -a images <<< "${DOCKER_CACHE_IMAGES:?Set DOCKER_CACHE_IMAGES}"
if [ "${#images[@]}" -eq 0 ]; then
    echo 'DOCKER_CACHE_IMAGES must contain at least one image' >&2
    exit 1
fi

# Pause cleanup while populating the cache; cron starts again at boot.
systemctl stop cron

# Use the same image store as the GPU AMI.
config_root="${DOCKER_CACHE_CONFIG_ROOT:-/etc}"
install -d "$config_root/docker"
python3 - "$config_root/docker/daemon.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
config = json.loads(path.read_text()) if path.exists() else {}
config['storage-driver'] = 'overlay2'
config.setdefault('features', {})['containerd-snapshotter'] = False
path.write_text(json.dumps(config, indent=2) + '\n')
PY
systemctl restart docker
for index in "${!images[@]}"; do
    image="${images[$index]}"
    pulled=false
    for attempt in 1 2 3; do
        if docker pull "$image"; then
            pulled=true
            break
        fi
        if [ "$attempt" -lt 3 ]; then
            sleep 10
        fi
    done
    if [ "$pulled" != true ]; then
        echo "Could not preload $image" >&2
        exit 1
    fi

    # Check native execution.
    docker run --pull=never --rm --network=none --entrypoint /bin/true "$image"

    # Pin cached layers with a stopped container.
    docker create --name "ci-ami-cache-${index}" --label ci.ami-cache=true \
        --network=none --entrypoint /bin/true "$image"
    docker image inspect "$image" --format '{{.Id}} {{.Os}}/{{.Architecture}} {{json .RepoDigests}}'
done
install -d "$config_root/jenkins"
printf '%s\n' "${images[@]}" > "$config_root/jenkins/docker-cache-images"
docker system df
sync
