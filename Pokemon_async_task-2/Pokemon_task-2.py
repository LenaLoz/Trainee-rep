import asyncio
import concurrent.futures
import aiohttp
import random
from bs4 import BeautifulSoup
from tabulate import tabulate

API_KEY = 'xxx'


class Pokemon:
    def __init__(self, name, type1, type2=None):
        self.name = name
        self.type1 = type1
        self.type2 = type2


def get_random_pokemons(pokemons, n=int(input('How many Pokemons do you want to know? '))):
    if n < 0 or n > len(pokemons):
        raise ValueError("Invalid number of Pokemons requested")
    return random.sample(pokemons, n)


def print_pokemon_names(pokemons):
    for pokemon in pokemons:
        print(pokemon.name)


async def pokemon_from_table(session):
    url = 'https://pokemon.fandom.com/wiki/List_of_Generation_I_Pok%C3%A9mon'
    try:
        async with session.get(url) as response:
            text = await response.text()
            return text
    except Exception as e:
        print(repr(e))
        return None


def parse_pokemon_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})

    pokemons = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) > 3:
            name = cols[2].text.strip()
            type1 = cols[3].text.strip()
            type2 = cols[4].text.strip() if len(cols) > 4 else None
            pokemons.append(Pokemon(name, type1, type2))

    return pokemons


async def fetch_pokemon_stats(name):
    url = f'https://pokeapi.co/api/v2/pokemon/{name.lower()}'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                if data:
                    stats = {
                        'HP': None,
                        'Attack': None,
                        'Defense': None
                    }

                    for stat in data['stats']:
                        stat_name = stat['stat']['name']
                        base_stat = stat['base_stat']
                        if stat_name == 'hp':
                            stats['HP'] = base_stat
                        elif stat_name == 'attack':
                            stats['Attack'] = base_stat
                        elif stat_name == 'defense':
                            stats['Defense'] = base_stat

                    info = [
                        ["Name", name],
                        ["HP", stats['HP']],
                        ["Attack", stats['Attack']],
                        ["Defense", stats['Defense']]
                    ]

                    return info
                else:
                    print("No data available.")
                    return None

        except aiohttp.ClientError as e:
            print(f"Error occurred while fetching data: {e}")
            return None


async def interesting_facts(random_pokemons):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    i = 1
    facts_request_content = "Tell me ONE interesting fact about each of the following Pokémon, but don't mention the pokémon's name twice in a sentence"
    facts_request_content += "\n".join([f"{i + 1} {pokemon.name}" for i, pokemon in enumerate(random_pokemons)])

    # Debugging print
    # print("Request content:", facts_request_content)

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": facts_request_content}],
        "max_tokens": 1000,
        "temperature": 1
    }

    # Debugging print
    # print("Request data:", data)
    print("There is/are some interesting fact/s about:")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=data) as response:
                response.raise_for_status()
                response_data = await response.json()
                return response_data['choices'][0]['message']['content']
        except aiohttp.ClientResponseError as e:
            if e.status == 400:
                error_text = await response.text()
                print(f"Client error: {e}, details: {error_text}")
            elif e.status == 429:
                print("Rate limit exceeded.")
            else:
                print(f"Client error: {e}")
        except Exception as e:
            print(f"Error: {e}")


def print_table(data):
    if not data:
        print("No data to display.")
        return

    headers = ["Name", "HP", "Attack", "Defense"]
    print(tabulate(data, headers=headers, tablefmt="grid"))


async def main():
    try:
        async with aiohttp.ClientSession() as session:
            html = await pokemon_from_table(session)
            if html is None:
                raise Exception("Failed to fetch HTML")
            pokemons = parse_pokemon_list(html)
            try:
                random_pokemons_lst = get_random_pokemons(pokemons)
            except ValueError as e:
                print(e)
                return []

            print_pokemon_names(random_pokemons_lst)

            return random_pokemons_lst
    except Exception as e:
        print(repr(e))
        return []


def run_main():
    return asyncio.run(main())


def run_fetch_pokemon_stats(pokemon_name):
    return asyncio.run(fetch_pokemon_stats(pokemon_name))


def run_interesting_facts(random_pokemons):
    return asyncio.run(interesting_facts(random_pokemons))


if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_main = executor.submit(run_main)
        try:
            random_pokemons = future_main.result()
        except Exception as e:
            print(repr(e))
            random_pokemons = []

        if not random_pokemons:
            print("No valid Pokémon data. Exiting...")
            exit()

        futures = []
        for pokemon in random_pokemons:
            futures.append(executor.submit(run_fetch_pokemon_stats, pokemon.name))

        concurrent.futures.wait(futures)

        stats_data = []
        for future in futures:
            try:
                stats = future.result()
                if stats:
                    stats_data.append([stats[0][1], stats[1][1], stats[2][1], stats[3][1]])
            except Exception as e:
                print(repr(e))

        print_table(stats_data)

        future_facts = executor.submit(run_interesting_facts, random_pokemons)
        try:
            facts = future_facts.result()
            print(facts)
        except Exception as e:
            print(repr(e))
