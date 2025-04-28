import os, sys
import streamlit as st

sys.path.append("..")
from session_state import set_session_state, get_session_state
from sheets import get_data_from_sheets

def get_download_data() -> bytes:
    """
    Processa a base de dados e a transforma em um arquivo para download

    :return: bytes, o conteúdo do arquivo Excel representando a planilha
    """

    # Configura o caminho do arquivo a ser criado
    dirname = os.path.dirname(__file__)
    temp_path = os.path.join(dirname, r".\temp")
    sheet_path = os.path.join(dirname, r".\temp\sheet.xlsx")

    # Extrai a planilha da base de dados
    data_ent = get_data_from_sheets("entregas")

    # Se o caminho não existir
    if not os.path.exists(sheet_path):
        # Cria o diretório \temp
        os.mkdir(temp_path)

    # Converte os dados para um arquivo Excel e salva no diretório \temp
    data_ent.to_excel(sheet_path, index=False, sheet_name="Entregas", engine="openpyxl")

    # Converte o arquivo em bytes
    with open(sheet_path, 'rb') as sheet:
        # Retorna o conteúdo do arquivo
        return sheet.read()

def main():
    # Configura o layout da página
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    st.title("Área do administrador")

    # Checa se o login foi realizado
    if not get_session_state("is_logged_in"):
        st.switch_page(r"pages/login_page.py")

    # Se há alguma mensagem de cadastro
    if get_session_state("admin_message") is not None:
        # Exibe a mensagem
        message = get_session_state("admin_message")
        st.success(message)

        # Reseta a variável que armazena a mensagem
        set_session_state("admin_message", None)

    # Botão de cadastro de funcionário
    manage_func = st.button(label="Gerenciar funcionários", type="primary")

    # Se o botão for pressionado
    if manage_func:
        # Troca a página para a página de funcionário
        st.switch_page(r"pages/func_page.py")

    # Botão de download da planilha de entregas
    st.download_button(label="Baixar planilha de entregas", file_name="entregas_h8.xlsx",
                       data=get_download_data(), on_click="rerun", icon=":material/download:", type="primary")

    # Botão de gerenciamento do histórico de entregas
    manage_data = st.button(label="Excluir histórico de entregas", type="primary")

    # Se o botão for pressionado
    if manage_data:
        # Troca a página para a página de gerenciamento do histórico
        st.switch_page(r"pages/data_page.py")

    # Botão de retorno à página principal
    go_back_button = st.button("Voltar à página inicial", type="secondary")

    # Se o botão de retornar for pressionado
    if go_back_button:
        # Faz o logout
        set_session_state("is_logged_in", False)

        # Troca de página para a página principal
        st.switch_page("main_page.py")

if __name__ == '__main__':
    main()