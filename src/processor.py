import random
import asyncio
import edge_tts
import os
import subprocess
from utils import get_ai_facts, get_random_script_meta

def format_timestamp_ass(ms):
    seconds, ms = divmod(int(ms), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02}:{seconds:02}.{ms // 10:02}"

def create_ass_file(word_boundaries, filename="subs.ass"):
    # FontSize: 115, Bold: 1, Outline: 8 (Bubble effect), Alignment: 5 (Middle)
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Quicksand Bold,115,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,5,100,100,0,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    
    events = ""
    # Jeden wyraz na raz dla mega dynamiki
    for i, b in enumerate(word_boundaries):
        start_t = format_timestamp_ass(b['start'])
        if i + 1 < len(word_boundaries):
            end_t = format_timestamp_ass(word_boundaries[i + 1]['start'])
        else:
            end_t = format_timestamp_ass(b['start'] + 500)
            
        text = b['text'].upper() # Wielkie litery
        events += f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{{\\fad(100,100)}}{text}\n"
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + events)
        f.flush()
        os.fsync(f.fileno())

async def process_tts(text):
    audio_path, subs_path = "output.mp3", "subs.ass"
    if os.path.exists(audio_path): os.remove(audio_path)
    
    try:
        # Jenny - najbardziej radosny i emocjonalny głos
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
    except:
        return None, None

def generate_content():
    cat, facts = get_ai_facts()
    intro, hook, outro = get_random_script_meta(cat)
    # Składamy skrypt
    full_text = f"{intro}! Fact 1. {facts[0]}. Fact 2. {facts[1]}. {hook}! Fact 3. {facts[2]}. Fact 4. {facts[3]}. Fact 5. {facts[4]}! {outro}"
    audio, subs = asyncio.run(process_tts(full_text))
    return {"script": full_text, "audio": audio, "subs": subs, "title": f"5 Amazing Facts about {cat}! #shorts"}