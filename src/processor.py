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
    """Pobiera czas trwania audio za pomocą ffprobe"""
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file_path}\""
    return float(subprocess.check_output(cmd, shell=True).decode().strip())

def create_srt_chunks(word_boundaries, words_per_chunk=3):
    """Grupuje słowa w paczki po 3, aby napisy były czytelne"""
    srt_content = ""
    for i in range(0, len(word_boundaries), words_per_chunk):
        chunk = word_boundaries[i:i + words_per_chunk]
        start_time = chunk[0]['start']
        
        if i + words_per_chunk < len(word_boundaries):
            end_time = word_boundaries[i + words_per_chunk]['start']
        else:
            # Dla ostatniego fragmentu dodajemy czas trwania ostatniego słowa
            end_time = chunk[-1]['start'] + 500 
        
        text = " ".join([w['text'] for w in chunk])
        
        # Automatyczne łamanie linii, jeśli tekst jest zbyt długi
        if len(text) > 22:
            mid = len(text) // 2
            split_idx = text.find(' ', mid)
            if split_idx != -1:
                text = text[:split_idx] + "\\N" + text[split_idx+1:]

        srt_content += f"{(i // words_per_chunk) + 1}\n"
        srt_content += f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n"
        srt_content += f"{text}\n\n"
    return srt_content

async def process_tts(text):
    audio_path = "output.mp3"
    subs_path = "subs.srt"
    
    # 1. PRÓBA EDGE-TTS (Wysoka jakość + precyzyjne napisy)
    try:
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="+10%")
        word_boundaries = []
        with open(audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    word_boundaries.append({"start": chunk["offset"]//10000, "text": chunk["text"]})
        
        if word_boundaries:
            srt_content = create_srt_chunks(word_boundaries, words_per_chunk=3)
            with open(subs_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
                f.flush()
                os.fsync(f.fileno())
            print("[TTS] Edge-TTS Success.")
            return audio_path, subs_path
    except Exception as e:
        print(f"[TTS] Edge-TTS failed: {e}. Switching to gTTS fallback...")

    # 2. TRYB AWARYJNY gTTS (Google TTS)
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(audio_path)
        
        # Obliczamy "sztuczne" ramy czasowe dla napisów gTTS
        duration = get_audio_duration(audio_path)
        words = text.split()
        avg_word_dur = (duration * 1000) / len(words)
        
        # Tworzymy strukturę word_boundaries dla gTTS
        fake_boundaries = []
        for i, word in enumerate(words):
            fake_boundaries.append({
                "start": i * avg_word_dur,
                "text": word
            })
            
        srt_content = create_srt_chunks(fake_boundaries, words_per_chunk=3)
        with open(subs_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
            f.flush()
            os.fsync(f.fileno())
            
        print("[TTS] gTTS Fallback Success.")
        return audio_path, subs_path
    except Exception as e:
        raise Exception(f"Critical: Both TTS engines failed. {e}")

def generate_content():
    category, facts = get_ai_facts()
    intro, hook, outro = get_random_script_meta(category)
    
    # Budujemy skrypt z 5 faktami
    full_text = f"{intro}. Number 1: {facts[0]}. Number 2: {facts[1]}. {hook}. Number 3: {facts[2]}. Number 4: {facts[3]}. Number 5: {facts[4]}. {outro}"
    
    audio, subs = asyncio.run(process_tts(full_text))
    # #shorts w tytule to klucz do algorytmu
    title = f"5 Shocking Facts about {category}! #shorts #facts #ai"
    return {"script": full_text, "audio": audio, "subs": subs, "title": title}