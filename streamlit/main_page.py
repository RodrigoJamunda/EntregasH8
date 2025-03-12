import streamlit as st
import pandas as pd
from dataset_url import get_url
from search_by_ap import run_ap_search
from search_by_name import run_name_search

@st.cache_data
def sheet_to_df(sheet_url, sheet_name=None):
    """
    Converte uma planilha específica em um documento público do Google Sheets para um dataframe.

    :param sheet_url: str, o URL do documento
    :param sheet_name: str, o nome da planilha específica convertida (primeira planilha por padrão)
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
        page_icon = ":package:"
    )

    # Configura o título da página
    st.title("Entregas H8")

    # Extrai o dataframe base e o armazena no cache do site
    data = sheet_to_df(get_url())

    # Cria uma caixa de escolha para que o usuário escolha buscar por apartamento ou nome
    # default: buscar por apartamento
    search = st.pills(label="", options=["Buscar por apartamento", "Buscar por nome"],
                      selection_mode="single", default="Buscar por apartamento")

    # Executa o script de cada opção
    if search=="Buscar por apartamento":
        run_ap_search(data)
    else:
        run_name_search(data)

if __name__ == "__main__":
    main()
