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

    # STYL:
    # MarginV=250 podnosi napisy wyżej, aby nie zasłaniał ich opis filmu
    # Alignment=10 (środek-środek)
    # WrapStyle=2 (lepsze zawijanie tekstu)
    style = (
        "Alignment=10,Fontname=Arial,FontSize=24,Bold=1,"
        "PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,"
        "BorderStyle=1,Outline=2,Shadow=1,MarginV=250,WrapStyle=2"
    )

    # Wymuszamy 1080x1920 i sprawdzamy proporcje (dar=9/16)
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"setsar=1,setdar=9/16,"
        f"subtitles='{subs_path}':force_style='{style}'"
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
        "-aspect", "9:16", # WYMUSZONY ASPEKT DLA SHORTS
        "-shortest",
        output_path
    ]
    
    print(f"[EDITOR] Rendering Shorts (9:16)...")
    subprocess.run(cmd, check=True)
    return output_path