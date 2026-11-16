"""Step 7: the workspace comparison.

Takes a picture of the workspace before an action and again after it, and
reports what actually changed: files created, deleted, or modified.

The reviewer says what it expects an action to do. This says what the action
did. It works from the files themselves, so it does not depend on the reviewer
or the agent being right.
"""

import hashlib
from pathlib import Path

from sandbox import WORKSPACE


def snapshot() -> dict[str, str]:
    """Return {file path: fingerprint of its content} for every file in the workspace."""
    files = {}
    for path in sorted(WORKSPACE.rglob("*")):
        name = str(path.relative_to(WORKSPACE))
        if path.is_symlink():
            # Record where a link points, but never follow it: a link made inside
            # the sandbox could point at a file outside the workspace.
            files[name] = f"link to {path.readlink()}"
        elif path.is_file():
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def compare(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    """Return which files were created, deleted, or modified between two snapshots."""
    return {
        "created": sorted(set(after) - set(before)),
        "deleted": sorted(set(before) - set(after)),
        "modified": sorted(name for name in set(before) & set(after) if before[name] != after[name]),
    }


def describe(changes: dict[str, list[str]]) -> str:
    """One readable line summarising the changes."""
    parts = [f"{kind} {', '.join(names)}" for kind, names in changes.items() if names]
    return "; ".join(parts) if parts else "no files changed"
