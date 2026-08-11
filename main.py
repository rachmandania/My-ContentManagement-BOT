import asyncio
import os
import requests
import edge_tts
from google import genai
from moviepy import AudioFileClip, ImageClip

# --- 1. SETTINGS & KEYS ---
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY is missing!")
    exit(1)

# --- 2. GENERATE SCRIPT (GEMINI) ---
print("--- 1. GENERATING SCRIPT ---")
client = genai.Client(api_key=api_key)
prompt = (
    "Write a catchy 30-second YouTube Short script about an interesting space fact. "
    "CRITICAL RULE: Return ONLY the exact spoken narration words. Do NOT include stage "
    "directions, brackets, scene descriptions, or labels like 'Voiceover:'."
)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
)
script_text = response.text
print(script_text)

# --- 3. GENERATE VOICEOVER (EDGE-TTS) ---
print("--- 2. GENERATING VOICEOVER ---")
VOICE = "en-US-ChristopherNeural"
AUDIO_FILE = "voiceover.mp3"

async def create_voiceover():
    communicate = edge_tts.Communicate(script_text, VOICE)
    await communicate.save(AUDIO_FILE)

asyncio.run(create_voiceover())
print(f"Saved {AUDIO_FILE}!")

# --- 4. DOWNLOAD BACKGROUND IMAGE ---
print("--- 3. DOWNLOADING BACKGROUND VISUAL ---")
# Fetches a free, vertical space image pre-cropped to 1080x1920
IMAGE_URL = "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1080&h=1920&fit=crop"
IMAGE_FILE = "background.jpg"

image_request = requests.get(IMAGE_URL)
with open(IMAGE_FILE, "wb") as file:
    file.write(image_request.content)
print(f"Saved {IMAGE_FILE}!")

# --- 5. RENDER FINAL VIDEO (MOVIEPY) ---
print("--- 4. RENDERING FINAL VIDEO ---")
# Find out exactly how long the voiceover audio is
audio_clip = AudioFileClip(AUDIO_FILE)
duration = audio_clip.duration

# Match the image duration to the audio duration and combine them using the new MoviePy 2.0 format
video_clip = ImageClip(IMAGE_FILE, duration=duration)
video_clip = video_clip.with_audio(audio_clip)

# Export the final MP4 file
FINAL_OUTPUT = "final_short.mp4"
video_clip.write_videofile(
    FINAL_OUTPUT, 
    fps=30, 
    codec="libx264", 
    audio_codec="aac"
)

print(f"SUCCESS! Your video is ready: {FINAL_OUTPUT}")
