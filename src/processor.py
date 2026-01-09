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

def get_weighted_timestamps(text, duration_ms):
    words = text.split()
    total_chars = sum(len(w) for w in words)
    ms_per_char = duration_ms / total_chars
    boundaries = []
    current_time = 0
    for word in words:
        boundaries.append({"start": current_time, "text": word})
        current_time += (len(word) * ms_per_char)
    return boundaries

def create_srt_chunks(word_boundaries, max_chars=18):
    srt = ""
    idx = 1
    i = 0
    while i < len(word_boundaries):
        chunk = []
        chars = 0
        start_t = word_boundaries[i]['start']
        while i < len(word_boundaries) and len(chunk) < 3:
            w_text = word_boundaries[i]['text']
            if chars + len(w_text) > max_chars and len(chunk) > 0: break
            chunk.append(word_boundaries[i]); chars += len(w_text) + 1; i += 1
        
        end_t = word_boundaries[i]['start'] if i < len(word_boundaries) else chunk[-1]['start'] + 600
        text = " ".join([w['text'] for w in chunk])
        if len(text) > 12 and " " in text:
            m = len(text)//2
            split = text.find(' ', m)
            if split != -1: text = text[:split] + "\\N" + text[split+1:]
        
        srt += f"{idx}\n{format_timestamp(start_t)} --> {format_timestamp(end_t)}\n{text}\n\n"
        idx += 1
    return srt

async def process_tts(text):
    audio_p, subs_p = "output.mp3", "subs.srt"
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="+15%")
        wb = []
        with open(audio_p, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    wb.append({"start": chunk["offset"]//10000, "text": chunk["text"]})
        if wb:
            with open(subs_p, "w", encoding="utf-8") as f:
                f.write(create_srt_chunks(wb)); f.flush(); os.fsync(f.fileno())
            return audio_p, subs_p
    except: pass

    tts = gTTS(text=text, lang='en')
    tts.save(audio_p)
    duration_ms = get_audio_duration(audio_p) * 1000
    with open(subs_p, "w", encoding="utf-8") as f:
        f.write(create_srt_chunks(get_weighted_timestamps(text, duration_ms)))
        f.flush(); os.fsync(f.fileno())
    return audio_p, subs_p

def generate_content():
    cat, facts = get_ai_facts()
    intro, hook, outro = get_random_script_meta(cat)
    full_text = f"{intro}. Number 1: {facts[0]}. Number 2: {facts[1]}. {hook}. Number 3: {facts[2]}. Number 4: {facts[3]}. Number 5: {facts[4]}. {outro}"
    audio, subs = asyncio.run(process_tts(full_text))
    return {"script": full_text, "audio": audio, "subs": subs, "title": f"5 Facts about {cat}! #shorts"}