import sys
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

sys.path.append("..")
from sheets import get_data_from_sheets, push_data_to_sheets
from session_state import set_session_state

def format_date(meses: int) -> str:
    """
    Formata o número de meses

    :param meses: int, número de meses
    :return: str, string com o número de meses formatado
    """

    # Formata o número de meses (1 mês, x meses ou 1 ano)
    if meses == 1:
        return "1 mês"
    if meses == 12:
        return "1 ano"
    else:
        return f"{meses} meses"

def delete_data(time: int, keep_unret: bool) -> None:
    """
    Exclui as entregas baseado na data de cadastro

    :param time: int, número de meses a partir do qual as entregas devem ser excluídas
    :param keep_unret: bool, manter as encomendas ainda não retiradas
    :return: None
    """

    # Extrai os dados das entregas
    data_ent = get_data_from_sheets("entregas")

    # Calcula a data a partir da qual as encomendas serão excluídas
    base_date = datetime.now() - relativedelta(months=time)

    # Calcula quais encomendas serão excluídas
    index_data = data_ent[(data_ent["Data"].apply(lambda x:datetime.strptime(x, r"%d/%m/%Y %H:%M:%S")<=base_date))
                          & ~(keep_unret & data_ent["Retirado por"].isna())].index

    # Exclui as encomendas
    data_ent.drop(index_data, inplace=True)

    # Atualiza a base de dados
    push_data_to_sheets("entregas", data_ent)

def main():
    # Configura o layout da página
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    st.title("Entregas H8")
    st.header("Limpar dados")

    # Input do tempo máximo das entregas mantidas
    time = st.selectbox("Manter os dados cadastrados há até:", index=4,
                        options=[1, 2, 3, 6, 12], format_func=format_date)

    # Input do mantimento das entregas não retiradas
    keep_unret = st.checkbox("Manter as entregas que não foram retiradas")

    # Botão de exclusão dos dados
    submit_button = st.button("Excluir dados", type="primary")

    # Se o botão de exclusão for pressionado
    if submit_button:
        # Deleta os dados
        delete_data(time, keep_unret)

        # Envia a mensagem de sucesso
        set_session_state("admin_message", "Histórico de entregas removido com sucesso!")

        # Troca para a página de administrador
        st.switch_page("pages/admin_page.py")

    # Exibe um aviso na tela
    st.markdown("**Atenção!** Após a remoção dos dados, não será possível recuperá-los!")

    # Botão de retorno à página d administrador
    go_back_button = st.button("Cancelar", type="secondary")

    # Se o botão de retorno for pressionado
    if go_back_button:
        # Troca para a página de administrador
        st.switch_page("pages/admin_page.py")


if __name__ == "__main__":
    main()