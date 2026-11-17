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


def run_in_sandbox(command: str, stdin_text: str | None = None, workspace: Path = WORKSPACE) -> str:
    """Run a shell command in the sandbox. Return its exit code and output as text.

    stdin_text, if given, is fed to the command as its input. write_file uses
    this to pass a file's content into the container.

    workspace is the folder shared with the container. Normally the real
    workspace; the rehearsal passes a throwaway copy instead.
    """
    docker_command = [
        "docker", "run",
        "--rm",                             # delete the container when the command ends
        *(["-i"] if stdin_text is not None else []),  # keep input open only when there is input
        "--network", "none",                # no internet access
        "-v", f"{workspace}:/workspace",    # the one shared folder
        "-w", "/workspace",                 # start inside that folder
        IMAGE,
        "sh", "-c", command,                # the command itself, run by a shell
    ]

    try:
        result = subprocess.run(
            docker_command,
            input=stdin_text,
            # With no input, give the command an empty input so it cannot sit waiting for typing.
            stdin=None if stdin_text is not None else subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"The command was stopped after {TIMEOUT_SECONDS} seconds."

    # Every command reports a number when it ends: 0 means it worked,
    # anything else means it failed. Say so in words, then give what it printed.
    status = "succeeded" if result.returncode == 0 else "failed"
    output = (result.stdout + result.stderr).strip() or "(the command printed nothing)"
    return f"Command {status} (exit code {result.returncode}). It printed:\n{output}"


if __name__ == "__main__":
    # A quick manual check, run with: python sandbox.py
    for command in ["ls -R", "cat notes.txt", "ls /Users"]:
        print(f"$ {command}")
        print(run_in_sandbox(command))
        print()
