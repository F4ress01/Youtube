import random
import asyncio
import edge_tts
import os
import subprocess
from gtts import gTTS
from utils import get_unique_fact

def format_timestamp(ms):
    seconds, ms = divmod(int(ms), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

def get_audio_duration(file_path):
    """Gets audio duration using ffprobe"""
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file_path}\""
    duration = subprocess.check_output(cmd, shell=True).decode().strip()
    return float(duration)

def create_pseudo_srt(text, duration_sec):
    """Creates subtitles for gTTS by distributing words over duration"""
    words = text.split()
    word_count = len(words)
    time_per_word = (duration_sec * 1000) / word_count
    
    srt_content = ""
    for i, word in enumerate(words):
        start = i * time_per_word
        end = (i + 1) * time_per_word
        srt_content += f"{i+1}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{word}\n\n"
    return srt_content

async def process_tts(text):
    current_dir = os.getcwd()
    audio_path = os.path.join(current_dir, "output.mp3")
    subs_path = os.path.join(current_dir, "subs.srt")
    
    # Attempt Edge-TTS (Primary)
    voices = ["en-US-GuyNeural", "en-US-AriaNeural", "en-GB-ThomasNeural", "en-GB-SoniaNeural"]
    for voice in voices:
        print(f"[TTS] Trying Edge-TTS with voice: {voice}")
        try:
            communicate = edge_tts.Communicate(text, voice)
            word_boundaries = []
            audio_received = False
            
            with open(audio_path, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                        audio_received = True
                    elif chunk["type"] == "WordBoundary":
                        word_boundaries.append({"start": chunk["offset"], "text": chunk["text"]})
            
            if audio_received and word_boundaries:
                srt_content = ""
                for i, b in enumerate(word_boundaries):
                    start = b['start'] // 10000
                    if i < len(word_boundaries)-1:
                        end = word_boundaries[i+1]['start'] // 10000
                    else:
                        end = start + 400
                    srt_content += f"{i+1}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{b['text']}\n\n"
                
                with open(subs_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                    f.flush()
                    os.fsync(f.fileno())
                
                print("[TTS] Edge-TTS Success.")
                return "output.mp3", "subs.srt"
        except Exception as e:
            print(f"[TTS] Edge-TTS voice {voice} failed: {e}")
            continue

    # FALLBACK: Use Google TTS
    print("[TTS] Edge-TTS failed or blocked. Using Google TTS Fallback...")
    try:
        tts = gTTS(text=text, lang='en', tld='com')
        tts.save(audio_path)
        
        duration = get_audio_duration(audio_path)
        srt_content = create_pseudo_srt(text, duration)
        
        with open(subs_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
            f.flush()
            os.fsync(f.fileno())
            
        print("[TTS] Google TTS Success.")
        return "output.mp3", "subs.srt"
    except Exception as e:
        raise Exception(f"Critical Error: Both TTS engines failed. {e}")

def generate_content():
    fact = get_unique_fact()
    if not fact:
        fact = "The human brain has the same consistency as tofu."
    
    script = f"Did you know? {fact} Like and follow for more!"
    audio, subs = asyncio.run(process_tts(script))
    
    return {
        "script": script,
        "audio": audio,
        "subs": subs,
        "title": f"Amazing Fact! #shorts #facts"
    }