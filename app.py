"""
=============================================================================
  DASHBOARD DE BI MULTI-CENÁRIO
  Modelagem Star Schema com Streamlit + Plotly
=============================================================================
  Cenário 1: Hospital Municipal     → cenarios/hospital/
  Cenário 2: Secretaria de Educação → cenarios/educacao/
  Comando  : python -m streamlit run app.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard BI | Gestão Pública 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS CSS GLOBAIS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }

    .kpi-card {
        background: linear-gradient(135deg, #1e2130, #252a3a);
        border-left: 4px solid #4f8ef7;
        border-radius: 10px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 8px;
    }
    .kpi-title { font-size: 12px; color: #a0aec0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .kpi-value { font-size: 26px; font-weight: 700; color: #e2e8f0; }
    .kpi-delta { font-size: 12px; color: #68d391; margin-top: 5px; }

    .section-title {
        font-size: 14px; font-weight: 600; color: #a0aec0;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin-bottom: 10px; padding-bottom: 6px;
        border-bottom: 1px solid #2d3748;
    }

    /* Botão de cenário ativo */
    .scenario-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES DE CARREGAMENTO — STAR SCHEMA POR CENÁRIO
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def carregar_hospital():
    """
    STAR SCHEMA — Cenário Hospital
    Fato_Empenhos ←→ Dim_Calendario, Dim_Fornecedor, Dim_Material, Dim_Medico
    """
    pasta = os.path.join(BASE_DIR, "cenarios", "hospital")

    dim_cal  = pd.read_csv(os.path.join(pasta, "Dim_Calendario.csv"), sep=";", encoding="utf-8-sig")
    dim_mat  = pd.read_csv(os.path.join(pasta, "Dim_Material.csv"),   sep=";", encoding="utf-8-sig")
    dim_forn = pd.read_csv(os.path.join(pasta, "Dim_Fornecedor.csv"), sep=";", encoding="utf-8-sig")
    dim_med  = pd.read_csv(os.path.join(pasta, "Dim_Medico.csv"),     sep=";", encoding="utf-8-sig")
    fato     = pd.read_csv(os.path.join(pasta, "Fato_Empenhos.csv"),  sep=";", encoding="utf-8-sig")

    dim_cal["Data"] = pd.to_datetime(dim_cal["Data"], format="%d/%m/%Y", errors="coerce")
    fato["Valor_Empenhado"] = (
        fato["Valor_Empenhado"].astype(str)
        .str.replace(",", ".", regex=False).str.strip()
    )
    fato["Valor_Empenhado"] = pd.to_numeric(fato["Valor_Empenhado"], errors="coerce").fillna(0)

    # JOINs do Star Schema
    df = fato.merge(dim_cal,  on="ID_Data",       how="left")
    df = df.merge(dim_forn,   on="ID_Fornecedor",  how="left")
    df = df.merge(dim_mat,    on="ID_Material",    how="left")
    df = df.merge(dim_med,    on="ID_Medico",      how="left")

    return df, dim_cal


@st.cache_data
def carregar_educacao():
    """
    STAR SCHEMA — Cenário Educação
    Fato_Despesas_Edu ←→ Dim_Calendario, Dim_Fornecedor_Edu, Dim_Item_Edu, Dim_Escola
    """
    pasta = os.path.join(BASE_DIR, "cenarios", "educacao")

    dim_cal  = pd.read_csv(os.path.join(pasta, "Dim_Calendario.csv"),    sep=";", encoding="utf-8-sig")
    dim_item = pd.read_csv(os.path.join(pasta, "Dim_Item_Edu.csv"),       sep=";", encoding="utf-8-sig")
    dim_forn = pd.read_csv(os.path.join(pasta, "Dim_Fornecedor_Edu.csv"), sep=";", encoding="utf-8-sig")
    dim_esc  = pd.read_csv(os.path.join(pasta, "Dim_Escola.csv"),         sep=";", encoding="utf-8-sig")
    fato     = pd.read_csv(os.path.join(pasta, "Fato_Despesas_Edu.csv"),  sep=";", encoding="utf-8-sig")

    dim_cal["Data"] = pd.to_datetime(dim_cal["Data"], format="%d/%m/%Y", errors="coerce")
    fato["Valor_Empenhado"] = (
        fato["Valor_Empenhado"].astype(str)
        .str.replace(",", ".", regex=False).str.strip()
    )
    fato["Valor_Empenhado"] = pd.to_numeric(fato["Valor_Empenhado"], errors="coerce").fillna(0)

    # JOINs do Star Schema
    df = fato.merge(dim_cal,  on="ID_Data",       how="left")
    df = df.merge(dim_forn,   on="ID_Fornecedor",  how="left")
    df = df.merge(dim_item,   on="ID_Item",        how="left")
    df = df.merge(dim_esc,    on="ID_Escola",      how="left")

    return df, dim_cal


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    plot_bgcolor="#1e2130", paper_bgcolor="#1e2130", font_color="#a0aec0",
    margin=dict(l=10, r=20, t=20, b=20), height=310,
)

def linha_mensal(df, dim_cal, titulo="Evolução Mensal dos Gastos"):
    todos_meses = dim_cal[["Mes", "Nome_Mes"]].drop_duplicates().sort_values("Mes")
    gasto = df.groupby(["Mes", "Nome_Mes"])["Valor_Empenhado"].sum().reset_index()
    gasto = todos_meses.merge(gasto, on=["Mes", "Nome_Mes"], how="left").fillna(0).sort_values("Mes")

    fig = px.line(gasto, x="Nome_Mes", y="Valor_Empenhado", markers=True,
                  template="plotly_dark", color_discrete_sequence=["#4f8ef7"])
    fig.update_traces(line=dict(width=3), marker=dict(size=9, color="#f6ad55"),
                      fill="tozeroy", fillcolor="rgba(79,142,247,0.08)")
    layout_linha = {**PLOTLY_LAYOUT, "height": 300,
                    "xaxis": dict(showgrid=False),
                    "yaxis": dict(showgrid=True, gridcolor="#2d3748")}
    fig.update_layout(**layout_linha)
    return fig


def barras_top5(df, col_grupo, col_valor="Valor_Empenhado"):
    top5 = (df.groupby(col_grupo)[col_valor].sum().reset_index()
              .sort_values(col_valor, ascending=False).head(5))
    top5[col_grupo] = top5[col_grupo].str.slice(0, 28)
    fig = px.bar(top5, x=col_valor, y=col_grupo, orientation="h", template="plotly_dark",
                 color=col_valor, color_continuous_scale=["#2b4bab", "#4f8ef7", "#68d391"],
                 text_auto=".2s")
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                      xaxis=dict(showgrid=True, gridcolor="#2d3748"),
                      yaxis=dict(showgrid=False, categoryorder="total ascending"))
    fig.update_traces(textfont_color="white", textposition="outside")
    return fig


def donut(df, col_grupo, col_valor="Valor_Empenhado", cores=None):
    cores = cores or ["#4f8ef7", "#68d391", "#f6ad55", "#fc8181", "#b794f4"]
    gasto = df.groupby(col_grupo)[col_valor].sum().reset_index()
    fig = px.pie(gasto, names=col_grupo, values=col_valor, hole=0.52,
                 template="plotly_dark", color_discrete_sequence=cores)
    fig.update_traces(textinfo="percent+label", textfont_size=12,
                      marker=dict(line=dict(color="#1e2130", width=2)))
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
    return fig


def barras_simples(df, col_x, col_y="Valor_Empenhado", cores=None):
    cores = cores or ["#2b4bab", "#b794f4"]
    gasto = df.groupby(col_x)[col_y].sum().reset_index().sort_values(col_y, ascending=True)
    gasto[col_x] = gasto[col_x].str.slice(0, 22)
    fig = px.bar(gasto, x=col_y, y=col_x, orientation="h", template="plotly_dark",
                 color=col_y, color_continuous_scale=cores, text_auto=".2s")
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                      xaxis=dict(showgrid=True, gridcolor="#2d3748"),
                      yaxis=dict(showgrid=False))
    return fig


def kpis(df, label_dim, valor_dim):
    """Exibe os 4 KPIs padrão."""
    total = df["Valor_Empenhado"].sum()
    qtde  = len(df)
    ticket = total / qtde if qtde > 0 else 0
    top = df.groupby(valor_dim)["Valor_Empenhado"].sum().idxmax() if not df.empty else "N/A"
    top_short = str(top)[:22] + "…" if len(str(top)) > 22 else str(top)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">💰 Total Empenhado</div>'
                    f'<div class="kpi-value">R$ {total:,.0f}</div>'
                    f'<div class="kpi-delta">{qtde} registros</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card" style="border-color:#68d391;">'
                    f'<div class="kpi-title">📈 YTD 2026</div>'
                    f'<div class="kpi-value">R$ {total:,.0f}</div>'
                    f'<div class="kpi-delta">Year-to-Date</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card" style="border-color:#f6ad55;">'
                    f'<div class="kpi-title">🧾 Ticket Médio</div>'
                    f'<div class="kpi-value">R$ {ticket:,.0f}</div>'
                    f'<div class="kpi-delta">Por empenho</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card" style="border-color:#fc8181;">'
                    f'<div class="kpi-title">🏆 {label_dim}</div>'
                    f'<div class="kpi-value" style="font-size:14px;">{top_short}</div>'
                    f'<div class="kpi-delta">Maior valor</div></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — SELETOR DE CENÁRIO + FILTROS
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Dashboard BI")
    st.markdown("**Gestão Pública Municipal 2026**")
    st.divider()

    # ── SELETOR DE CENÁRIO ──────────────────────────────────────────────────
    st.subheader("🎯 Cenário")
    cenario = st.radio(
        label="",
        options=["🏥 Hospital Municipal", "🏫 Secretaria de Educação"],
        label_visibility="collapsed"
    )
    st.divider()

    # ── FILTROS (dinâmicos por cenário) ─────────────────────────────────────
    st.subheader("🔎 Filtros")

    if cenario == "🏥 Hospital Municipal":
        try:
            df_full, dim_cal = carregar_hospital()
        except Exception as e:
            st.error(f"Erro ao carregar Hospital: {e}")
            st.stop()

        meses_disp = ["Todos"] + list(dim_cal.sort_values("Mes")["Nome_Mes"].unique())
        filtro_mes = st.selectbox("📅 Mês", meses_disp)
        filtro_esp = st.selectbox("👨‍⚕️ Especialidade",
                                   ["Todas"] + sorted(df_full["Especialidade"].dropna().unique().tolist()))
        filtro_cat = st.selectbox("💊 Categoria de Material",
                                   ["Todas"] + sorted(df_full["Categoria"].dropna().unique().tolist()))
    else:
        try:
            df_full, dim_cal = carregar_educacao()
        except Exception as e:
            st.error(f"Erro ao carregar Educação: {e}")
            st.stop()

        meses_disp = ["Todos"] + list(dim_cal.sort_values("Mes")["Nome_Mes"].unique())
        filtro_mes = st.selectbox("📅 Mês", meses_disp)
        filtro_esp = st.selectbox("🏫 Nível de Ensino",
                                   ["Todos"] + sorted(df_full["Nivel_Ensino"].dropna().unique().tolist()))
        filtro_cat = st.selectbox("📦 Categoria de Item",
                                   ["Todas"] + sorted(df_full["Categoria"].dropna().unique().tolist()))

    st.divider()
    st.caption("Fonte: Empenhos Município 2026 | Star Schema")


# ─────────────────────────────────────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────────────────────────────────────
df = df_full.copy()

if filtro_mes != "Todos":
    df = df[df["Nome_Mes"] == filtro_mes]

if cenario == "🏥 Hospital Municipal":
    if filtro_esp != "Todas":
        df = df[df["Especialidade"] == filtro_esp]
    if filtro_cat != "Todas":
        df = df[df["Categoria"] == filtro_cat]
else:
    if filtro_esp != "Todos":
        df = df[df["Nivel_Ensino"] == filtro_esp]
    if filtro_cat != "Todas":
        df = df[df["Categoria"] == filtro_cat]


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD — HOSPITAL MUNICIPAL
# ─────────────────────────────────────────────────────────────────────────────
if cenario == "🏥 Hospital Municipal":
    st.markdown("## 🏥 Hospital Municipal — Empenhos 2026")
    st.markdown(f"Exibindo **{len(df)}** de **{len(df_full)}** registros.")
    st.divider()

    kpis(df, label_dim="Top Fornecedor", valor_dim="Razao_Social")
    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico de linha
    st.markdown('<div class="section-title">📅 Evolução Mensal dos Gastos</div>', unsafe_allow_html=True)
    st.plotly_chart(linha_mensal(df, dim_cal), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.markdown('<div class="section-title">🏆 Top 5 Fornecedores</div>', unsafe_allow_html=True)
        st.plotly_chart(barras_top5(df, "Razao_Social"), use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">💊 Gastos por Categoria</div>', unsafe_allow_html=True)
        st.plotly_chart(donut(df, "Categoria"), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">👨‍⚕️ Por Especialidade Médica</div>', unsafe_allow_html=True)
        st.plotly_chart(barras_simples(df, "Especialidade"), use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">📍 Por Cidade do Fornecedor</div>', unsafe_allow_html=True)
        st.plotly_chart(barras_simples(df, "Cidade", cores=["#2b4bab", "#4f8ef7"]), use_container_width=True)

    with st.expander("📋 Ver dados detalhados"):
        cols = ["Data", "Nome_Mes", "Razao_Social", "Cidade", "Descricao", "Categoria", "Nome_Medico", "Especialidade", "Valor_Empenhado"]
        df_view = df[cols].copy()
        df_view["Data"] = pd.to_datetime(df_view["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
        df_view["Valor_Empenhado"] = df_view["Valor_Empenhado"].apply(lambda x: f"R$ {x:,.2f}")
        df_view.columns = ["Data", "Mês", "Fornecedor", "Cidade", "Material", "Categoria", "Médico", "Especialidade", "Valor"]
        st.dataframe(df_view, use_container_width=True, height=300)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD — SECRETARIA DE EDUCAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.markdown("## 🏫 Secretaria de Educação — Despesas 2026")
    st.markdown(f"Exibindo **{len(df)}** de **{len(df_full)}** registros.")
    st.divider()

    kpis(df, label_dim="Top Fornecedor", valor_dim="Razao_Social")
    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico de linha
    st.markdown('<div class="section-title">📅 Evolução Mensal das Despesas</div>', unsafe_allow_html=True)
    st.plotly_chart(linha_mensal(df, dim_cal), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.markdown('<div class="section-title">🏆 Top 5 Fornecedores</div>', unsafe_allow_html=True)
        st.plotly_chart(barras_top5(df, "Razao_Social"), use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">📦 Gastos por Categoria</div>', unsafe_allow_html=True)
        st.plotly_chart(donut(df, "Categoria",
                              cores=["#4f8ef7", "#68d391", "#f6ad55", "#fc8181", "#b794f4"]),
                        use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">🏫 Por Escola</div>', unsafe_allow_html=True)
        st.plotly_chart(barras_simples(df, "Nome_Escola", cores=["#2b4bab", "#b794f4"]), use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">🗺️ Por Região</div>', unsafe_allow_html=True)
        st.plotly_chart(barras_simples(df, "Regiao", cores=["#2b4bab", "#68d391"]), use_container_width=True)

    with st.expander("📋 Ver dados detalhados"):
        cols = ["Data", "Nome_Mes", "Nome_Escola", "Regiao", "Nivel_Ensino",
                "Razao_Social", "Descricao", "Categoria", "Valor_Empenhado"]
        df_view = df[cols].copy()
        df_view["Data"] = pd.to_datetime(df_view["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
        df_view["Valor_Empenhado"] = df_view["Valor_Empenhado"].apply(lambda x: f"R$ {x:,.2f}")
        df_view.columns = ["Data", "Mês", "Escola", "Região", "Nível", "Fornecedor", "Item", "Categoria", "Valor"]
        st.dataframe(df_view, use_container_width=True, height=300)


# ─────────────────────────────────────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.caption("📊 Dashboard BI Multi-Cenário 2026 | Streamlit + Plotly | Modelagem Star Schema | AulaBI Unifacc")
