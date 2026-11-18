"""Step 12: compare harness runs over time.

Every run of harness.py adds one line to results/history.jsonl, recording what
the run was made from (the git commit, any uncommitted changes, the version of
the scenarios and of the reviewer instructions) and its scores.

This prints those runs side by side, oldest first, for one reviewer, so you can
see which change made the results better or worse.

Run with:
    python history.py                  the model reviewer that sees the task
    python history.py combined         any other reviewer, by its harness name
"""

import json
import sys
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "results" / "history.jsonl"

# The numbers worth watching, in the order they are printed.
MEASURES = [
    ("harmful caught", "Harmful stopped"),
    ("harmful blocked outright", "Harmful blocked"),
    ("safe wrongly stopped", "Safe stopped"),
    ("unclear: allowed", "Unclear allowed"),
    ("exact match", "Exact match"),
    ("review time, median", "Median time"),
]


def count(value: str) -> str:
    """'11/12 (92%)' becomes '11/12'."""
    return value.split(" ")[0]


if __name__ == "__main__":
    reviewer_name = sys.argv[1] if len(sys.argv) > 1 else "model-with-task"
    runs = [json.loads(line) for line in HISTORY_FILE.read_text().splitlines() if line.strip()]
    runs = [run for run in runs if reviewer_name in run["scores"]]
    if not runs:
        sys.exit(f"No runs recorded for {reviewer_name}.")

    print(f"Reviewer: {reviewer_name}\n")
    header = ["Run time (UTC)", "Commit", "Scenarios", "Subset", "Instructions"] + [label for _, label in MEASURES]
    rows = []
    previous = None
    for run in runs:
        commit = run["commit"] + ("*" if run["uncommitted_changes"] else "")
        scenarios = run["scenarios_version"]
        instructions = run["reviewer_instructions_version"]
        if previous and scenarios != previous["scenarios_version"]:
            scenarios += " new"
        if previous and instructions != previous["reviewer_instructions_version"]:
            instructions += " new"
        scores = run["scores"][reviewer_name]
        rows.append([run["time"][:16].replace("T", " "), commit, scenarios, run.get("scenario_subset", "all"), instructions]
                    + [count(scores.get(key, "-")) for key, _ in MEASURES])
        previous = run

    widths = [max(len(str(row[i])) for row in rows + [header]) + 2 for i in range(len(header))]
    print("".join(f"{h:<{w}}" for h, w in zip(header, widths)))
    for row in rows:
        print("".join(f"{str(c):<{w}}" for c, w in zip(row, widths)))

    print("\n* the run used uncommitted code changes")
    print("new: the scenarios or reviewer instructions changed since the run above.")
    print("Runs with different scenarios are not directly comparable.")
