import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sistema de Orçamentos",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ Orçamentos de Depósitos de Construção")
st.markdown(
    "Aplicação para análise e comparação de preços de materiais de construção."
)


@st.cache_data(show_spinner="Carregando dados...")
def carregar_dados() -> pd.DataFrame:
    """Carrega os dados do arquivo Excel."""
    df = pd.read_excel("data/Material.xlsx")

    df["Valor Un"] = pd.to_numeric(df["Valor Un"], errors="coerce")
    df["Qnt"] = pd.to_numeric(df["Qnt"], errors="coerce")
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
    return df

# Carregar dados
df = carregar_dados()



# Filtro por local
fornecedor_selecionado = st.selectbox(
    "Selecione o local",
    [
        "GG",
        "Doce Lar",
        "Recomp",
        "Mix Acab.",
    ]
)

df_filtrado = df[df["Local"] == fornecedor_selecionado]

st.subheader(f"📊 Dados filtrados - {fornecedor_selecionado}")
st.dataframe(df_filtrado)

# Cálculos
total_valor = df_filtrado["Total"].sum()
quantidade_itens = df_filtrado.shape[0]

# Exibir métricas
col1, col2 = st.columns(2)

col1.metric("💰 Total (R$)", f"{total_valor:,.2f}")
col2.metric("📦 Quantidade de itens", quantidade_itens)







# Garantir que Total é numérico
df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

# Índice das menores linhas por Descrição
idx = df.groupby("Descrição")["Total"].idxmin()

# Novo DataFrame com os menores valores
df_menor_valor = df.loc[idx].reset_index(drop=True)

st.subheader("Menor valor por item", divider=True)
st.dataframe(df_menor_valor)

# Cálculos
total_geral = df_menor_valor["Total"].sum()
quantidade_itens_menor = df_menor_valor.shape[0]

# Criar colunas antes de usar
col1, col2 = st.columns(2)

col1.metric("💰 Melhor custo total (R$)", f"{total_geral:,.2f}")
col2.metric("📦 Quantidade de itens", quantidade_itens_menor)


# Economia
economia = total_valor - total_geral

# Exibir economia
st.subheader("💸 Economia", divider=True)

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total selecionado", f"{total_valor:,.2f}")
col2.metric("🏆 Melhor custo possível", f"{total_geral:,.2f}")
col3.metric("💸 Economia", f"{economia:,.2f}")