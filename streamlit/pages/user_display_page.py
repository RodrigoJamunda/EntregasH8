import os, sys
import streamlit as st
import pandas as pd

sys.path.append("..")
from session_state import get_session_state
from main_page import get_data_from_csv

def process_data(data, person_id):
    entregas_database = get_data_from_csv(r"entregas.csv")
    processed_database = entregas_database[0:0]
    if type(person_id) == list:
        for id in person_id:
            name = data[data["ID"] == id]["Nome"].item()
            processed_database = pd.concat([entregas_database[[name in c for c in list(entregas_database["Destinatário"])]],
                                           processed_database], ignore_index=True)
    else:
        name = data[data["ID"] == person_id]["Nome"].item()
        processed_database = pd.concat([entregas_database[[name in c for c in list(entregas_database["Destinatário"])]],
                                        processed_database], ignore_index=True)
    processed_database.drop_duplicates(subset="ID", inplace=True)

    filtered_database = processed_database.filter(items=["Destinatário", "Recebido por", "Retirado por", "Data"])
    filtered_database["Destinatário"] = filtered_database["Destinatário"].apply(lambda x: ", ".join(x.split(";")))
    st.dataframe(filtered_database.sort_values(by=['Data'], ascending=False), hide_index=True)

def main():
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    st.title("Entregas H8")

    st.header("Resultados da busca")

    data = get_session_state("data")
    person_id = get_session_state("person_id_user")

    if person_id is None:
        st.switch_page(r"pages\user_page.py")

    process_data(data, person_id)

if __name__ == '__main__':
    main()