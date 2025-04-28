import sys
import streamlit as st
import hashlib

sys.path.append("..")
from session_state import set_session_state, get_session_state

sys.path.append("..")

def check_password(entered_password: str) -> bool:
    """
    Checa se a senha digitada corresponde à senha cadastrada

    :param entered_password: str, a senha digitada
    :return: bool, se a senha corresponde à senha cadastrada
    """

    # Criptografa a senha (algoritmo SHA-256, com salt salvo no arquivo secrets.toml e 600.000 iterações)
    hashed_password = hashlib.pbkdf2_hmac('sha256', entered_password.encode("utf-8"),
                                          st.secrets["admin_salt"].encode("utf-8"), 600000).hex()

    # Retorna se a senha criptografada corresponde à senha criptografada cadastrada
    return hashed_password == st.secrets["admin_password_hashed"]

def main():
    # Configura o layout da página
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    # Cria o formulário de login
    with st.form("password_form"):
        # Exibe as instruções na tela
        st.write("Insira a senha para acessar a página de administrador")

        # Input da senha
        entered_password = st.text_input("Senha", type="password")

        # Botão de envio do formulário
        submit_button = st.form_submit_button(label="Avançar")

        # Se o botão de envio for pressionado
        if submit_button:
            # Se a senha estiver correta
            if check_password(entered_password):
                # Cadastra o login
                set_session_state("is_logged_in", True)

                # Troca para a página de administrador
                st.switch_page(r"pages/admin_page.py")

            # Caso contrário
            else:
                # Exibe uma mensagem de erro
                st.error("Senha incorreta!")

    # Botão de retorno à página principal
    go_back_button = st.button("Voltar", type="secondary")

    # Se o botão de retorno for pressionado
    if go_back_button:
        # Troca para a página principal
        st.switch_page("main_page.py")

if __name__ == "__main__":
    main()