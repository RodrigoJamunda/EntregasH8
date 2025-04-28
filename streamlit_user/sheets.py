import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def get_url(sheet_name: str) -> str | None:
    """
    Extrai o url de uma planilha da base de dados

    :param sheet_name: str, nome da planilha
    :return: str ou None, o url da planilha
    """

    # Retorna o url de cada planilha da base de dados
    if sheet_name == 'moradores':
        return "https://docs.google.com/spreadsheets/d/1eXEpOJkSri7oGbDsBZ1qZ3BX-RBZY24mXc8znuKglYc/edit?usp=sharing"
    if sheet_name == 'funcionarios':
        return "https://docs.google.com/spreadsheets/d/1RKV0RzNmZ7oKhEJK6GQqVQUEnFCHkQXlXQE-RG1oBBM/edit?usp=sharing"
    if sheet_name == 'entregas':
        return "https://docs.google.com/spreadsheets/d/1vrPznaP9T1QhdXFAtPaLDyJ-q3W5lqNoDR1BEyd85uE/edit?usp=sharing"

@st.cache_data(show_spinner="Carregando dados...")
def get_data(sheet_name: str) -> pd.DataFrame:
    """
    Extrai a base de dados

    :param sheet_name: str, nome da planilha da base de dados
    :return: pd.DataFrame, a base de dados
    """

    # Inicializa a API responsável por ler os dados da planilha
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Lê os dados da planilha
    df = conn.read(spreadsheet=get_url(sheet_name))

    # Processa os dados lidos
    if(sheet_name == 'moradores'):
        df["Apartamento"] = df["Apartamento"].apply(lambda x:int(x))

    # Retorna a base de dados
    return df

def get_data_from_sheets(sheet_name: str, clear_cache: bool = False) -> pd.DataFrame:
    """
    Gerencia o cache e retorna a base de dados

    :param sheet_name: str, nome da planilha da base de dados
    :return: pd.DataFrame, a base de dados
    """

    # Limpa o cache
    if clear_cache:
        st.cache_data.clear()

    # Retorna a base de dados
    return get_data(sheet_name)

def push_data_to_sheets(sheet_name: str, data: pd.DataFrame) -> None:
    """
    Envia os dados para a base de dados

    :param sheet_name: str, nome da planilha da base de dados
    :param data: pd.DataFrame, os dados enviados
    :return: None
    """

    # Spinner
    with st.spinner("Carregando dados..."):
        # Inicializa a API responsável por escrever os dados na planilha
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Envia os dados para a planilha
        conn.update(spreadsheet=get_url(sheet_name), data=data)

        # Limpa o cache
        st.cache_data.clear()