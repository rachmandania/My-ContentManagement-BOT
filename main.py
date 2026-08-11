import os
from google import genai

# Fetch the API key safely from environment variables
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY is missing!")
    exit(1)

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

# Generate a YouTube Short script
prompt = "Write a catchy 30-second YouTube Short script about an interesting space fact. Include a hook at the beginning."

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

print("--- GENERATED SCRIPT ---")
print(response.text)
