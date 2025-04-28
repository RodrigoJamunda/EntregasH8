import pandas as pd
from sheets import get_data_from_sheets, push_data_to_sheets

def get_func_data() -> pd.DataFrame:
    """
    Extrai a base de dados de funcionários

    :return: pd.DataFrame, a base de dados de funcionários
    """

    return get_data_from_sheets("funcionarios")

def add_func(nome: str) -> None:
    """
    Adiciona um funcionário à base de dados

    :param nome: str, nome do funcionário
    :return: None
    """

    # Extrai a base de dados de funcionários
    data_func = get_func_data()

    # Gera um novo ID para o funcionário
    new_id = 0 if len(data_func) == 0 else data_func.iloc[-1]["ID"] + 1

    # Gera e adiciona uma nova linha à base de dados
    data_func.loc[len(data_func)] = [new_id, nome]

    # Salva a base de dados atualizada
    push_data_to_sheets("funcionarios", data_func)

def remove_func(nome) -> None:
    """
    Remove um funcionário da base de dados

    :param nome: str, nome do funcionário
    :return: None
    """

    # Extrai a base de dados de funcionários
    data_func = get_func_data()

    # Exclui os dados do funcionário
    data_func.drop(data_func.index[data_func["Nome"]==nome], inplace=True)

    # Salva a base de dados atualizada
    push_data_to_sheets("funcionarios", data_func)

def func_options() -> list:
    """
    Extrai o nome dos funcionários em ordem alfabética

    :return: list, a lista de nomes dos funcionários
    """

    # Extrai a base de dados de funcionários
    data_func = get_func_data()

    # Retorna a lista de nomes
    return sorted(data_func["Nome"])

def get_func_id(func_name: str) -> int:
    """
    Extrai o ID de um funcionário

    :param func_name: str, nome do funcionário
    :return: int, o ID do funcionário
    """

    # Extrai a base de dados de funcionários
    data_func = get_func_data()

    # Extrai e retorna o ID do funcionário
    return data_func[data_func["Nome"]==func_name]["ID"].item()

def get_func_name(func_id: int) -> str:
    """
    Extrai o nome de um funcionário

    :param func_id: int, o ID do funcionário
    :return: str, o nome do funcionário
    """

    # Extrai a base de dados de funcionários
    data_func = get_func_data()

    # Extrai e retorna o nome do funcionário
    return data_func[data_func["ID"]==func_id]["Nome"].item()

def get_func_index(func_id: int | None) -> int | None:
    """
    Extrai o índice do funcionário na lista de nomes

    :param func_id: int ou None, ID do funcionário
    :return: int ou None, o índice do funcionário
    """

    # Se nenhum funcionário for selecionado, retorna None
    if func_id is None:
        return None

    # Extrai a lista de nomes
    options = func_options()

    i = 0
    # Para cada funcionário
    for func_name in options:
        # Retorna se o funcionário for encontrado
        if get_func_id(func_name) == func_id:
            return i
        i = i+1

    return None