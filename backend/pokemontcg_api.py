from pokemontcgsdk import RestClient
import os
import pandas as pd
import requests
import yaml
import httpx
import certifi


script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "..", "config.yaml")
with open(config_path, 'r') as y:
    config = yaml.safe_load(y)
API_KEY = config["api_key"]
BASE_URL = "https://api.pokemontcg.io/v2/cards"
RestClient.configure(API_KEY)
headers = {
    "X-Api-Key": API_KEY
}


def get_cards(*pokemon: str | int) -> pd.DataFrame:
    """
    Get a DataFrame including a list of all the given Pokemon.
    :param pokemon: one or more names or pokedex numbers of  desired Pokemon to list.
    :return: DataFrame including the desired List.
    """
    strPokes = []
    intPokes = []
    for poke in pokemon:
        (strPokes if isinstance(poke, str) else intPokes).append(str(poke))
    parts = []
    if strPokes:
        parts.append("name:" + " OR name:".join(strPokes))
    if intPokes:
        parts.append("(nationalPokedexNumbers:" + " OR nationalPokedexNumbers:".join(map(str, intPokes)) + ")")

    q = " OR ".join(parts)

    params = {
        "q": q,
        "orderBy": "-set.releaseDate"
    }

    try:
        print("Requesting:", BASE_URL, params)
        with httpx.Client(timeout=1000, verify=certifi.where()) as client:
            response = client.get(BASE_URL, headers=headers, params=params)
            print("Status:", response.status_code)
            print("URL:", response.url)
            print("Antwort:", response.text[:200])
        print("Status Code:", response.status_code)
        print("URL:", response.url)
        print("Response headers:", response.headers)
        if response.status_code == 200:
            try:
                print("Attempting to parse JSON...")
                data = response.json()
                print("JSON parsed successfully")
            except ValueError:
                print("Fehler: Antwort ist kein gültiges JSON.")
                return pd.DataFrame()
            cards = data.get("data", [])
            df = pd.DataFrame(cards)

            if not df.empty and "set" in df.columns:
                df["image_url"] = df["images"].apply(lambda x: x.get("large") if isinstance(x, dict) else None)
                if "owned" not in df.columns:
                    df["owned"] = False
                set_df = df["set"].apply(pd.Series)
                set_columns = ["name", "series", "releaseDate"]
                set_df = set_df[set_columns]
                set_df = set_df.rename(columns={'name': 'set_name', 'releaseDate': 'release_date'})
                df = pd.concat([df.drop(columns=["set"]), set_df], axis=1)
                df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
                df = df.sort_values(by=["release_date", "id"], ascending=True)
            return df
        else:
            print(f"Fehler: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        print("Timeout! Server has not responded in 15 Seconds.")


def get_card(pokemon: str):
    url = f"https://api.pokemontcg.io/v2/cards?q=name:{pokemon}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout:
        print("Timeout – Server antwortet nicht.")
    except requests.exceptions.RequestException as e:
        print(f"Anfrage fehlgeschlagen: {e}")
