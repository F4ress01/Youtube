import random
import asyncio
import edge_tts
import os
import subprocess
from gtts import gTTS
from utils import get_ai_facts, get_random_script_meta

def format_timestamp(ms):
    seconds, ms = divmod(int(ms), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

def get_audio_duration(file_path):
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file_path}\""
    return float(subprocess.check_output(cmd, shell=True).decode().strip())

def create_pseudo_srt(text, duration_sec):
    words = text.split()
    avg_dur = (duration_sec * 1000) / len(words)
    srt = ""
    for i, w in enumerate(words):
        start = i * avg_dur
        end = (i + 1) * avg_dur
        srt += f"{i+1}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{w}\n\n"
    return srt

async def process_tts(text):
    audio_path = os.path.join(os.getcwd(), "output.mp3")
    subs_path = os.path.join(os.getcwd(), "subs.srt")
    
    # Edge-TTS
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="+4%")
        word_boundaries = []
        with open(audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    word_boundaries.append({"start": chunk["offset"]//10000, "text": chunk["text"]})
        
        if word_boundaries:
            srt_content = ""
            for i, b in enumerate(word_boundaries):
                start = b['start']
                end = word_boundaries[i+1]['start'] if i < len(word_boundaries)-1 else start + 400
                srt_content += f"{i+1}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{b['text']}\n\n"
            with open(subs_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
                f.flush()
                os.fsync(f.fileno())
            return "output.mp3", "subs.srt"
    except:
        print("[TTS] Edge-TTS failed, using gTTS...")

    # gTTS Fallback
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)
    duration = get_audio_duration(audio_path)
    with open(subs_path, "w", encoding="utf-8") as f:
        f.write(create_pseudo_srt(text, duration))
        f.flush()
        os.fsync(f.fileno())
    return "output.mp3", "subs.srt"

def generate_content():
    category, facts = get_ai_facts()
    intro, hook, outro = get_random_script_meta(category)
    
    full_text = f"{intro} . . . Number 1: {facts[0]} . . . Number 2: {facts[1]} . . . {hook} . . . Number 3: {facts[2]} . . . Number 4: {facts[3]} . . . Number 5: {facts[4]} . . . {outro}"
    
    audio, subs = asyncio.run(process_tts(full_text))
    return {"script": full_text, "audio": audio, "subs": subs, "title": f"5 Amazing Facts about {category}! #shorts #ai"}