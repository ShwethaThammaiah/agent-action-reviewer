"""Ask reviewers about one scenario many times, to see how steady their answers are.

Used to check whether a difference between two reviewers on one scenario is
real or chance.

Run with:  python repeat_scenario.py F4 10
           (scenario id, number of times; default 10)
"""

import json
import sys
from collections import Counter
from pathlib import Path

from chain_reviewer import review_chain
from rehearse import rehearse
from reset_workspace import reset_workspace
from reviewer import review

SCENARIOS_FILE = Path(__file__).parent / "scenarios" / "scenarios.json"

REVIEWERS = {
    "model-with-effect": lambda s: review(s["tool"], s["arguments"], task=s["task"],
                                          effect=rehearse(s["tool"], s["arguments"])),
    "chain": lambda s: review_chain(s["tool"], s["arguments"], task=s["task"]),
}

if __name__ == "__main__":
    scenario_id = sys.argv[1]
    times = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    scenario = next(s for s in json.loads(SCENARIOS_FILE.read_text()) if s["id"] == scenario_id)
    reset_workspace()

    print(f"{scenario_id}: {scenario['task']}")
    print(f"Action: {scenario['tool']} {scenario['arguments']}")
    print(f"Label: {scenario['label']}")
    print(f"Rehearsed effect:\n  " + rehearse(scenario["tool"], scenario["arguments"]).replace("\n", "\n  "))
    print()
    for name, judge in REVIEWERS.items():
        decisions = [judge(scenario).decision for _ in range(times)]
        print(f"{name:<18} {dict(Counter(decisions))}   in order: {' '.join(decisions)}")
