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


def snapshot(folder: Path = WORKSPACE) -> dict[str, str]:
    """Return {file path: fingerprint and size of its content} for every file in the folder.

    The size (lines and bytes) is kept so a change can be described, such as
    "3 lines (84 bytes) before, 1 line (22 bytes) after".
    """
    files = {}
    for path in sorted(folder.rglob("*")):
        name = str(path.relative_to(folder))
        if path.is_symlink():
            # Record where a link points, but never follow it: a link made inside
            # the sandbox could point at a file outside the workspace.
            files[name] = f"link to {path.readlink()}"
        elif path.is_file():
            content = path.read_bytes()
            lines = content.count(b"\n") + (1 if content and not content.endswith(b"\n") else 0)
            files[name] = f"{hashlib.sha256(content).hexdigest()} {lines} {len(content)}"
    return files


def size(fingerprint: str) -> str:
    """'<hash> 3 84' becomes '3 lines, 84 bytes'."""
    if fingerprint.startswith("link to"):
        return fingerprint
    _, lines, length = fingerprint.split()
    return f"{lines} line{'s' if lines != '1' else ''}, {length} bytes"


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
