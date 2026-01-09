import subprocess
import random
import os

def create_video(data):
    current_dir = os.getcwd()
    bg_dir = os.path.join(current_dir, "assets/backgrounds/")
    bg_video = os.path.join(bg_dir, random.choice(os.listdir(bg_dir)))
    
    audio_path = "output.mp3"
    subs_file = "subs.ass"
    output = "final_shorts.mp4"

    if not os.path.exists(subs_file):
        raise Exception("Subtitle file was not generated!")

    # --- PARAMETRY UNIKALNOŚCI (ANTI-BAN) ---
    rotation = random.uniform(-1.5, 1.5)
    zoom = random.uniform(1.0, 1.1)
    # Losowa prędkość (98% - 102%) - zmienia sumę MD5 filmu
    speed = random.uniform(0.98, 1.02)
    # Losowa zmiana jasności i kontrastu (niewidoczna dla oka)
    brightness = random.uniform(-0.02, 0.02)
    contrast = random.uniform(0.98, 1.02)
    # Losowe ziarno (noise) - każda klatka będzie unikalna bitowo
    noise_seed = random.randint(1, 999999)

    # Budujemy zaawansowany filtr wideo
    # 1. Skalowanie/Docięcie
    # 2. Napisy
    # 3. Zmiana kolorów (eq)
    # 4. Dodanie ziarna (noise)
    # 5. Zmiana prędkości (setpts)
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"setsar=1,setdar=9/16,subtitles={subs_file},"
        f"eq=brightness={brightness}:contrast={contrast},"
        f"noise=alls={random.randint(1,3)}:allf=t+u:all_seed={noise_seed},"
        f"setpts={1/speed}*PTS"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",        # Zapętla tło
        "-ss", str(random.uniform(0, 5)), # Losowy punkt startowy tła
        "-i", bg_video,
        "-i", audio_path,
        "-vf", vf,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "22",
        "-aspect", "9:16",
        "-shortest",                 # Utnij do długości audio
        output
    ]
    
    print(f"[EDITOR] Creating UNIQUE video: Speed={speed:.2f}, NoiseSeed={noise_seed}")
    subprocess.run(cmd, check=True)
    return output