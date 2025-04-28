import sys
import streamlit as st
import numpy as np
import pandas as pd

sys.path.append("..")
from session_state import get_session_state, set_session_state
from database import update_ret
from sheets import get_data_from_sheets

def get_ret_data(data_mor: pd.DataFrame, data_ent: pd.DataFrame, person_id: list) -> list | None:
    """
    Extrai os IDs das encomendas cadastradas para retirada

    :param data_mor: pd.DataFrame, base de dados dos moradores
    :param data_ent: pd.DataFrame, base de dados das entregas
    :param person_id: list, ID ou IDs dos destinatários
    :return: list ou None, IDs das encomendas
    """

    # Inicialização da lista de IDs
    ret_data_id = []

    # Para cada destinatário
    for id_dest in person_id:
        # Extrai o nome do destinatário
        name = data_mor[data_mor["ID"] == id_dest]["Nome"].item()

        # Extrai as entregas cadastradas sob o nome do destinatário
        data_filtered = data_ent[[name in c for c in data_ent["Destinatário"]]]

        # Filtra as encomendas que ainda não foram retiradas
        data_filtered = data_filtered[data_filtered["Retirado por"].isna()]["ID"].tolist()

        # Adiciona as encomendas à lista
        ret_data_id = ret_data_id + data_filtered

    # Inicializa a lista de IDs sem repetição
    ret_data_id_uniq = []

    # Para cada ID
    for id_ret in ret_data_id:
        # Se o ID não está na lista
        if id_ret not in ret_data_id_uniq:
            # Adiciona o ID à lista
            ret_data_id_uniq.append(id_ret)

    # Retorna a lista de IDs
    return ret_data_id_uniq

def display_ret(data_mor: pd.DataFrame, data_ent: pd.DataFrame, person_id: list) -> list:
    """
    Exibe os dados das entregas a serem retiradas e retorna se eles foram selecionados

    :param data_mor: pd.DataFrame, base de dados dos moradores
    :param data_ent: pd.DataFrame, base de dados das entregas
    :param person_id: list, ID ou IDs dos destinatários
    :return: np.array, entregas que foram selecionadas para retirada
    """

    # Extrai os IDs das entregas
    data_ret = get_ret_data(data_mor, data_ent, person_id)

    # Inicializa o vetor de controle das entregas e a lista de IDs das entregas retiradas
    ret = np.empty(len(data_ret))
    ids = []

    # Para cada entrega
    for i in range(len(data_ret)):
        # Extrai a data que a entrega foi cadastrada
        data_ent_i = data_ent[data_ent["ID"] == data_ret[i]]["Data"].item()

        # Input de seleção de entregas
        ret[i] = st.checkbox("{} ({})".format(data_ret[i], data_ent_i), key=f'ret_cb_{i}')

        # Se a entrega for selecionada
        if ret[i]:
            # Adiciona o ID à lista
            ids.append(data_ret[i])

    # Retorna a lista de IDs
    return ids

def main():
    # Configura o layout da página
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    st.title("Entregas H8")

    # Extrai os dados dos moradores, das entregas e das encomendas a serem retiradas
    data_mor = get_data_from_sheets("moradores")
    data_ent = get_data_from_sheets("entregas", clear_cache=True)
    person_id = get_session_state("person_id_ret")
    name_ret = get_session_state("name_ret")

    # Se não foi realizada uma busca para a retirada
    if person_id is None:
        # Troca para a página inicial
        st.switch_page("main_page.py")

    # Exibe as instruções na tela
    st.header("Selecione as encomendas a serem retiradas")

    # Extrai os IDs das encomendas a serem retiradas
    ids = display_ret(data_mor, data_ent, person_id)

    # Checa se o botão estará ativo
    is_button_inactive = len(ids) == 0

    # Botão de cadastro das retiradas
    submit_button = st.button(label="Cadastrar", disabled=is_button_inactive, type="primary")

    # Se o botão de cadastro for pressionado
    if submit_button:
        # Atualiza a base de dados
        update_ret(name_ret, ids)

        # Envia a mensagem de sucesso
        set_session_state("sent_message", "Retirada cadastrada com sucesso!")

        # Troca para a página principal
        st.switch_page("main_page.py")

if __name__ == '__main__':
    main()