import os
import time
import random
import requests
import sys
from moviepy import ImageClip, AudioFileClip, concatenate_audioclips

# --- 1. SETTINGS & DURATIONS ---
HORIZONTAL_DURATION = 30  
VERTICAL_DURATION = 15    

# --- 2. GENERATE MAGICAL COZY CAFE IMAGE ---
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
print(f"Prompt: '{chosen_prompt}' (Seed: {random_seed})")

image_downloaded = False

# Give the AI up to 5 attempts with a smart fallback system
for attempt in range(5):
    print(f"Attempt {attempt + 1}: Contacting AI server...")
    
    # Attempts 1-3 use the heavy FLUX model. Attempts 4-5 fallback to standard high-speed model.
    current_model = "&model=flux" if attempt < 3 else ""
    if attempt == 3:
        print("FLUX model servers are busy. Switching to standard high-speed AI model...")
        
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1920&height=1080&nologo=true&seed={random_seed}{current_model}"
    
    try:
        # Increased timeout to 60 seconds to give the AI plenty of time to paint
        img_data = requests.get(image_url, timeout=60)
        
        # Lowered size restriction to 10KB (10000) to account for extreme WebP compression
        if img_data.status_code == 200 and len(img_data.content) > 10000:
            with open(IMAGE_FILE, "wb") as f:
                f.write(img_data.content)
            print("SUCCESS: High-Def Magical Cafe image generated and saved!")
            image_downloaded = True
            break
        else:
            print(f"Server returned status {img_data.status_code} with size {len(img_data.content)} bytes. Retrying in 5 seconds...")
            time.sleep(5)
    except Exception as e:
        print(f"Connection timeout/error: {e}. Retrying in 5 seconds...")
        time.sleep(5)

if not image_downloaded:
    print("CRITICAL ERROR: AI Image generator servers are completely down after 5 attempts.")
    sys.exit(1)

# --- 3. LOAD RANDOM LOCAL AUDIO ---
print("--- 2. LOADING LOCAL AUDIO FROM ASSETS FOLDER ---")
assets_dir = "assets"

if not os.path.exists(assets_dir):
    print(f"CRITICAL ERROR: '{assets_dir}' folder not found in repository.")
    sys.exit(1)

audio_files = [f for f in os.listdir(assets_dir) if f.endswith('.mp3')]

if not audio_files:
    print(f"CRITICAL ERROR: No .mp3 files found inside the '{assets_dir}' folder.")
    sys.exit(1)

random_audio = random.choice(audio_files)
AUDIO_FILE = os.path.join(assets_dir, random_audio)
print(f"SUCCESS: Selected local audio track -> {random_audio}")

# --- 4. RENDER STATIC VIDEOS (MAXIMUM SHARPNESS) ---
print("--- 3. RENDERING SHARP STATIC VIDEOS ---")
base_clip = ImageClip(IMAGE_FILE)
audio_clip = AudioFileClip(AUDIO_FILE)

def prepare_audio(a_clip, target_dur):
    if a_clip.duration < target_dur:
        loops = int(target_dur // a_clip.duration) + 1
        a_out = concatenate_audioclips([a_clip] * loops)
    else:
        a_out = a_clip
    return a_out.subclipped(0, target_dur)

# Horizontal Rendering
print(f"Rendering horizontal_short.mp4 ({HORIZONTAL_DURATION}s)...")
horiz_audio = prepare_audio(audio_clip, HORIZONTAL_DURATION)
horiz_final = base_clip.with_duration(HORIZONTAL_DURATION).with_audio(horiz_audio)
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac", bitrate="8000k")

# Vertical Rendering
print(f"Rendering vertical_short.mp4 ({VERTICAL_DURATION}s)...")
w, h = base_clip.size
target_v_w = int(h * 9 / 16)
target_v_h = h

if target_v_w % 2 != 0: target_v_w -= 1
if target_v_h % 2 != 0: target_v_h -= 1

vert_clip = base_clip.cropped(width=target_v_w, height=target_v_h, x_center=w/2, y_center=h/2)
vert_audio = prepare_audio(audio_clip, VERTICAL_DURATION)
vert_final = vert_clip.with_duration(VERTICAL_DURATION).with_audio(vert_audio)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac", bitrate="8000k")

print("SUCCESS! Razor-sharp static videos generated using local assets!")
