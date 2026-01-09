import random
import hashlib
import os
import requests

CATEGORIES = ["science", "history", "space", "animals", "geography", "technology", "nature"]

INTRO_TEMPLATES = [
    "Did you know about these 5 facts about {category}?",
    "Prepare to be amazed by these 5 {category} facts!",
    "Stop scrolling! Here are 5 insane facts about {category}."
]

ENGAGEMENT_HOOKS = [
    "Comment 'FACT' if you love {category}!",
    "I bet you didn't know the last one! Tell us your favorite in the comments.",
    "Quick challenge: Type your favorite {category} fact below!"
]

OUTRO_TEMPLATES = [
    "Subscribe for more daily {category} facts!",
    "Follow us to become the smartest person in the room!",
    "Don't miss out! Subscribe now."
]

def get_ai_facts():
    category = random.choice(CATEGORIES)
    facts = []
    try:
        for _ in range(12):
            r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
            if r.status_code == 200: facts.append(r.json()['text'])
            if len(facts) >= 5: break
    except:
        facts = [f"Amazing {category} fact {i}" for i in range(1, 6)]

    history_file = "assets/used_ids.txt"
    if not os.path.exists(history_file):
        os.makedirs("assets", exist_ok=True)
        with open(history_file, 'w') as f: f.write("")

    with open(history_file, "r") as f:
        used = set(f.read().splitlines())

    final_facts = []
    for f in facts:
        f_hash = hashlib.md5(f.encode()).hexdigest()
        if f_hash not in used:
            final_facts.append(f)
            with open(history_file, "a") as h: h.write(f_hash + "\n")
        if len(final_facts) >= 5: break
    return category.upper(), final_facts[:5]

def get_random_script_meta(category):
    return random.choice(INTRO_TEMPLATES).format(category=category), \
           random.choice(ENGAGEMENT_HOOKS).format(category=category), \
           random.choice(OUTRO_TEMPLATES).format(category=category)