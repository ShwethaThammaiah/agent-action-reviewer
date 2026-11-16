"""Step 6: the decision log.

Every reviewed action is written to a file as one line, whether it ran or not.
This is the record you go back to when you want to know what the agent tried,
what the reviewer decided and why, and what happened as a result.

The file is results/live_decisions.jsonl. Each line is one JSON object.
(It is not a .log file because this repo's .gitignore ignores *.log.)
"""

import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path(__file__).parent / "results" / "live_decisions.jsonl"


def record(**fields) -> None:
    """Append one entry to the decision log, stamped with the current time."""
    LOG_FILE.parent.mkdir(exist_ok=True)
    entry = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), **fields}
    with LOG_FILE.open("a") as log:
        log.write(json.dumps(entry) + "\n")
