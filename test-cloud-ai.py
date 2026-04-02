from dotenv import load_dotenv
import os
import anthropic

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY") # You would need Credits to use the API, get them from https://console.anthropic.com/ ':'(
)

response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Hola"}
    ]
)

print(response.content)