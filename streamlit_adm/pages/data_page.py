import os, sys
import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

sys.path.append("..")
from sheets import get_data_from_sheets, push_data_to_sheets
from session_state import set_session_state

def format_date(meses):
    if meses == 1:
        return "1 mês"
    if meses == 12:
        return "1 ano"
    else:
        return f"{meses} meses"

def delete_data(time, keep_unret):
    database = get_data_from_sheets("entregas")
    base_date = datetime.now() - relativedelta(months=time)
    index_data = database[(database["Data"].apply(lambda x:datetime.strptime(x, r"%d/%m/%Y %H:%M:%S")<=base_date))
                          & ~(keep_unret & database["Retirado por"].isna())].index

    database.drop(index_data, inplace=True)
    push_data_to_sheets("entregas", database)

def main():
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    st.title("Entregas H8")

    st.header("Limpar dados")

    time = st.selectbox("Manter os dados cadastrados há até:", index=4,
                        options=[1, 2, 3, 6, 12], format_func=format_date)

    keep_unret = st.checkbox("Manter as entregas que não foram retiradas")

    submit_button = st.button("Excluir dados", type="primary")

    if submit_button:
        delete_data(time, keep_unret)
        set_session_state("admin_message", "Histórico de entregas removido com sucesso!")
        st.switch_page("pages/admin_page.py")

    st.markdown("**Atenção!** Após a remoção dos dados, não será possível recuperá-los!")

    if st.button("Cancelar", type="secondary"):
        st.switch_page("pages/admin_page.py")


if __name__ == "__main__":
    main()