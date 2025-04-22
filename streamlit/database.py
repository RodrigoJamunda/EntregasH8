import pandas
import pandas as pd
from datetime import datetime
from func import get_func_name
from random import randint

def get_database():
    return pd.read_csv("entregas.csv")

def get_name(data, person_id):
    if type(person_id) is list:
        names = []
        for id in person_id:
            names.append(data[data["ID"] == id]["Nome"].item())
        name = ";".join(names)
    else:
        name = data[data["ID"] == person_id]["Nome"].item()

    return name

def get_id(database, name):
    initials = "".join([(word[0] if word[0].isupper() else "") for word in name.split(" ")])
    if len(initials) <= 2:
        initials = name[0:2].upper() + initials[-1]
    else:
        initials = initials[0:2] + initials[-1]

    id = ""
    while id == "" or database["ID"].isin([id]).any():
        id = initials + datetime.now().strftime("%d%m") + "{:04d}".format(randint(0,9999))

    return id

def update_database(data, person_id, func_id):
    database = get_database()

    new_name = get_name(data, person_id)
    new_id = get_id(database, new_name)

    new_entry = [new_id, new_name, get_func_name(func_id),
                 None, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
    database.loc[len(database)] = new_entry

    database.to_csv("entregas.csv", index=False)

def update_ret(name_ret, ids):
    database = get_database()
    for id in ids:
        database["Retirado por"].loc[database["ID"] == id] = name_ret

    database.to_csv("entregas.csv", index=False)

def print_database():
    database = get_database()

    print(database)

if __name__ == "__main__":
    for i in range(1, 1000):
        print(get_id(get_database(), "Rodrigo Jamundá"))