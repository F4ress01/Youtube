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

def create_srt_chunks(word_boundaries, words_per_chunk=3):
    """Grupuje słowa po 3, aby napisy nadążały i nie wychodziły za ekran"""
    srt_content = ""
    for i in range(0, len(word_boundaries), words_per_chunk):
        chunk = word_boundaries[i:i + words_per_chunk]
        start_time = chunk[0]['start']
        # End time to start następnego chunka lub start + 800ms
        if i + words_per_chunk < len(word_boundaries):
            end_time = word_boundaries[i + words_per_chunk]['start']
        else:
            end_time = chunk[-1]['start'] + 600
        
        text = " ".join([w['text'] for w in chunk])
        # Jeśli tekst jest bardzo długi (rzadkie), dodajemy nową linię w środku
        if len(text) > 20:
            mid = len(text) // 2
            split_idx = text.find(' ', mid)
            if split_idx != -1:
                text = text[:split_idx] + "\\N" + text[split_idx+1:]

        srt_content += f"{(i // words_per_chunk) + 1}\n"
        srt_content += f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n"
        srt_content += f"{text}\n\n"
    return srt_content

async def process_tts(text):
    audio_path = os.path.join(os.getcwd(), "output.mp3")
    subs_path = os.path.join(os.getcwd(), "subs.srt")
    
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="+8%")
        word_boundaries = []
        with open(audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    word_boundaries.append({"start": chunk["offset"]//10000, "text": chunk["text"]})
        
        if word_boundaries:
            # Używamy inteligentnego grupowania słów
            srt_content = create_srt_chunks(word_boundaries, words_per_chunk=3)
            with open(subs_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
                f.flush()
                os.fsync(f.fileno())
            return "output.mp3", "subs.srt"
    except Exception as e:
        print(f"[TTS ERROR] {e}")

    # Fallback gTTS (uproszczony)
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)
    return "output.mp3", "subs.srt"

def generate_content():
    category, facts = get_ai_facts()
    intro, hook, outro = get_random_script_meta(category)
    
    # Krótsze pauzy (tylko jedna kropka), aby dynamika była większa
    full_text = f"{intro}. Number 1: {facts[0]}. Number 2: {facts[1]}. {hook}. Number 3: {facts[2]}. Number 4: {facts[3]}. Number 5: {facts[4]}. {outro}"
    
    audio, subs = asyncio.run(process_tts(full_text))
    # DODAJEMY #SHORTS DO TYTUŁU
    title = f"5 Facts about {category}! #shorts #facts #ai"
    return {"script": full_text, "audio": audio, "subs": subs, "title": title}