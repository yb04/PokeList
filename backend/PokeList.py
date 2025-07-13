import pandas as pd


def read_file(file: str) -> pd.DataFrame:
    return pd.read_csv(file, sep=";")


def get_pokemon_list(*pokemon: str | int, pokelist: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame containing given Pokemon.
    :param pokemon: PokedexNumber or Name
    :param pokelist: Pokemon csv
    :return: DataFrame
    """
    df = pd.DataFrame()
    for p in pokemon:
        if isinstance(p, int):
            df1 = pokelist[pokelist['nationalPokedexNumbers'] == "["+str(p)+"]"]
        else:
            df1 = pokelist[pokelist['name'] == p]
        df = pd.concat([df, df1]).sort_values(['id'])
    return df


def print_list(pl: pd.DataFrame):
    """
    Print list
    :param pl:
    :return:
    """
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    print(pl[['name', 'id', 'nationalPokedexNumbers', 'set_name', 'release_date']])


def print_list_head(pl: pd.DataFrame):
    """
    Debugging, return first 5 Entries.
    :param pl:
    :return:
    """
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    print(pl[['name', 'id', 'nationalPokedexNumbers', 'set_name', 'release_date']].head(5))


def get_list(pl: pd.DataFrame):
    """
    returns the given list with relevant information
    :param pl:
    :return:
    """
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    return pl[['name', 'id', 'nationalPokedexNumbers', 'rarity', 'set_name', 'release_date']]


def save_list(pl: pd.DataFrame, path):
    """
    save list as .csv
    :param pl:
    :param path:
    :return:
    """
    l = get_list(pl)
    l.to_csv("output/"+path+".csv", header=True)


pok = ["arcanine", "zapdos", "charmander"]
#pl = read_file("pokelist.csv")
#pl.info()
#arcanines = get_pokemon_list(59, 58, pokelist=pl)
#print_list(arcanines)
#save_list(arcanines, "Arcanine_list")'


