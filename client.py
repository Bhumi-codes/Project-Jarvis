import os
from dotenv import load_dotenv
from openai import OpenAI 
load_dotenv()

# Use OpenRouter instead of OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",  # OpenRouter routes this to GPT-4o-mini
    messages=[
        {"role": "system", "content": "You are a virtual assistant named jarvis, skilled in general tasks like Alexa and Google"},
        {"role": "assistant", "content": "Write a short story on life hinderances."},
        {"role": "user", "content": "What is coding?"},
    ],
)

print(response.choices[0].message.content)
