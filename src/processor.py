import random
import asyncio
import edge_tts
from utils import get_unique_fact

# Manual SRT formatter to avoid library attribute errors
def format_timestamp(milliseconds):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def create_srt(word_boundaries):
    srt_content = ""
    for i, boundary in enumerate(word_boundaries):
        start = format_timestamp(boundary['start'] / 10000) # Convert to ms
        # End time is either next word start or current + 500ms
        if i < len(word_boundaries) - 1:
            end = format_timestamp(word_boundaries[i+1]['start'] / 10000)
        else:
            end = format_timestamp((boundary['start'] / 10000) + 500)
        
        srt_content += f"{i+1}\n{start} --> {end}\n{boundary['text']}\n\n"
    return srt_content

async def process_tts(text, voice):
    audio_path = "output.mp3"
    subs_path = "subs.srt"
    
    communicate = edge_tts.Communicate(text, voice)
    word_boundaries = []
    
    # Save audio and collect word boundaries for subtitles
    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Offset and duration are in 100-nanosecond units
                word_boundaries.append({
                    "start": chunk["offset"],
                    "text": chunk["text"]
                })
    
    # Generate SRT content manually
    srt_data = create_srt(word_boundaries)
    with open(subs_path, "w", encoding="utf-8") as f:
        f.write(srt_data)
    
    return audio_path, subs_path

def generate_content():
    fact = get_unique_fact()
    voices = [
        "en-US-GuyNeural", 
        "en-GB-GeorgeNeural", 
        "en-US-ChristopherNeural", 
        "en-GB-RyanNeural"
    ]
    
    # Randomly select a voice
    voice = random.choice(voices)
    script = f"Did you know? {fact} Like and follow for more!"
    
    # Run async TTS process
    audio, subs = asyncio.run(process_tts(script, voice))
    
    return {
        "script": script,
        "audio": audio,
        "subs": subs,
        "title": f"Mind-blowing Fact! #shorts #facts"
    }