import io
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="DataPulse | Executive Reports",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS minimalista para interface limpa e moderna
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
""",
    unsafe_allow_html=True,
)


# Geração de Dados Fictícios de Exemplo (Caso o usuário não faça upload)
@st.cache_data
def load_default_data():
    data = {
        "Data": pd.date_range(start="2026-01-01", periods=100, freq="D"),
        "Setor": [
            "Vendas B2B",
            "Suporte",
            "Infraestrutura",
            "Consultoria",
            "Marketing",
        ]
        * 20,
        "Responsável": [
            "Ana Costa",
            "Carlos Silva",
            "Beatriz Souza",
            "Marcos Lima",
            "Julia Dias",
        ]
        * 20,
        "Receita": [1200, 4500, 3200, 8900, 5400] * 20,
        "Satisfação_Cliente": [4.5, 4.8, 3.9, 4.9, 4.2] * 20,
        "Status": ["Concluído", "Pendente", "Em Andamento", "Concluído", "Atrasado"]
        * 20,
    }
    return pd.DataFrame(data)


# Cabeçalho da Aplicação
st.title("📊 DataPulse Executive Dashboard & Reports")
st.markdown(
    "Sistema automatizado de inteligência de negócios para geração de relatórios gerenciais."
)

# Barra Lateral (Filtros e Controles)
st.sidebar.header("⚙️ Configurações do Relatório")

uploaded_file = st.sidebar.file_uploader(
    "Carregar Base de Dados (CSV / Excel)", type=["csv", "xlsx"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
else:
    df = load_default_data()

# Filtros interativos na Sidebar
st.sidebar.subheader("Filtros Globais")
setores_disponiveis = df["Setor"].unique().tolist()
setor_selecionado = st.sidebar.multiselect(
    "Filtrar por Setor", setores_disponiveis, default=setores_disponiveis
)

df_filtrado = df[df["Setor"].isin(setor_selecionado)]

# --- Métricas Principais (KPIs) ---
total_receita = df_filtrado["Receita"].sum()
ticket_medio = df_filtrado["Receita"].mean()
satisfacao_media = df_filtrado["Satisfação_Cliente"].mean()
total_transacoes = len(df_filtrado)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Receita Total", f"R$ {total_receita:,.2f}")
col2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("Satisfação Média", f"{satisfacao_media:.2f} / 5.0")
col4.metric("Volume de Registros", f"{total_transacoes}")

st.markdown("---")

# --- Visualizações Gráficas ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Receita por Setor")
    fig_setor = px.bar(
        df_filtrado.groupby("Setor")["Receita"].sum().reset_index(),
        x="Setor",
        y="Receita",
        color="Setor",
        template="plotly_dark",
    )
    st.plotly_chart(fig_setor, use_container_width=True)

with row1_col2:
    st.subheader("Evolução Temporal da Receita")
    if "Data" in df_filtrado.columns:
        df_filtrado["Data"] = pd.to_datetime(df_filtrado["Data"])
        fig_tempo = px.line(
            df_filtrado.groupby("Data")["Receita"].sum().reset_index(),
            x="Data",
            y="Receita",
            template="plotly_dark",
        )
        st.plotly_chart(fig_tempo, use_container_width=True)

st.markdown("---")

# --- Visualização de Dados Tabeados ---
st.subheader("🔍 Detalhamento dos Registros Filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# --- Módulo de Exportação Gratuita de Relatórios ---
st.markdown("---")
st.subheader("📥 Exportar Relatório Executivo")


def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode("utf-8")


col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    csv_data = convert_df_to_csv(df_filtrado)
    st.download_button(
        label="Baixar Relatório em CSV",
        data=csv_data,
        file_name="relatorio_gerencial.csv",
        mime="text/csv",
    )

with col_exp2:
    # Exportação em Excel usando openpyxl (nativo no Pandas)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name="Relatorio_Executivo")
    excel_data = output.getvalue()

    st.download_button(
        label="Baixar Relatório em Excel (.xlsx)",
        data=excel_data,
        file_name="relatorio_gerencial.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )