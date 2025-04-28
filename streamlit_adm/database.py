import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from func import get_func_name
from sheets import get_data_from_sheets, push_data_to_sheets

def get_database() -> pd.DataFrame:
    """
    Extrai a base de dados de entregas

    :return: pd.DataFrame, a base de dados de entregas
    """

    return get_data_from_sheets("entregas", clear_cache=True)

def get_name(data_mor: pd.DataFrame, person_id: list) -> str:
    """
    Extrai o nome do destinatário ou destinatários

    :param data_mor: pd.DataFrame, base de dados dos moradores
    :param person_id: list, ID ou IDs dos destinatários
    :return: str, os nomes dos destinatários
    """

    # Inicializa a lista de nomes
    names = []

    # Para cada destinatário
    for id_mor in person_id:
        # Adiciona o seu nome à lista
        names.append(data_mor[data_mor["ID"] == id_mor]["Nome"].item())

    # Formata os nomes em uma string
    name = ";".join(names)

    # Retorna a string formatada
    return name

def update_database(data_mor: pd.DataFrame, person_id: list, func_id: int, id_enc: str) -> None:
    """
    Adiciona uma entrega à base de dados

    :param data_mor: pd.DataFrame, base de dados dos moradores
    :param person_id: list, ID ou IDs dos destinatários
    :param func_id: int, ID do funcionário que cadastrou a entrega
    :param id_enc: ID da entrega
    :return: None
    """

    # Extrai a base de dados de entregas
    data_ent = get_database()

    # Extrai o nome do destinatário ou destinatários
    name_dest = get_name(data_mor, person_id)

    # Extrai a data do cadastro
    date_ent =  datetime.now() + relativedelta(hours=-3)

    # Cria a nova linha da base de dados
    new_entry = [id_enc, name_dest, get_func_name(func_id),
                 None, date_ent.strftime("%d/%m/%Y %H:%M:%S")]

    # Adiciona a nova linha à base de dados
    data_ent.loc[len(data_ent)] = new_entry

    # Salva a base de dados atualizada
    push_data_to_sheets("entregas", data_ent)

def update_ret(name_ret: str, ids: list) -> None:
    """
    Atualiza a retirada de entregas

    :param name_ret: str, nome da retirada
    :param ids: list, IDs das entregas retiradas
    :return: None
    """

    # Extrai a base de dados de entregas
    data_ent = get_database()

    # Para cada entrega retirada
    for id_ent in ids:
        # Marca a retirada
        data_ent["Retirado por"].loc[data_ent["ID"] == id_ent] = name_ret

    # Salva a base de dados atualizada
    push_data_to_sheets("entregas", data_ent)
