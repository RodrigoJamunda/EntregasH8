import streamlit as st
import typing

def init_session_state(key: str, value: typing.Any) -> None:
    """
    Inicializa um valor no st.session_state, caso ele não tenha sido inicializado antes

    :param key: chave do st.session_state
    :param value: valor associado à chave
    :return: None
    """

    if key not in st.session_state:
        st.session_state[key] = value

def set_session_state(key: str, value: typing.Any) -> None:
    """
    Altera um valor do st.session_state

    :param key: chave do st.session_state
    :param value: valor associado à chave
    :return: void
    """

    st.session_state[key] = value

def get_session_state(key: str, default: typing.Any | None = None) -> typing.Any:
    """
    Retorna um valor do st.session_state

    :param key: chave do st.session_state
    :param default: valor retornado caso a chave não exista (default: None)
    :return: st.session_state.value, valor associado à chave
    """

    if key in st.session_state:
        return st.session_state[key]

    return default
