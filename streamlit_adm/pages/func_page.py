import sys
import streamlit as st

sys.path.append("..")
from func import add_func, remove_func, func_options
from session_state import set_session_state

def cadastro():
    """
    Cria o formulário para o cadastro de um novo funcionário na base de dados

    :return: None
    """

    # Exibe as instruções na tela
    st.subheader("Insira os dados do funcionário")

    # Input do nome do funcionário cadastrado
    nome = st.text_input(label="Nome", placeholder="Insira aqui o nome...")

    # Checa se o botão está ativo
    is_button_inactive = nome is None

    # Botão de envio dos dados
    submit_button = st.button(label="Cadastrar", disabled=is_button_inactive, type="primary")

    # Se o botão for pressionado
    if submit_button:
        # Cadastra o funcionário
        add_func(nome)

        # Envia a mensagem de sucesso
        set_session_state("admin_message", "Funcionário cadastrado com sucesso!")

        # Troca para a página de adminstrador
        st.switch_page(r"pages/admin_page.py")

def remocao():
    """
    Cria o formulário para a remoção de um funcionário na base de dados

    :return: None
    """

    # Exibe as instruções na tela
    st.subheader("Insira os dados do funcionário")

    # Input do nome do funcionário a ser removido
    nome = st.selectbox(label="Nome", options=func_options(), index=None,
                               placeholder="Insira aqui o nome...")
    # Checa se o botão está ativo
    is_button_inactive = nome is None

    # Botão de envio dos dados
    submit_button = st.button(label="Remover", disabled=is_button_inactive, type="primary")

    # Se o botão for pressionado
    if submit_button:
        # Remove o funcionário
        remove_func(nome)

        # Envia a mensagem de sucesso
        set_session_state("admin_message", "Funcionário removido com sucesso!")

        # Troca para a página de adminstrador
        st.switch_page(r"pages/admin_page.py")

def main():
    # Configura o layout da página
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    st.title("Gerenciar funcionários")

    # Seleciona a ação a ser realizada
    mode = st.pills(label="Modo", options=["Cadastrar funcionário", "Remover funcionário"],
                    selection_mode="single", default="Cadastrar funcionário", label_visibility="hidden")

    # Seleciona o formulário a ser apresentado
    if mode == "Cadastrar funcionário":
        cadastro()
    elif mode == "Remover funcionário":
        remocao()

    # Botão de retorno à página de administrador
    go_back_button = st.button("Cancelar", type="secondary")

    # Se o botão de retorno for pressionado
    if go_back_button:
        # Troca para a página de administrador
        st.switch_page("pages/admin_page.py")

if __name__ == "__main__":
    main()