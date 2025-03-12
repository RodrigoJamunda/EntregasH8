import streamlit as st

def run_name_search(data):
    """
    Executa o formulário de busca por nome

    :param data: pd.DataFrame, dataframe base
    :return: str, nome da pessoa encontrada
    """

    # Cria uma caixa de escolha para selecionar o nome
    name_selected = st.selectbox(label="Nome", options=sorted(data["Nome"].unique()),
                               index=None, placeholder="Insira aqui o nome...")

    # Checa se o botão deve ficar desabilitado
    is_button_inactive = name_selected is None

    # Cria um botão para buscar os dados
    search_button = st.button(label="Buscar", disabled=is_button_inactive, type="primary")

    # Se o botão for pressionado
    if search_button:
        return name_selected