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

# --- 3. GENERATE AUDIOCRAFT / MUSICGEN AUDIO (HUGGING FACE API) ---
print("--- 2. GENERATING LOFI AUDIO VIA META AUDIOCRAFT ---")
AUDIO_FILE = "cafe_music.wav"

audio_prompt = "lofi slow bpm electro chill with organic samples, dusty vinyl crackle, warm piano chords"
print(f"Prompting MusicGen: '{audio_prompt}'")

hf_api_url = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
headers = {"Authorization": f"Bearer {hf_key}"}

audio_downloaded = False
for attempt in range(3):
    try:
        # We use a 120-second timeout because AI audio generation takes time to process
        audio_response = requests.post(hf_api_url, headers=headers, json={"inputs": audio_prompt}, timeout=120)
        
        if audio_response.status_code == 200:
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio_response.content)
            print("SUCCESS: AudioCraft Lofi track generated!")
            audio_downloaded = True
            break
        elif "is currently loading" in audio_response.text:
            print("The AI model is warming up on the server. Waiting 20 seconds...")
            time.sleep(20)
        else:
            print(f"Audio Generation Failed: {audio_response.text}. Retrying...")
            time.sleep(5)
    except Exception as e:
        print(f"Attempt {attempt + 1} Error: {e}")
        time.sleep(5)

if not audio_downloaded:
    print("CRITICAL ERROR: Failed to generate AI audio after 3 attempts.")
    sys.exit(1)

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
