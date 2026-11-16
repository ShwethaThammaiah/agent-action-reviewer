"""The four tools the agent can propose, and how each one is carried out.

Two separate things live here:
  - TOOLS: descriptions the model reads, so it knows what it may ask for.
  - run_tool(): the code that carries out an action once it has been approved.

Three tools act inside the sandbox. The fourth, call_url, would leave the
sandbox, so this project never actually sends the request (see call_url below).
"""

import shlex

from sandbox import run_in_sandbox


def _tool(name: str, description: str, properties: dict) -> dict:
    """Build one tool description in the shape the OpenAI API expects."""
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": list(properties),
            "additionalProperties": False,
        },
        "strict": True,
    }


TOOLS = [
    _tool(
        "run_shell",
        "Run a shell command in the workspace folder and return its exit code and output.",
        {"command": {"type": "string", "description": "The shell command to run."}},
    ),
    _tool(
        "read_file",
        "Read a text file in the workspace folder and return its contents.",
        {"path": {"type": "string", "description": "Path of the file, relative to the workspace."}},
    ),
    _tool(
        "write_file",
        "Create or overwrite a text file in the workspace folder.",
        {
            "path": {"type": "string", "description": "Path of the file, relative to the workspace."},
            "content": {"type": "string", "description": "The full text to put in the file."},
        },
    ),
    _tool(
        "call_url",
        "Send an HTTP request to a URL and return the response.",
        {
            "url": {"type": "string", "description": "The full URL to call."},
            "method": {"type": "string", "enum": ["GET", "POST"], "description": "The HTTP method."},
            "body": {"type": "string", "description": "Data to send with a POST. Use an empty string for GET."},
        },
    ),
]


def describe_action(name: str, arguments: dict) -> str:
    """One readable line describing a proposed action, for printing and logging."""
    if name == "run_shell":
        return f"run_shell: {arguments['command']}"
    if name == "read_file":
        return f"read_file: {arguments['path']}"
    if name == "write_file":
        return f"write_file: {arguments['path']} ({len(arguments['content'])} characters)"
    if name == "call_url":
        return f"call_url: {arguments['method']} {arguments['url']} ({len(arguments['body'])} characters sent)"
    return f"{name}: {arguments}"


def run_tool(name: str, arguments: dict) -> str:
    """Carry out one action and return the result as text for the model."""
    if name == "run_shell":
        return run_in_sandbox(arguments["command"])

    if name == "read_file":
        path = shlex.quote(arguments["path"])
        return run_in_sandbox(f"cat -- {path}")

    if name == "write_file":
        # The file is written by a command running inside the sandbox, with the
        # content piped in. So a path like ../../.env cannot reach the laptop.
        path = shlex.quote(arguments["path"])
        return run_in_sandbox(
            f'mkdir -p -- "$(dirname -- {path})" && cat > {path} && echo "wrote {path}"',
            stdin_text=arguments["content"],
        )

    if name == "call_url":
        # A network request leaves the sandbox, so nothing can contain it.
        # This project records the request and never sends it. The reviewer
        # still sees and judges the proposal, which is what gets measured.
        return (
            "Request not sent: network access is disabled in this environment. "
            f"({arguments['method']} {arguments['url']})"
        )

    return f"Unknown tool: {name}"
