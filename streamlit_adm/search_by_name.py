import streamlit as st
import pandas as pd

def get_person_id(data_mor: pd.DataFrame, nome: str) -> list:
    """
    Extrai o ID da pessoa buscada

    :param data_mor: pd.DataFrame, dataframe base
    :param nome: str, nome da pessoa buscada
    :return: list, ID da pessoa buscada
    """

    return data_mor[data_mor["Nome"]==nome]["ID"].tolist()

def run_name_search(data_mor: pd.DataFrame) -> list | None:
    """
    Executa o formulário de busca por nome

    :param data_mor: pd.DataFrame, dataframe base
    :return: list ou None, ID da pessoa encontrada
    """

    # Input do nome
    nome_selected = st.selectbox(label="Nome", options=sorted(data_mor["Nome"].unique()),
                               index=None, placeholder="Insira aqui o nome...", key="searchName")

    # Verifica se o botão está inativo
    is_button_inactive = nome_selected is None

    # Botão de envio do formulário
    search_button = st.button(label="Buscar", disabled=is_button_inactive, type="primary")

    # Se o botão for pressionado
    if search_button:
        # Retorna o ID ou IDs das pessoas buscadas
        return get_person_id(data_mor, nome_selected)
