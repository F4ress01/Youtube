import subprocess
import random
import os

def create_video(data):
    bg_dir = "assets/backgrounds/"
    bg_video = os.path.join(bg_dir, random.choice(os.listdir(bg_dir)))
    output = "final_shorts.mp4"
    
    # Humanization: Random rotation (-2 to 2 deg) and Zoom (1.0 to 1.1)
    rot = random.uniform(-2.0, 2.0)
    zoom = random.uniform(1.0, 1.1)
    
    # Format subtitle path for FFmpeg
    subs_path = data['subs'].replace("\\", "/").replace(":", "\\:")
    
    # FFmpeg Filter Complex
    vf = (
        f"scale=1080:1920, "
        f"zoompan=z='{zoom}':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=1:s=1080x1920, "
        f"rotate={rot}*PI/180:ow=1080:oh=1920, "
        f"subtitles={subs_path}:force_style='Alignment=10,FontSize=20,PrimaryColour=&H00FFFFFF&'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(random.randint(0, 5)), # Random start point
        "-i", bg_video,
        "-i", data['audio'],
        "-vf", vf,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-shortest",
        output
    ]
    
    subprocess.run(cmd, check=True)
    return output