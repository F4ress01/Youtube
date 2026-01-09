import random
import hashlib
import os

FACTS_POOL = [
    "A single bolt of lightning contains enough energy to toast 100,000 slices of bread.",
    "The heart of a shrimp is located in its head.",
    "Human teeth are the only part of the body that cannot heal themselves."
    # Add more facts here...
]

def get_unique_fact():
    history_file = "assets/used_ids.txt"
    if not os.path.exists(history_file):
        open(history_file, 'w').close()
        
    with open(history_file, "r") as f:
        used = set(f.read().splitlines())
    
    available = [f for f in FACTS_POOL if hashlib.md5(f.encode()).hexdigest() not in used]
    
    if not available:
        return random.choice(FACTS_POOL)
        
    chosen = random.choice(available)
    with open(history_file, "a") as f:
        f.write(hashlib.md5(chosen.encode()).hexdigest() + "\n")
    return chosen