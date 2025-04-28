import smtplib, ssl
import pandas as pd
import streamlit as st
from email.message import EmailMessage
from email.mime.text import MIMEText

def get_address(data_mor: pd.DataFrame, person_id: list) ->  list:
    """
    Retorna o e-mail das pessoas encontradas

    :param data_mor: pd.DataFrame, base de dados de moradores
    :param person_id: list, ID ou IDs da pessoas encontradas
    :return: list, e-mail ou e-mails das pessoas encontradas
    """

    # Inicializa a lista de e-mails
    address_list = []

    # Para cada destinatário
    for id_mor in person_id:
        # Adiciona o e-mail à lista
        address_list.append(data_mor[data_mor["ID"]==id_mor]["Email"].item())

    # Retorna a lista de e-mails
    return address_list

def get_data(data_mor: pd.DataFrame, person_id: list) -> tuple[str, str, str]:
    """
    Retorna os dados formatados das pessoas encontradas

    :param data_mor: pd.DataFrame, base de dados de moradores
    :param person_id: list, ID ou IDs da pessoas encontradas
    :return: tuple[str, str, str], dados formatados das pessoas encontradas
    """

    # Se houver mais de um ID
    if len(person_id) > 1:
        # Extrai os dados da primeira pessoa
        person_data = data_mor[data_mor["ID"]==person_id[0]]

        # Extrai os dados do apartamento
        ap = person_data["Apartamento"].item()
        bloco = person_data["Bloco"].item()

        # Formata as variáveis do e-mail
        primeiro_nome = "morador(a)"
        dados = f"Apartamento H8{bloco} {ap}"
        tipo = "destinada para o seu apartamento"

    # Se houver só um ID
    else:
        # Extrai os da pessoa correspondente
        person_data = data_mor[data_mor["ID"]==person_id[0]]

        # Extrai os dados do apartamento, nome e vaga
        ap = person_data["Apartamento"].item()
        bloco = person_data["Bloco"].item()
        nome = person_data["Nome"].item()
        vaga = person_data["Vaga"].item()

        # Formata as variáveis do e-mail
        primeiro_nome = nome.split(" ")[0]
        dados = rf"{nome}<br>Apartamento H8{bloco} {ap}, vaga {vaga}"
        tipo = "em seu nome"

    # Retorna as variáveis formatadas
    return primeiro_nome, dados, tipo

def get_message(sender: str, receiver: list, person: dict[str, str]) -> EmailMessage:
    """
    Cria um objeto contendo a mensagem de e-mail

    :param sender: str, e-mail do remetente
    :param receiver: list, e-mail ou e-mails dos destinatários
    :param person: tuple[str, str, str], variáveis de texto formatadas
    :return: EmailMessage, a mensagem de e-mail
    """

    # Lê o template de e-mail e o formata com as variáveis
    # with open(r"streamlit_adm/email_template.txt", "r") as content_message:
    with open(r"streamlit_adm/email_template.txt", "r") as content_message:
        content = MIMEText(content_message.read().format(**person), "html")

    # Cria um objeto correspondente à mensagem
    msg = EmailMessage()

    # Insere os parâmetros da mensagem
    msg.set_content(content)
    msg["Subject"] = "Notificação de entrega"
    msg["From"] = sender
    msg["To"] = ", ".join(receiver)

    # Retorna o objeto contendo a mensagem
    return msg

def send_email(msg: EmailMessage, sender: str, password: str, receiver: list) -> None:
    """
    Envia a mensagem para o e-mail dado

    :param msg: EmailMessage, a mensagem de e-mail a ser enviada
    :param sender: str, e-mail do remetente
    :param password: str, senha do e-mail do remetente
    :param receiver: list, e-mail ou e-mails dos destinatários
    :return: None
    """

    # Cria o sistema de criptografia do e-mail
    context = ssl.create_default_context()

    # Cria a API responsável por enviar o e-mail
    with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context) as server:
        # Login na conta do remetente
        server.login(sender, password)

        # Envia a mensagem para o destinatário
        server.sendmail(sender, receiver, msg.as_string())

def notify(data_mor: pd.DataFrame, person_id: list) -> None:
    """
    Processa e envia a notificação para a pessoa encontrada

    :param data_mor: pd.DataFrame, base de dados de moradores
    :param person_id: list, ID ou IDs das pessoas encontradas
    :return: None
    """

    # Extrai os dados de login do bot
    api_email = "bot.entregash8@gmail.com"
    api_password = st.secrets["email_password"]

    # Extrai os dados da pessoa notificada
    target_email = get_address(data_mor, person_id)
    primeiro_nome, dados, tipo = get_data(data_mor, person_id)
    person = {"primeiro_nome": primeiro_nome, "dados": dados, "tipo": tipo}

    # Cria a mensagem a ser enviada
    msg = get_message(api_email, target_email, person)

    # Envia a mensagem ao destinatário
    send_email(msg, api_email, api_password, target_email)
