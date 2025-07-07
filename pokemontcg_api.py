import pandas as pd
import requests
import PokeList
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


def get_cards(*pokemon) -> pd.DataFrame:
    """
    Get a DataFrame including a list of all the given Pokemon.
    :param pokemon: one or more desired Pokemon to list.
    :return: DataFrame including the desired List.
    """
    params = {
        "q": "(name:" + " OR name:".join(pokemon) + ")"
    }

    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        cards = data.get("data", [])
        df = pd.DataFrame(cards)
        if not df.empty:
            # set-Spalte zerlegen
            set_df = df["set"].apply(pd.Series)  # `set`-Objekt in separate Spalten zerlegen
            set_columns = ["name", "series", "releaseDate"]  # Wähle gewünschte Felder
            set_df = set_df[set_columns]  # Nur relevante Spalten behalten
            set_df = set_df.rename(columns={'name': 'set_name'})
            set_df = set_df.rename(columns={'releaseDate': 'release_date'})
            # Füge die extrahierten Spalten dem Haupt-DataFrame hinzu
            df = pd.concat([df.drop(columns=["set"]), set_df], axis=1)

            # Konvertiere `releaseDate` zu einem Datumsformat
            df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

            # Sortiere nach `releaseDate`
            df = df.sort_values(by=["release_date", "id"], ascending=True)
        return df
    else:
        print(f"Fehler: {response.status_code} - {response.text}")


df = get_cards("arbok")
PokeList.print_list(df)
PokeList.save_list(df, "arbok")

