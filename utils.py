# utils.py
# ------------------------------
# Funções auxiliares da aplicação Telemarketing Analysis

import pandas as pd
import streamlit as st
from io import BytesIO


# ------------------------------
# Leitura de dados
# ------------------------------
@st.cache_data(show_spinner=True)
def load_data_any(file_or_path):
    """Lê CSV (sep=';') ou Excel, de uploader ou caminho local."""
    try:
        return pd.read_csv(file_or_path, sep=';')
    except:
        return pd.read_excel(file_or_path)


# ------------------------------
# Filtro múltiplo com opção "Todos"
# ------------------------------
def multiselect_filter(df, column, selected):
    """Aplica filtro em uma coluna com opção de selecionar 'Todos'."""
    if 'Todos' in selected or not selected:
        return df
    return df[df[column].isin(selected)].reset_index(drop=True)


# ------------------------------
# Conversão para Excel (download)
# ------------------------------
def to_excel_bytes(df):
    """Converte um DataFrame em bytes de Excel para download."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()
