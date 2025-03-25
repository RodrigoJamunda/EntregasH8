import sys

from streamlit import switch_page

sys.path.append("..")
from session_state import get_session_state, set_session_state
from send_email import notify

import streamlit as st

def hide_format(string):
    """
    Formata a string de email para esconder seu valor

    :param string: str, string base
    :return: str, string formatada
    """

    # Separa a string em antes e depois do "@"
    split = string.split("@")

    # Primeira parte da string
    start = split[0]

    # Segunda parte da string
    end = split[1:]

    # Substitui caracteres da string por "*" de acordo com o seu tamanho
    if len(start) == 1:
        start = "*"
    elif len(start) == 2:
        start = start[0] + "*" * 1
    elif len(start) == 3:
        start = start[:1] + "*" * 2
    elif len(start) <= 5:
        start = start[:2] + "*" * (len(start) - 2)
    else:
        start = start[:2] + "****"

    # Une as duas partes da string novamente
    format_str = start + "@" + "@".join(end)

    return format_str

def print_data(data):
    """
    Formata e imprime uma linha de um dataframe

    :param data: pd.DataFrame, dataframe composto de uma linha
    :return: void
    """

    # Formata e imprime o dataframe
    st.write(f"{data["Nome"].item()} - H8{data["Bloco"].item()} {data["Apartamento"].item()} vaga {data['Vaga'].item()}  \n"
             f"Email: {hide_format(data['Email'].item())}")
    return

def process_data(data, person_id):
    """
    Converte um nome ou uma lista de nomes em uma linha de dataframe

    :param data: pd.DataFrame, dataframe base
    :param person: str ou list, nome ou nomes das pessoas a serem processadas
    :return: void
    """
    if type(person_id) is not list:
        st.divider()

        person_data = data[data["ID"] == person_id]
        print_data(person_data)

        st.divider()
        return

    st.divider()
    for id in person_id:
        person_data = data[data["ID"] == id]
        print_data(person_data)

        st.divider()

    return


def main():
    # Configura o layout da aba da página
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    # Se a busca não foi realizada, retorna à página inicial
    if get_session_state("person_id") is None:
        st.switch_page("main_page.py")

    # Configura o título da página
    st.title("Confirmar")

    # Escreve na tela as instruções
    st.subheader("Confirme os dados para enviar a notificação da entrega:")

    # Extrai os dados da st.session_state
    data = get_session_state("data")
    person_id = get_session_state("person_id")

    # Imprime os dados na tela
    process_data(data, person_id)

    # Cria um botão para confirmar os dados
    confirm_button = st.button(label="Enviar notificação", type="primary")

    # Cria um botão para retornar à página principal
    go_back_button = st.button(label="Cancelar", type="secondary")

    # Se o botão de confirmar for pressionado
    if confirm_button:
        # Envia os dados
        with st.spinner("Enviando..."):
            notify(data, person_id)

        set_session_state("sent_message", True)
        st.switch_page(r"main_page.py")

    # Se o botão de retornar for pressionado
    if go_back_button:
        # Retorna à página principal
        st.switch_page("main_page.py")




if __name__ == "__main__":
    main()