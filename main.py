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
VERTICAL_DURATION = 15    # 15 seconds for testing

# --- 2. GENERATE MAGICAL COZY CAFE IMAGE (FLUX MODEL) ---
print("--- 1. GENERATING HIGH-DEF MAGICAL CAFE IMAGE ---")
IMAGE_FILE = "background.jpg"

chosen_prompt = (
    "Super quality Hyper reallistic Cozy Stunning cafe, magical interior, "
    "warm glowing lanterns, a steaming cup of coffee on a wooden table. "
    "Large open windows revealing a spectacular fantasy landscape with glowing bioluminescent plants, "
    "vibrant purple and pink sunset, crystal clear stream, glowing fireflies, lush colorful flowers. "
    "Masterpiece, ethereal cinematic lighting, 8k resolution, ultra-sharp."
)

encoded_prompt = requests.utils.quote(chosen_prompt)
random_seed = random.randint(1, 999999)

image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1920&height=1080&nologo=true&seed={random_seed}&model=flux"
print(f"Prompt: '{chosen_prompt}' (Seed: {random_seed})")

image_downloaded = False

# Give the AI 3 attempts to generate the image in case the server is busy
for attempt in range(3):
    print(f"Attempt {attempt + 1}: Contacting AI server...")
    try:
        img_data = requests.get(image_url, timeout=45)
        if img_data.status_code == 200 and len(img_data.content) > 50000:
            with open(IMAGE_FILE, "wb") as f:
                f.write(img_data.content)
            print("SUCCESS: High-Def Magical Cafe image generated and saved!")
            image_downloaded = True
            break
        else:
            print("Server returned empty data. Retrying in 5 seconds...")
            time.sleep(5)
    except Exception as e:
        print(f"Connection timeout: {e}. Retrying in 5 seconds...")
        time.sleep(5)

if not image_downloaded:
    print("CRITICAL ERROR: AI Image generator failed after 3 attempts.")
    sys.exit(1)

# --- 3. LOAD RANDOM LOCAL AUDIO ---
print("--- 2. LOADING LOCAL AUDIO FROM ASSETS FOLDER ---")
assets_dir = "assets"

if not os.path.exists(assets_dir):
    print(f"CRITICAL ERROR: '{assets_dir}' folder not found in repository.")
    sys.exit(1)

# Collect all mp3 files located in your local folder
audio_files = [f for f in os.listdir(assets_dir) if f.endswith('.mp3')]

if not audio_files:
    print(f"CRITICAL ERROR: No .mp3 files found inside the '{assets_dir}' folder.")
    sys.exit(1)

# Pick a completely random track instantly, with no network delay!
random_audio = random.choice(audio_files)
AUDIO_FILE = os.path.join(assets_dir, random_audio)
print(f"SUCCESS: Selected local audio track -> {random_audio}")

# --- 4. RENDER MOVING VIDEOS (HIGH BITRATE PAN & ZOOM) ---
print("--- 3. RENDERING SHARP MOVING VIDEOS ---")
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

# Horizontal Rendering
print(f"Rendering horizontal_short.mp4 ({HORIZONTAL_DURATION}s)...")
def make_horiz_frame(t):
    p = t / HORIZONTAL_DURATION  
    zoom = 1.0 + 0.10 * p
    crop_w = orig_w / zoom
    crop_h = orig_h / zoom
    x1 = (orig_w - crop_w) * p * 0.5
    y1 = (orig_h - crop_h) * p * 0.5
    cropped = base_pil.crop((x1, y1, x1 + crop_w, y1 + crop_h))
    resized = cropped.resize((1920, 1080), Image.Resampling.LANCZOS)
    return np.array(resized)

horiz_video = VideoClip(make_horiz_frame, duration=HORIZONTAL_DURATION)
horiz_audio = prepare_audio(audio_clip, HORIZONTAL_DURATION)
horiz_final = horiz_video.with_audio(horiz_audio)
# Enforcing the 8000k bitrate so the final export stays perfectly sharp!
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac", bitrate="8000k")

# Vertical Rendering
print(f"Rendering vertical_short.mp4 ({VERTICAL_DURATION}s)...")
target_v_w = int(orig_h * 9 / 16)
target_v_h = orig_h

if target_v_w % 2 != 0: target_v_w -= 1
if target_v_h % 2 != 0: target_v_h -= 1

def make_vert_frame(t):
    p = t / VERTICAL_DURATION
    zoom = 1.0 + 0.10 * p
    base_x1 = (orig_w - target_v_w) / 2
    crop_w = target_v_w / zoom
    crop_h = target_v_h / zoom
    x1 = base_x1 + (target_v_w - crop_w) * p * 0.5
    y1 = (target_v_h - crop_h) * p * 0.5
    cropped = base_pil.crop((x1, y1, x1 + crop_w, y1 + crop_h))
    resized = cropped.resize((1080, 1920), Image.Resampling.LANCZOS)
    return np.array(resized)

vert_video = VideoClip(make_vert_frame, duration=VERTICAL_DURATION)
vert_audio = prepare_audio(audio_clip, VERTICAL_DURATION)
vert_final = vert_video.with_audio(vert_audio)
# Enforcing the 8000k bitrate so the final export stays perfectly sharp!
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac", bitrate="8000k")

print("SUCCESS! High-Def, magical Cozy Cafe videos generated using local assets!")
