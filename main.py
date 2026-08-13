import os
import time
import random
import requests
import sys
from google import genai
from moviepy import ImageClip, AudioFileClip, concatenate_audioclips

# --- 1. SETTINGS & KEYS ---
gemini_key = os.environ.get("GEMINI_API_KEY")
pixabay_key = os.environ.get("PIXABAY_API_KEY")

if not gemini_key or not pixabay_key:
    print("Error: Missing GEMINI_API_KEY or PIXABAY_API_KEY environment variables!")
    sys.exit(1)

# You mentioned 10 minutes for horizontal, 15 seconds for vertical
HORIZONTAL_DURATION = 30   # 30 seconds in seconds
VERTICAL_DURATION = 15     # 15 seconds

# --- 2. GENERATE COZY CAFE IMAGE (GOOGLE IMAGEN 3) ---
print("--- 1. GENERATING COZY CAFE IMAGE VIA GEMINI/IMAGEN ---")
IMAGE_FILE = "background.jpg"

try:
    client = genai.Client(api_key=gemini_key)
    
    # We randomize the prompt slightly so every video is unique!
    atmospheres = ["raining outside", "warm sunset glowing", "snowing gently outside", "starry night sky"]
    chosen_atmosphere = random.choice(atmospheres)
    
    prompt = (
        f"A cozy, warm, and inviting cafe interior, soft warm ambient lighting, "
        f"a steaming cup of coffee on a wooden table, large window showing {chosen_atmosphere}, "
        f"lofi aesthetic, anime style or digital painting masterpiece, high quality, highly detailed."
    )
    
    print(f"Prompting AI: {prompt}")
    
    result = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt=prompt,
        config=dict(
            number_of_images=1,
            aspect_ratio="16:9",
            output_mime_type="image/jpeg",
        )
    )
    
    # Save the generated image
    image_bytes = result.generated_images[0].image.image_bytes
    with open(IMAGE_FILE, "wb") as f:
        f.write(image_bytes)
    print("SUCCESS: AI Image generated and saved!")
    
except Exception as e:
    print(f"CRITICAL ERROR generating image: {e}")
    sys.exit(1)

# --- 3. DOWNLOAD LOFI / JAZZ MUSIC (PIXABAY) ---
print("--- 2. FETCHING RELAXING LOFI / JAZZ AUDIO ---")
AUDIO_FILE = "cafe_music.mp3"
audio_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
audio_downloaded = False

print("Searching Pixabay Audio API...")
try:
    MUSIC_QUERIES = ["lofi", "jazz cafe", "chillhop", "relaxing jazz", "lofi chill"]
    chosen_music_query = random.choice(MUSIC_QUERIES)
    print(f"Searching for vibe: '{chosen_music_query}'")
    
    pixabay_audio_url = f"https://pixabay.com/api/audio/?key={pixabay_key}&q={chosen_music_query}&per_page=15"
    audio_response = requests.get(pixabay_audio_url).json()
    audio_hits = audio_response.get("hits", [])
    
    if audio_hits:
        chosen_track = random.choice(audio_hits)
        audio_download_url = chosen_track["download"]
        audio_data = requests.get(audio_download_url, headers=audio_headers, timeout=15)
        
        if audio_data.status_code == 200 and len(audio_data.content) > 10000:
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio_data.content)
            print("Pixabay Lofi/Jazz track downloaded successfully!")
            audio_downloaded = True
except Exception as e:
    print(f"Audio Fetch Failed: {e}")

# Backup if Pixabay fails
if not audio_downloaded:
    print("Switching to reliable backup Lofi/Chill stream...")
    # A reliable royalty-free chillhop loop
    backup_url = "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3" 
    audio_data = requests.get(backup_url, headers=audio_headers, allow_redirects=True)
    with open(AUDIO_FILE, "wb") as f:
        f.write(audio_data.content)
    print("Emergency backup audio secured.")

# --- 4. RENDER DUAL FORMAT VIDEOS ---
print("--- 3. RENDERING HORIZONTAL (10 MIN) & CROPPED VERTICAL (15 SEC) ---")
# Because we are using a static image, rendering is much faster and cleaner!
base_img_clip = ImageClip(IMAGE_FILE)
audio_clip = AudioFileClip(AUDIO_FILE)

def build_media(img_clip, a_clip, target_dur):
    # Set the static image to last exactly the target duration
    v_out = img_clip.with_duration(target_dur)
    
    # Loop the audio to match the 10 minute or 15 sec duration
    if a_clip.duration < target_dur:
        a_loops = int(target_dur // a_clip.duration) + 1
        a_out = concatenate_audioclips([a_clip] * a_loops)
    else:
        a_out = a_clip
        
    a_out = a_out.subclipped(0, target_dur)
    return v_out.with_audio(a_out)

print(f"Rendering horizontal_short.mp4 ({HORIZONTAL_DURATION} seconds)...")
horiz_final = build_media(base_img_clip, audio_clip, HORIZONTAL_DURATION)
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print(f"Rendering vertical_short.mp4 by cropping horizontal source ({VERTICAL_DURATION} seconds)...")
w, h = base_img_clip.size
target_width = int(h * 9 / 16)
target_height = int(h)

# ENSURE EVEN DIMENSIONS SO MP4 ENCODER DOESN'T CRASH
if target_width % 2 != 0:
    target_width -= 1
if target_height % 2 != 0:
    target_height -= 1

cropped_base = base_img_clip.cropped(width=target_width, height=target_height, x_center=w/2, y_center=h/2)
vert_final = build_media(cropped_base, audio_clip, VERTICAL_DURATION)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("SUCCESS! Cozy Cafe videos generated successfully!")
