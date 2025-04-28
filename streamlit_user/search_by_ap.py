import streamlit as st
import pandas as pd

@st.cache_data(show_spinner="Carregando dados...")
def get_ap_data(data_mor: pd.DataFrame) -> pd.DataFrame:
    """
    Cria um dataframe com os dados formatados

    :param data_mor: pd.Dataframe, base de dados de moradores
    :return: pd.DataFrame, dataframe modificada
    """

    # Inicializa o dataframe
    data_ap = pd.DataFrame(columns=["ID", "Apartamento", "Vaga", "Nome"])

    # Para cada linha do dataframe base
    for index, row in data_mor.iterrows():
        # Gera uma linha do dataframe
        data_ap.loc[index] = [row["ID"], f"H8{row["Bloco"]} {row["Apartamento"]}", f"{row["Vaga"]} - {row["Nome"]}", row["Nome"]]

    # Retorna o dataframe modificado
    return data_ap

def get_person_id(data_mor: pd.DataFrame, ap: str, vaga: str, not_include_vaga: bool) -> list:
    """
    Extrai o ID da pessoa buscada

    :param data_mor: pd.DataFrame, dataframe base
    :param ap: str, apartamento da pessoa buscada
    :param vaga: str, vaga da pessoa buscada
    :param not_include_vaga: bool, parametro que controla se a vaga está preenchida ou não
    :return: list, ID ou IDs das pessoas buscadas
    """

    # Se a vaga não for especificada
    if not_include_vaga:
        # Retorna todos do apartamento
        return data_mor[data_mor["Apartamento"] == ap]["ID"].tolist()

    # Retorna apenas a pessoa da vaga selecionada
    return data_mor[(data_mor["Apartamento"] == ap) & (data_mor["Vaga"] == vaga)]["ID"].tolist()

def run_ap_search(data_mor: pd.DataFrame) ->  list | None:
    """
    Executa o formulário de busca por apartamento

    :param data_mor: pd.DataFrame, dataframe base
    :return: list ou None, ID ou IDs das pessoas encontradas
    """

    # Cria um dataframe modificado e o armazena no cache
    data_ap = get_ap_data(data_mor)

    # Input de seleção do apartamento
    ap_selected = st.selectbox(label="Apartamento", options=sorted(data_ap["Apartamento"].unique()),
                               index=None, placeholder="Insira aqui o apartamento...")

    # Verifica se o botão está inativo
    is_button_inactive = True

    # Se um apartamento for selecionado
    if ap_selected is not None:
        # Input da exclusão da vaga
        not_include_vaga = st.checkbox("Buscar todas as vagas")

        # Filtra o dataframe pelo apartamento selecionado
        data_vaga = data_ap[data_ap["Apartamento"]==ap_selected]

        # Input de seleção da vaga
        vaga_selected = st.radio(label="Vaga", index=None, disabled=not_include_vaga,
                                 options=sorted(data_vaga["Vaga"].unique()))

        # Verifica se o botão está inativo
        is_button_inactive = not not_include_vaga and vaga_selected is None

    # Botão de envio do formulário
    search_button = st.button(label="Buscar", disabled=is_button_inactive, type="primary")

    # Se o botão for pressionado
    if search_button:
        # Retorna o ID ou IDs das pessoas buscadas
        return get_person_id(data_ap, ap_selected, vaga_selected, not_include_vaga)
