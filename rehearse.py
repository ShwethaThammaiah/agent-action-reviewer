"""Step 13: the rehearsal (Shwetha's idea).

Before an action runs for real, run it on a throwaway copy of the workspace,
compare the copy before and after, and describe exactly what changed.

The result is a measured fact, not a prediction, such as:
    Deleted: logs/app.log (3 lines, 132 bytes)
    Changed: notes.txt, from 3 lines, 84 bytes to 1 line, 22 bytes

Why this is safe even though the action has not been reviewed yet: the copy is
the only folder the container can see, and the container has no network. The
same sandbox that contains a wrong "allow" contains the rehearsal.

Run with:  python rehearse.py   (rehearses a few hand-written actions)
"""

import shutil
import tempfile
from pathlib import Path

from sandbox import WORKSPACE
from tools import run_tool
from workspace_diff import compare, size, snapshot

# Throwaway copies live inside the project folder, because Docker on a Mac can
# only share folders under your home folder.
REHEARSALS = Path(__file__).parent / ".rehearsals"


def rehearse(name: str, arguments: dict) -> str:
    """Run the action on a copy of the workspace and describe what it changed."""
    if name == "call_url":
        return (f"Cannot be rehearsed: it would send {len(arguments['body'])} characters "
                f"to {arguments['url']}, which is outside the sandbox.")

    REHEARSALS.mkdir(exist_ok=True)
    holder = Path(tempfile.mkdtemp(dir=REHEARSALS))   # a unique folder per rehearsal
    copy = holder / "workspace"
    try:
        shutil.copytree(WORKSPACE, copy, symlinks=True)
        before = snapshot(copy)
        result = run_tool(name, arguments, workspace=copy)
        after = snapshot(copy)
    finally:
        shutil.rmtree(holder, ignore_errors=True)    # the copy is thrown away either way

    changes = compare(before, after)
    lines = []
    for path in changes["deleted"]:
        lines.append(f"Deleted: {path} ({size(before[path])})")
    for path in changes["modified"]:
        lines.append(f"Changed: {path}, from {size(before[path])} to {size(after[path])}")
    for path in changes["created"]:
        lines.append(f"Created: {path} ({size(after[path])})")
    if not lines:
        lines.append("No files were created, changed, or deleted.")

    first_line = result.splitlines()[0] if result else ""
    if "failed" in first_line:
        lines.append(f"The command failed during the rehearsal ({first_line}). "
                     "The rehearsal has no network, so anything that needs the internet fails here.")
    return "\n".join(lines)


if __name__ == "__main__":
    examples = [
        ("run_shell", {"command": "rm -f logs/*"}),
        ("write_file", {"path": "notes.txt", "content": "- pens were restocked\n"}),
        ("run_shell", {"command": 'echo "- restock pens" >> notes.txt'}),
        ("run_shell", {"command": "truncate -s 0 logs/app.log logs/old.log"}),
        ("run_shell", {"command": "ls -la"}),
        ("call_url", {"url": "https://supplier.example.com/api/orders", "method": "POST", "body": "item,quantity\npens,3\n"}),
    ]
    for name, arguments in examples:
        print(f"Action:   {name} {arguments}")
        for line in rehearse(name, arguments).splitlines():
            print(f"Effect:   {line}")
        print()
