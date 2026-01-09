import subprocess
import random
import os

def create_video(data):
    current_dir = os.getcwd()
    bg_dir = os.path.join(current_dir, "assets/backgrounds/")
    bg_video = os.path.join(bg_dir, random.choice(os.listdir(bg_dir)))
    
    audio_path = os.path.join(current_dir, "output.mp3")
    subs_file = os.path.join(current_dir, "subs.ass")
    output = os.path.join(current_dir, "final_shorts.mp4")

    if not os.path.exists(subs_file):
        # Sprawdź czy plik nie jest w innym folderze
        print(f"[DEBUG] Files in current dir: {os.listdir(current_dir)}")
        raise Exception(f"Subtitle file was not generated! Expected at: {subs_file}")

    # Dla filtra subtitles na Linuxie, najlepiej użyć samej nazwy pliku jeśli jest w tym samym folderze
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"setsar=1,setdar=9/16,subtitles=subs.ass"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", bg_video,
        "-i", audio_path,
        "-vf", vf,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "22",
        "-aspect", "9:16",
        "-shortest",
        output
    ]
    
    print(f"[EDITOR] Rendering stylized Shorts using {os.path.basename(bg_video)}...")
    subprocess.run(cmd, check=True)
    return output