//Import das blibliotecas necessárias
import os
import json
import requests
from pymongo import MongoClient
from pymongo.errors import PyMongoError

//Requisição HTTP para obter o JSON da URL fornecida
def fetch_json(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main():
    ditto_url = "https://pokeapi.co/api/v2/pokemon/ditto"
    ability_url = "https://pokeapi.co/api/v2/ability/battle-armor"

    try:
        ditto = fetch_json(ditto_url)
    except Exception as e:
        print(f"Failed to fetch Ditto: {e}")
        return

    abilities = [a["ability"]["name"] for a in ditto.get("abilities", [])]
    print("Abilities of Ditto:")
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
        "ditto": {"url": ditto_url, "abilities": abilities},
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
        col.update_one({"_id": "ditto"}, {"$set": {"abilities": abilities, "source": ditto_url}}, upsert=True)
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
