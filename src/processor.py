import random
import asyncio
import edge_tts
import os
import subprocess
from gtts import gTTS
from utils import get_ai_facts, get_random_script_meta

def format_timestamp_ass(ms):
    """Formatuje czas dla standardu ASS (H:MM:SS.cs)"""
    seconds, ms = divmod(int(ms), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    centiseconds = ms // 10
    return f"{hours}:{minutes:02}:{seconds:02}.{centiseconds:02}"

def get_audio_duration(file_path):
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file_path}\""
    return float(subprocess.check_output(cmd, shell=True).decode().strip())

def create_ass_file(word_boundaries, filename="subs.ass"):
    """Tworzy plik ASS z animacjami pojawiania się (fading)"""
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Arial,70,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,1,10,120,120,400,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    
    events = ""
    words_per_chunk = 3
    for i in range(0, len(word_boundaries), words_per_chunk):
        chunk = word_boundaries[i:i + words_per_chunk]
        start_t = format_timestamp_ass(chunk[0]['start'])
        if i + words_per_chunk < len(word_boundaries):
            end_t = format_timestamp_ass(word_boundaries[i + words_per_chunk]['start'])
        else:
            end_t = format_timestamp_ass(chunk[-1]['start'] + 600)
            
        text = " ".join([w['text'] for w in chunk])
        # {\fad(200,200)} - 200ms pojawiania się i 200ms znikania
        events += f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{{\\fad(200,200)}}{text}\n"
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + events)

async def process_tts(text):
    audio_path, subs_path = "output.mp3", "subs.ass"
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="+12%")
        wb = []
        with open(audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    wb.append({"start": chunk["offset"]//10000, "text": chunk["text"]})
        if wb:
            create_ass_file(wb, subs_path)
            return audio_path, subs_path
    except: pass

    # gTTS Fallback
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)
    dur = get_audio_duration(audio_path) * 1000
    words = text.split()
    ms_per_word = dur / len(words)
    wb = [{"start": i * ms_per_word, "text": w} for i, w in enumerate(words)]
    create_ass_file(wb, subs_path)
    return audio_path, subs_path

def generate_content():
    cat, facts = get_ai_facts()
    intro, hook, outro = get_random_script_meta(cat)
    full_text = f"{intro}. Number 1: {facts[0]}. Number 2: {facts[1]}. {hook}. Number 3: {facts[2]}. Number 4: {facts[3]}. Number 5: {facts[4]}. {outro}"
    audio, subs = asyncio.run(process_tts(full_text))
    return {"script": full_text, "audio": audio, "subs": subs, "title": f"5 Facts about {cat}! #shorts"}