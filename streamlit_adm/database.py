import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
from func import get_func_name
from sheets import get_data_from_sheets, push_data_to_sheets

def get_database():
    return get_data_from_sheets("entregas")

def get_name(data, person_id):
    if type(person_id) is list:
        names = []
        for id in person_id:
            names.append(data[data["ID"] == id]["Nome"].item())
        name = ";".join(names)
    else:
        name = data[data["ID"] == person_id]["Nome"].item()

    return name

def update_database(data, person_id, func_id, new_id):
    database = get_database()

    new_name = get_name(data, person_id)

    new_entry = [new_id, new_name, get_func_name(func_id),
                 None, (datetime.now()+relativedelta(hours=-3)).strftime("%d/%m/%Y %H:%M:%S")]
    database.loc[len(database)] = new_entry

    push_data_to_sheets("entregas", database)

def update_ret(name_ret, ids):
    database = get_database()
    for id in ids:
        database["Retirado por"].loc[database["ID"] == id] = name_ret

    push_data_to_sheets("entregas", database)

def print_database():
    database = get_database()

    print(database)

if __name__ == "__main__":
    for i in range(1, 1000):
        print(get_id(get_database(), "Rodrigo Jamundá"))