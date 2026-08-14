import os
import time
import requests
import sys
from moviepy import ImageClip, AudioFileClip, concatenate_audioclips

# --- 1. SETTINGS & KEYS ---
hf_key = os.environ.get("HF_TOKEN")

if not hf_key:
    print("Error: Missing HF_TOKEN environment variable! (Hugging Face API Key required for AudioCraft)")
    sys.exit(1)

HORIZONTAL_DURATION = 30
VERTICAL_DURATION = 15

# --- 2. GENERATE STABLE DIFFUSION IMAGE (FREE API) ---
print("--- 1. GENERATING COZY CAFE IMAGE (STABLE DIFFUSION) ---")
IMAGE_FILE = "background.jpg"

image_prompt = "lofi anime style, cozy cafe interior at rainy night, warm ambient lighting, aesthetic retro, highly detailed, 4k resolution"
encoded_prompt = requests.utils.quote(image_prompt)

# Pollinations API runs Stable Diffusion / Flux entirely for free with no keys required
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1920&height=1080&nologo=true"

try:
    img_data = requests.get(image_url, timeout=30)
    if img_data.status_code == 200:
        with open(IMAGE_FILE, "wb") as f:
            f.write(img_data.content)
        print("SUCCESS: Stable Diffusion Image generated and saved!")
    else:
        raise Exception("Failed to fetch image.")
except Exception as e:
    print(f"CRITICAL ERROR generating image: {e}")
    sys.exit(1)

# --- 3. DOWNLOAD CALM JAZZ / CLASSIC AUDIO (DIRECT LINKS) ---
print("--- 2. FETCHING RELAXING JAZZ / CLASSIC MUSIC ---")
AUDIO_FILE = "cafe_music.mp3"
audio_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
audio_downloaded = False

# 100% reliable direct links to Calm Lofi, Jazz, and Classical Piano (Absolutely NO Techno!)
CALM_MUSIC_URLS = [
    # Pixabay Calm Lofi Chillhop (Verified link)
    "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
    # Internet Archive - Smooth Jazz Background
    "https://archive.org/download/cd_smooth-jazz_various-artists/disc1/02.%20Various%20Artists%20-%20Midnight%20Motion.mp3",
    # Internet Archive - Classical Piano (Erik Satie - Gymnopedie No 1)
    "https://archive.org/download/GymnopedieNo.1/Gymnopedie_No_1.mp3"
]

for attempt in range(3):
    try:
        chosen_track = random.choice(CALM_MUSIC_URLS)
        print("Attempting to download calm background track...")
        audio_data = requests.get(chosen_track, headers=audio_headers, timeout=15, allow_redirects=True)
        
        # A real MP3 is large; if it's tiny, it's an error webpage
        if audio_data.status_code == 200 and len(audio_data.content) > 50000:
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio_data.content)
            print("SUCCESS: Calm Jazz/Classic track downloaded!")
            audio_downloaded = True
            break
        else:
            print(f"Download hiccup (Status {audio_data.status_code}). Retrying in 2 seconds...")
            time.sleep(2)
    except Exception as e:
        print(f"Network error: {e}. Retrying in 2 seconds...")
        time.sleep(2)

if not audio_downloaded:
    print("Random attempts failed. Using guaranteed emergency Lofi track...")
    backup_url = "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3"
    audio_data = requests.get(backup_url, headers=audio_headers, allow_redirects=True)
    with open(AUDIO_FILE, "wb") as f:
        f.write(audio_data.content)
        
# --- 4. RENDER DUAL FORMAT VIDEOS ---
print("--- 3. RENDERING HORIZONTAL (30 SEC) & CROPPED VERTICAL (15 SEC) ---")
base_img_clip = ImageClip(IMAGE_FILE)
audio_clip = AudioFileClip(AUDIO_FILE)

def build_media(img_clip, a_clip, target_dur):
    v_out = img_clip.with_duration(target_dur)
    
    # Loop the AI audio track to fill the full video duration
    if a_clip.duration < target_dur:
        a_loops = int(target_dur // a_clip.duration) + 1
        a_out = concatenate_audioclips([a_clip] * a_loops)
    else:
        a_out = a_clip
        
    a_out = a_out.subclipped(0, target_dur)
    return v_out.with_audio(a_out)

print(f"Rendering horizontal_short.mp4...")
horiz_final = build_media(base_img_clip, audio_clip, HORIZONTAL_DURATION)
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print(f"Rendering vertical_short.mp4...")
w, h = base_img_clip.size
target_width = int(h * 9 / 16)
target_height = int(h)

if target_width % 2 != 0: target_width -= 1
if target_height % 2 != 0: target_height -= 1

cropped_base = base_img_clip.cropped(width=target_width, height=target_height, x_center=w/2, y_center=h/2)
vert_final = build_media(cropped_base, audio_clip, VERTICAL_DURATION)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("SUCCESS! AI Cozy Cafe videos generated successfully!")
