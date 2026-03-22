import streamlit as st
import pandas as pd
import plotly.express as px
from decimal import Decimal


st.set_page_config(
    page_title="Orçamentos Denis",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ Orçamentos de Depósitos")
st.markdown(
    "Análise e comparação de preços de materiais de construção."
)


@st.cache_data(show_spinner="Carregando dados...")
def carregar_dados() -> pd.DataFrame:
    """Carrega os dados do arquivo Excel."""
    df = pd.read_excel("data/Material.xlsx")

    df["Valor Un"] = pd.to_numeric(df["Valor Un"], errors="coerce")
    df["Qnt"] = pd.to_numeric(df["Qnt"], errors="coerce")
    df["Total"] = df["Valor Un"] * df["Qnt"]
    return df

# Carregar dados
df = carregar_dados()


# Filtro por local
fornecedor_selecionado = st.selectbox(
    "Selecione o depósito local",
    [
        "GG",
        "Doce Lar",
        "Recomp",
        "Mix Acab.",
    ]
)

df_filtrado = df[df["Local"] == fornecedor_selecionado]

st.subheader(f"📊 Dados filtrados - {fornecedor_selecionado}")
st.dataframe(
    df_filtrado[["Descrição", "Qnt", "Valor Un", "Total"]],
    hide_index=True,  # oculta o índice
    column_config={
        "Valor Un": st.column_config.NumberColumn("Valor Un", format="R$ %.2f"),
        "Total": st.column_config.NumberColumn("Total", format="R$ %.2f"),
    },
)

# Cálculos
total_valor = df_filtrado["Total"].sum()
quantidade_itens = df_filtrado.shape[0]

# Exibir métricas
col1, col2 = st.columns(2)

col1.metric("💰 Total Geral", f"R$ {total_valor:,.2f}")
col2.metric("📦 Quantidade de itens", quantidade_itens)







st.subheader("Menor valor por item", divider=True)

# Filtro aplicado ANTES de calcular o menor valor
categoria_selecionada = st.pills("Filtrar por categoria", ["Apenas comércio local"])

if categoria_selecionada == "Apenas comércio local":
    df_base = df[df["Categoria"] == "Local"]
else:
    df_base = df

# Índice das menores linhas por Descrição (usando df_base filtrado)
idx = df_base.groupby("Descrição")["Total"].idxmin()

# Novo DataFrame com os menores valores
df_menor_valor = df_base.loc[idx].reset_index(drop=True)

st.dataframe(
    df_menor_valor[["Local", "Descrição", "Qnt", "Valor Un", "Total"]],
    hide_index=True,
    width='stretch',
    column_config={
        "Valor Un": st.column_config.NumberColumn("Valor Un", format="R$ %.2f"),
        "Total": st.column_config.NumberColumn("Total", format="R$ %.2f"),
    },
)

# Cálculos
total_geral = df_menor_valor["Total"].sum()
quantidade_itens_menor = df_menor_valor.shape[0]

col3, col4 = st.columns(2)
col3.metric("💰 Melhor custo total", f"R$ {total_geral:,.2f}")
col4.metric("📦 Quantidade de itens", quantidade_itens_menor)

# Economia
economia = total_valor - total_geral

st.subheader("💸 Economia", divider=True)

col5, col6, col7 = st.columns(3)

economia = Decimal(economia)
total_valor = Decimal(total_valor)

percentual_economia = (
    (economia / total_valor) * Decimal(100)
    if total_valor > 0
    else Decimal("0.0")
)

col5.metric("💰 Selecionado: " f"{fornecedor_selecionado}", f"R$ {total_valor:,.2f}")
col6.metric("🏆 Melhor custo possível", f"R$ {total_geral:,.2f}")
col7.metric(
    "💸 Economia",
    f"R$ {economia:,.2f}",
    delta=f"{percentual_economia:.1f}%"
)


st.subheader("Valor Por Item", divider=True)

itens = df["Descrição"].unique().tolist()
itens_selecionada = st.selectbox("Filtrar por Itens", itens)

itens_df = (
    df[df["Descrição"] == itens_selecionada]
    .sort_values(by="Valor Un", ascending=True)
)

# Detecta se é mobile pelo número de itens (layout adaptativo)
n_locais = itens_df["Local"].nunique()
altura = max(400, n_locais * 55)  # altura dinâmica conforme quantidade de barras

fig = px.bar(
    itens_df,
    x="Local",
    y="Valor Un",
    text="Valor Un",
    title=f"{itens_selecionada}",
    labels={"Valor Un": "Valor Unitário (R$)", "Local": "Local"},
    color="Valor Un",
    color_continuous_scale="RdYlGn_r",
    custom_data=["Descrição", "Qnt", "Total"],
)

fig.update_traces(
    texttemplate="R$ %{y:,.2f}",
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "────────────────<br>"
        "📦 Item: %{customdata[0]}<br>"
        "🔢 Quantidade: %{customdata[1]}<br>"
        "💰 Valor Un: R$ %{y:,.2f}<br>"
        "🧾 Total: R$ %{customdata[2]:,.2f}<br>"
        "<extra></extra>"
    ),
)

fig.update_layout(
    coloraxis_showscale=False,
    yaxis_tickprefix="R$ ",
    yaxis_tickformat=",.2f",
    xaxis_tickangle=-35,
    height=altura,
    margin=dict(l=10, r=10, t=50, b=80),  # margens menores para mobile
    font=dict(size=12),
    title=dict(font=dict(size=15), x=0.5),  # título centralizado
    xaxis=dict(
        tickfont=dict(size=11),
        automargin=True,  # evita corte dos labels no mobile
    ),
    yaxis=dict(
        tickfont=dict(size=11),
        automargin=True,
    ),
)

# Tabela responsiva — menos colunas em telas pequenas
st.dataframe(
    itens_df[["Local", "Descrição", "Qnt", "Valor Un", "Total"]],
    hide_index=True,
    width='stretch',
    column_config={
        "Descrição": st.column_config.TextColumn("Descrição", width="medium"),
        "Qnt": st.column_config.NumberColumn("Qtd", format="%d"),
        "Valor Un": st.column_config.NumberColumn("Valor Un", format="R$ %.2f"),
        "Total": st.column_config.NumberColumn("Total", format="R$ %.2f"),
    },
)

st.plotly_chart(
    fig,
    width='stretch',
    config={
        "scrollZoom": False,        # evita zoom acidental no mobile
        "displayModeBar": False,    # esconde toolbar (limpa UI mobile)
        "responsive": True,         # adapta ao tamanho da tela
    },
)

# Exportar
df_export = df.drop(columns=["Total"], errors="ignore")
csv = df_export.to_csv(index=False, sep=";").encode("utf-8-sig")

st.download_button(
    label="📥 Exportar Dados",
    data=csv,
    file_name="Orcamentos.csv",
    mime="text/csv",
    width='stretch',   # botão ocupa largura total no mobile
)