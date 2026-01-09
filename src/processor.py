import random
import asyncio
import edge_tts
import os
import subprocess
from gtts import gTTS
from utils import get_ai_facts, get_unique_metadata

def format_timestamp_ass(ms):
    h, ms = divmod(int(ms), 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h}:{m:02}:{s:02}.{ms // 10:02}"

def get_audio_duration(file_path):
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file_path}\""
    return float(subprocess.check_output(cmd, shell=True).decode().strip())

def create_ass_file(boundaries, filename="subs.ass"):
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Quicksand Bold,110,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,5,100,100,0,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events = ""
    for i, b in enumerate(boundaries):
        start_t = format_timestamp_ass(b['start'])
        end_t = format_timestamp_ass(boundaries[i+1]['start']) if i+1 < len(boundaries) else format_timestamp_ass(b['start'] + 600)
        text = b['text'].upper()
        if len(text) > 12 and " " in text: text = text.replace(" ", "\\N", 1)
        events += f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{{\\fad(150,150)}}{text}\n"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + events)
        f.flush(); os.fsync(f.fileno())

async def process_tts(text):
    audio_path, subs_path = "output.mp3", "subs.ass"
    if os.path.exists(audio_path): os.remove(audio_path)
    
    try: # EDGE-TTS (Jenny)
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural", rate="+15%", pitch="+10%")
        wb = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                with open(audio_path, "ab") as f: f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                wb.append({"start": chunk["offset"]//10000, "text": chunk["text"]})
        if wb:
            create_ass_file(wb, subs_path)
            return audio_path, subs_path
    except: pass

    # FALLBACK gTTS
    print("[TTS] Falling back to gTTS...")
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)
    duration_ms = get_audio_duration(audio_path) * 1000
    words = text.split()
    ms_p_w = duration_ms / len(words)
    wb = [{"start": i * ms_p_w, "text": w} for i, w in enumerate(words)]
    create_ass_file(wb, subs_path)
    return audio_path, subs_path

def generate_content():
    cat, facts = get_ai_facts()
    title, tags = get_unique_metadata(cat)
    full_text = f"Did you know these 5 facts about {cat}! Number 1: {facts[0]}. Number 2: {facts[1]}. Number 3: {facts[2]}. Number 4: {facts[3]}. Number 5: {facts[4]}! Subscribe for more!"
    audio, subs = asyncio.run(process_tts(full_text))
    return {"script": full_text, "audio": audio, "subs": subs, "title": f"{title} {tags}"}