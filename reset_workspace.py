"""Step 8: reset the workspace to a known starting state.

Deletes the workspace folder and replaces it with a fresh copy of
workspace_template. Run it before a task when you want a clean start:

    python reset_workspace.py

The test harness will call reset_workspace() before every scenario, so each
one starts from exactly the same files.
"""

import shutil
from pathlib import Path

from sandbox import WORKSPACE

TEMPLATE = Path(__file__).parent / "workspace_template"


def reset_workspace() -> None:
    """Throw away the current workspace and copy the template in its place."""
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    # symlinks=True copies a link as a link and never follows it.
    shutil.copytree(TEMPLATE, WORKSPACE, symlinks=True)


if __name__ == "__main__":
    reset_workspace()
    files = sorted(str(path.relative_to(WORKSPACE)) for path in WORKSPACE.rglob("*") if path.is_file())
    print(f"Workspace reset. It now contains {len(files)} files:")
    for name in files:
        print(f"  {name}")
