import random
import hashlib
import os
import requests

# TWOJA RĘCZNA BAZA DANYCH (Fallback)
# Jeśli AI/API zawiedzie, bot wybierze jedną z tych kategorii.
THEMES = {
    "ANIMALS": [
        "A shrimp's heart is located in its head.",
        "An ostrich's eye is bigger than its brain.",
        "A snail can sleep for three years.",
        "Sloths can hold their breath longer than dolphins.",
        "Gorillas burp when they are happy.",
        "Koalas have fingerprints almost identical to humans.",
        "A group of flamingos is called a flamboyance."
    ],
    "SPACE": [
        "Space is completely silent because there is no air.",
        "Venus is the hottest planet in our solar system.",
        "One day on Venus is longer than a whole year on Earth.",
        "The footprints on the Moon will stay there for millions of years.",
        "There are more stars in the universe than grains of sand on Earth.",
        "Neutron stars can spin 600 times per second."
    ],
    "HUMAN BODY": [
        "Your heart beats about 100,000 times a day.",
        "Human teeth are as strong as shark teeth.",
        "Your nose can remember fifty thousand different scents.",
        "The small intestine is about four times longer than an adult tall.",
        "The only muscle that never gets tired is the heart."
    ]
}

INTRO_T = ["Did you know these 5 facts about {category}?", "5 mind-blowing facts about {category}!", "Check out these 5 facts about {category}!"]
HOOK_T = ["Comment '{category}' for more!", "Which of these is the craziest? Let us know!", "Can you believe this? Comment below!"]
OUTRO_T = ["Subscribe for more daily facts!", "Follow for your daily dose of {category}!", "Hit like for more {category} facts!"]

def get_ai_facts():
    """Próbuje pobrać fakty z AI (API), jeśli nie - bierze z THEMES."""
    history_file = "assets/used_ids.txt"
    if not os.path.exists(history_file):
        os.makedirs("assets", exist_ok=True)
        with open(history_file, 'w') as f: f.write("")
    
    with open(history_file, "r") as f:
        used = set(f.read().splitlines())

    facts = []
    category_name = "GENERAL KNOWLEDGE"

    # 1. PRÓBA POBRANIA Z "AI" (Darmowe API)
    try:
        print("[AI] Attempting to fetch live facts from API...")
        # Pobieramy 10 faktów, żeby mieć z czego wybierać po odfiltrowaniu użytych
        for _ in range(10):
            r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5)
            if r.status_code == 200:
                text = r.json()['text']
                h = hashlib.md5(text.encode()).hexdigest()
                if h not in used:
                    facts.append(text)
                    used.add(h)
                    with open(history_file, "a") as hf: hf.write(h + "\n")
            if len(facts) >= 5:
                break
        
        if len(facts) >= 5:
            print("[AI] Successfully fetched facts from online API.")
            return category_name, facts[:5]
            
    except Exception as e:
        print(f"[AI] API failed or timeout ({e}). Switching to manual themes...")

    # 2. FALLBACK: JEŚLI API NIE DAŁO 5 FAKTÓW, BIERZEMY Z TWOJEJ LISTY
    category_name = random.choice(list(THEMES.keys()))
    print(f"[FALLBACK] Selecting curated facts from category: {category_name}")
    
    all_category_facts = THEMES[category_name]
    # Filtrujemy nieużyte z tej kategorii
    available = [f for f in all_category_facts if hashlib.md5(f.encode()).hexdigest() not in used]
    
    if len(available) < 5:
        selected = random.sample(all_category_facts, 5) # Jeśli mało, bierzemy losowe (powtórki)
    else:
        selected = random.sample(available, 5)

    # Zapisz do historii
    with open(history_file, "a") as hf:
        for s in selected:
            hf.write(hashlib.md5(s.encode()).hexdigest() + "\n")

    return category_name, selected

def get_random_script_meta(cat):
    return random.choice(INTRO_T).format(category=cat), \
           random.choice(HOOK_T).format(category=cat), \
           random.choice(OUTRO_T).format(category=cat)