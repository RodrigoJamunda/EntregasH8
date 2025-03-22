import os
from google import genai
import pandas as pd
from .get_database import normalize_string, get_norm_database
from rapidfuzz import fuzz, process

def get_genai_key(filename: str) -> str:
    """
    Retorna a chave da API da Gemini AI

    :param filename: str, o caminho relativo até o arquivo contendo a chave
    :return: str, a chave da API
    """

    # Computa o caminho completo do arquivo
    dirname = os.path.dirname(__file__)
    full_path = os.path.join(dirname, filename)

    # Abre o arquivo e retorna seu conteúdo
    with open(full_path, 'r') as file:
        api_key = file.read().strip()
        if api_key == "":
            raise FileNotFoundError("API key vazia! Certifique-se de preenchê-la antes de executar o código.")
        return api_key

def get_text_from_image(image) -> str:
    """
    Extrai o texto de uma imagem utilizando a API da Gemini AI

    :param image: imagem a ser processada
    :return: str, o texto extraído
    """

    # Configura a API
    client = genai.Client(api_key=get_genai_key('gemini_api_key.txt'))

    # Requisita a leitura da imagem
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=["Extraia o nome do destinatário dessa entrega e retorne uma string simples contendo esse nome",
                  image]
    )

    # Retorna o texto lido
    return response.text


def get_best_match(nome: str, data: pd.DataFrame) -> str:
    """
    Processa uma string e retorna a melhor correspondência a partir de uma base de dados usando Fuzzy Matching

    :param nome: str, o texto a ser comparado com a base de dados
    :param data: pd.DataFrame, a base de dados
    :return: str, a melhor correspondência do texto
    """

    # Extrai a melhor correspondência usando Partial Fuzzy Matching
    best_match = process.extractOne(nome, data["Nome"], scorer=fuzz.partial_ratio)
    return best_match[0]

def get_id(image, data: pd.DataFrame) -> int:
    """
    Extrai o ID do destinatário a partir da imagem

    :param image: imagem a ser processada
    :param data: pd.DataFrame, a base de dados de todos os moradores
    :return: int, o ID extraído
    """

    # Normaliza a base de dados
    norm_database = get_norm_database(data)

    # Extrai e normaliza o nome mostrado na imagem
    nome = get_text_from_image(image)
    norm_nome = normalize_string(nome)

    # Retorna a melhor correspondência do nome encontrado
    best_match = get_best_match(norm_nome, norm_database)
    return norm_database[norm_database["Nome"] == best_match]["ID"].item()
