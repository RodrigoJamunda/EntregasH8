import streamlit as st
from search_by_ap import run_ap_search
from search_by_name import run_name_search
from search_by_cam import run_camera_search
from session_state import init_session_state, set_session_state, get_session_state

def cadastro(data):
    # Escreve na tela as instruções
    st.subheader("Insira os dados da entrega")

    # Cria uma caixa de escolha para que o usuário escolha buscar por apartamento ou por nome
    # (default: buscar por apartamento)
    search = st.pills(label="Busca", options=["Buscar por apartamento", "Buscar por nome", "Buscar usando a câmera"],
                      selection_mode="single", default="Buscar por apartamento", label_visibility="hidden", key="entPill")

    st.divider()

    # Executa o script de cada opção
    if search == "Buscar por apartamento":
        person_id = run_ap_search(data)
    elif search == "Buscar por nome":
        person_id = run_name_search(data)
    elif search == "Buscar usando a câmera":
        person_id = run_camera_search(data)
    else:
        person_id = None

    # Troca de página ao encontrar a pessoa
    if person_id:
        set_session_state("person_id", person_id)
        st.switch_page(r"pages/confirm_page.py")
