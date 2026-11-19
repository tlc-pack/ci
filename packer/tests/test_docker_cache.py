"""Exercise preload failure handling without Docker or AWS access."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "preload-docker-images.sh"


class DockerCacheTest(unittest.TestCase):
    def run_preload(
        self,
        images,
        pull_failures=0,
        run_failure=False,
        fail_command="",
        restart_failure=False,
        initial_config=None,
    ):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docker = root / "docker"
            docker.write_text(
                """#!/usr/bin/env bash
set -eu
echo "$*" >> "$TEST_ROOT/commands"
if [ "$1" = "$FAIL_COMMAND" ]; then
    exit 1
fi
if [ "$1" = pull ]; then
    count=$(cat "$TEST_ROOT/pulls" 2>/dev/null || echo 0)
    count=$((count + 1))
    echo "$count" > "$TEST_ROOT/pulls"
    [ "$count" -gt "$PULL_FAILURES" ]
elif [ "$1" = run ]; then
    [ "$RUN_FAILURE" = false ]
fi
"""
            )
            docker.chmod(0o755)
            for command in ("systemctl", "sleep", "sync"):
                stub = root / command
                stub.write_text(
                    '#!/usr/bin/env bash\n'
                    'echo "$(basename "$0") $*" >> "$TEST_ROOT/services"\n'
                    'if [ "$(basename "$0") $*" = "systemctl restart docker" ] '
                    '&& [ "$RESTART_FAILURE" = true ]; then exit 1; fi\n'
                    'exit 0\n'
                )
                stub.chmod(0o755)
            config_path = root / "etc/docker/daemon.json"
            if initial_config is not None:
                config_path.parent.mkdir(parents=True)
                config_path.write_text(initial_config)
            result = subprocess.run(
                ["bash", str(SCRIPT)],
                env={
                    **os.environ,
                    "PATH": f"{root}:{os.environ['PATH']}",
                    "TEST_ROOT": str(root),
                    "DOCKER_CACHE_IMAGES": images,
                    "PULL_FAILURES": str(pull_failures),
                    "RUN_FAILURE": str(run_failure).lower(),
                    "DOCKER_CACHE_CONFIG_ROOT": str(root / "etc"),
                    "FAIL_COMMAND": fail_command,
                    "RESTART_FAILURE": str(restart_failure).lower(),
                },
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                config = json.loads((root / "etc/docker/daemon.json").read_text())
                self.assertEqual(config["storage-driver"], "overlay2")
                self.assertFalse(config["features"]["containerd-snapshotter"])
                self.assertEqual(
                    (root / "etc/jenkins/docker-cache-images").read_text().splitlines(),
                    images.split(),
                )
                if initial_config is not None:
                    original = json.loads(initial_config)
                    self.assertEqual(config["log-driver"], original["log-driver"])
                    self.assertTrue(config["features"]["buildkit"])
                services = (root / "services").read_text().splitlines()
                self.assertLess(
                    services.index("systemctl stop cron"),
                    services.index("systemctl restart docker"),
                )
            else:
                self.assertFalse((root / "etc/jenkins/docker-cache-images").exists())
            log = root / "commands"
            return result, log.read_text().splitlines() if log.exists() else []

    def test_each_image_is_validated_before_pinning(self):
        result, commands = self.run_preload(
            "example/first@sha256:123 example/second:v2"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for index, image in enumerate(
            ("example/first@sha256:123", "example/second:v2")
        ):
            run = next(
                i
                for i, line in enumerate(commands)
                if line.startswith("run ") and line.endswith(image)
            )
            create = next(
                i
                for i, line in enumerate(commands)
                if line.startswith(f"create --name ci-ami-cache-{index} ")
            )
            self.assertLess(run, create)
            self.assertIn("--pull=never", commands[run])
            self.assertIn("--label ci.ami-cache=true", commands[create])

    def test_transient_pull_failure_retries(self):
        result, commands = self.run_preload("example/image:v1", pull_failures=2)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sum(line.startswith("pull ") for line in commands), 3)

    def test_failed_pull_prevents_success_and_pinning(self):
        result, commands = self.run_preload("example/image:v1", pull_failures=3)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(line.startswith(("run ", "create ")) for line in commands))

    def test_wrong_architecture_or_unrunnable_image_fails_build(self):
        result, commands = self.run_preload("example/image:v1", run_failure=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(line.startswith("create ") for line in commands))

    def test_empty_image_list_fails(self):
        result, commands = self.run_preload("")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(commands, [])

    def test_whitespace_image_list_fails(self):
        result, commands = self.run_preload("   ")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(commands, [])

    def test_failed_cache_container_creation_fails_build(self):
        result, commands = self.run_preload("example/image:v1", fail_command="create")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any(line.startswith("create ") for line in commands))

    def test_failed_image_inspection_fails_build(self):
        result, commands = self.run_preload("example/image:v1", fail_command="image")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any(line.startswith("image inspect ") for line in commands))

    def test_failed_docker_restart_prevents_pulls(self):
        result, commands = self.run_preload("example/image:v1", restart_failure=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(commands, [])

    def test_preserves_existing_daemon_settings(self):
        result, _ = self.run_preload(
            "example/image:v1",
            initial_config=json.dumps(
                {"log-driver": "local", "features": {"buildkit": True}}
            ),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_malformed_daemon_config_prevents_pulls(self):
        result, commands = self.run_preload("example/image:v1", initial_config="{")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(commands, [])


if __name__ == "__main__":
    unittest.main()
