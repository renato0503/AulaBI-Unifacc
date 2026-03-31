"""
=============================================================================
  DASHBOARD DE BI - HOSPITAL MUNICIPAL
  Modelagem Star Schema com Streamlit + Plotly
=============================================================================
  Autor  : Engenheiro de Dados / Aula Prática - Unifacc
  Arquivo: app.py
  Comando: streamlit run app.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard BI - Hospital Municipal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS CSS CUSTOMIZADOS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fundo e tipografia geral */
    .main { background-color: #0f1117; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }

    /* Cartões de KPI */
    .kpi-card {
        background: linear-gradient(135deg, #1e2130, #252a3a);
        border-left: 4px solid #4f8ef7;
        border-radius: 10px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .kpi-title {
        font-size: 13px;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #e2e8f0;
    }
    .kpi-delta {
        font-size: 12px;
        color: #68d391;
        margin-top: 5px;
    }

    /* Seções dos gráficos */
    .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid #2d3748;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. CARREGAMENTO DOS DADOS (CAMADA BRONZE)
#    Leitura dos arquivos CSV individuais (tabelas dimensão + tabela fato)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data  # Cache para não recarregar a cada interação
def carregar_dados():
    """
    Carrega os CSVs do Star Schema e realiza os JOINs (merges).
    Retorna o DataFrame já modelado (tabela fato + dimensões desnormalizadas).
    """
    # Detecta o diretório onde o script está sendo executado
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # ── LEITURA DAS TABELAS DIMENSÃO ────────────────────────────────────────
    dim_calendario = pd.read_csv(
        os.path.join(base_dir, "Dim_Calendario.csv"),
        sep=";", encoding="utf-8-sig"
    )
    dim_material = pd.read_csv(
        os.path.join(base_dir, "Dim_Material.csv"),
        sep=";", encoding="utf-8-sig"
    )
    dim_fornecedor = pd.read_csv(
        os.path.join(base_dir, "Dim_Fornecedor.csv"),
        sep=";", encoding="utf-8-sig"
    )
    dim_medico = pd.read_csv(
        os.path.join(base_dir, "Dim_Medico.csv"),
        sep=";", encoding="utf-8-sig"
    )
    # ── LEITURA DA TABELA FATO ───────────────────────────────────────────────
    fato = pd.read_csv(
        os.path.join(base_dir, "Fato_Empenhos.csv"),
        sep=";", encoding="utf-8-sig"
    )

    # ── LIMPEZA E TIPAGEM ────────────────────────────────────────────────────
    # Converte Valor_Empenhado: troca vírgula decimal por ponto e converte para float
    fato["Valor_Empenhado"] = (
        fato["Valor_Empenhado"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace(";", "", regex=False)   # Remove possíveis artefatos
        .str.strip()
    )
    fato["Valor_Empenhado"] = pd.to_numeric(fato["Valor_Empenhado"], errors="coerce").fillna(0)

    # Converte a coluna Data da Dim_Calendario para datetime
    dim_calendario["Data"] = pd.to_datetime(dim_calendario["Data"], format="%d/%m/%Y", errors="coerce")

    # ── STAR SCHEMA: JOINs (MERGE) ───────────────────────────────────────────
    # Este bloco representa o coração do Star Schema:
    # a Fato_Empenhos é enriquecida com colunas das dimensões via LEFT JOIN.
    # Cada merge usa a chave FK da fato com a PK da dimensão correspondente.

    # JOIN 1: Fato ←→ Dim_Calendario (FK: ID_Data → PK: ID_Data)
    df = fato.merge(dim_calendario, on="ID_Data", how="left")

    # JOIN 2: Fato ←→ Dim_Fornecedor (FK: ID_Fornecedor → PK: ID_Fornecedor)
    df = df.merge(dim_fornecedor, on="ID_Fornecedor", how="left")

    # JOIN 3: Fato ←→ Dim_Material (FK: ID_Material → PK: ID_Material)
    df = df.merge(dim_material, on="ID_Material", how="left")

    # JOIN 4: Fato ←→ Dim_Medico (FK: ID_Medico → PK: ID_Medico)
    df = df.merge(dim_medico, on="ID_Medico", how="left")

    return df, dim_calendario


# ─────────────────────────────────────────────────────────────────────────────
# EXECUÇÃO DO CARREGAMENTO
# ─────────────────────────────────────────────────────────────────────────────
try:
    df_full, dim_calendario = carregar_dados()
except FileNotFoundError as e:
    st.error(f"❌ Arquivo não encontrado: {e}\n\nCertifique-se de que todos os CSVs estão na mesma pasta do app.py.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# 2. SIDEBAR — FILTROS INTERATIVOS
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital.png", width=60)
    st.title("🏥 Hospital Municipal")
    st.markdown("**Dashboard de Empenhos 2026**")
    st.divider()

    st.subheader("🔎 Filtros")

    # Filtro por Mês (usa Dim_Calendario → coluna Nome_Mes)
    meses_disponiveis = ["Todos"] + list(
        dim_calendario.sort_values("Mes")["Nome_Mes"].unique()
    )
    filtro_mes = st.selectbox("📅 Mês", options=meses_disponiveis)

    # Filtro por Especialidade (usa Dim_Medico → coluna Especialidade)
    especialidades = ["Todas"] + sorted(df_full["Especialidade"].dropna().unique().tolist())
    filtro_especialidade = st.selectbox("👨‍⚕️ Especialidade Médica", options=especialidades)

    # Filtro por Categoria de Material (usa Dim_Material → coluna Categoria)
    categorias = ["Todas"] + sorted(df_full["Categoria"].dropna().unique().tolist())
    filtro_categoria = st.selectbox("💊 Categoria de Material", options=categorias)

    st.divider()
    st.caption("Fonte: Empenhos Hospital Municipal - 2026")


# ─────────────────────────────────────────────────────────────────────────────
# 3. APLICAÇÃO DOS FILTROS NO DATAFRAME
#    Os filtros alternam sobre o DataFrame já modelado com Star Schema
# ─────────────────────────────────────────────────────────────────────────────
df = df_full.copy()

if filtro_mes != "Todos":
    df = df[df["Nome_Mes"] == filtro_mes]

if filtro_especialidade != "Todas":
    df = df[df["Especialidade"] == filtro_especialidade]

if filtro_categoria != "Todas":
    df = df[df["Categoria"] == filtro_categoria]


# ─────────────────────────────────────────────────────────────────────────────
# 4. CÁLCULO DOS KPIs FINANCEIROS
# ─────────────────────────────────────────────────────────────────────────────
total_empenhado = df["Valor_Empenhado"].sum()
total_registros = len(df)
ticket_medio     = total_empenhado / total_registros if total_registros > 0 else 0

# YTD: acumulado do ano (equivale ao total quando não há filtro de mês)
ytd = df_full["Valor_Empenhado"].sum() if filtro_mes == "Todos" else total_empenhado

# Fornecedor com maior gasto
top_fornecedor = (
    df.groupby("Razao_Social")["Valor_Empenhado"].sum().idxmax()
    if not df.empty else "N/A"
)


# ─────────────────────────────────────────────────────────────────────────────
# 5. LAYOUT — CABEÇALHO DO DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## 🏥 Dashboard de Empenhos — Hospital Municipal 2026")
st.markdown(
    f"Exibindo **{total_registros}** registros filtrados de "
    f"**{len(df_full)}** empenhos totais."
)
st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# 6. LINHA DE KPIs (CARTÕES)
# ─────────────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💰 Total Empenhado</div>
        <div class="kpi-value">R$ {total_empenhado:,.2f}</div>
        <div class="kpi-delta">Período filtrado</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:#68d391;">
        <div class="kpi-title">📈 YTD (Acum. 2026)</div>
        <div class="kpi-value">R$ {ytd:,.2f}</div>
        <div class="kpi-delta">Year-to-Date</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:#f6ad55;">
        <div class="kpi-title">🧾 Ticket Médio</div>
        <div class="kpi-value">R$ {ticket_medio:,.2f}</div>
        <div class="kpi-delta">Por empenho</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card" style="border-color:#fc8181;">
        <div class="kpi-title">🏆 Top Fornecedor</div>
        <div class="kpi-value" style="font-size:16px;">{top_fornecedor}</div>
        <div class="kpi-delta">Maior valor empenhado</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 7. GRÁFICO DE LINHA — EVOLUÇÃO MENSAL
#    STAR SCHEMA: agrupa por Mes + Nome_Mes (vindos da Dim_Calendario)
#    garantindo continuidade do calendário mesmo em meses sem empenhos
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📅 Evolução Mensal dos Gastos</div>', unsafe_allow_html=True)

# Usa a Dim_Calendario para garantir todos os 12 meses no eixo X
todos_os_meses = (
    dim_calendario[["Mes", "Nome_Mes"]]
    .drop_duplicates()
    .sort_values("Mes")
)

gasto_mensal = (
    df.groupby(["Mes", "Nome_Mes"])["Valor_Empenhado"]
    .sum()
    .reset_index()
)

# LEFT JOIN com todos os meses → meses sem dados aparecem como 0
gasto_mensal = todos_os_meses.merge(gasto_mensal, on=["Mes", "Nome_Mes"], how="left").fillna(0)
gasto_mensal = gasto_mensal.sort_values("Mes")

fig_linha = px.line(
    gasto_mensal,
    x="Nome_Mes",
    y="Valor_Empenhado",
    markers=True,
    labels={"Nome_Mes": "Mês", "Valor_Empenhado": "Valor Empenhado (R$)"},
    template="plotly_dark",
    color_discrete_sequence=["#4f8ef7"],
)
fig_linha.update_traces(
    line=dict(width=3),
    marker=dict(size=9, color="#f6ad55"),
    fill="tozeroy",
    fillcolor="rgba(79,142,247,0.08)"
)
fig_linha.update_layout(
    plot_bgcolor="#1e2130",
    paper_bgcolor="#1e2130",
    font_color="#a0aec0",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#2d3748"),
    margin=dict(l=20, r=20, t=30, b=20),
    height=320,
)
st.plotly_chart(fig_linha, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 8. GRÁFICOS LADO A LADO (BARRAS + PIZZA)
# ─────────────────────────────────────────────────────────────────────────────
col_bar, col_pie = st.columns([1.2, 0.8])

# ── GRÁFICO DE BARRAS: Top 5 Fornecedores ───────────────────────────────────
# STAR SCHEMA: usa coluna Razao_Social vinda da Dim_Fornecedor após merge
with col_bar:
    st.markdown('<div class="section-title">🏆 Top 5 Fornecedores por Valor</div>', unsafe_allow_html=True)

    top5_fornecedores = (
        df.groupby("Razao_Social")["Valor_Empenhado"]
        .sum()
        .reset_index()
        .sort_values("Valor_Empenhado", ascending=False)
        .head(5)
    )
    # Encurta nomes longos para melhor visualização
    top5_fornecedores["Razao_Social"] = top5_fornecedores["Razao_Social"].str.replace(
        r" (Ltda|S\.A\.|S/A)", "", regex=True
    ).str.strip()

    fig_bar = px.bar(
        top5_fornecedores,
        x="Valor_Empenhado",
        y="Razao_Social",
        orientation="h",
        labels={"Razao_Social": "", "Valor_Empenhado": "Valor (R$)"},
        template="plotly_dark",
        color="Valor_Empenhado",
        color_continuous_scale=["#2b4bab", "#4f8ef7", "#68d391"],
        text_auto=".2s",
    )
    fig_bar.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        font_color="#a0aec0",
        coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor="#2d3748"),
        yaxis=dict(showgrid=False, categoryorder="total ascending"),
        margin=dict(l=10, r=20, t=10, b=20),
        height=340,
    )
    fig_bar.update_traces(textfont_color="white", textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)


# ── GRÁFICO DONUT: Distribuição por Categoria ────────────────────────────────
# STAR SCHEMA: usa coluna Categoria vinda da Dim_Material após merge
with col_pie:
    st.markdown('<div class="section-title">💊 Gastos por Categoria</div>', unsafe_allow_html=True)

    gasto_categoria = (
        df.groupby("Categoria")["Valor_Empenhado"]
        .sum()
        .reset_index()
        .sort_values("Valor_Empenhado", ascending=False)
    )

    fig_donut = px.pie(
        gasto_categoria,
        names="Categoria",
        values="Valor_Empenhado",
        hole=0.52,
        template="plotly_dark",
        color_discrete_sequence=["#4f8ef7", "#68d391", "#f6ad55", "#fc8181"],
    )
    fig_donut.update_traces(
        textinfo="percent+label",
        textfont_size=13,
        marker=dict(line=dict(color="#1e2130", width=2)),
    )
    fig_donut.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        font_color="#a0aec0",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=10, b=10),
        height=340,
    )
    st.plotly_chart(fig_donut, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 9. TABELA DETALHADA — VISÃO POR ESPECIALIDADE MÉDICA
#    STAR SCHEMA: usa colunas de 3 dimensões (Medico, Material, Fornecedor)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">👨‍⚕️ Gastos por Especialidade Médica</div>', unsafe_allow_html=True)

col_esp, col_forn = st.columns(2)

# Barras horizontais por Especialidade
with col_esp:
    gasto_esp = (
        df.groupby("Especialidade")["Valor_Empenhado"]
        .sum()
        .reset_index()
        .sort_values("Valor_Empenhado", ascending=True)
    )
    fig_esp = px.bar(
        gasto_esp,
        x="Valor_Empenhado",
        y="Especialidade",
        orientation="h",
        labels={"Especialidade": "", "Valor_Empenhado": "Valor (R$)"},
        template="plotly_dark",
        color="Valor_Empenhado",
        color_continuous_scale=["#2b4bab", "#fc8181"],
        text_auto=".2s",
    )
    fig_esp.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        font_color="#a0aec0",
        coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor="#2d3748"),
        yaxis=dict(showgrid=False),
        margin=dict(l=10, r=20, t=10, b=10),
        height=300,
    )
    st.plotly_chart(fig_esp, use_container_width=True)

# Gráfico de barras por Cidade do Fornecedor
with col_forn:
    st.markdown("**📍 Gastos por Cidade do Fornecedor**")
    gasto_cidade = (
        df.groupby("Cidade")["Valor_Empenhado"]
        .sum()
        .reset_index()
        .sort_values("Valor_Empenhado", ascending=False)
        .head(8)
    )
    fig_cidade = px.bar(
        gasto_cidade,
        x="Cidade",
        y="Valor_Empenhado",
        labels={"Cidade": "Cidade", "Valor_Empenhado": "Valor (R$)"},
        template="plotly_dark",
        color="Valor_Empenhado",
        color_continuous_scale=["#2b4bab", "#68d391"],
        text_auto=".2s",
    )
    fig_cidade.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        font_color="#a0aec0",
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#2d3748"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
    )
    st.plotly_chart(fig_cidade, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 10. TABELA DE DADOS FILTRADOS (EXPANDER)
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📋 Ver dados detalhados filtrados"):
    colunas_exibir = [
        "Data", "Nome_Mes", "Razao_Social", "Cidade",
        "Descricao", "Categoria", "Nome_Medico",
        "Especialidade", "Valor_Empenhado"
    ]
    # Formata a coluna Data para exibição
    df_exibir = df[colunas_exibir].copy()
    df_exibir["Data"] = pd.to_datetime(df_exibir["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
    df_exibir["Valor_Empenhado"] = df_exibir["Valor_Empenhado"].apply(lambda x: f"R$ {x:,.2f}")
    df_exibir.columns = [
        "Data", "Mês", "Fornecedor", "Cidade",
        "Material", "Categoria", "Médico",
        "Especialidade", "Valor Empenhado"
    ]
    st.dataframe(df_exibir, use_container_width=True, height=350)

st.divider()
st.caption("🏥 Dashboard BI — Hospital Municipal 2026 | Desenvolvido com Streamlit + Plotly | Modelagem Star Schema")
