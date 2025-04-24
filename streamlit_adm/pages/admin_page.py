import os, sys
import streamlit as st
import pandas as pd
import openpyxl

sys.path.append("..")
from session_state import set_session_state, get_session_state
from sheets import get_data_from_sheets

def get_download_data():
    dirname = os.path.dirname(__file__)
    temp_path = os.path.join(dirname, r".\temp")
    sheet_path = os.path.join(dirname, r".\temp\sheet.xlsx")

    df = get_data_from_sheets("moradores")
    if not os.path.exists(sheet_path):
        os.mkdir(temp_path)

    df.to_excel(sheet_path, index=False, sheet_name="Entregas", engine="openpyxl")
    with open(sheet_path, 'rb') as sheet:
        return sheet.read()

def main():
    st.set_page_config(
        page_title="Entregas H8",
        page_icon=":package:",
        initial_sidebar_state="collapsed"
    )

    if get_session_state("is_logged_in") == False:
        st.switch_page(r"pages\login_page.py")

    st.title("Área do administrador")

    if get_session_state("admin_message") is not None:
        message = get_session_state("admin_message")
        st.success(message)
        set_session_state("admin_message", None)

    manage_func = st.button(label="Gerenciar funcionários", type="secondary")

    if manage_func:
        st.switch_page(r"pages/func_page.py")

    st.download_button(label="Baixar planilha de entregas", file_name="entregas_h8.xlsx",
                       data=get_download_data(), on_click="rerun", icon=":material/download:", type="secondary")

    manage_data = st.button(label="Excluir histórico de entregas", type="secondary")

    if manage_data:
        st.switch_page(r"pages/data_page.py")



if __name__ == '__main__':
    main()