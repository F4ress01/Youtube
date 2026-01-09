import random
import hashlib
import os
import requests

CATEGORIES = ["science", "history", "space", "animals", "geography", "nature"]
INTRO_T = ["Did you know about these 5 facts about {category}?", "Stop scrolling! 5 insane {category} facts!"]
HOOK_T = ["Comment 'FACT' if you love {category}!", "Which {category} fact shocked you? Tell us!"]
OUTRO_T = ["Subscribe for more!", "Follow for daily dose of {category}!"]

def get_ai_facts():
    cat = random.choice(CATEGORIES)
    facts = []
    try:
        for _ in range(12):
            r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
            if r.status_code == 200: facts.append(r.json()['text'])
            if len(facts) >= 5: break
    except: facts = [f"Amazing {cat} fact {i}" for i in range(1, 6)]

    history_file = "assets/used_ids.txt"
    if not os.path.exists(history_file):
        os.makedirs("assets", exist_ok=True)
        with open(history_file, 'w') as f: f.write("")
    
    with open(history_file, "r") as f:
        used = set(f.read().splitlines())
    
    final = []
    for f in facts:
        h = hashlib.md5(f.encode()).hexdigest()
        if h not in used:
            final.append(f)
            with open(history_file, "a") as hf: hf.write(h + "\n")
        if len(final) >= 5: break
    return cat.upper(), final[:5]

def get_random_script_meta(cat):
    return random.choice(INTRO_T).format(category=cat), \
           random.choice(HOOK_T).format(category=cat), \
           random.choice(OUTRO_T).format(category=cat)