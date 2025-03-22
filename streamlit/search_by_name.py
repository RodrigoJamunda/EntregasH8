import pandas as pd
import streamlit as st

def get_person_id(data: pd.DataFrame, nome: str) -> int:
    """
    Extrai o ID da pessoa buscada

    :param data: pd.DataFrame, dataframe base
    :param nome: str, nome da pessoa buscada
    :return: int, ID da pessoa buscada
    """

    return data[data["Nome"]==nome]["ID"].item()

def run_name_search(data: pd.DataFrame) -> int:
    """
    Executa o formulário de busca por nome

    :param data: pd.DataFrame, dataframe base
    :return: int, ID da pessoa encontrada
    """

    # Cria uma caixa de escolha para selecionar o nome
    nome_selected = st.selectbox(label="Nome", options=sorted(data["Nome"].unique()),
                               index=None, placeholder="Insira aqui o nome...")

    # Checa se o botão deve ficar desabilitado
    is_button_inactive = nome_selected is None

    # Cria um botão para buscar os dados
    search_button = st.button(label="Buscar", disabled=is_button_inactive, type="primary")

    # Se o botão for pressionado
    if search_button:
        return get_person_id(data, nome_selected)