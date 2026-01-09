import subprocess
import random
import os

def create_video(data):
    bg_dir = "assets/backgrounds/"
    bg_video = os.path.join(bg_dir, random.choice(os.listdir(bg_dir)))
    subs_file = "subs.ass"
    output = "final_shorts.mp4"

    if not os.path.exists(subs_file):
        raise Exception("Subtitle file was not generated!")

    # ANTI-BAN JITTER
    speed = random.uniform(0.98, 1.02)
    noise = random.randint(1, 3)
    brightness = random.uniform(-0.02, 0.02)
    
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"setsar=1,setdar=9/16,subtitles={subs_file},"
        f"eq=brightness={brightness}:contrast=1.02,"
        f"noise=alls={noise}:allf=t+u,setpts={1/speed}*PTS"
    )

    cmd = [
        "ffmpeg", "-y", "-stream_loop", "-1", "-ss", str(random.uniform(0, 5)),
        "-i", bg_video, "-i", "output.mp3", "-vf", vf, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-aspect", "9:16", "-shortest", output
    ]
    subprocess.run(cmd, check=True)
    return output