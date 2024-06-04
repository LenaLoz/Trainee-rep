import Pokedex


def main():
    print('Welcome to the Pokédex!')

    while True:
        user_input = input('Enter a command: ').strip().lower()

        if user_input == "load":
            data = Pokedex.load()
            print(f'Loaded data: {data}')

        elif user_input == "search":
            search_pokemon()

        elif user_input == "add":
            add_pokemon()

        elif user_input == "save":
            Pokedex.save_data()

        elif user_input == "remove":
            remove_pokemon()

        elif user_input == "filter":
            filter_pokemon()

        elif user_input == "top_matches":
            top_matches()

        elif user_input == "exit":
            print("Goodbye!")
            break

        else:
            print("Unknown command. Please try again.")


def search_pokemon():
    while True:
        try:
            name_pokemon = input('Which pokemon? ').strip()
            true_name = Pokedex.search(name_pokemon)
            print(true_name)
            break
        except Exception as e:
            print(e)


def top_matches():
    while True:
        try:
            name_pokemon = input('Which letters should describe top matches? ').strip()
            top_match = Pokedex.top_matches(name_pokemon)
            if top_match:
                top_match2= [x.matched for x in top_match[0]]
                print(top_match2)
            else:
                print(f'No matches found for "{name_pokemon}".')
            break
        except Exception as e:
            print(e)


def add_pokemon():
    while True:
        try:
            name_pokemon = input('Which pokemon should be added? ').strip()
            Pokedex.add(name_pokemon)
            break
        except Exception as e:
            print(e)


def remove_pokemon():
    while True:
        try:
            name_pokemon = input('Which pokemon? ').strip()
            Pokedex.remove(name_pokemon)
            break
        except Exception as e:
            print(e)


def filter_pokemon():
    valid_attributes = ["type", "abilities", "moves", "stats"]
    valid_stats_attributes = ["HP", "Attack", "Defense"]

    while True:
        try:
            attr_name = input('What parameter do you want to find a pokémon by? ').strip()
            if attr_name not in valid_attributes:
                raise ValueError(
                    f'There is no attribute "{attr_name}" for filtering. Valid attributes are: {valid_attributes}')
            break
        except ValueError as ve:
            print(ve)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    while True:
        try:
            if attr_name == "stats":
                while True:
                    try:
                        attr_value1 = input('Which attribute? ').strip()
                        if attr_value1 not in valid_stats_attributes:
                            raise ValueError(
                                f'There is no attribute "{attr_value1}" for filtering. Valid attributes are: {valid_stats_attributes}')
                        break
                    except ValueError as ve:
                        print(ve)

                while True:
                    try:
                        attr_value2 = int(input('Which value? ').strip())
                        break
                    except ValueError:
                        print('The value for stats must be an integer. Please try again.')

                names = Pokedex.find_pokemon(attr_name, attr_value1, attr_value2)
            else:
                while True:
                    try:
                        attr_value1 = input('Which value? ').strip()
                        if not (attr_value1[0].isupper() and attr_value1[1:].islower()):
                            raise ValueError(
                                f'The attribute value "{attr_value1}" must start with a capital letter followed by lowercase letters.')
                        break
                    except ValueError as ve:
                        print(ve)

                names = Pokedex.find_pokemon(attr_name, attr_value1)

            if not names:
                print(f'There is no Pokemon by "{attr_name}" in data')
            else:
                print(f'Pokémon found: {names}')
            break
        except ValueError as e:
            print(e)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()


