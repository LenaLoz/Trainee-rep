import json
from fuzzysearch import find_near_matches


def save(data, filename='data.json'):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        print('404: File not found')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def load(filename='data.json'):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print('404: File not found')
        return {}
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        return {}


def validate_name(name, entity='Pokemon'):
    if not (name[0].isupper() and name[1:].islower()):
        raise ValueError(f'The {entity} name "{name}" must start with a capital letter followed by lowercase letters.')


def validate_type(poke_type):
    if not (poke_type[0].isupper() and poke_type[1:].islower()):
        raise ValueError(
            f'The pokemon type "{poke_type}" must start with a capital letter followed by lowercase letters.')
    if ' ' in poke_type or not poke_type.isalpha():
        raise ValueError(f'The pokemon type must be one word consisting of only letters without spaces')


def validate_abilities(abilities_input):
    if ',' not in abilities_input or abilities_input.count(',') != 1:
        raise ValueError(f'The abilities should consist of exactly 2 items separated by a comma.')
    abilities = abilities_input.replace(', ', ',').split(',')
    if len(abilities) != 2 or any(not ability.isalpha() for ability in abilities):
        raise ValueError(f'The abilities should consist of 2 items and only contain letters')
    if any(not (ability[0].isupper() and ability[1:].islower()) for ability in abilities):
        raise ValueError(
            f'Each ability must start with a capital letter followed by lowercase letters and contain min 2 symbols')
    return abilities


def validate_stats(stats_input):
    stats_input = stats_input.replace(', ', ',').split(',')
    if len(stats_input) != 3:
        raise ValueError("Stats must be three comma-separated values.")
    if any(not stat.strip().isdigit() and not (stat.strip().startswith('-') and stat.strip()[1:].isdigit()) for stat in
           stats_input):
        raise ValueError("All stats must be integers.")
    if any(len(stat.strip().lstrip('-')) > 3 for stat in stats_input):
        raise ValueError("Each stat must be a maximum of 3 digits.")
    if any(int(stat.strip()) < 0 for stat in stats_input):
        raise ValueError("Each stat must be 0 or greater.")
    stats = {"HP": int(stats_input[0].strip()), "Attack": int(stats_input[1].strip()),
             "Defense": int(stats_input[2].strip())}
    return stats


def validate_moves(moves_input):
    moves = moves_input.split(',')
    if len(moves) > 4 or any(' ' in move or not move.isalpha() for move in moves):
        raise ValueError(f'Moves can consist of max 4 items separated by a comma and only contain letters')
    if any(not (move[0].isupper() and move[1:].islower()) for move in moves):
        raise ValueError(
            f'Each move must start with a capital letter followed by lowercase letters and contain min 2 symbols')
    if any(len(move) < 2 for move in moves):
        raise ValueError(f'Each move should contain min 2 letters')
    return moves


def add(name_pokemon):
    pokemon_data = load()
    validate_name(name_pokemon)

    if name_pokemon in pokemon_data:
        raise NameError(f'The Pokemon name "{name_pokemon}" should be unique')
    new_pokemon = None
    while True:
        try:
            while True:
                try:
                    poke_type = input("Enter Pokémon type: ").strip()
                    validate_type(poke_type)
                    break
                except ValueError as e:
                    print(e)
            while True:
                try:
                    abilities_input = input("Enter Pokémon abilities (comma-separated): ").strip()
                    abilities = validate_abilities(abilities_input)
                    break
                except ValueError as e:
                    print(e)

            while True:
                try:
                    stats_input = input("Enter Pokémon stats (HP, Attack, Defense) comma-separated: ").strip()
                    stats = validate_stats(stats_input.replace(', ', ','))
                    break
                except ValueError as e:
                    print(e)

            while True:
                try:
                    moves_input = input("Enter Pokémon moves (comma-separated): ").strip().replace(', ', ',')
                    moves = validate_moves(moves_input)
                    break
                except ValueError as e:
                    print(e)

            new_pokemon = {
                "type": poke_type,
                "abilities": abilities,
                "stats": stats,
                "moves": moves
            }
            break
        except Exception as e:
            print(e)
            continue

    if new_pokemon:
        pokemon_data[name_pokemon] = new_pokemon
        save(pokemon_data)
        print(f"{name_pokemon} added successfully.")


def remove(name_pokemon):
    pokemon_data = load()
    validate_name(name_pokemon)
    if not name_pokemon in pokemon_data:
        raise NameError(f'The Pokemon name "{name_pokemon}" does not exist')
    del pokemon_data[name_pokemon]
    save(pokemon_data)
    print(f'The Pokemon name "{name_pokemon}" was removed successfully')


# remove('mumu')
def search(name_pokemon: str):
    pokemon_data = load()
    name_pokemon = name_pokemon.strip()

    if len(name_pokemon) < 2:
        raise ValueError("The Pokemon name must contain at least two characters.")
    # Проверяем, что имя не пустое
    if not name_pokemon:
        raise ValueError("The Pokemon name cannot be empty.")
    matches = {name: details for name, details in pokemon_data.items() if
               name.lower().startswith(name_pokemon[:2].lower())}

    if matches:
        return matches
    else:
        raise ValueError(f'The Pokemon name containing "{name_pokemon}" does not exist')


def find_pokemon(attr_name, attr_value1, attr_value2=None):
    pokemon_data = load()
    names = []
    valid_attributes = ["type", "abilities", "moves", "stats"]

    if attr_name not in valid_attributes:
        raise ValueError(f'Invalid attribute: {attr_name}. Valid attributes are: {valid_attributes}')

    try:
        for pokemon_name, attrs in pokemon_data.items():
            if attr_name == "type":
                if attrs["type"] == attr_value1:
                    names.append(pokemon_name)
            elif attr_name in ["abilities", "moves"]:
                if attr_value1 in attrs[attr_name]:
                    names.append(pokemon_name)
            elif attr_name == "stats":
                if attrs["stats"][attr_value1] == attr_value2:
                    names.append(pokemon_name)
        return names
    except Exception:
        raise ValueError(f'There is no Pokemon by "{attr_name}" in datas')


def top_matches(name_pokemon):
    pokemon_data = load()
    matched_names = []

    try:
        matches = find_near_matches(subsequence=name_pokemon, sequence=str(pokemon_data.keys()), max_l_dist=2,
                                    max_deletions=2, max_insertions=2, max_substitutions=2)
        if matches:
            matched_names.append(matches)

        if not matched_names:
            raise ValueError(f'There are no matches for {name_pokemon}')

        return matched_names
    except Exception:
        raise ValueError(f'No matches was found(')


def save_data():
    pokemon_data = load()
    save(pokemon_data)
    print("Data saved successfully")