"""Step 4: the agent loop.

Connects the two earlier pieces:
  - the model proposes an action      (as in propose_action.py)
  - the action is carried out         (tools.py, using sandbox.py)
and adds the loop: the result goes back to the model, which then
proposes the next action, until it says the task is finished.

Before any action is carried out, the reviewer judges it (reviewer.py):
  allow -> the action runs
  block -> the action does not run, and the agent is told why
  ask   -> the person at the terminal decides

Run with:  python agent.py "your task in plain words"
"""

import json
import sys

from dotenv import load_dotenv
from openai import OpenAI

from reviewer import review
from tools import TOOLS, describe_action, run_tool, who_runs

load_dotenv()
client = OpenAI()

MODEL = "gpt-5.5"
MAX_STEPS = 10

# True: the reviewer is shown the person's task as well as the action.
# False: the reviewer sees only the action.
REVIEWER_SEES_TASK = True

# Standing instructions the model gets on every request.
INSTRUCTIONS = (
    "You complete file and shell tasks inside a workspace folder. "
    "Act only through the tools you are given, one action at a time. "
    "When the task is finished, reply with a short summary and call no tool."
)

def say(who: str, text: str) -> None:
    """Print text with a label showing which component it came from."""
    label = f"[{who}]"
    for line in (text.splitlines() or [""]):
        print(f"{label:<17} {line}")


def run_agent(task: str) -> None:
    # The conversation is the model's only memory. It starts with the task
    # and grows by one proposal and one result on every turn of the loop.
    conversation = [{"role": "user", "content": task}]

    for step in range(1, MAX_STEPS + 1):
        response = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            input=conversation,
            tools=TOOLS,
        )

        # Keep everything the model just said, so it sees it next time.
        conversation += response.output

        proposals = [item for item in response.output if item.type == "function_call"]

        # No proposal means the model considers the task finished.
        if not proposals:
            say("Agent model", "Task finished. Summary:")
            say("Agent model", response.output_text)
            return

        for proposal in proposals:
            name = proposal.name
            arguments = json.loads(proposal.arguments)
            say("Agent model", f"Step {step}, proposes {describe_action(name, arguments)}")

            # The reviewer judges the proposal before anything runs.
            verdict = review(name, arguments, task=task if REVIEWER_SEES_TASK else None)
            say("Reviewer model", f"{verdict.decision}: {verdict.reason}")

            if verdict.decision == "allow":
                result = run_tool(name, arguments)
                say(who_runs(name), result)
            elif verdict.decision == "block":
                result = f"This action was blocked and did not run. Reason: {verdict.reason}"
                say("Program", "Action not run. Telling the agent model it was blocked.")
            else:  # "ask": the person decides
                answer = input(f"{'[Program]':<17} Allow this action? Type y to allow, anything else to refuse: ")
                if answer.strip().lower() == "y":
                    say("Person", "Allowed.")
                    result = run_tool(name, arguments)
                    say(who_runs(name), result)
                else:
                    say("Person", "Refused.")
                    result = "The person refused this action, so it did not run."
                    say("Program", "Action not run. Telling the agent model it was refused.")

            print()

            # Hand the result back to the model, tied to the proposal it answers.
            conversation.append({
                "type": "function_call_output",
                "call_id": proposal.call_id,
                "output": result,
            })

    say("Program", f"Stopped: reached the limit of {MAX_STEPS} steps without finishing.")


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "List the files in the workspace."
    say("Person", f"Task: {task}")
    print()
    run_agent(task)
