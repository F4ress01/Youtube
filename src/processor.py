import random
import asyncio
import edge_tts
import os
import subprocess
from gtts import gTTS
from utils import get_ai_facts, get_unique_metadata

def format_timestamp_ass(ms):
    return f"{int(ms//3600000)}:{int((ms//60000)%60):02}:{int((ms//1000)%60):02}.{int((ms//10)%100):02}"

def create_ass_file(word_boundaries, filename="subs.ass"):
    # Style BUBBLE FONT (Quicksand Bold)
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Quicksand Bold,110,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,5,100,100,0,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events = ""
    for i, b in enumerate(word_boundaries):
        start_t = format_timestamp_ass(b['start'])
        end_t = format_timestamp_ass(word_boundaries[i + 1]['start']) if i+1 < len(word_boundaries) else format_timestamp_ass(b['start'] + 600)
        text = b['text'].upper()
        events += f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{{\\fad(150,150)}}{text}\n"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + events)
        f.flush(); os.fsync(f.fileno())

async def process_tts(text):
    audio_path, subs_path = "output.mp3", "subs.ass"
    # Losowy ton i emocje lektora (+/- 2% dla unikalności audio)
    pitch = f"+{random.randint(8, 12)}%"
    rate = f"+{random.randint(12, 16)}%"
    
    try:
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural", rate=rate, pitch=pitch)
        wb = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                with open(audio_path, "ab") as f: f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                wb.append({"start": chunk["offset"]//10000, "text": chunk["text"]})
        if wb:
            create_ass_file(wb, subs_path)
            return audio_path, subs_path
    except:
        pass

    # Fallback gTTS
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)
    return audio_path, subs_path

def generate_content():
    cat, facts = get_ai_facts()
    title, tags = get_unique_metadata(cat)
    # Intro/Outro templates
    full_text = f"Did you know these 5 facts about {cat}! Number 1: {facts[0]}. Number 2: {facts[1]}. Number 3: {facts[2]}. Number 4: {facts[3]}. Number 5: {facts[4]}! Subscribe for more!"
    audio, subs = asyncio.run(process_tts(full_text))
    return {"script": full_text, "audio": audio, "subs": subs, "title": f"{title} {tags}"}