import random
import hashlib

FACTS_POOL = [
    "A day on Venus is longer than a year on Venus.",
    "Bananas are berries, but strawberries aren't.",
    "The first person convicted of speeding was going 8 mph.",
    # Add more facts here
]

def get_unique_fact():
    history_file = "assets/used_ids.txt"
    if not os.path.exists(history_file):
        open(history_file, 'w').close()
        
    with open(history_file, "r") as f:
        used_hashes = set(f.read().splitlines())
    
    random.shuffle(FACTS_POOL)
    for fact in FACTS_POOL:
        f_hash = hashlib.md5(fact.encode()).hexdigest()
        if f_hash not in used_hashes:
            with open(history_file, "a") as af:
                af.write(f_hash + "\n")
            return fact
            
    return random.choice(FACTS_POOL) # Fallback if pool exhausted