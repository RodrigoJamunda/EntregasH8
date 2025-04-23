import streamlit as st
from streamlit_gsheets import GSheetsConnection

def get_url(sheet_name):
    if sheet_name == 'moradores':
        return "https://docs.google.com/spreadsheets/d/1fRz_OI2e6Fh2v6stKWZIsb1dbu-23mThGEC4BdlSTj4/edit?usp=sharing"
    if sheet_name == 'funcionarios':
        return "https://docs.google.com/spreadsheets/d/1RKV0RzNmZ7oKhEJK6GQqVQUEnFCHkQXlXQE-RG1oBBM/edit?usp=sharing"
    if sheet_name == 'entregas':
        return "https://docs.google.com/spreadsheets/d/1vrPznaP9T1QhdXFAtPaLDyJ-q3W5lqNoDR1BEyd85uE/edit?usp=sharing"

@st.cache_data(show_spinner=False)
def get_data_from_sheets(sheet_name):
    with st.spinner("Carregando dados..."):
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=get_url(sheet_name))

    return df

def push_data_to_sheets(sheet_name, data):
    with st.spinner("Carregando dados..."):
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(spreadsheet=get_url(sheet_name), data=data)
        st.cache_data.clear()