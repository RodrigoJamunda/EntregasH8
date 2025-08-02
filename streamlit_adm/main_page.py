import sys
import streamlit as st
from session_state import set_session_state, get_session_state
from func import func_options, get_func_id, get_func_index
import cadastro_entrega, cadastro_retirada
from streamlit_extras.stylable_container import stylable_container
from sheets import get_data_from_sheets
sys.path.append(__file__)

def main():
    # Configura o layout da aba da página
    st.set_page_config(
        page_title = "Entregas H8",
        page_icon = ":package:",
        initial_sidebar_state="collapsed"
    )

    # Inicializa a variável de login como False
    set_session_state("is_logged_in", False)

    # Configura o layout do botão de login
    with stylable_container(
        key="sc_main_page",
        css_styles="""
            button{
                float: right;
            }
            """
    ):
        # Botão de login
        login_button = st.button("LOGIN", type="secondary")

        # Se o botão for pressionado
        if login_button:
            # Troca para a página de login
            st.switch_page(r"pages/login_page.py")

    # Configura o título da página
    st.title("Entregas H8")

    # Extrai a base de dados de moradores
    data_mor = get_data_from_sheets("moradores")

    # Salva a base de dados na session state
    set_session_state("data_mor", data_mor)

    # Se há alguma mensagem de cadastro
    if get_session_state("sent_message") is not None:
        # Exibe a mensagem
        message = get_session_state("sent_message")
        st.success(message)

        # Reseta a variável que armazena a mensagem
        set_session_state("sent_message", None)

    # Extrai o índice do funcionário selecionado
    func_index = get_func_index(get_session_state("func_id"))

    # Input de seleção do funcionário
    funcionario = st.selectbox(label="Nome", options=func_options(), index=func_index,
                               placeholder="Insira aqui seu nome...")

    # Se o funcionário for selecionado
    if funcionario:
        # Armazena o ID do funcionário na session state
        set_session_state("func_id", get_func_id(funcionario))

        # Seleciona a ação a ser realizada
        mode = st.pills(label="Busca", options=["Entrega", "Retirada"],
                      selection_mode="single", default="Entrega", label_visibility="hidden")

        # Reseta a variável do ID de entrega
        set_session_state("ent_id", None)

        # Executa a ação selecionada
        if mode == "Entrega":
            cadastro_entrega.cadastro(data_mor)
        elif mode == "Retirada":
            cadastro_retirada.cadastro(data_mor)

if __name__ == "__main__":
    main()
    # teste