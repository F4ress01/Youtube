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
    centiseconds = ms // 10
    return f"{hours}:{minutes:02}:{seconds:02}.{centiseconds:02}"

def get_audio_duration(file_path):
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file_path}\""
    return float(subprocess.check_output(cmd, shell=True).decode().strip())

def create_ass_file(word_boundaries, filename="subs.ass"):
    """Generuje napisy ASS z centrowaniem i animacją pojawiania się."""
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Arial,80,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,1,10,100,100,0,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    
    events = ""
    words_per_chunk = 2
    for i in range(0, len(word_boundaries), words_per_chunk):
        chunk = word_boundaries[i:i + words_per_chunk]
        start_t = format_timestamp_ass(chunk[0]['start'])
        if i + words_per_chunk < len(word_boundaries):
            end_t = format_timestamp_ass(word_boundaries[i + words_per_chunk]['start'])
        else:
            end_t = format_timestamp_ass(chunk[-1]['start'] + 800)
            
        text = " ".join([w['text'] for w in chunk])
        if len(text) > 15: text = text.replace(" ", "\\N", 1)
        # Dodajemy animację fad (200ms)
        events += f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{{\\fad(200,200)}}{text}\n"
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + events)
        f.flush()
        os.fsync(f.fileno())

async def process_tts(text):
    audio_path, subs_path = "output.mp3", "subs.ass"
    # Jenny jest bardziej stabilna i emocjonalna
    voice = "en-US-JennyNeural"
    
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+12%")
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
        print(f"[TTS] Edge-TTS failed: {e}. Using gTTS fallback...")

    # AWARYJNY gTTS - Teraz również tworzy subs.ass
    if os.path.exists(audio_path): os.remove(audio_path)
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)
    
    duration_ms = get_audio_duration(audio_path) * 1000
    words = text.split()
    ms_per_word = duration_ms / len(words)
    wb = [{"start": i * ms_per_word, "text": w} for i, w in enumerate(words)]
    
    create_ass_file(wb, subs_path)
    return audio_path, subs_path

def generate_content():
    cat, facts = get_ai_facts()
    intro, hook, outro = get_random_script_meta(cat)
    full_text = f"{intro}! Fact 1: {facts[0]}. Fact 2: {facts[1]}. {hook}! Fact 3: {facts[2]}. Fact 4: {facts[3]}. Fact 5: {facts[4]}! {outro}"
    audio, subs = asyncio.run(process_tts(full_text))
    return {"script": full_text, "audio": audio, "subs": subs, "title": f"5 Amazing Facts about {cat}! #shorts"}