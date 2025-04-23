import os, sys
import streamlit as st

sys.path.append("..")
from func import add_func, remove_func, func_options
from session_state import set_session_state

def cadastro():
    st.subheader("Insira os dados do funcionário")
    nome = st.text_input(label="Nome", placeholder="Insira aqui o nome...")

    is_button_inactive = nome is None

    submit_button = st.button(label="Cadastrar", disabled=is_button_inactive, type="primary")

    if submit_button:
        add_func(nome)
        set_session_state("admin_message", "Funcionário cadastrado com sucesso!")
        st.switch_page(r"pages/admin_page.py")

def remocao():
    st.subheader("Insira os dados do funcionário")
    nome = st.selectbox(label="Nome", options=func_options(), index=None,
                               placeholder="Insira aqui o nome...")

    is_button_inactive = nome is None

    submit_button = st.button(label="Remover", disabled=is_button_inactive, type="primary")

    if submit_button:
        remove_func(nome)
        set_session_state("admin_message", "Funcionário removido com sucesso!")
        st.switch_page(r"pages/admin_page.py")

def main():
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    st.title("Gerenciar funcionários")

    mode = st.pills(label="Modo", options=["Cadastrar funcionário", "Remover funcionário"],
                    selection_mode="single", default="Cadastrar funcionário", label_visibility="hidden")

    if mode == "Cadastrar funcionário":
        cadastro()
    elif mode == "Remover funcionário":
        remocao()



if __name__ == "__main__":
    main()