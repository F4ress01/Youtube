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

def create_ass_file(word_boundaries, filename="subs.ass"):
    """Tworzy profesjonalne napisy wyśrodkowane z animacją fade."""
    # PlayResY: 1920 (wysokość pionowa)
    # Alignment 10: Środek ekranu (w pionie i poziomie)
    # MarginV 0: Bo Alignment 10 zajmuje się pionem
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Arial,85,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,1,10,100,100,0,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    
    events = ""
    words_per_chunk = 2 # Mniej słów = lepsza dynamika i brak wychodzenia za ekran
    for i in range(0, len(word_boundaries), words_per_chunk):
        chunk = word_boundaries[i:i + words_per_chunk]
        start_t = format_timestamp_ass(chunk[0]['start'])
        if i + words_per_chunk < len(word_boundaries):
            end_t = format_timestamp_ass(word_boundaries[i + words_per_chunk]['start'])
        else:
            end_t = format_timestamp_ass(chunk[-1]['start'] + 600)
            
        text = " ".join([w['text'] for w in chunk])
        # Automatyczne łamanie linii dla bardzo długich słów
        if len(text) > 15:
            text = text.replace(" ", "\\N", 1)
            
        # {\fad(150,150)} - płynne pojawianie i znikanie
        events += f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{{\\fad(150,150)}}{text}\n"
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + events)

async def process_tts(text):
    audio_path, subs_path = "output.mp3", "subs.ass"
    # Głos 'JennyNeural' jest bardzo emocjonalny i naturalny
    # pitch="+10%" nadaje radosny, szybki ton
    voice = "en-US-JennyNeural"
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+12%", pitch="+10%")
        wb = []
        with open(audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    wb.append({"start": chunk["offset"]//10000, "text": chunk["text"]})
        if wb:
            create_ass_file(wb, subs_path)
            return audio_path, subs_path
    except:
        print("[TTS] Edge-TTS failed, using fallback...")
        # Fallback gTTS (mniej emocji, ale stabilny)
        from gtts import gTTS
        tts = gTTS(text=text, lang='en')
        tts.save(audio_path)
        return audio_path, None

def generate_content():
    cat, facts = get_ai_facts()
    intro, hook, outro = get_random_script_meta(cat)
    # Dodajemy wykrzykniki i kropki, aby AI wiedziało gdzie modulować głos
    full_text = f"{intro}! Fact 1: {facts[0]}. Fact 2: {facts[1]}. Hey! {hook}! Fact 3: {facts[2]}. Fact 4: {facts[3]}. Fact 5: {facts[4]}! {outro}"
    audio, subs = asyncio.run(process_tts(full_text))
    return {"script": full_text, "audio": audio, "subs": subs, "title": f"5 MIND-BLOWING Facts about {cat}! #shorts"}