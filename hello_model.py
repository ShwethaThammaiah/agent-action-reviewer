"""Step 1: send one message to a model and print the reply.

This is the smallest possible program that talks to a model.
No agent, no tools, no reviewer yet.
"""

from dotenv import load_dotenv
from openai import OpenAI

# Read OPENAI_API_KEY from the .env file into this program's environment.
load_dotenv()

# Create the connection to OpenAI. It finds the key automatically.
client = OpenAI()

# Send one message and wait for the reply.
response = client.responses.create(
    model="gpt-5.5",
    input="In one sentence, what is an AI agent?",
)

# Print the text of the reply.
print(response.output_text)
