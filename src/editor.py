import subprocess
import random
import os

def create_video(data):
    bg_dir = "assets/backgrounds/"
    bg_files = [f for f in os.listdir(bg_dir) if f.endswith('.mp4')]
    
    if not bg_files:
        raise Exception("No background videos found in assets/backgrounds/")
        
    bg_video = os.path.join(bg_dir, random.choice(bg_files))
    output = "final_shorts.mp4"
    
    # Humanization parameters
    rotation = random.uniform(-2.0, 2.0)
    zoom = random.uniform(1.0, 1.1) # 10% zoom range
    
    # FFmpeg Filter Complex:
    # 1. Scale to 1080:1920
    # 2. Apply random zoom and rotate
    # 3. Burn subtitles (srt)
    # 4. Force 9:16 aspect
    
    # Ensure SRT path is escaped for FFmpeg
    subs_path = data['subs'].replace("\\", "/").replace(":", "\\:")
    
    vf_chain = (
        f"scale=1080:1920, "
        f"zoompan=z='{zoom}':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=1:s=1080x1920, "
        f"rotate={rotation}*PI/180:ow=1080:oh=1920, "
        f"subtitles={subs_path}:force_style='Alignment=10,FontSize=24,PrimaryColour=&H00FFFFFF&'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(random.randint(0, 5)), # Random start point
        "-i", bg_video,
        "-i", data['audio'],
        "-vf", vf_chain,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac", "-shortest",
        output
    ]
    
    subprocess.run(cmd, check=True)
    return output