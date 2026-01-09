import subprocess
import random
import os

def create_video(data):
    current_dir = os.getcwd()
    bg_dir = os.path.join(current_dir, "assets/backgrounds/")
    bg_video = os.path.join(bg_dir, random.choice(os.listdir(bg_dir)))
    
    audio_path = os.path.join(current_dir, data['audio'])
    subs_path = os.path.join(current_dir, data['subs']).replace("\\", "/").replace(":", "\\:")
    output_path = os.path.join(current_dir, "final_shorts.mp4")

    style = "Alignment=10,Fontname=Arial,FontSize=28,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2.5,Shadow=1.5"
    vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles='{subs_path}':force_style='{style}'"

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", bg_video,
        "-i", audio_path,
        "-vf", vf,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast",
        "-shortest", output_path
    ]
    
    print(f"[EDITOR] Rendering stylized 30s+ video...")
    subprocess.run(cmd, check=True)
    return output_path