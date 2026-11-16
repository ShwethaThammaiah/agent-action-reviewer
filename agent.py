"""Step 4: the agent loop.

Connects the two earlier pieces:
  - the model proposes an action      (as in propose_action.py)
  - the sandbox runs it               (as in sandbox.py)
and adds the loop: the result goes back to the model, which then
proposes the next action, until it says the task is finished.

There is no reviewer yet. Every proposed action is run.

Run with:  python agent.py "your task in plain words"
"""

import json
import sys

from dotenv import load_dotenv
from openai import OpenAI

from sandbox import run_in_sandbox

load_dotenv()
client = OpenAI()

MODEL = "gpt-5.5"
MAX_STEPS = 10

# Standing instructions the model gets on every request.
INSTRUCTIONS = (
    "You complete file and shell tasks inside a workspace folder. "
    "Use the run_shell tool to act, one command at a time. "
    "When the task is finished, reply with a short summary and call no tool."
)

RUN_SHELL_TOOL = {
    "type": "function",
    "name": "run_shell",
    "description": "Run a shell command in the workspace folder and return its exit code and output.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to run.",
            },
        },
        "required": ["command"],
        "additionalProperties": False,
    },
    "strict": True,
}


def run_agent(task: str) -> None:
    # The conversation is the model's only memory. It starts with the task
    # and grows by one proposal and one result on every turn of the loop.
    conversation = [{"role": "user", "content": task}]

    for step in range(1, MAX_STEPS + 1):
        response = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            input=conversation,
            tools=[RUN_SHELL_TOOL],
        )

        # Keep everything the model just said, so it sees it next time.
        conversation += response.output

        proposals = [item for item in response.output if item.type == "function_call"]

        # No proposal means the model considers the task finished.
        if not proposals:
            print("Agent finished:")
            print(f"  {response.output_text}")
            return

        for proposal in proposals:
            command = json.loads(proposal.arguments)["command"]
            print(f"Step {step}: the model proposed: {command}")

            # ---- The reviewer will go here. For now, every action is run. ----
            result = run_in_sandbox(command)
            print(result)
            print()

            # Hand the result back to the model, tied to the proposal it answers.
            conversation.append({
                "type": "function_call_output",
                "call_id": proposal.call_id,
                "output": result,
            })

    print(f"Stopped: reached the limit of {MAX_STEPS} steps without finishing.")


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "List the files in the workspace."
    print(f"Task: {task}")
    print()
    run_agent(task)
