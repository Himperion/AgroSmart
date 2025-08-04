import os, pickle

def get_dict_aptitude() -> dict:

    dict_aptitude = {
        4: {
            "Name": "Aptitud alta",
            "Color": "#138848",
            "Emoji": "\U0001F947",
            "Description": "Zonas con las mejores condiciones desde el punto de vista físico, socioecosistémico y socioeconómico."
        },
        3: {
            "Name": "Aptitud media",
            "Color": "#79C162",
            "Emoji": "\U0001F7E2",
            "Description": "Zonas con limitaciones moderadas de tipo físico, socioecosistémico y/o socioeconómico."
        },
        2: {
            "Name": "Aptitud baja",
            "Color": "#FCC070",
            "Emoji": "\U0001F7E1",
            "Description": "Zonas con fuertes limitaciones de tipo físico, socioecosistémico y/o socioeconómico, las cuales podrían adecuarse con grandes inversiones y/o el desarrollo de nuevas tecnologías."
        },
        1: {
            "Name": "No apta",
            "Color": "#E44432",
            "Emoji": "\U0001F534",
            "Description": "Zonas con restricciones físicas y socioecosistémicas que imposibilitan el desarrollo de la actividad."
        },
        0: {
            "Name": "Exclusión legal",
            "Color": "#C4C4C4",
            "Emoji": "\U0001F6AB",
            "Description": "Zonas en las cuales, por mandato legal, no se permite el desarrollo de la producción con fines comerciales."
        }
    }

    return dict_aptitude

def add_key_label_aptitude(dict_aptitude: dict) -> dict:

    for key, value in dict_aptitude.items():
        value["Label"] = f"{value['Emoji']} {value['Name']}"

    return dict_aptitude

if not os.path.exists(r"assets/DICT_APTITUDE.pickle"):

    DICT_APTITUDE = get_dict_aptitude()
    DICT_APTITUDE = add_key_label_aptitude(DICT_APTITUDE)

    with open("assets/DICT_APTITUDE.pickle", "wb") as f:
        pickle.dump(DICT_APTITUDE, f)

else:
    with open("assets/DICT_APTITUDE.pickle", "rb") as f:
        DICT_APTITUDE: dict = pickle.load(f)

DICT_LABEL_APTITUDE = {value["Label"]: key for key, value in DICT_APTITUDE.items()}
DICT_APTITUDE_NAME = {key: value["Name"] for key, value in DICT_APTITUDE.items()}
DICT_APTITUDE_COLOR = {key: value["Color"] for key, value in DICT_APTITUDE.items()}
DICT_APTITUDE_LABEL = {key: value["Label"] for key, value in DICT_APTITUDE.items()}
LIST_APTITUDE_LABEL = [DICT_APTITUDE[key]["Label"] for key in DICT_APTITUDE]