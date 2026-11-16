"""Step 2: give the model one tool and watch it propose an action.

The model is told a tool called run_shell exists. It can ask for that tool
to be used, but it cannot use it. This script prints what the model asked
for and then stops. Nothing is run.
"""

import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# A description of one tool, written for the model to read.
# It says what the tool is called, what it is for, and what input it takes.
run_shell_tool = {
    "type": "function",
    "name": "run_shell",
    "description": "Run a shell command in the project workspace and return its output.",
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

task = "List the files in the current folder."

response = client.responses.create(
    model="gpt-5.5",
    input=task,
    tools=[run_shell_tool],
)

print(f"Task given to the model: {task}")
print()

# The reply is a list of items. Each item is either ordinary text
# or a request to use a tool (type "function_call").
for item in response.output:
    if item.type == "function_call":
        arguments = json.loads(item.arguments)
        print("The model proposed an action:")
        print(f"  tool:    {item.name}")
        print(f"  command: {arguments['command']}")
    elif item.type == "message":
        # A message holds one or more parts; keep only the text parts of this one.
        text = "".join(part.text for part in item.content if part.type == "output_text")
        print("The model replied with text:")
        print(f"  {text}")

print()
print("Nothing was run. The proposal is only data until this program acts on it.")
