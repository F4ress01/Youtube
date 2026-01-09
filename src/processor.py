import random
import asyncio
import edge_tts
from edge_tts import SubMaker
from utils import get_unique_fact

async def amain(script, voice, rate) -> tuple:
    communicate = edge_tts.Communicate(script, voice, rate=rate)
    submaker = edge_tts.SubMaker()
    audio_path = "output.mp3"
    subs_path = "subs.srt"
    
    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
    
    # Save as SRT for FFmpeg burning
    with open(subs_path, "w", encoding="utf-8") as f:
        f.write(submaker.generate_subs())
        
    return audio_path, subs_path

def generate_content():
    fact = get_unique_fact()
    intros = ["Fact check:", "Did you know?", "The dark truth:", "Mind-blowing:"]
    outros = ["Subscribe for more.", "Follow for daily facts.", "Believe it?"]
    
    script = f"{random.choice(intros)} {fact} {random.choice(outros)}"
    
    # Voice selection including requested Guy and George
    voices = [
        "en-US-ChristopherNeural", 
        "en-US-GuyNeural", 
        "en-GB-GeorgeNeural", 
        "en-GB-RyanNeural"
    ]
    
    audio_path, subs_path = asyncio.run(amain(
        script, 
        random.choice(voices), 
        f"{random.randint(-5, 5)}%"
    ))
    
    return {
        "script": script,
        "audio": audio_path,
        "subs": subs_path,
        "title": f"Amazing Fact: {fact[:50]}... #shorts"
    }