import re

A = "Ash caught Pikachu and then encountered Bulbasaur and Charmander. Misty has a Starmie and Psyduck, while Brock's favorite is Onix."
regs = r'\b(?!Ash|Misty|Brock\b)[A-Z][a-z]+\b'
pokemon_names = re.findall(regs, A)
print(pokemon_names)

B = ['T001', 'T123', 'T0456', 'A123', 'T12', 'T999']
regs = r'\bT[0-9]{3}\b'
reg = re.findall(regs, str(B))
print(reg)

C = 'Pikachu used Thunderbolt, Charmander used Flamethrower, and Bulbasaur used Vine Whip. Another Pikachu used Thunderthrow.'
regs = r'\b(Thunder|Flame)(bolt|throw)'
reg = re.findall(regs, C)
moves = [f"{x[0]}{x[1]}" for x in reg]
print(moves)

D = 'Pikachu: HP 35, Attack 55; Bulbasaur: HP 45, Attack 49; Charmander: HP 39, Attack 52.'
regs = re.findall(r'([a-zA-Z]+): HP (\d+), Attack (\d+)', D)
pokemon_dict = {name: {'HP': int(hp), 'Attack': int(attack)} for name, hp, attack in regs}
print(pokemon_dict)

E = "Hitmonchan used Mega Punch, Hitmonlee used High Jump Kick, Machamp used Dynamic Punch, and Primeape used Karate Chop."
regs = r'\b(\w+ (Punch|Kick))\b'
rock = lambda x: f"[{x.group(0)}]"
new_regs = re.sub(regs, rock, E)
print(new_regs)

F = 'Name: Pikachu, Type: Electric, Description: Pikachu is a small, yellow mouse-like Pokemon with electrical abilities. Name: Bulbasaur, Type: Grass/Poison, Description: Bulbasaur is a small, quadruped Pokemon with blue-green skin and darker blue-green spots.[Name: Charmander, Type: Fire, Description: Charmander is a bipedal, reptilian Pokemon with a primarily orange body and a tail flame.'
reg = r'Name: ([^,]+), Type: ([^,]+), Description: ([^\.]+)\.'
matches = re.findall(reg, F)
pokemon_data = {}

for match in matches:
    name, poke_type, description = match
    if poke_type not in pokemon_data:
        pokemon_data[poke_type] = []
    pokemon_data[poke_type].append({'name': name, 'description': description.strip()})
print(pokemon_data)