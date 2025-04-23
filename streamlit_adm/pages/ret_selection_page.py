import os, sys
import streamlit as st
import numpy as np

sys.path.append("..")
from main_page import get_data_from_csv
from session_state import get_session_state, set_session_state
from database import update_ret
from sheets import get_data_from_sheets

def get_ret_data(data, entregas_data, person_id):
    ret_data_id = []
    if type(person_id) is list:
        for id in person_id:
            name = data[data["ID"] == id]["Nome"].item()
            data_filtered = entregas_data[[name in c for c in entregas_data["Destinatário"]]]
            data_filtered = data_filtered[data_filtered["Retirado por"].isna()]["ID"].tolist()
            ret_data_id = ret_data_id + data_filtered
    else:
        name = data[data["ID"] == person_id]["Nome"].item()
        data_filtered = entregas_data[[name in c for c in entregas_data["Destinatário"]]]
        ret_data_id = ret_data_id + data_filtered[data_filtered["Retirado por"].isna()]["ID"].tolist()

    return ret_data_id

def display_ret(data, entregas_data, person_id):
    ret_data_id = get_ret_data(data, entregas_data, person_id)

    ret = np.empty(len(ret_data_id))
    ids = []
    for i in range(len(ret_data_id)):
        data_ent = entregas_data[entregas_data["ID"] == ret_data_id[i]]["Data"].item()
        ret[i] = st.checkbox("{} ({})".format(ret_data_id[i], data_ent))

        if ret[i]:
            ids.append(ret_data_id[i])
    return ids

def main():
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    data = get_session_state("data")
    entregas_data = get_data_from_sheets("entregas")
    person_id = get_session_state("person_id_ret")
    name_ret = get_session_state("name_ret")

    st.write(entregas_data)

    if person_id is None:
        st.switch_page("main_page.py")

    st.title("Entregas H8")

    st.header("Selecione as encomendas a serem retiradas")

    ids = display_ret(data, entregas_data, person_id)

    is_button_inactive = len(ids) == 0
    submit_button = st.button(label="Cadastrar", disabled=is_button_inactive, type="primary")

    if submit_button:
        update_ret(name_ret, ids)
        set_session_state("sent_message", "Retirada cadastrada com sucesso!")
        st.switch_page("main_page.py")

if __name__ == '__main__':
    main()