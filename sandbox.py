"""Step 3: run one shell command inside the sandbox and return what it printed.

The sandbox is a Docker container that:
  - is created fresh for each command and deleted afterwards,
  - has no network access,
  - shares exactly one folder with this laptop: ./workspace

Nothing here involves a model. This is the only place in the project
where a command actually runs.
"""

import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).parent / "workspace"
IMAGE = "python:3.12-slim"
TIMEOUT_SECONDS = 30


def run_in_sandbox(command: str) -> str:
    """Run a shell command in the sandbox. Return its exit code and output as text."""
    docker_command = [
        "docker", "run",
        "--rm",                             # delete the container when the command ends
        "--network", "none",                # no internet access
        "-v", f"{WORKSPACE}:/workspace",    # the one shared folder
        "-w", "/workspace",                 # start inside that folder
        IMAGE,
        "sh", "-c", command,                # the command itself, run by a shell
    ]

    try:
        result = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"The command was stopped after {TIMEOUT_SECONDS} seconds."

    output = (result.stdout + result.stderr).strip()
    return f"exit code: {result.returncode}\n{output}"


if __name__ == "__main__":
    # A quick manual check, run with: python sandbox.py
    for command in ["ls -R", "cat notes.txt", "ls /Users"]:
        print(f"$ {command}")
        print(run_in_sandbox(command))
        print()
