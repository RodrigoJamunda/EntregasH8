import os, sys
import streamlit as st
from session_state import set_session_state
from search_by_name import run_name_search
from search_by_ap import run_ap_search

def cadastro_database():
    # Todo: COMO ENCONTRAR A PORRA DA ENTREGA?
    pass

def cadastro(data):
    st.subheader("Insira o nome do retirante")

    name_ret = st.selectbox(label="Nome", options=sorted(data["Nome"].unique()),
                        index=None, placeholder="Insira aqui o nome...", key="retName")

    set_session_state("name_ret", name_ret)

    if name_ret is not None:

        st.subheader("Insira os dados da entrega")

        search = st.pills(label="Busca", options=["Buscar por nome", "Buscar por apartamento"],
                          selection_mode="single", default="Buscar por nome", label_visibility="hidden", key="retPill")

        if search == "Buscar por nome":
            person_id = run_name_search(data)
        elif search == "Buscar por apartamento":
            person_id = run_ap_search(data)
        else:
            person_id = None

        if person_id:
            set_session_state("person_id_ret", person_id)
            st.switch_page(r"pages/ret_selection_page.py")