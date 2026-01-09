import subprocess
import random
import os

def create_video(data):
    bg_dir = "assets/backgrounds/"
    bg_video = os.path.join(bg_dir, random.choice(os.listdir(bg_dir)))
    subs_file = "subs.srt"
    output = "final_shorts.mp4"

    style = "Alignment=10,Fontname=Arial,FontSize=24,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2.5,Shadow=1,MarginV=280,MarginL=120,MarginR=120,WrapStyle=2"
    vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,setdar=9/16,subtitles={subs_file}:force_style='{style}'"

    cmd = [
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", bg_video, "-i", "output.mp3",
        "-vf", vf, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "22", "-aspect", "9:16", "-shortest", output
    ]
    subprocess.run(cmd, check=True)
    return output