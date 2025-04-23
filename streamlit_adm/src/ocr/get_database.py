import pandas as pd
import numpy as np
import re
import unicodedata

def normalize(text: str) -> str:
    """
    Normaliza uma palavra para o formato minúsculo, sem acentos

    :param text: str, o texto a ser normalizado
    :return: str, o texto normalizado
    """

    text_normalized = unicodedata.normalize('NFD', text.lower())
    text_without_accents = text_normalized.encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'\W+', '', text_without_accents)


def normalize_string(string: str) -> str:
    """
    Normaliza uma string com espaços para o formato minúsculo, sem acentos

    :param string: str, o texto a ser normalizado
    :return: str, o texto normalizado
    """

    if pd.isnull(string):
        return ""
    else:
        words = string.split()
        words = [normalize(word) for word in words]
        return ' '.join(words)


def normalize_cell(cell: str) -> str | None:
    """
    Normaliza o número de celular, removendo parênteses, espaços e hífens

    :param cell: str, o texto a ser normalizado
    :return: str, o texto normalizado
    """

    if pd.isnull(cell) or cell == np.nan:
        return None
    cell = re.sub(r'\W+', '', cell)
    return cell

def get_norm_database(data: pd.DataFrame, col_nome: str = "Nome", col_tel: str | None = None) -> pd.DataFrame:
    """
    Normaliza a base de dados

    :param data: pd.DataFrame, dataframe a ser normalizada
    :param col_nome: str, coluna que contém o nome do morador
    :param col_tel: str ou None, coluna que contém o número de celular do morador
    :return: pd.DataFrame, a base normalizada
    """

    data_norm = data.copy()

    data_norm[col_nome] = data_norm[col_nome].apply(lambda x: normalize_string(x))
    if col_tel is not None:
        data_norm[col_tel] = data_norm[col_tel].apply(lambda x: normalize_cell(x))

    return data_norm