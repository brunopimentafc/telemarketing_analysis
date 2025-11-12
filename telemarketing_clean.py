# telemarketing_clean.py
# ------------------------------
# Dashboard interativo - Telemarketing Analysis

import streamlit as st
import plotly.express as px
import pandas as pd
from utils import load_data_any, multiselect_filter, to_excel_bytes

# ------------------------------
# Configuração da página
# ------------------------------
st.set_page_config(
    page_title='Telemarketing Analysis',
    page_icon='📊',
    layout='wide'
)

st.title("📊 Telemarketing Analysis")
st.markdown("---")

# ------------------------------
# Leitura dos dados
# ------------------------------
DATA_PATH = "data/input/bank-additional-full.csv"
df_raw = load_data_any(DATA_PATH)

st.sidebar.header("Filtros")
# ------------------------------
# Filtros dinâmicos
# ------------------------------
filt_age = st.sidebar.multiselect("Idade", sorted(df_raw["age"].unique()), default=['Todos'])
filt_job = st.sidebar.multiselect("Profissão", sorted(df_raw["job"].unique()), default=['Todos'])
filt_contact = st.sidebar.multiselect("Tipo de Contato", sorted(df_raw["contact"].unique()), default=['Todos'])

df_filtered = multiselect_filter(df_raw, "age", filt_age)
df_filtered = multiselect_filter(df_filtered, "job", filt_job)
df_filtered = multiselect_filter(df_filtered, "contact", filt_contact)

# ------------------------------
# Proporção de aceite (variável 'y')
# ------------------------------
def calc_acceptance_rate(df):
    y_counts = df["y"].value_counts(normalize=True) * 100
    return pd.DataFrame(y_counts).reset_index().rename(columns={"index": "y", "y": "%"})


st.subheader("📈 Proporção de aceite (y)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Proporção original**")
    prop_raw = calc_acceptance_rate(df_raw)
    st.dataframe(prop_raw, hide_index=True)
    st.download_button("📥 Download (Excel)", to_excel_bytes(prop_raw), file_name="proporcao_original.xlsx")

with col2:
    st.markdown("**Proporção filtrada**")
    if len(df_filtered) > 0:
        prop_filtered = calc_acceptance_rate(df_filtered)
        st.dataframe(prop_filtered, hide_index=True)
        st.download_button("📥 Download (Excel)", to_excel_bytes(prop_filtered), file_name="proporcao_filtrada.xlsx")
    else:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")

st.markdown("---")

# ------------------------------
# Visualização interativa
# ------------------------------
st.subheader("📊 Visualização da proporção de aceite")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.pie(prop_raw, names='y', values='%', title='Dados Brutos - Proporção de aceite')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    if len(df_filtered) > 0:
        fig2 = px.pie(prop_filtered, names='y', values='%', title='Dados Filtrados - Proporção de aceite')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Aguardando seleção de filtros para exibir gráfico filtrado.")
