import streamlit as st

def run_name_search(data):
    """
    Executa o formulário de busca por nome

    :param data: dataframe base
    :return: void
    """

    # Escreve as instruções na tela
    st.write("Insira os dados da entrega:")

    # Cria uma caixa de escolha para selecionar o nome
    name_selected = st.selectbox(label="Nome", options=sorted(data["Nome"].unique()),
                               index=None, placeholder="Insira aqui o nome...")

    # Checa se o botão deve ficar desabilitado
    is_button_inactive = name_selected is None

    # Cria um botão para buscar os dados
    search_button = st.button(label="Buscar", disabled=is_button_inactive)

    # Se o botão for pressionado
    if search_button:
        st.write("Enviado!")