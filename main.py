import asyncio
import os
import requests
import edge_tts
from google import genai
from moviepy import AudioFileClip, VideoFileClip

# --- 1. SETTINGS & KEYS ---
api_key = os.environ.get("GEMINI_API_KEY")
pexels_key = os.environ.get("PEXELS_API_KEY")

if not api_key or not pexels_key:
    print("Error: Missing API keys!")
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

# --- 4. DOWNLOAD MOVING STOCK VIDEO (PEXELS) ---
print("--- 3. DOWNLOADING MOVING VIDEO BACKGROUND ---")
headers = {"Authorization": pexels_key}
# Search for vertical space video loops on Pexels
pexel_url = "https://api.pexels.com/videos/search?query=space+nebula+vertical&per_page=1"
search_response = requests.get(pexel_url, headers=headers).json()

# Grab the direct download link for the HD vertical video file
video_files = search_response["videos"][0]["video_files"]
# Filter for a good mobile resolution download link
vertical_video_url = next((v["link"] for v in video_files if v["width"] <= 1080 and v["height"] >= 1280), video_files[0]["link"])

VIDEO_FILE = "background.mp4"
video_data = requests.get(vertical_video_url)
with open(VIDEO_FILE, "wb") as f:
    f.write(video_data.content)
print(f"Saved moving video {VIDEO_FILE}!")

# --- 5. RENDER FINAL VIDEO (MOVIEPY) ---
print("--- 4. RENDERING FINAL VIDEO ---")
audio_clip = AudioFileClip(AUDIO_FILE)
duration = audio_clip.duration

# Load the background video clip
background_clip = VideoFileClip(VIDEO_FILE)

# If the stock video is shorter than the audio, loop it. If longer, trim it.
if background_clip.duration < duration:
    from moviepy import concatenate_videoclips
    loops_needed = int(duration // background_clip.duration) + 1
    background_clip = concatenate_videoclips([background_clip] * loops_needed)

video_clip = background_clip.subclipped(0, duration)
video_clip = video_clip.with_audio(audio_clip)

# Export the final MP4 file
FINAL_OUTPUT = "final_short.mp4"
video_clip.write_videofile(
    FINAL_OUTPUT, 
    fps=24, 
    codec="libx264", 
    audio_codec="aac"
)

print(f"SUCCESS! Your dynamic video is ready: {FINAL_OUTPUT}")
