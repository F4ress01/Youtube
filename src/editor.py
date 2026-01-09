import subprocess
import random
import os

def create_video(data):
    # Ważne: FFmpeg na Linuxie najlepiej radzi sobie z relatywnymi ścieżkami w filtrze subtitles
    bg_dir = "assets/backgrounds/"
    bg_files = [f for f in os.listdir(bg_dir) if f.endswith('.mp4')]
    bg_video = os.path.join(bg_dir, random.choice(bg_files))
    
    audio_path = "output.mp3"
    subs_filename = "subs.srt" # Używamy nazwy pliku zamiast pełnej ścieżki
    output_path = "final_shorts.mp4"

    # Sprawdzenie czy napisy istnieją
    if not os.path.exists(subs_filename):
        raise Exception("Subtitle file was not generated!")

    # STYLIZACJA (WrapStyle=2 zapobiega wychodzeniu poza ekran)
    style = (
        "Alignment=10,Fontname=Arial,FontSize=26,Bold=1,"
        "PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,"
        "BorderStyle=1,Outline=2,Shadow=1,MarginV=280,WrapStyle=2"
    )

    # Filtr wideo:
    # 1. Skalowanie i docięcie do 1080x1920
    # 2. Wymuszenie proporcji 9:16
    # 3. Nałożenie napisów (używając relatywnej ścieżki)
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"setsar=1,setdar=9/16,"
        f"subtitles={subs_filename}:force_style='{style}'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",  # Zapętlanie wideo tła
        "-i", bg_video,
        "-i", audio_path,
        "-vf", vf,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "22",
        "-aspect", "9:16",
        "-shortest",           # Utnij film gdy skończy się audio
        output_path
    ]
    
    print(f"[EDITOR] Rendering Shorts (9:16) using {bg_video}...")
    subprocess.run(cmd, check=True)
    return output_path