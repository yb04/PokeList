import pandas as pd
import requests
import yaml

# API-Endpunkt und Schlüssel,
with open("config.yaml", 'r') as y:
    config = yaml.safe_load(y)
API_KEY = config["api_key"]
BASE_URL = "https://api.pokemontcg.io/v2/cards"

# Header für die Authentifizierung
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
        parts.append("(name:" + " OR name:".join(strPokes) + ")")
    if intPokes:
        parts.append("(nationalPokedexNumbers:" + " OR nationalPokedexNumbers:".join(map(str, intPokes)) + ")")

    q = " OR ".join(parts)

    params = {
        "q": q,
        "orderBy": "-set.releaseDate"
    }

    try:
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            cards = data.get("data", [])
            df = pd.DataFrame(cards)
            if not df.empty:
                set_df = df["set"].apply(pd.Series)
                set_columns = ["name", "series", "releaseDate"]
                set_df = set_df[set_columns]
                set_df = set_df.rename(columns={'name': 'set_name'})
                set_df = set_df.rename(columns={'releaseDate': 'release_date'})
                df = pd.concat([df.drop(columns=["set"]), set_df], axis=1)
                df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
                df = df.sort_values(by=["release_date", "id"], ascending=True)
            return df
        else:
            print(f"Fehler: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        print("Timeout! Server has not responded in 5 Seconds.")
