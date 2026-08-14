import os
import time
import random
import requests
import sys
import numpy as np
from PIL import Image
from moviepy import VideoClip, AudioFileClip, concatenate_audioclips

# --- 1. SETTINGS & DURATIONS ---
HORIZONTAL_DURATION = 30  # 30 seconds for testing
VERTICAL_DURATION = 15     # 15 seconds for testing

# --- 2. GENERATE FANTASY COZY CAFE IMAGE (STABLE DIFFUSION) ---
print("--- 1. GENERATING COZY FANTASY CAFE IMAGE ---")
IMAGE_FILE = "background.jpg"

image_prompt = (
    "A breathtaking digital painting of a cozy, calm, and warm fantasy cafe interior, "
    "warm glowing lamps, a steaming cup of coffee on a wooden table, large arched window "
    "showing an enchanted glowing forest with a waterfall and floating fireflies, "
    "lush magical plants, vibrant flowers, masterpiece, 8k resolution, cinematic lighting, "
    "cozy lofi fantasy aesthetic"
)
encoded_prompt = requests.utils.quote(image_prompt)

# Free serverless endpoint for Stable Diffusion / Flux
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1920&height=1080&nologo=true"

try:
    img_data = requests.get(image_url, timeout=30)
    if img_data.status_code == 200:
        with open(IMAGE_FILE, "wb") as f:
            f.write(img_data.content)
        print("SUCCESS: Fantasy Cafe image generated and saved!")
    else:
        raise Exception("Failed to fetch image.")
except Exception as e:
    print(f"CRITICAL ERROR generating image: {e}")
    sys.exit(1)

# --- 3. DOWNLOAD CALM LOFI / JAZZ AUDIO ---
print("--- 2. FETCHING RELAXING MUSIC ---")
AUDIO_FILE = "cafe_music.mp3"
audio_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
audio_downloaded = False

CALM_MUSIC_URLS = [
    "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://archive.org/download/cd_smooth-jazz_various-artists/disc1/02.%20Various%20Artists%20-%20Midnight%20Motion.mp3",
    "https://archive.org/download/GymnopedieNo.1/Gymnopedie_No_1.mp3"
]

for attempt in range(3):
    try:
        chosen_track = random.choice(CALM_MUSIC_URLS)
        print("Attempting to download calm background track...")
        audio_data = requests.get(chosen_track, headers=audio_headers, timeout=15, allow_redirects=True)
        if audio_data.status_code == 200 and len(audio_data.content) > 50000:
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio_data.content)
            print("SUCCESS: Calm track downloaded!")
            audio_downloaded = True
            break
    except Exception as e:
        print(f"Network error: {e}. Retrying...")
        time.sleep(2)

if not audio_downloaded:
    print("Using guaranteed emergency Lofi track...")
    backup_url = "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3"
    audio_data = requests.get(backup_url, headers=audio_headers, allow_redirects=True)
    with open(AUDIO_FILE, "wb") as f:
        f.write(audio_data.content)

# --- 4. RENDER MOVING VIDEOS (DYNAMIC PAN & ZOOM) ---
print("--- 3. RENDERING MOVING VIDEOS WITH CAMERA MOTION ---")
audio_clip = AudioFileClip(AUDIO_FILE)
base_pil = Image.open(IMAGE_FILE)
orig_w, orig_h = base_pil.size

def prepare_audio(a_clip, target_dur):
    if a_clip.duration < target_dur:
        loops = int(target_dur // a_clip.duration) + 1
        a_out = concatenate_audioclips([a_clip] * loops)
    else:
        a_out = a_clip
    return a_out.subclipped(0, target_dur)

# --- 16:9 HORIZONTAL PAN & ZOOM ---
print(f"Rendering horizontal_short.mp4 ({HORIZONTAL_DURATION}s)...")
def make_horiz_frame(t):
    p = t / HORIZONTAL_DURATION  # Progress ratio 0.0 -> 1.0
    zoom = 1.0 + 0.15 * p        # Smooth zoom from 100% to 115%
    
    crop_w = orig_w / zoom
    crop_h = orig_h / zoom
    
    # Slow pan down and right
    x1 = (orig_w - crop_w) * p * 0.5
    y1 = (orig_h - crop_h) * p * 0.5
    
    cropped = base_pil.crop((x1, y1, x1 + crop_w, y1 + crop_h))
    resized = cropped.resize((orig_w, orig_h), Image.Resampling.LANCZOS)
    return np.array(resized)

horiz_video = VideoClip(make_horiz_frame, duration=HORIZONTAL_DURATION)
horiz_audio = prepare_audio(audio_clip, HORIZONTAL_DURATION)
horiz_final = horiz_video.with_audio(horiz_audio)
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac")

# --- 9:16 VERTICAL CROPPED PAN & ZOOM ---
print(f"Rendering vertical_short.mp4 ({VERTICAL_DURATION}s)...")
target_v_w = int(orig_h * 9 / 16)
target_v_h = orig_h

# Ensure even dimensions for video encoder
if target_v_w % 2 != 0: target_v_w -= 1
if target_v_h % 2 != 0: target_v_h -= 1

def make_vert_frame(t):
    p = t / VERTICAL_DURATION
    zoom = 1.0 + 0.12 * p
    
    base_x1 = (orig_w - target_v_w) / 2
    crop_w = target_v_w / zoom
    crop_h = target_v_h / zoom
    
    x1 = base_x1 + (target_v_w - crop_w) * p * 0.5
    y1 = (target_v_h - crop_h) * p * 0.5
    
    cropped = base_pil.crop((x1, y1, x1 + crop_w, y1 + crop_h))
    resized = cropped.resize((target_v_w, target_v_h), Image.Resampling.LANCZOS)
    return np.array(resized)

vert_video = VideoClip(make_vert_frame, duration=VERTICAL_DURATION)
vert_audio = prepare_audio(audio_clip, VERTICAL_DURATION)
vert_final = vert_video.with_audio(vert_audio)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac")

print("SUCCESS! Fantasy Cafe videos with dynamic motion generated successfully!")
