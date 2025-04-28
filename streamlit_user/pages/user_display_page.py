import sys
import streamlit as st
import pandas as pd

sys.path.append("../../streamlit_adm")
from session_state import get_session_state
from sheets import get_data_from_sheets

def process_data(data_mor: pd.DataFrame, person_id: list) -> pd.DataFrame:
    """
    Processa os dados das entregas dos destinatários

    :param data_mor: pd.DataFrame, base de dados de moradores
    :param person_id: list, ID ou IDs dos destinatários
    :return: pd.DataFrame, os dados de entrega dos destinatários
    """

    # Extrai a base de dados de entregas
    data_ent = get_data_from_sheets("entregas", clear_cache=True)

    # Inicializa o dataframe das entregas dos destinatários
    processed_data = data_ent[0:0]

    # Para cada destinatário
    for id_mor in person_id:
        # Extrai o nome do destinatário
        name = data_mor[data_mor["ID"] == id_mor]["Nome"].item()

        # Extrai as entregas que contém o nome do destinatário
        name_df = data_ent[[name in c for c in list(data_ent["Destinatário"])]]

        # Adiciona as entregas ao dataframe
        processed_data = pd.concat([name_df, processed_data], ignore_index=True)

    # Exclui entregas de mesmo ID
    processed_data.drop_duplicates(subset="ID", inplace=True)

    # Filtra as colunas do dataframe
    filtered_database = processed_data.filter(items=["Destinatário", "Recebido por", "Retirado por", "Data"])

    # Formata a coluna de destinatários
    filtered_database["Destinatário"] = filtered_database["Destinatário"].apply(lambda x: ", ".join(x.split(";")))

    # Ordena as linhas por data e retorna o dataframe
    return filtered_database.sort_values(by=['Data'], ascending=False)

def main():
    # Configura o layout da página
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    st.title("Entregas H8")

    st.header("Resultados da busca")

    # Extrai a base de dados de moradores e os destinatários buscados
    data_mor = get_data_from_sheets("moradores")
    person_id = get_session_state("person_id_user")

    # Se não houver destinatário
    if person_id is None:
        # Troca para a página inicial
        st.switch_page(r"user_page.py")

    # Processa os dados das entregas
    data_user_ent = process_data(data_mor, person_id)

    # Exibe os dados na tela
    st.dataframe(data_user_ent, hide_index=True)

    # Botão de retorno à página inicial
    go_back_button = st.button(label="Voltar", type="secondary")

    # Se o botão de retorno for pressionado
    if go_back_button:
        # Troca para a página inicial
        st.switch_page("user_page.py")

if __name__ == '__main__':
    main()