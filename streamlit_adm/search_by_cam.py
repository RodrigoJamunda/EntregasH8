import streamlit as st
import pandas as pd
from PIL import Image
from src.ocr.get_name import get_id

def run_camera_search(data_mor: pd.DataFrame) -> list | None:
    """
    Executa o formulário de busca por imagem

    :param data_mor: pd.DataFrame, dataframe base
    :return: list, o ID da pessoa encontrada
    """

    # Exibe as intruções na tela
    st.subheader("Aponte a câmera para o nome do destinatário")

    # Input de imagem
    cam_input = st.camera_input(label="Tirar foto", label_visibility="hidden")

    # Se a foto for tirada
    if cam_input is not None:
        # Processa a imagem
        image = Image.open(cam_input)

        # Extrai o ID do destinatário
        with st.spinner("Processando imagem..."):
            person_id = get_id(image, data_mor)

        # Retorna o ID do destinatário
        return person_id
