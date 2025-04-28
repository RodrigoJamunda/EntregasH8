import sys

import streamlit as st
import pandas as pd
from datetime import datetime
from random import randint

sys.path.append("..")
from session_state import get_session_state, set_session_state
from send_email import notify
from database import update_database
from sheets import get_data_from_sheets

def hide_format(string: str) -> str:
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

    # Retorna a string formatada
    return format_str

def get_ent_id(data_mor: pd.DataFrame, data_ent: pd.DataFrame, person_id: list) -> str:
    """
    Gera o ID da encomenda

    :param data_mor: pd.DataFrame, base de dados dos moradores
    :param data_ent: pd.DataFrame, base de dados das entregas
    :param person_id: ID do destinatário
    :return: str, ID da encomenda
    """

    # Considera o primeiro destinatário para gerar o ID
    first_person_id = person_id[0]

    # Extrai o nome do destinatário
    name = data_mor[data_mor["ID"]==first_person_id]["Nome"].item()

    # Extrai as iniciais do nome
    initials = "".join([(word[0] if word[0].isupper() else "") for word in name.split(" ")])

    # Se o nome tiver apenas duas palavras
    if len(initials) <= 2:
        # Toma as primeiras duas letras do nome e a última inicial
        initials = name[0:2].upper() + initials[-1]

    # Caso contrário
    else:
        # Toma as duas primeiras e a última inicial
        initials = initials[0:2] + initials[-1]

    # Inicializa a variável de ID da encomenda
    id_enc = ""

    # Enquanto o ID não é vazio e o ID não está na base de dados
    while id_enc == "" or data_ent["ID"].isin([id_enc]).any():
        # O ID é gerado (iniciais + dia e mês do cadastro + número aleatório)
        id_enc = initials + datetime.now().strftime("%d%m") + "{:04d}".format(randint(0,9999))

    # Retorna o ID
    return id_enc

def print_data(data_mor: pd.Series) -> None:
    """
    Formata e imprime os dados do destinatário

    :param data_mor: pd.Series, dados do destinatário
    :return: None
    """

    # Formata e imprime o dataframe
    st.write(f"{data_mor["Nome"].item()} - H8{data_mor["Bloco"].item()} {data_mor["Apartamento"].item()} vaga {data_mor['Vaga'].item()}" +
             "  \n" + f"Email: {hide_format(data_mor['Email'].item())}")

def process_data(data_mor: pd.DataFrame, person_id: list, ent_id: str) -> None:
    """
    Converte um nome ou uma lista de nomes em uma linha de dataframe

    :param data_mor: pd.DataFrame, base de dados dos moradores
    :param person_id: list, ID ou IDs dos destinatários
    :param ent_id: str, ID da encomenda
    :return: None
    """

    # Divisor de texto
    st.divider()

    # Para cada destinatário
    for id_dest in person_id:
        # Extrai os dados do destinatário
        person_data = data_mor[data_mor["ID"] == id_dest]

        # Exibe os dados do destinatário
        print_data(person_data)

        # Divisor de texto
        st.divider()

    # Exibe o ID da entrega
    st.write(f"ID da entrega: **{ent_id}**")


def main():
    # Configura o layout da página
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    # Se a busca não foi realizada
    if get_session_state("person_id") is None:
        # Retorna à página inicial
        st.switch_page("main_page.py")

    # Configura o título da página
    st.title("Confirmar")

    # Escreve na tela as instruções
    st.subheader("Confirme os dados para cadastrar a entrega:")

    # Extrai os dados dos moradores, das entregas e da busca realizada
    data_mor = get_data_from_sheets("moradores")
    data_ent = get_data_from_sheets("entregas", clear_cache=True)
    person_id = get_session_state("person_id")

    # Se o ID não foi gerado
    if get_session_state("ent_id") is None:
        # Gera o ID da entrega
        ent_id = get_ent_id(data_mor, data_ent, person_id)

        # Salva o ID na session state
        set_session_state("ent_id", ent_id)

    # Caso contrário
    else:
        # Extrai o ID da session state
        ent_id = get_session_state("ent_id")

    # Exibe os dados na tela
    process_data(data_mor, person_id, ent_id)

    # Botão de confirmação de dados
    confirm_button = st.button(label="Enviar notificação", type="primary")

    # Se o botão de confirmação for pressionado
    if confirm_button:
        with st.spinner("Enviando..."):
            # Salva a entrega na base de dados
            update_database(data_mor, person_id, get_session_state("func_id"), ent_id)

            # Envia um e-mail ao destinatário
            notify(data_mor, person_id)

        # Envia a mensagem de sucesso
        set_session_state("sent_message", "Cadastro de entrega realizado com sucesso!")

        # Retorna à página inicial
        st.switch_page(r"main_page.py")

    # Botão de retorno à página principal
    go_back_button = st.button(label="Cancelar", type="secondary")

    # Se o botão de retornar for pressionado
    if go_back_button:
        # Retorna à página principal
        st.switch_page("main_page.py")

if __name__ == "__main__":
    main()