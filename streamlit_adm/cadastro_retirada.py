import streamlit as st
import pandas as pd
from session_state import set_session_state
from search_by_name import run_name_search
from search_by_ap import run_ap_search

def cadastro(data_mor: pd.DataFrame) -> None:
    """
    Cria o formulário de cadastro de retiradas

    :param data_mor: pd.DataFrame, base de dados dos moradores
    :return: None
    """

    # Exibe na tela as instruções
    st.subheader("Insira o nome do retirante")

    # Input do nome do retirante
    name_ret = st.selectbox(label="Nome", options=sorted(data_mor["Nome"].unique()),
                        index=None, placeholder="Insira aqui o nome...", key="retName")

    # Salva o nome do retirante na session state
    set_session_state("name_ret", name_ret)

    # Se algum nome for selecionado
    if name_ret is not None:
        # Exibe as instruções na tela
        st.subheader("Insira os dados da entrega")

        # Input de escolha para que o usuário escolha buscar por apartamento ou por nome
        # (default: buscar por nome)
        search = st.pills(label="Busca", options=["Buscar por nome", "Buscar por apartamento"],
                          selection_mode="single", default="Buscar por nome", label_visibility="hidden", key="retPill")

        # Executa o script de cada opção
        if search == "Buscar por nome":
            person_id = run_name_search(data_mor)
        elif search == "Buscar por apartamento":
            person_id = run_ap_search(data_mor)
        else:
            person_id = None

        # Troca de página ao encontrar a pessoa
        if person_id is not None:
            set_session_state("person_id_ret", person_id)
            st.switch_page(r"pages/ret_selection_page.py")