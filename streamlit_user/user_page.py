import streamlit as st

from search_by_name import run_name_search
from search_by_ap import run_ap_search
from session_state import set_session_state
from sheets import get_data_from_sheets

def main():
    # Configura o layout da página
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    st.title("Entregas H8")

    # Extrai a base de dados de moradores
    data = get_data_from_sheets("moradores")

    # Exibe as instruções na tela
    st.subheader("Insira os seus dados")

    # Seleciona a ação a ser realizada
    search = st.pills(label="Busca", options=["Buscar por nome", "Buscar por apartamento"],
                      selection_mode="single", default="Buscar por nome", label_visibility="hidden", key="userPill")

    # Exibe o formulário de cada ação
    if search == "Buscar por nome":
        person_id = run_name_search(data)
    elif search == "Buscar por apartamento":
        person_id = run_ap_search(data)
    else:
        person_id = None

    # Troca de página ao encontrar a pessoa
    if person_id is not None:
        set_session_state("person_id_user", person_id)
        st.switch_page(r"pages/user_display_page.py")

if __name__ == '__main__':
    main()