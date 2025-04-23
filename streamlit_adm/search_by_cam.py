import streamlit as st
import pandas as pd
from PIL import Image
from src.ocr.get_name import get_id

def run_camera_search(data: pd.DataFrame) -> int:
    """
    Executa o formulário de busca por imagem

    :param data: pd.DataFrame, dataframe base
    :return: int, o ID da pessoa encontrada
    """

    # Mostra as intruções na tela
    st.subheader("Aponte a câmera para o nome do destinatário")

    # Cria uma caixa de input de imagem
    cam_input = st.camera_input(label="Tirar foto", label_visibility="hidden")

    # Se uma foto é tirada
    if cam_input is not None:
        # Processa a imagem
        image = Image.open(cam_input)

        # Extrai o nome e o ID do destinatário
        with st.spinner("Processando imagem..."):
            person_id = get_id(image, data)

        return person_id
