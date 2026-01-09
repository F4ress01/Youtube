import random
import hashlib
import os
import requests

THEMES = {
    "ANIMALS": ["A shrimp's heart is in its head.", "Snails can sleep for 3 years.", "Sloths hold breath longer than dolphins."],
    "SPACE": ["Space is silent.", "Venus is hotter than Mercury.", "Neutron stars spin 600 times per second."],
    "HUMAN": ["Heart beats 100k times a day.", "Nose remembers 50k scents.", "Small intestine is 4x your height."]
}

# Pula hashtagów do losowania
TAGS_POOL = ["#shorts", "#facts", "#ai", "#knowledge", "#mindblowing", "#dailyfacts", "#education", "#viral"]

def get_ai_facts():
    history_file = "assets/used_ids.txt"
    if not os.path.exists(history_file):
        os.makedirs("assets", exist_ok=True)
        with open(history_file, 'w') as f: f.write("")
    
    with open(history_file, "r") as f:
        used = set(f.read().splitlines())

    facts = []
    category = "GENERAL"

    try:
        # Próba pobrania 10 faktów z API
        for _ in range(10):
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
        pass

    if len(facts) < 5:
        category = random.choice(list(THEMES.keys()))
        all_theme_facts = THEMES[category]
        available = [f for f in all_theme_facts if hashlib.md5(f.encode()).hexdigest() not in used]
        facts = random.sample(available, 5) if len(available) >= 5 else random.sample(all_theme_facts, 5)

    return category, facts[:5]

def get_unique_metadata(category):
    """Generuje unikalny tytuł i hashtagi dla każdego filmu"""
    intros = ["Mind-blowing", "Shocking", "Unbelievable", "Hidden", "Crazy"]
    titles = [
        f"{random.choice(intros)} Facts about {category}!",
        f"5 {category} Facts You Didn't Know!",
        f"Wait until you hear these {category} facts!"
    ]
    selected_tags = random.sample(TAGS_POOL, 4)
    return random.choice(titles), " ".join(selected_tags)