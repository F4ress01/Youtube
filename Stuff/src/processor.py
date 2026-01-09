import random
import asyncio
import edge_tts
from edge_tts import SubMaker
from utils import get_unique_fact

async def generate_assets(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()
    audio_path = "output.mp3"
    
    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
                
    with open("subs.srt", "w", encoding="utf-8") as f:
        f.write(submaker.generate_subs())
    return audio_path, "subs.srt"

def generate_content():
    fact = get_unique_fact()
    # Adding requested voices
    voices = ["en-US-GuyNeural", "en-GB-GeorgeNeural", "en-US-ChristopherNeural"]
    voice = random.choice(voices)
    
    script = f"Did you know? {fact} Like and follow for more!"
    audio, subs = asyncio.run(generate_assets(script, voice))
    
    return {
        "script": script,
        "audio": audio,
        "subs": subs,
        "title": f"Mind-Blowing Fact! #shorts #facts"
    }