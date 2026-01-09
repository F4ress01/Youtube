import random
import hashlib
import os
import requests

THEMES = {
    "ANIMALS": ["A shrimp's heart is in its head.", "Snails can sleep for 3 years.", "Sloths hold breath longer than dolphins.", "Gorillas burp when happy.", "A group of flamingos is a flamboyance."],
    "SPACE": ["Space is silent.", "Venus is hotter than Mercury.", "Neutron stars spin 600 times per second.", "One day on Venus is longer than a year.", "Moon footprints last millions of years."],
}

def get_ai_facts():
    history_file = "assets/used_ids.txt"
    if not os.path.exists(history_file):
        os.makedirs("assets", exist_ok=True)
        with open(history_file, 'w') as f: f.write("")
    with open(history_file, "r") as f: used = set(f.read().splitlines())

    facts, cat = [], "GENERAL"
    try:
        for _ in range(12):
            r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5)
            if r.status_code == 200:
                txt = r.json()['text']
                h = hashlib.md5(txt.encode()).hexdigest()
                if h not in used:
                    facts.append(txt); used.add(h)
                    with open(history_file, "a") as hf: hf.write(h + "\n")
            if len(facts) >= 5: break
    except: pass

    if len(facts) < 5:
        cat = random.choice(list(THEMES.keys()))
        avail = [f for f in THEMES[cat] if hashlib.md5(f.encode()).hexdigest() not in used]
        facts = random.sample(avail, 5) if len(avail) >= 5 else random.sample(THEMES[cat], 5)
    
    return cat, facts[:5]

def get_unique_metadata(cat):
    titles = [f"5 Amazing {cat} Facts!", f"Shocking {cat} Facts!", f"Did you know this about {cat}?"]
    tags = ["#shorts", "#facts", "#ai", "#knowledge", "#viral"]
    return random.choice(titles), " ".join(random.sample(tags, 4))