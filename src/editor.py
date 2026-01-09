import subprocess
import random
import os

def create_video(data):
    # Use absolute paths to fix FFmpeg "Unable to open" errors
    current_dir = os.getcwd()
    
    bg_dir = os.path.join(current_dir, "assets/backgrounds/")
    bg_files = [f for f in os.listdir(bg_dir) if f.endswith('.mp4')]
    
    if not bg_files:
        raise Exception("No background videos found in assets/backgrounds/")
        
    bg_video = os.path.join(bg_dir, random.choice(bg_files))
    audio_path = os.path.join(current_dir, data['audio'])
    subs_path = os.path.join(current_dir, data['subs'])
    output_path = os.path.join(current_dir, "final_shorts.mp4")

    # Safety check
    if not os.path.exists(subs_path):
        raise Exception(f"Subtitle file missing at: {subs_path}")

    # Prepare subtitle path for FFmpeg filter (handle Linux escaping)
    # Using single quotes inside the filter is required by libass on Linux
    safe_subs_path = subs_path.replace("\\", "/").replace(":", "\\:")
    
    rotation = random.uniform(-2.0, 2.0)
    zoom = random.uniform(1.0, 1.1)
    
    # Filter Chain: Scale -> Zoom -> Rotate -> Burn Subtitles
    vf = (
        f"scale=1080:1920, "
        f"zoompan=z='{zoom}':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=1:s=1080x1920, "
        f"rotate={rotation}*PI/180:ow=1080:oh=1920, "
        f"subtitles='{safe_subs_path}':force_style='Alignment=10,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(random.randint(0, 5)),
        "-i", bg_video,
        "-i", audio_path,
        "-vf", vf,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast",
        "-c:a", "aac", "-shortest",
        output_path
    ]
    
    print(f"[EDITOR] Rendering video: Zoom={zoom:.2f}, Rotation={rotation:.2f}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error Output: {e.stderr}")
        raise Exception(f"FFmpeg failed with exit code {e.returncode}")

    return output_path