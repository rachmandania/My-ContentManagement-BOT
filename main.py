import os
import time
import random
import requests
import traceback
import sys
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL")

def notify_discord(message):
    if discord_webhook:
        requests.post(discord_webhook, json={"content": message})

try:
    notify_discord("⏳ **Workflow Started:** The automated nature video factory is now running!")

    # --- 1. SETTINGS & KEYS ---
    pixabay_key = os.environ.get("PIXABAY_API_KEY")
    if not pixabay_key:
        raise ValueError("Missing PIXABAY_API_KEY environment variable!")

    HORIZONTAL_DURATION = 30
    VERTICAL_DURATION = 15

    # --- 2. FETCH RANDOM NATURE VIDEO (PIXABAY API) ---
    # Smart mapping: Each video theme is now permanently linked to a matching NATURE sound!
    THEME_MAP = {
        "forest stream": "https://archive.org/download/NatureSounds_201709/02%20Stream%20Water.mp3",
        "mountain river": "https://archive.org/download/NatureSounds_201709/02%20Stream%20Water.mp3",
        "waterfall mist": "https://archive.org/download/NatureSounds_201709/02%20Stream%20Water.mp3",
        "ocean waves": "https://archive.org/download/NatureSounds_201709/01%20Rain%20%26%20Thunder.mp3",
        "rain leaves": "https://archive.org/download/NatureSounds_201709/01%20Rain%20%26%20Thunder.mp3",
        "peaceful lake": "https://archive.org/download/NatureSounds_201709/03%20Forest%20Birds.mp3"
    }

    selected_topic = random.choice(list(THEME_MAP.keys()))
    selected_sound_url = THEME_MAP[selected_topic] 

    print(f"--- 1. SEARCHING PIXABAY VIDEO FOR THEME: '{selected_topic}' ---")
    pixabay_video_url = f"https://pixabay.com/api/videos/?key={pixabay_key}&q={selected_topic}&per_page=30"
    video_response = requests.get(pixabay_video_url).json()
    video_hits = video_response.get("hits", [])

    horizontal_hits = []
    for v in video_hits:
        med = v.get("videos", {}).get("medium", {})
        if med.get("width", 0) > med.get("height", 0):
            horizontal_hits.append(v)

    if not horizontal_hits:
        pixabay_video_url = f"https://pixabay.com/api/videos/?key={pixabay_key}&q=nature&per_page=20"
        video_response = requests.get(pixabay_video_url).json()
        video_hits = video_response.get("hits", [])
        for v in video_hits:
            med = v.get("videos", {}).get("medium", {})
            if med.get("width", 0) > med.get("height", 0):
                horizontal_hits.append(v)

    if not horizontal_hits and video_hits:
        horizontal_hits.append(video_hits[0])

    chosen_video = random.choice(horizontal_hits)
    video_variants = chosen_video.get("videos", {})
    download_video_url = (
        video_variants.get("large", {}).get("url") or 
        video_variants.get("medium", {}).get("url") or 
        video_variants.get("small", {}).get("url")
    )

    VIDEO_FILE = "background.mp4"
    print("Downloading true horizontal nature video from Pixabay...")
    video_data = requests.get(download_video_url)
    with open(VIDEO_FILE, "wb") as f:
        f.write(video_data.content)
    print(f"Saved nature video: {VIDEO_FILE}")

    # --- 3. DOWNLOAD AMBIENT NATURE SOUNDS (INTERNET ARCHIVE) ---
    print("--- 2. FETCHING PERFECTLY MATCHING NATURE SOUNDS ---")
    AUDIO_FILE = "nature_sound.mp3" # Must be .mp3!
    audio_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    audio_downloaded = False

    print("Downloading matching nature sound track...")
    for attempt in range(3):
        audio_data = requests.get(selected_sound_url, headers=audio_headers, allow_redirects=True)
        
        # Ensure we actually get an audio file, not a 404 HTML page
        if audio_data.status_code == 200 and len(audio_data.content) > 1000:
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio_data.content)
            print("Matching nature sound downloaded successfully!")
            audio_downloaded = True
            break
        else:
            print(f"Server overloaded or blocked (Status {audio_data.status_code}). Retrying in 2 seconds...")
            time.sleep(2)

    # Bulletproof fallback to a highly reliable nature river stream (No techno!)
    if not audio_downloaded:
        print("Switching to reliable backup nature stream...")
        backup_url = "https://archive.org/download/NatureSounds_201709/02%20Stream%20Water.mp3"
        audio_data = requests.get(backup_url, headers=audio_headers, allow_redirects=True)
        with open(AUDIO_FILE, "wb") as f:
            f.write(audio_data.content)

    # --- 4. RENDER DUAL FORMAT VIDEOS FROM ONE SOURCE ---
    print("--- 3. RENDERING HORIZONTAL & CROPPED VERTICAL VIDEOS ---")
    base_video_clip = VideoFileClip(VIDEO_FILE)
    audio_clip = AudioFileClip(AUDIO_FILE)

    def build_media(v_clip, a_clip, target_dur):
        if v_clip.duration < target_dur:
            loops = int(target_dur // v_clip.duration) + 1
            v_out = concatenate_videoclips([v_clip] * loops)
        else:
            v_out = v_clip
        v_out = v_out.subclipped(0, target_dur)
        
        if a_clip.duration < target_dur:
            a_loops = int(target_dur // a_clip.duration) + 1
            a_out = concatenate_audioclips([a_clip] * a_loops)
        else:
            a_out = a_clip
        a_out = a_out.subclipped(0, target_dur)
        
        return v_out.with_audio(a_out)

    print("Rendering horizontal_short.mp4...")
    horiz_final = build_media(base_video_clip, audio_clip, HORIZONTAL_DURATION)
    horiz_final.write_videofile("horizontal_short.mp4", fps=24, codec="libx264", audio_codec="aac")

    print("Rendering vertical_short.mp4 by cropping horizontal source...")
    w, h = base_video_clip.size
    target_width = int(h * 9 / 16)
    
    cropped_base = base_video_clip.cropped(width=target_width, height=h, x_center=w/2, y_center=h/2)
    vert_final = build_media(cropped_base, audio_clip, VERTICAL_DURATION)
    vert_final.write_videofile("vertical_short.mp4", fps=24, codec="libx264", audio_codec="aac")

    if discord_webhook:
        print("--- 4. UPLOADING TO DISCORD ---")
        files_to_upload = ["horizontal_short.mp4", "vertical_short.mp4"]
        
        for vid_file in files_to_upload:
            if os.path.exists(vid_file):
                with open(vid_file, "rb") as f:
                    payload = {"content": f"✅ The video successfully generated: **{vid_file}**"}
                    files = {"file": (vid_file, f, "video/mp4")}
                    response = requests.post(discord_webhook, data=payload, files=files)

except Exception as e:
    error_trace = traceback.format_exc()
    print("CRITICAL ERROR ENCOUNTERED:")
    print(error_trace)
    notify_discord(f"❌ **Workflow Encountered an Error:**\n```python\n{error_trace[-1800:]}\n```")
    sys.exit(1)
