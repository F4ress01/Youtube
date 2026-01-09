import subprocess
import random
import os

def create_video(data):
    current_dir = os.getcwd()
    bg_dir = os.path.join(current_dir, "assets/backgrounds/")
    bg_video = os.path.join(bg_dir, random.choice(os.listdir(bg_dir)))
    subs_file = "subs.ass"
    output = "final_shorts.mp4"

    if not os.path.exists(subs_file):
        raise Exception("Subtitle file was not generated!")

    # Prostsza sciezka do napisow dla Linux
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"setsar=1,setdar=9/16,subtitles={subs_file}"
    )

    cmd = [
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", bg_video, "-i", "output.mp3",
        "-vf", vf, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "22", "-aspect", "9:16", "-shortest", output
    ]
    
    print(f"[EDITOR] Rendering stylized Shorts with animations...")
    subprocess.run(cmd, check=True)
    return output