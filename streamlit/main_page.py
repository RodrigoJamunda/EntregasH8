import os, sys
import streamlit as st
import pandas as pd
from search_by_ap import run_ap_search
from search_by_name import run_name_search
from search_by_cam import run_camera_search
from session_state import init_session_state, set_session_state, get_session_state
sys.path.append(__file__)

def get_url(filename: str) -> str:
    """
    Retorna o link da planilha base de dados

    :param filename: str, o caminho relativo até o arquivo contendo o link
    :return: str, o URL da planilha
    """

    # Computa o caminho completo do arquivo
    dirname = os.path.dirname(__file__)
    full_path = os.path.join(dirname, filename)

    # Abre o arquivo e retorna seu conteúdo
    with open(full_path, 'r') as file:
        return file.read().strip()


@st.cache_data
def sheet_to_df(sheet_url: str, sheet_name: str | None = None) -> pd.DataFrame:
    """
    Converte uma planilha específica em um documento público do Google Sheets para um dataframe.

    :param sheet_url: str, o URL do documento
    :param sheet_name: str, o nome da planilha específica convertida (default: None, corresponde à primeira planilha)
    :return: dataframe do pandas contendo os dados da planilha.
    """

    # Extrai o ID do documento do Google Sheets do URL
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]

    # Constrói o URL para o API do Google Sheets
    api_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

    if sheet_name:
        # Se uma planilha específica for dada, afixa-a no link
        api_url += f"&sheet={sheet_name}"

    # Lê os dados do arquivo CSV e converte para um DataFrame
    df = pd.read_csv(api_url)

    return df

def main():
    # Configura o layout da aba da página
    st.set_page_config(
        page_title = "Entregas H8",
        page_icon = ":package:",
        initial_sidebar_state="collapsed"
    )

    # Configura o título da página
    st.title("Entregas H8")

    # Extrai o dataframe base e o armazena no cache do site
    data = sheet_to_df(get_url("dataset_url.txt"))
    init_session_state("data", data)
    init_session_state("person", None)

    if get_session_state("sent_message"):
        st.success("Notificação enviada com sucesso!")

    # Escreve na tela as instruções
    st.subheader("Insira os dados da entrega")

    # Cria uma caixa de escolha para que o usuário escolha buscar por apartamento ou por nome
    # (default: buscar por apartamento)
    search = st.pills(label="Busca", options=["Buscar por apartamento", "Buscar por nome", "Buscar usando a câmera"],
                      selection_mode="single", default="Buscar por apartamento", label_visibility="hidden")

    st.divider()

    # Executa o script de cada opção
    if search == "Buscar por apartamento":
        person_id = run_ap_search(data)
    elif search == "Buscar por nome":
        person_id = run_name_search(data)
    elif search == "Buscar usando a câmera":
        person_id = run_camera_search(data)
    else:
        person_id = None

    # Troca de página ao encontrar a pessoa
    if person_id:
        set_session_state("person_id", person_id)
        st.switch_page(r"pages/confirm_page.py")

if __name__ == "__main__":
    main()
