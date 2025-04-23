import pandas as pd
import streamlit as st
from sheets import get_data_from_sheets, push_data_to_sheets

def get_func_df():
    return get_data_from_sheets("funcionarios")

def add_func(nome):
    func = get_func_df()

    new_id = 0 if len(func) == 0 else func.iloc[-1]["ID"] + 1
    func.loc[len(func)] = [new_id, nome]

    push_data_to_sheets("funcionarios", func)

def remove_func(nome):
    func = get_func_df()

    func.drop(func.index[func["Nome"]==nome], inplace=True)

    push_data_to_sheets("funcionarios", func)

def func_options():
    func = get_func_df()
    return sorted(func["Nome"])

def get_func_id(func_name):
    func = get_func_df()
    return func[func["Nome"]==func_name]["ID"].item()

def get_func_name(func_id):
    func = get_func_df()
    return func[func["ID"]==func_id]["Nome"].item()

def get_func_index(func_id):
    if func_id is None:
        return None

    options = func_options()
    i = 0
    for func_name in options:
        if get_func_id(func_name) == func_id:
            return i
        i = i+1

    return None