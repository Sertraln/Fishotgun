import random
from shared.registry import fish_list, Rarity

def generate_fishing_pool() -> list[int]:
    abondants = []
    discrets = []
    insaisissables = []

    for idx, data in enumerate(fish_list):
        rarity_name = data.rarity.name if hasattr(data.rarity, 'name') else data.rarity
        
        if rarity_name == "Abondants" or data.rarity == Rarity.ABONDANTS:
            abondants.append(idx)
        elif rarity_name == "Discrets" or data.rarity == Rarity.DISCRETS:
            discrets.append(idx)
        elif rarity_name == "Insaississables" or data.rarity == Rarity.INSAISISSABLES:
            insaisissables.append(idx)

    if not abondants: abondants = [0]
    if not discrets: discrets = abondants
    if not insaisissables: insaisissables = discrets

    chosen_ids = []
    for _ in range(4):
        rand = random.random()
        if rand < 0.60:
            chosen_ids.append(random.choice(abondants))
        elif rand < 0.90:
            chosen_ids.append(random.choice(discrets))
        else:
            chosen_ids.append(random.choice(insaisissables))
            
    return chosen_ids