import json
from google.genai import Client, types

client = Client(vertexai=True, project='gde-access', location='us-central1')

def my_tool() -> dict:
    return {"status": "ok"}

try:
    res = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='call my tool',
        config=types.GenerateContentConfig(
            tools=[my_tool]
        )
    )
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
