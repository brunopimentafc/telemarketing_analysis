# telemarketing_clean.py

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Configuração da página
st.set_page_config(
    page_title="Telemarketing Analysis",
    layout="wide",
    page_icon="📊"
)

# Título
st.title("📊 Telemarketing Analysis")

# Caminho dos dados
DATA_PATH = os.path.join("data", "input", "bank-additional-full.csv")

# Função para carregar dados
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, sep=';')
        return df
    else:
        st.error("🚨 Envie um arquivo CSV/XLSX ou coloque o CSV em 'data/input/'.")
        return None

# Upload manual ou leitura automática
uploaded_file = st.file_uploader("Bank marketing data", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, sep=';')
    else:
        df = pd.read_excel(uploaded_file)
else:
    df = load_data()

# Verifica se há dados
if df is not None:
    st.sidebar.header("Filtros")
    
    # Filtros interativos
    job_filter = st.sidebar.multiselect("Job", df['job'].unique(), default=df['job'].unique())
    marital_filter = st.sidebar.multiselect("Marital", df['marital'].unique(), default=df['marital'].unique())
    education_filter = st.sidebar.multiselect("Education", df['education'].unique(), default=df['education'].unique())

    df_filtered = df[
        (df['job'].isin(job_filter)) &
        (df['marital'].isin(marital_filter)) &
        (df['education'].isin(education_filter))
    ]

    # Exibe os dados filtrados
    st.subheader("📄 Dados filtrados")
    st.dataframe(df_filtered.head(10))

    st.markdown("---")

    # Gráficos
    st.subheader("📈 Distribuição da variável alvo")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.countplot(data=df_filtered, x='y', palette='viridis', ax=ax1)
    ax1.set_title('Distribuição da variável alvo (y)')
    st.pyplot(fig1)

    st.subheader("💼 Distribuição por profissão")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    job_counts = df_filtered['job'].value_counts().reset_index()
    sns.barplot(data=job_counts, x='index', y='job', palette='coolwarm', ax=ax2)
    ax2.set_xlabel("Profissão")
    ax2.set_ylabel("Contagem")
    ax2.set_title("Distribuição de contatos por profissão")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    st.subheader("📞 Duração da chamada vs resultado")
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df_filtered, x='y', y='duration', palette='crest', ax=ax3)
    ax3.set_title("Duração das chamadas por resultado")
    st.pyplot(fig3)

else:
    st.warning("Nenhum dado foi carregado ainda. Por favor, envie um arquivo CSV/XLSX.")
