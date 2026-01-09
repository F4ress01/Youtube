import random
import asyncio
import edge_tts
import os
from utils import get_unique_fact

def format_timestamp(milliseconds):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def create_srt(word_boundaries):
    srt_content = ""
    for i, boundary in enumerate(word_boundaries):
        start = format_timestamp(boundary['start'] // 10000)
        if i < len(word_boundaries) - 1:
            end = format_timestamp(word_boundaries[i+1]['start'] // 10000)
        else:
            end = format_timestamp((boundary['start'] // 10000) + 500)
        srt_content += f"{i+1}\n{start} --> {end}\n{boundary['text']}\n\n"
    return srt_content

async def process_tts(text, preferred_voice):
    audio_path = "output.mp3"
    subs_path = "subs.srt"
    
    # Lista głosów do wypróbowania w razie błędu
    fallback_voices = [
        preferred_voice,
        "en-US-AriaNeural",
        "en-US-GuyNeural",
        "en-GB-SoniaNeural",
        "en-US-ChristopherNeural"
    ]

    for voice in fallback_voices:
        print(f"[TTS] Attempting with voice: {voice}")
        try:
            communicate = edge_tts.Communicate(text, voice)
            word_boundaries = []
            audio_received = False
            
            with open(audio_path, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                        audio_received = True
                    elif chunk["type"] == "WordBoundary":
                        word_boundaries.append({
                            "start": chunk["offset"],
                            "text": chunk["text"]
                        })
            
            if audio_received and word_boundaries:
                srt_data = create_srt(word_boundaries)
                with open(subs_path, "w", encoding="utf-8") as f:
                    f.write(srt_data)
                print(f"[TTS] Success with voice: {voice}")
                return audio_path, subs_path
            
        except Exception as e:
            print(f"[TTS] Voice {voice} failed: {e}")
            continue # Przejdź do następnego głosu

    raise Exception("All TTS voices failed to receive audio.")

def generate_content():
    fact = get_unique_fact()
    if not fact:
        fact = "The static on your TV is actually leftover radiation from the Big Bang."

    # Start with a random voice from your preferred list
    initial_voice = random.choice(["en-US-GuyNeural", "en-GB-GeorgeNeural"])
    script = f"Did you know? {fact} Like and follow for more!"
    
    audio, subs = asyncio.run(process_tts(script, initial_voice))
    
    return {
        "script": script,
        "audio": audio,
        "subs": subs,
        "title": f"Mind-Blowing Fact! #shorts #facts"
    }