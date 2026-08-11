import asyncio
import os
import edge_tts
from google import genai

# 1. Fetch API Key
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY is missing!")
    exit(1)

client = genai.Client(api_key=api_key)

# 2. Ask Gemini for clean spoken text ONLY
prompt = (
    "Write a catchy 30-second YouTube Short script about an interesting space fact. "
    "CRITICAL RULE: Return ONLY the exact spoken narration words. Do NOT include stage "
    "directions, brackets, scene descriptions, or labels like 'Voiceover:'."
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

script_text = response.text
print("--- GENERATED SCRIPT ---")
print(script_text)

# 3. Convert script text to audio file (.mp3)
VOICE = "en-US-ChristopherNeural"  # Clear, natural English voice
OUTPUT_FILE = "voiceover.mp3"


async def create_voiceover():
    print("--- GENERATING VOICEOVER AUDIO ---")
    communicate = edge_tts.Communicate(script_text, VOICE)
    await communicate.save(OUTPUT_FILE)
    print(f"Successfully saved voiceover to {OUTPUT_FILE}!")


# Run the audio generation
asyncio.run(create_voiceover())import os
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
