import random
import hashlib
import os
import requests

CATEGORIES = ["science", "history", "space", "animals", "geography", "nature", "technology"]

# Pula rezerwowa na wypadek problemów z API
BACKUP_FACTS = [
    "A single bolt of lightning contains enough energy to toast 100,000 slices of bread.",
    "The heart of a shrimp is located in its head.",
    "Human teeth are the only part of the body that cannot heal themselves.",
    "Honey never spoils; archaeologists found 3000-year-old honey that is still edible.",
    "A Venus Flytrap can actually eat small frogs and even birds.",
    "Bananas are berries, but strawberries are not.",
    "Sharks have been around longer than trees.",
    "A day on Venus is longer than a year on Venus.",
    "The static on your TV is actually radiation from the Big Bang.",
    "The human brain has the same consistency as tofu."
]

INTRO_T = ["Did you know about these 5 facts about {category}?", "Number 5 will shock you! 5 facts about {category}.", "I bet you didn't know these 5 {category} facts."]
HOOK_T = ["Comment 'FACT' if you love {category}!", "Which of these shocked you the most? Tell us!", "Wait! Comment which topic we should cover next!"]
OUTRO_T = ["Subscribe for more daily facts!", "Follow for your daily dose of {category}!", "Hit that like button and subscribe!"]

def get_ai_facts():
    category = random.choice(CATEGORIES)
    facts = []
    history_file = "assets/used_ids.txt"
    
    if not os.path.exists(history_file):
        os.makedirs("assets", exist_ok=True)
        with open(history_file, 'w') as f: f.write("")
    
    with open(history_file, "r") as f:
        used = set(f.read().splitlines())

    # Próba pobrania z API
    try:
        for _ in range(15):
            r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5)
            if r.status_code == 200:
                text = r.json()['text']
                h = hashlib.md5(text.encode()).hexdigest()
                if h not in used:
                    facts.append(text)
                    used.add(h)
                    with open(history_file, "a") as hf: hf.write(h + "\n")
            if len(facts) >= 5: break
    except:
        print("[UTILS] API unreachable, using backup pool.")

    # Uzupelnij liste, jesli API zwrocilo za malo faktow
    while len(facts) < 5:
        backup = random.choice(BACKUP_FACTS)
        h = hashlib.md5(backup.encode()).hexdigest()
        if h not in used:
            facts.append(backup)
            used.add(h)
            with open(history_file, "a") as hf: hf.write(h + "\n")
        elif len(used) >= len(BACKUP_FACTS): # Jesli wszystko zuzyte
            facts.append(backup)
            if len(facts) >= 5: break

    return category.upper(), facts[:5]

def get_random_script_meta(cat):
    return random.choice(INTRO_T).format(category=cat), \
           random.choice(HOOK_T).format(category=cat), \
           random.choice(OUTRO_T).format(category=cat)