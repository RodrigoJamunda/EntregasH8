import streamlit as st
import pandas as pd

@st.cache_data
def get_ap_data(data):
    """
    Converte o dataframe base em um dataframe com os dados concatenados em duas colunas

    :param data: pd.Dataframe, dataframe base
    :return: pd.DataFrame, dataframe modificada
    """

    data_ap = pd.DataFrame(columns=["Apartamento", "Vaga", "Nome"])
    for index, row in data.iterrows():
        data_ap.loc[index] = [f"H8{row["Bloco"]} {row["Apartamento"]}", f"{row["Vaga"]} - {row["Nome"]}", row["Nome"]]

    return data_ap

def get_person(data, ap, vaga, not_include_vaga):
    """
    Extrai o nome da pessoa buscada

    :param data: pd.DataFrame, dataframe base
    :param ap: str, apartamento da pessoa buscada
    :param vaga: str, vaga da pessoa buscada
    :param not_include_vaga: bool, parametro que controla se a vaga está preenchida ou não
    :return: str ou list, pessoa ou pessoas buscadas
    """

    if not_include_vaga:
        return data[data["Apartamento"] == ap]["Nome"].tolist()
    return data[(data["Apartamento"] == ap) & (data["Vaga"] == vaga)]["Nome"].item();

def run_ap_search(data):
    """
    Executa o formulário de busca por apartamento

    :param data: pd.DataFrame, dataframe base
    :return: str ou list, nome ou nomes das pessoas encontradas
    """

    # Cria um dataframe modificado e o armazena no cache
    data_ap = get_ap_data(data)

    # Cria uma caixa de escolha para selecionar o apartamento
    ap_selected = st.selectbox(label="Apartamento", options=sorted(data_ap["Apartamento"].unique()),
                               index=None, placeholder="Insira aqui o apartamento...")

    # Desabilita o botão de enviar
    is_button_inactive = True

    # Se algum apartamento for selecionado
    if ap_selected is not None:
        # Cria uma caixa de decisão para enviar notificações para todos do aparamento
        not_include_vaga = st.checkbox("Notificar todos do apartamento")

        # Filtra o dataframe com base no apartamento selecionado
        data_vaga = data_ap[data_ap["Apartamento"]==ap_selected]

        # Cria uma lista de escolhas para selecionar a vaga
        vaga_selected = st.radio(label="Vaga", index=None, disabled=not_include_vaga,
                                 options=sorted(data_vaga["Vaga"].unique()))

        # Checa se o botão deve ficar desabilitado
        is_button_inactive = not not_include_vaga and vaga_selected is None

    # Cria um botão para buscar os dados
    search_button = st.button(label="Buscar", disabled=is_button_inactive, type="primary")

    # Se o botão for pressionado
    if search_button:
        return get_person(data_ap, ap_selected, vaga_selected, not_include_vaga)
