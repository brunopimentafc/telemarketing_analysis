# -*- coding: utf-8 -*-
# =========================
# Telemarketing Analysis App (Fully Fixed)
# =========================

import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="Telemarketing analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------
# Seaborn theme
# -------------------------------
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)


# -------------------------------
# Utility functions
# -------------------------------
@st.cache_data(show_spinner=True)
def load_data_any(file_or_path):
    """Reads CSV (sep=';') or Excel, works for uploader or local file."""
    try:
        return pd.read_csv(file_or_path, sep=";")
    except Exception:
        return pd.read_excel(file_or_path)


def multiselect_filter(df, col, selected):
    """Filter with multiselect + 'all' option."""
    if "all" in selected:
        return df
    return df[df[col].isin(selected)].reset_index(drop=True)


@st.cache_data
def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to Excel bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()


# -------------------------------
# Streamlit App
# -------------------------------
def main():
    st.title("📊 Telemarketing analysis")
    st.markdown("---")

    # Sidebar image
    try:
        img = Image.open("img/Bank-Branding.jpg")
        st.sidebar.image(img, use_container_width=True)
    except FileNotFoundError:
        st.sidebar.info("📷 Coloque 'img/Bank-Branding.jpg' na pasta 'img'.")

    # Sidebar data source
    st.sidebar.subheader("Fonte dos dados")
    uploaded = st.sidebar.file_uploader("Bank marketing data", type=["csv", "xlsx"])

    if uploaded is not None:
        bank_raw = load_data_any(uploaded)
    else:
        try:
            bank_raw = load_data_any("data/input/bank-additional-full.csv")
        except Exception:
            st.error("❌ Envie um arquivo CSV/XLSX ou coloque o CSV em 'data/input/'.")
            return

    bank = bank_raw.copy()

    # Initial preview
    st.subheader("Antes dos filtros")
    st.dataframe(bank_raw.head())
    st.markdown("---")

    # -------------------------------
    # Sidebar filters
    # -------------------------------
    with st.sidebar.form(key="filtros"):
        st.markdown("### 🎛️ Filtros")

        graph_type = st.radio("Tipo de gráfico:", ("Barras", "Pizza"))

        min_age = int(bank["age"].min())
        max_age = int(bank["age"].max())
        idades = st.slider("Idade", min_value=min_age, max_value=max_age,
                           value=(min_age, max_age), step=1)

        def opts(col):
            lst = sorted(map(str, bank[col].dropna().unique().tolist()))
            return lst + ["all"]

        jobs_selected = st.multiselect("Profissão", opts("job"), ["all"])
        marital_selected = st.multiselect("Estado civil", opts("marital"), ["all"])
        default_selected = st.multiselect("Default", opts("default"), ["all"])
        housing_selected = st.multiselect("Tem financiamento imob?", opts("housing"), ["all"])
        loan_selected = st.multiselect("Tem empréstimo?", opts("loan"), ["all"])
        contact_selected = st.multiselect("Meio de contato", opts("contact"), ["all"])
        month_selected = st.multiselect("Mês do contato", opts("month"), ["all"])
        day_of_week_selected = st.multiselect("Dia da semana", opts("day_of_week"), ["all"])

        submit = st.form_submit_button("Aplicar filtros")

    # -------------------------------
    # Apply filters
    # -------------------------------
    bank = bank.query("age >= @idades[0] and age <= @idades[1]")
    bank = multiselect_filter(bank, "job", jobs_selected)
    bank = multiselect_filter(bank, "marital", marital_selected)
    bank = multiselect_filter(bank, "default", default_selected)
    bank = multiselect_filter(bank, "housing", housing_selected)
    bank = multiselect_filter(bank, "loan", loan_selected)
    bank = multiselect_filter(bank, "contact", contact_selected)
    bank = multiselect_filter(bank, "month", month_selected)
    bank = multiselect_filter(bank, "day_of_week", day_of_week_selected)

    # -------------------------------
    # After filters
    # -------------------------------
    st.subheader("Após os filtros")
    st.dataframe(bank.head())

    df_xlsx = to_excel_bytes(bank)
    st.download_button(
        label="📥 Download tabela filtrada (Excel)",
        data=df_xlsx,
        file_name="bank_filtered.xlsx",
    )

    st.markdown("---")

    # -------------------------------
    # Acceptance proportion tables
    # -------------------------------
    st.subheader("Proporção de aceite (y)")

    # Original data
    bank_raw_target_perc = (
        bank_raw["y"].value_counts(normalize=True).mul(100).sort_index().to_frame(name="Proporção (%)")
    ).reset_index().rename(columns={"index": "y"})

    # Filtered data
    if not bank.empty and "y" in bank.columns:
        bank_target_perc = (
            bank["y"].value_counts(normalize=True).mul(100).sort_index().to_frame(name="Proporção (%)")
        ).reset_index().rename(columns={"index": "y"})
    else:
        bank_target_perc = pd.DataFrame(columns=["y", "Proporção (%)"])

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Proporção original")
        st.dataframe(bank_raw_target_perc)
        st.download_button(
            "📥 Download (Excel)",
            data=to_excel_bytes(bank_raw_target_perc),
            file_name="bank_raw_y.xlsx",
        )

    with col2:
        st.write("### Proporção filtrada")
        st.dataframe(bank_target_perc)
        st.download_button(
            "📥 Download (Excel)",
            data=to_excel_bytes(bank_target_perc),
            file_name="bank_filtered_y.xlsx",
        )

    st.markdown("---")

    # -------------------------------
    # Charts: acceptance comparison
    # -------------------------------
    st.subheader("Visualização da proporção de aceite")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))

    if graph_type == "Barras":
        sns.barplot(x="y", y="Proporção (%)", data=bank_raw_target_perc, ax=ax[0])
        ax[0].bar_label(ax[0].containers[0])
        ax[0].set_title("Dados brutos", fontweight="bold")

        if not bank_target_perc.empty:
            sns.barplot(x="y", y="Proporção (%)", data=bank_target_perc, ax=ax[1])
            ax[1].bar_label(ax[1].containers[0])
            ax[1].set_title("Dados filtrados", fontweight="bold")
        else:
            ax[1].set_visible(False)

    else:
        bank_raw_target_perc.set_index("y").plot(
            kind="pie", y="Proporção (%)", autopct="%.2f%%", ax=ax[0], legend=False
        )
        ax[0].set_ylabel("")
        ax[0].set_title("Dados brutos", fontweight="bold")

        if not bank_target_perc.empty:
            bank_target_perc.set_index("y").plot(
                kind="pie", y="Proporção (%)", autopct="%.2f%%", ax=ax[1], legend=False
            )
            ax[1].set_ylabel("")
            ax[1].set_title("Dados filtrados", fontweight="bold")
        else:
            ax[1].set_visible(False)

    st.pyplot(fig)


# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    main()
