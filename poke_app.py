"""Import das bibliotecas necessárias"""
import os
import json
import requests
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Requisição HTTP para obter o JSON da URL fornecida
def fetch_json(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

# Requisição da URL de habilidade e pokemon
def main():
    import sys

    # Allow pokemon name via CLI arg or interactive input
    if len(sys.argv) > 1:
        pokemon_name = sys.argv[1].strip().lower()
    else:
        pokemon_name = input("Nome do Pokémon (ex: ditto): ").strip().lower()

    if not pokemon_name:
        print("Nenhum nome de Pokémon fornecido. Encerrando.")
        return

    pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    ability_url = "https://pokeapi.co/api/v2/ability/battle-armor"

    try:
        pokemon = fetch_json(pokemon_url)
    except Exception as e:
        print(f"Failed to fetch {pokemon_name}: {e}")
        return

    abilities = [a["ability"]["name"] for a in pokemon.get("abilities", [])]
    print(f"Abilities of {pokemon_name.capitalize()}:")
    for a in abilities:
        print("-", a)

    try:
        ability = fetch_json(ability_url)
    except Exception as e:
        print(f"Failed to fetch ability: {e}")
        return

    short_effect = None
    for entry in ability.get("effect_entries", []):
        if entry.get("language", {}).get("name") == "en":
            short_effect = entry.get("short_effect") or entry.get("effect")
            break

    print("\nshort_effect (en) for 'battle-armor':")
    print(short_effect)

    pokemons_with_ability = [p["pokemon"]["name"] for p in ability.get("pokemon", [])]
    print(f"\nPokémons with 'battle-armor' ({len(pokemons_with_ability)}):")
    for p in pokemons_with_ability:
        print("-", p)

    # Save JSON file
    result = {
        pokemon_name: {"url": pokemon_url, "abilities": abilities},
        "battle_armor": {
            "url": ability_url,
            "short_effect_en": short_effect,
            "pokemons": pokemons_with_ability,
        },
    }

    out_path = os.path.join(os.path.dirname(__file__), "poke_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nSaved fetched data to {out_path}")

    # Insert into MongoDB
    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Trigger server selection
        client.server_info()
    except PyMongoError as e:
        print(f"Could not connect to MongoDB at {uri}: {e}")
        return

    db = client["pokeapi"]
    col = db["abilities"]

    try:
        col.update_one({"_id": pokemon_name}, {"$set": {"abilities": abilities, "source": pokemon_url}}, upsert=True)
        col.update_one(
            {"_id": "battle-armor"},
            {"$set": {"short_effect_en": short_effect, "pokemons": pokemons_with_ability, "source": ability_url}},
            upsert=True,
        )
        print(f"Inserted/updated documents in MongoDB database 'pokeapi', collection 'abilities'.")
    except PyMongoError as e:
        print(f"MongoDB write failed: {e}")


if __name__ == "__main__":
    main()
