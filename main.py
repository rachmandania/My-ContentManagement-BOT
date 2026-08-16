import os
import json
import random
import sys
from moviepy import ImageClip, AudioFileClip, concatenate_audioclips

# --- 1. SETTINGS & DURATIONS ---
HORIZONTAL_DURATION = 600  # 10 minutes (set to 30 for testing)
VERTICAL_DURATION = 15     # 15 seconds

ASSETS_DIR = "assets"

if not os.path.exists(ASSETS_DIR):
    print(f"CRITICAL ERROR: '{ASSETS_DIR}' folder not found.")
    sys.exit(1)

# Scan for game folders inside assets/
game_folders = [
    d for d in os.listdir(ASSETS_DIR) 
    if os.path.isdir(os.path.join(ASSETS_DIR, d)) and d not in ["images", "audio"]
]

if not game_folders:
    print("CRITICAL ERROR: No game subfolders found in assets/.")
    sys.exit(1)

# --- 2. RANDOM GAME SELECTION & ASSET PAIRING ---
chosen_game = random.choice(game_folders)
game_path = os.path.join(ASSETS_DIR, chosen_game)
print(f"--- SELECTED GAME FACTORY: {chosen_game} ---")

img_horiz_dir = os.path.join(game_path, "images_horizontal")
img_vert_dir = os.path.join(game_path, "images_vertical")
audio_dir = os.path.join(game_path, "audio")
credits_file = os.path.join(game_path, "credits.txt")

# Verify horizontal images
if not os.path.exists(img_horiz_dir):
    print(f"CRITICAL ERROR: Missing directory {img_horiz_dir}")
    sys.exit(1)

horiz_files = [f for f in os.listdir(img_horiz_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
if not horiz_files:
    print(f"CRITICAL ERROR: No images found in {img_horiz_dir}")
    sys.exit(1)

# Verify vertical images
if not os.path.exists(img_vert_dir):
    print(f"CRITICAL ERROR: Missing directory {img_vert_dir}")
    sys.exit(1)

vert_files = [f for f in os.listdir(img_vert_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
if not vert_files:
    print(f"CRITICAL ERROR: No images found in {img_vert_dir}")
    sys.exit(1)

# Verify audio
if not os.path.exists(audio_dir):
    print(f"CRITICAL ERROR: Missing directory {audio_dir}")
    sys.exit(1)

audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav', '.ogg'))]
if not audio_files:
    print(f"CRITICAL ERROR: No audio files found in {audio_dir}")
    sys.exit(1)

# Load Credits text
credits_text = ""
if os.path.exists(credits_file):
    with open(credits_file, "r", encoding="utf-8") as f:
        credits_text = f.read().strip()

# Randomly select image and audio assets
selected_horiz_img = os.path.join(img_horiz_dir, random.choice(horiz_files))
selected_vert_img = os.path.join(img_vert_dir, random.choice(vert_files))
selected_audio = os.path.join(audio_dir, random.choice(audio_files))

print(f"Loaded Horizontal Image: {os.path.basename(selected_horiz_img)}")
print(f"Loaded Vertical Image:   {os.path.basename(selected_vert_img)}")
print(f"Loaded Audio Track:      {os.path.basename(selected_audio)}")

# --- 3. RENDER DUAL FORMAT VIDEOS (DIRECT NO-CROP) ---
print("--- RENDERING DUAL FORMAT VIDEOS ---")
horiz_clip_base = ImageClip(selected_horiz_img)
vert_clip_base = ImageClip(selected_vert_img)
audio_clip = AudioFileClip(selected_audio)

def prepare_audio(a_clip, target_dur):
    if a_clip.duration < target_dur:
        loops = int(target_dur // a_clip.duration) + 1
        a_out = concatenate_audioclips([a_clip] * loops)
    else:
        a_out = a_clip
    return a_out.subclipped(0, target_dur)

# Render Horizontal Video (16:9)
print(f"Rendering horizontal_short.mp4 ({HORIZONTAL_DURATION}s)...")
horiz_audio = prepare_audio(audio_clip, HORIZONTAL_DURATION)
horiz_final = horiz_clip_base.with_duration(HORIZONTAL_DURATION).with_audio(horiz_audio)
horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac", bitrate="8000k")

# Render Vertical Video (9:16 - Native Asset)
print(f"Rendering vertical_short.mp4 ({VERTICAL_DURATION}s)...")
vert_audio = prepare_audio(audio_clip, VERTICAL_DURATION)
vert_final = vert_clip_base.with_duration(VERTICAL_DURATION).with_audio(vert_audio)
vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac", bitrate="8000k")

# --- 4. TOP 3 GAME TAGS MAPPING & METADATA SAVE ---
GAME_TAG_MAP = {
    "Genshin Impact": ["GenshinImpact", "Genshin", "HoYoverse"],
    "Arknights Endfield": ["ArknightsEndfield", "Endfield", "Arknights"],
    "Neverness to Everness": ["NevernessToEverness", "NTE", "HottaStudio"]
}

top_3_tags = GAME_TAG_MAP.get(chosen_game, [chosen_game.replace(" ", ""), "FanContent", "Lofi"])

metadata = {
    "game_name": chosen_game,
    "top_3_tags": top_3_tags,
    "credits": credits_text
}

with open("video_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print("SUCCESS! Dedicated orientation rendering complete!")