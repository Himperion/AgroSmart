import pandas as pd
import os, pickle

def get_dataset_file_name_partial(ITEM: int):

    if ITEM < 10:
        return f"datasetSimp_0{ITEM}.parquet"
    else:
        return f"datasetSimp_{ITEM}.parquet"
    
def get_label_with_emoji(NAME: str, ICON: str) -> str:

    if ICON != "":
        return f"{ICON} {NAME}"
    else:
        return f":{NAME}"
    
def get_dict_dpto_mpio(df_mpio_filter: pd.DataFrame):

    dict_mpio, list_mpio = {}, []

    for index, row in df_mpio_filter.iterrows():
        dict_mpio[row["MUNICIPIO"]] = row["MPIO_CODE"]
        list_mpio.append(row["MUNICIPIO"])

    return dict_mpio, list_mpio


path = r"assets/dict.xlsx"

sheets: dict[str, pd.DataFrame] = pd.read_excel(path, sheet_name=None)
df_datasets: pd.DataFrame = sheets["ITEMS"]

df_datasets["NAME"] = df_datasets["NAME"].astype("string")
df_datasets["ICON"] = df_datasets["ICON"].astype("string")

DICT_ITEMS: dict = {}
DICT_ITEMS_NAME_LABEL: dict = {}
DICT_ITEMS_LABEL_NAME: dict = {}

for index, row in df_datasets.iterrows():
    if pd.isna(row["ICON"]):
        ICON = ""
    else:
        ICON = str(row["ICON"]).encode().decode("unicode_escape")

    dict_item = {
        "ITEM": int(row["ITEM"]),
        "ICON": ICON,
        "TE": int(row["TE"]),
        "TN": int(row["TN"]),
        "TEC": int(row["TEC"]),
        "PAS": int(row["PAS"]),
        "S1": int(row["S1"]),
        "S2": int(row["S2"]),
        "URL_DA": row["URL_DA"],
        "PARTIAL_NAME": get_dataset_file_name_partial(row["ITEM"]),
        "LABEL": get_label_with_emoji(row["NAME"], ICON)
    }

    DICT_ITEMS[row["NAME"]] = dict_item
    DICT_ITEMS_NAME_LABEL[row["NAME"]] = dict_item["LABEL"]
    DICT_ITEMS_LABEL_NAME[dict_item["LABEL"]] = row["NAME"]

if not os.path.exists(r"assets/DICT_DPTO.pickle") or not os.path.exists(r"assets/LIST_DPTO_NAME.pickle"):
    df_dpto: pd.DataFrame = sheets["DICT_DPTO"]
    df_dpto["DEPARTAMENTO"] = df_dpto["DEPARTAMENTO"].astype("string")

    df_mpio: pd.DataFrame = sheets["DICT_MPIO"]
    df_mpio["MUNICIPIO"] = df_mpio["MUNICIPIO"].astype("string")
    df_mpio["DEPARTAMENTO"] = df_mpio["DEPARTAMENTO"].astype("string")
    df_mpio["MPIO_TIPO"] = df_mpio["MPIO_TIPO"].astype("string")

    DICT_DPTO: dict = {}
    LIST_DPTO_NAME: list = []
    
    for index, row in df_dpto.iterrows():
        dict_mpio, list_mpio = get_dict_dpto_mpio(df_mpio_filter=df_mpio[df_mpio["DEPARTAMENTO"] == row["DEPARTAMENTO"]])

        DICT_DPTO[row["DEPARTAMENTO"]] = {
            "DPTO_CODE": row["DPTO_CODE"],
            "DICT_MPIO": dict_mpio,
            "LIST_MPIO_NAME": list_mpio
        }

        LIST_DPTO_NAME.append(row["DEPARTAMENTO"])

    with open("assets/DICT_DPTO.pickle", "wb") as f:
        pickle.dump(DICT_DPTO, f)

    with open("assets/LIST_DPTO_NAME.pickle", "wb") as f:
        pickle.dump(LIST_DPTO_NAME, f)

    del df_dpto, df_mpio

else:
    with open("assets/DICT_DPTO.pickle", "rb") as f:
        DICT_DPTO: dict = pickle.load(f)

    with open("assets/LIST_DPTO_NAME.pickle", "rb") as f:
        LIST_DPTO_NAME: list = pickle.load(f)

del path, sheets, df_datasets, dict_item











