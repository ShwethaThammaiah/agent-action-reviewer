"""Step 11: the combined reviewer (Shwetha's design).

Uses the three reviewers together, but only calls the third when needed:

  1. The rules decide first. They are free and instant.
  2. The model that sees the task decides second.
  3. If those two agree, that is the decision.
  4. If one says ask and the other says block, the decision is ask:
     both mean "don't run it", so the person decides. No third call.
  5. Otherwise (allow against ask, or allow against block), the model that
     sees only the action breaks the tie, and the majority of the three wins.

One safeguard: a block can never be outvoted all the way to allow.
If the majority says allow but any reviewer said block, the decision is ask.

Run with:  python combined_reviewer.py   (judges a few hand-written actions)
"""

from collections import Counter

from reviewer import Decision, review
from rule_reviewer import review_by_rules


def review_combined(name: str, arguments: dict, task: str | None = None) -> Decision:
    rules = review_by_rules(name, arguments, task=task)
    model = review(name, arguments, task=task)
    summary = f"rules said {rules.decision}, model with task said {model.decision}"

    # The two agree: done, no third call.
    if rules.decision == model.decision:
        return Decision(decision=rules.decision, reason=f"Combined, agreed ({summary}). {model.reason}")

    # Ask against block: both mean don't run it, so the person decides.
    if {rules.decision, model.decision} == {"ask", "block"}:
        return Decision(decision="ask", reason=f"Combined, ask or block, so the person decides ({summary}).")

    # Allow against ask, or allow against block: the third reviewer breaks the tie.
    third = review(name, arguments)
    votes = [rules.decision, model.decision, third.decision]
    winner, count = Counter(votes).most_common(1)[0]
    if count < 2:
        winner = "ask"          # all three differ: nobody has a majority
    if winner == "allow" and "block" in votes:
        winner = "ask"          # the safeguard: a block is never outvoted to allow

    return Decision(
        decision=winner,
        reason=f"Combined, tie-break ({summary}, model without task said {third.decision}).",
    )


if __name__ == "__main__":
    examples = [
        ("run_shell", {"command": "ls -la"}, "List the files."),
        ("write_file", {"path": "notes.txt", "content": "- pens were restocked\n"}, "Add a note that the pens were restocked."),
        ("run_shell", {"command": "cp data/inventory.csv data/inventory.backup.csv"}, "Make a backup copy of the inventory data."),
        ("run_shell", {"command": "rm -rf logs"}, "Free up some disk space."),
    ]
    for name, arguments, task in examples:
        result = review_combined(name, arguments, task=task)
        print(f"Task:     {task}")
        print(f"Action:   {name} {arguments}")
        print(f"Decision: {result.decision}")
        print(f"Reason:   {result.reason}\n")
