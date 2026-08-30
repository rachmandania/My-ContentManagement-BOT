import os
import json
import random
import sys
from moviepy import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    concatenate_audioclips
)
from moviepy.video.fx import CrossFadeIn

# --- 1. SETTINGS & DURATIONS ---
HORIZONTAL_DURATION = 600  # 10 minutes
VERTICAL_DURATION = 170     # 2 minutes 50 sec

# Ken Burns settings
ZOOM_MIN = 1.0    # starting zoom (no zoom)
ZOOM_MAX = 1.15   # max zoom (15% push-in)
NUM_IMAGES_HORIZ = 5   # images per horizontal video
NUM_IMAGES_VERT = 3    # images per vertical video
CROSSFADE_HORIZ = 2.0  # seconds of crossfade between images
CROSSFADE_VERT = 1.5

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

# Verify and collect image files
for label, directory in [("horizontal", img_horiz_dir), ("vertical", img_vert_dir)]:
    if not os.path.exists(directory):
        print(f"CRITICAL ERROR: Missing directory {directory}")
        sys.exit(1)
    files = [f for f in os.listdir(directory) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if not files:
        print(f"CRITICAL ERROR: No images found in {directory}")
        sys.exit(1)
    if label == "horizontal":
        horiz_files = files
    else:
        vert_files = files

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

selected_audio = os.path.join(audio_dir, random.choice(audio_files))
print(f"Loaded Audio Track: {os.path.basename(selected_audio)}")

# --- 3. HELPER: KEN BURNS EFFECT ON A SINGLE IMAGE ---
def make_ken_burns_clip(image_path, duration):
    """Create a clip with slow zoom-in (Ken Burns) centered on the image."""
    zoom_in = random.choice([True, False])
    zoom_fn = (lambda t: ZOOM_MIN + (ZOOM_MAX - ZOOM_MIN) * (t / duration)) if zoom_in \
              else (lambda t: ZOOM_MAX - (ZOOM_MAX - ZOOM_MIN) * (t / duration))

    return (
        ImageClip(image_path)
        .with_duration(duration)
        .resized(zoom_fn)
        .with_position("center")
    )

# --- 4. HELPER: BUILD A MULTI-IMAGE VIDEO WITH CROSSFADES ---
def build_video(image_dir, all_files, target_duration, num_images, crossfade_dur, label):
    """Select images, apply Ken Burns, and join with crossfade transitions."""
    count = min(num_images, len(all_files))
    chosen = random.sample(all_files, count)
    print(f"  [{label}] Using {count} images with Ken Burns + crossfade")

    # Segment duration: divide total time among images.
    # Crossfade overlap adds ~crossfade_dur to total, so we trim later.
    seg_dur = target_duration / count

    clips = []
    for i, fname in enumerate(chosen):
        path = os.path.join(image_dir, fname)
        print(f"    Image {i+1}/{count}: {fname}")
        clip = make_ken_burns_clip(path, seg_dur)

        if i > 0:
            clip = clip.with_effects([CrossFadeIn(crossfade_dur)])
            clip = clip.with_start(i * seg_dur - crossfade_dur)

        clips.append(clip)

    # Composite layers all clips at their scheduled start times
    video = CompositeVideoClip(clips)
    # Trim to exact target duration (crossfade overlap may overshoot slightly)
    video = video.with_duration(target_duration)
    return video

# --- 5. RENDER DUAL FORMAT VIDEOS ---
print("--- RENDERING DUAL FORMAT VIDEOS WITH KEN BURNS EFFECTS ---")
audio_clip = AudioFileClip(selected_audio)

def prepare_audio(a_clip, target_dur):
    if a_clip.duration < target_dur:
        loops = int(target_dur // a_clip.duration) + 1
        a_out = concatenate_audioclips([a_clip] * loops)
    else:
        a_out = a_clip
    return a_out.subclipped(0, target_dur)

# Horizontal Video (16:9)
print(f"Rendering horizontal_short.mp4 ({HORIZONTAL_DURATION}s)...")
horiz_video = build_video(
    img_horiz_dir, horiz_files, HORIZONTAL_DURATION,
    NUM_IMAGES_HORIZ, CROSSFADE_HORIZ, "horizontal"
)
horiz_audio = prepare_audio(audio_clip, HORIZONTAL_DURATION)
horiz_final = horiz_video.with_audio(horiz_audio)
horiz_final.write_videofile(
    "horizontal_short.mp4", fps=24, codec="libx264",
    audio_codec="libmp3lame", bitrate="8000k"
)

# Vertical Video (9:16)
print(f"Rendering vertical_short.mp4 ({VERTICAL_DURATION}s)...")
vert_video = build_video(
    img_vert_dir, vert_files, VERTICAL_DURATION,
    NUM_IMAGES_VERT, CROSSFADE_VERT, "vertical"
)
vert_audio = prepare_audio(audio_clip, VERTICAL_DURATION)
vert_final = vert_video.with_audio(vert_audio)
vert_final.write_videofile(
    "vertical_short.mp4", fps=24, codec="libx264",
    audio_codec="libmp3lame", bitrate="8000k"
)

# --- 6. METADATA SAVE (same format for youtube_upload.py) ---
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

print("SUCCESS! Ken Burns video rendering complete!")
