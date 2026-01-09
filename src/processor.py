import random
import asyncio
import edge_tts
import os
import subprocess
from gtts import gTTS
from utils import get_ai_facts, get_random_script_meta

def format_timestamp_ass(ms):
    seconds, ms = divmod(int(ms), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02}:{seconds:02}.{ms // 10:02}"

def get_audio_duration(file_path):
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file_path}\""
    return float(subprocess.check_output(cmd, shell=True).decode().strip())

def get_weighted_timestamps(text, duration_ms):
    """Inteligentne AI: Oblicza czas słów na podstawie ich długości (znaków)"""
    words = text.split()
    total_chars = sum(len(w) for w in words)
    ms_per_char = duration_ms / total_chars
    boundaries = []
    current_time = 0
    for word in words:
        boundaries.append({"start": current_time, "text": word})
        current_time += (len(word) * ms_per_char)
    return boundaries

def create_ass_file(word_boundaries, filename="subs.ass"):
    """Tworzy profesjonalne napisy BUBBLE FONT na środku ekranu"""
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Quicksand Bold,115,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,5,100,100,0,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events = ""
    for i, b in enumerate(word_boundaries):
        start_t = format_timestamp_ass(b['start'])
        if i + 1 < len(word_boundaries):
            end_t = format_timestamp_ass(word_boundaries[i + 1]['start'])
        else:
            end_t = format_timestamp_ass(b['start'] + 600)
        text = b['text'].upper()
        events += f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{{\\fad(100,100)}}{text}\n"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + events)
        f.flush()
        os.fsync(f.fileno())

async def process_tts(text):
    audio_path, subs_path = "output.mp3", "subs.ass"
    if os.path.exists(audio_path): os.remove(audio_path)
    
    # 1. PRÓBA EDGE-TTS
    try:
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural", rate="+15%")
        wb = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                with open(audio_path, "ab") as f: f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                wb.append({"start": chunk["offset"]//10000, "text": chunk["text"]})
        if wb:
            create_ass_file(wb, subs_path)
            print("[TTS] Edge-TTS Success.")
            return audio_path, subs_path
    except Exception as e:
        print(f"[TTS] Edge-TTS failed ({e}). Switching to gTTS fallback...")

    # 2. GWARANTOWANY FALLBACK gTTS
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(audio_path)
        duration_ms = get_audio_duration(audio_path) * 1000
        # AI wylicza czasy dla gTTS
        wb = get_weighted_timestamps(text, duration_ms)
        create_ass_file(wb, subs_path)
        print("[TTS] gTTS Fallback Success.")
        return audio_path, subs_path
    except Exception as e:
        raise Exception(f"CRITICAL: Both TTS engines failed. {e}")

def generate_content():
    category, facts = get_ai_facts()
    intro, hook, outro = get_random_script_meta(category)
    full_text = f"{intro}! Number 1. {facts[0]}. Number 2. {facts[1]}. {hook}! Number 3. {facts[2]}. Number 4. {facts[3]}. Number 5. {facts[4]}! {outro}"
    audio, subs = asyncio.run(process_tts(full_text))
    return {"script": full_text, "audio": audio, "subs": subs, "title": f"5 Amazing Facts about {category}! #shorts"}