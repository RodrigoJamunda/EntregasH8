import os, sys
import streamlit as st
import pandas as pd
from session_state import init_session_state, set_session_state, get_session_state
from func import func_options, get_func_id, get_func_index
import cadastro_entrega, cadastro_retirada
from streamlit_extras.stylable_container import stylable_container
from sheets import get_data_from_sheets
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


@st.cache_data(show_spinner="Carregando dados...")
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

def get_data_from_csv(filename):
    dirname = os.path.dirname(__file__)
    full_path = os.path.join(dirname, filename)

    return pd.read_csv(full_path)


def main():
    # Configura o layout da aba da página
    st.set_page_config(
        page_title = "Entregas H8",
        page_icon = ":package:",
        initial_sidebar_state="collapsed"
    )

    set_session_state("is_logged_in", False)

    with stylable_container(
        key="sc_main_page",
        css_styles="""
            button{
                float: right;
            }
            """
    ):
        _, col1 = st.columns([7, 1])
        with col1:
            if st.button("LOGIN", type="secondary"):
                    st.switch_page(r"pages/login_page.py")

    # Configura o título da página
    st.title("Entregas H8")

    # Extrai o dataframe base e o armazena no cache do site

    data = get_data_from_sheets("moradores")
    init_session_state("data", data)
    init_session_state("person", None)

    if get_session_state("sent_message") is not None:
        message = get_session_state("sent_message")
        st.success(message)
        set_session_state("sent_message", None)

    func_index = get_func_index(get_session_state("func_id"))

    funcionario = st.selectbox(label="Nome", options=func_options(), index=func_index,
                               placeholder="Insira aqui seu nome...")

    if funcionario:
        set_session_state("func_id", get_func_id(funcionario))

        mode = st.pills(label="Busca", options=["Entrega", "Retirada"],
                      selection_mode="single", default="Entrega", label_visibility="hidden")

        if mode == "Entrega":
            cadastro_entrega.cadastro(data)
        elif mode == "Retirada":
            cadastro_retirada.cadastro(data)
        


if __name__ == "__main__":
    main()
