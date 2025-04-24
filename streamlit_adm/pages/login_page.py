import os, sys
import streamlit as st
import hashlib

sys.path.append("..")
from session_state import set_session_state, get_session_state

sys.path.append("..")

def check_password(entered_password):
    hashed_password = hashlib.pbkdf2_hmac('sha256', entered_password.encode("utf-8"),
                                          "855a5095c515e040".encode("utf-8"), 600000).hex()
    return hashed_password == st.secrets["admin_password_hashed"]

def main():
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    with st.form("password_form"):
        st.write("Insira a senha para acessar a página de administrador")
        entered_password = st.text_input("Senha", type="password")

        submit_button = st.form_submit_button(label="Avançar")
        if submit_button:
            if check_password(entered_password):
                set_session_state("is_logged_in", True)
                st.switch_page(r"pages/admin_page.py")
            else:
                st.error("Senha incorreta!")

    if st.button("Voltar", type="secondary"):
        st.switch_page("main_page.py")

if __name__ == "__main__":
    main()