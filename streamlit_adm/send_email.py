import smtplib, ssl
import pandas as pd
import streamlit as st
from email.message import EmailMessage
from email.mime.text import MIMEText
from datetime import datetime
import traceback

def get_address(data_mor: pd.DataFrame, person_id: list[str]) ->  list:
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

def get_data(data_mor: pd.DataFrame, person_id: list[str]) -> tuple[str, str, str]:
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

def create_notification_message(person: dict[str, str]) -> MIMEText:
    """
    Cria um objeto contendo a mensagem de notificação
    
    :param person: dict[str, str], variáveis de texto formatadas
    :return: MIMEText, conteúdo da mensagem de notificação
    """
    # Lê o template de e-mail e o formata com as variáveis
    with open(r"streamlit_adm/email_template.txt", "r") as content_message:
        content = MIMEText(content_message.read().format(**person), "html")
    
    return content

def create_error_message(error: Exception, person_id: list[int]) -> MIMEText:
    """
    Cria um objeto contendo a mensagem de erro
    
    :param error: Exception, a exceção que ocorreu
    :param person_id: int, ID da pessoa que estava sendo notificada quando o erro ocorreu
    :return: MIMEText, conteúdo da mensagem de erro
    """

    with open(r"streamlit_adm/error_template.txt", "r") as content_message:
        content = MIMEText(content_message.read().format(
            time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            error_name=type(error).__name__,
            error=str(error),
            stack_trace=traceback.format_exc(),
            person=person_id
        ), "html")
    
    return content

def get_message(sender: str, receiver: list[str], content: MIMEText,
                subject: str) -> EmailMessage:
    """
    Cria um objeto contendo os parâmetros da mensagem de e-mail

    :param sender: str, e-mail do remetente
    :param receiver: list, e-mail ou e-mails dos destinatários
    :param person: tuple[str, str, str], variáveis de texto formatadas
    :param subject: str, assunto do e-mail
    :return: EmailMessage, a mensagem de e-mail
    """
    # Cria um objeto correspondente à mensagem
    msg = EmailMessage()

    # Insere os parâmetros da mensagem
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(receiver)

    # Retorna o objeto contendo a mensagem
    return msg

def send_email(msg: EmailMessage, sender: str, password: str, receiver: list[str]) -> None:
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

def get_email_data() -> tuple[str, str]:
    """
    Extrai os dados de e-mail do bot

    :return: tuple[str, str], e-mail e senha do bot
    """

    # Extrai os dados de login do bot
    api_email = "bot.entregash8@gmail.com"
    api_password = st.secrets["email_password"]
    
    return api_email, api_password
 

def notify(data_mor: pd.DataFrame, person_id: list[str]) -> None:
    """
    Processa e envia a notificação para a pessoa encontrada

    :param data_mor: pd.DataFrame, base de dados de moradores
    :param person_id: list, ID ou IDs das pessoas encontradas
    :return: None
    """

    # Extrai os dados de e-mail do bot
    api_email, api_password = get_email_data()
   
    # Extrai os dados da pessoa notificada
    target_email = get_address(data_mor, person_id)
    primeiro_nome, dados, tipo = get_data(data_mor, person_id)
    person = {"primeiro_nome": primeiro_nome, "dados": dados, "tipo": tipo}

    # Cria o conteúdo da mensagem de notificação
    content = create_notification_message(person)

    # Cria a mensagem a ser enviada
    msg = get_message(api_email, target_email, content, subject="Notificação de Entrega")

    # Envia a mensagem ao destinatário
    send_email(msg, api_email, api_password, target_email)

def notify_error(error: Exception, person_id: list[int]) -> None:
    """
    Notifica o desenvolvedor de um erro ocorrido durante a execução

    :param error: Exception, a exceção que ocorreu
    :param person_id: int, ID da pessoa que estava sendo notificada quando o erro ocorreu
    :return: None
    """

    api_email, api_password = get_email_data()
    content = create_error_message(error, person_id)
    email_dev = st.secrets["email_dev"]
    msg = get_message(api_email, [email_dev], content, subject="Notificação de Erro")
    
    print("aaaa")
    send_email(msg, api_email, api_password, [email_dev])
