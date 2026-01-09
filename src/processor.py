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
        start = format_timestamp(boundary['start'] // 10000) # Convert 100ns to ms
        if i < len(word_boundaries) - 1:
            end = format_timestamp(word_boundaries[i+1]['start'] // 10000)
        else:
            end = format_timestamp((boundary['start'] // 10000) + 500)
        
        srt_content += f"{i+1}\n{start} --> {end}\n{boundary['text']}\n\n"
    return srt_content

async def process_tts(text, voice, retries=3):
    audio_path = "output.mp3"
    subs_path = "subs.srt"
    
    if not text.strip():
        raise ValueError("The script text is empty!")

    print(f"[TTS] Using voice: {voice}")
    print(f"[TTS] Text length: {len(text)} characters")

    for attempt in range(retries):
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
            
            if not audio_received:
                raise Exception("API returned success but no audio data was found.")
                
            srt_data = create_srt(word_boundaries)
            with open(subs_path, "w", encoding="utf-8") as f:
                f.write(srt_data)
            
            print("[TTS] Audio and subtitles generated successfully.")
            return audio_path, subs_path

        except Exception as e:
            print(f"[TTS] Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2) # Wait before retry
            else:
                raise e

def generate_content():
    fact = get_unique_fact()
    
    # Validation: Ensure fact is not None or empty
    if not fact:
        fact = "The human brain has enough memory to hold three million hours of television."
        print("[WARNING] Fact pool returned empty. Using fallback fact.")

    voices = [
        "en-US-GuyNeural", 
        "en-GB-GeorgeNeural", 
        "en-US-ChristopherNeural", 
        "en-GB-RyanNeural"
    ]
    
    voice = random.choice(voices)
    script = f"Did you know? {fact} Subscribe for more!"
    
    # Run async process
    audio, subs = asyncio.run(process_tts(script, voice))
    
    return {
        "script": script,
        "audio": audio,
        "subs": subs,
        "title": f"Amazing Fact! #shorts #facts"
    }