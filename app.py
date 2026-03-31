"""
=============================================================================
  DASHBOARD DE BI MULTI-CENÁRIO
  Modelagem Star Schema com Streamlit + Plotly
=============================================================================
  Cenário 1: Hospital Municipal        → cenarios/hospital/
  Cenário 2: Secretaria de Educação    → cenarios/educacao/
  Cenário 3: Segurança Pública         → cenarios/seguranca/
  Cenário 4: Secretaria de Urbanismo   → cenarios/urbanismo/
  Cenário 5: Arrecadação Municipal MT  → cenarios/arrecadacao/
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
    .kpi-title { font-size: 12px; color: #a0aec0; text-transform: uppercase;
                 letter-spacing: 1px; margin-bottom: 8px; }
    .kpi-value { font-size: 26px; font-weight: 700; color: #e2e8f0; }
    .kpi-delta { font-size: 12px; color: #68d391; margin-top: 5px; }

    .section-title {
        font-size: 14px; font-weight: 600; color: #a0aec0;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin-bottom: 10px; padding-bottom: 6px;
        border-bottom: 1px solid #2d3748;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — PLOTLY SEM CHAVE DUPLICADA
# ─────────────────────────────────────────────────────────────────────────────
_BASE = dict(
    plot_bgcolor="#1e2130", paper_bgcolor="#1e2130", font_color="#a0aec0",
    margin=dict(l=10, r=20, t=20, b=20),
)

def _layout(**kwargs):
    return {**_BASE, **kwargs}


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES DE CARREGAMENTO — STAR SCHEMA POR CENÁRIO
# ─────────────────────────────────────────────────────────────────────────────
def _ler_csv(pasta, nome):
    return pd.read_csv(os.path.join(pasta, nome), sep=";", encoding="utf-8-sig")

def _limpar_valor(df):
    df["Valor_Empenhado"] = (
        df["Valor_Empenhado"].astype(str).str.replace(",", ".", regex=False).str.strip()
    )
    df["Valor_Empenhado"] = pd.to_numeric(df["Valor_Empenhado"], errors="coerce").fillna(0)
    return df

def _limpar_cal(dim_cal):
    dim_cal["Data"] = pd.to_datetime(dim_cal["Data"], format="%d/%m/%Y", errors="coerce")
    return dim_cal


@st.cache_data
def carregar_hospital():
    pasta = os.path.join(BASE_DIR, "cenarios", "hospital")
    dim_cal  = _limpar_cal(_ler_csv(pasta, "Dim_Calendario.csv"))
    dim_mat  = _ler_csv(pasta, "Dim_Material.csv")
    dim_forn = _ler_csv(pasta, "Dim_Fornecedor.csv")
    dim_med  = _ler_csv(pasta, "Dim_Medico.csv")
    fato     = _limpar_valor(_ler_csv(pasta, "Fato_Empenhos.csv"))
    df = fato.merge(dim_cal,  on="ID_Data",      how="left")
    df = df.merge(dim_forn,   on="ID_Fornecedor", how="left")
    df = df.merge(dim_mat,    on="ID_Material",   how="left")
    df = df.merge(dim_med,    on="ID_Medico",     how="left")
    return df, dim_cal


@st.cache_data
def carregar_educacao():
    pasta = os.path.join(BASE_DIR, "cenarios", "educacao")
    dim_cal  = _limpar_cal(_ler_csv(pasta, "Dim_Calendario.csv"))
    dim_item = _ler_csv(pasta, "Dim_Item_Edu.csv")
    dim_forn = _ler_csv(pasta, "Dim_Fornecedor_Edu.csv")
    dim_esc  = _ler_csv(pasta, "Dim_Escola.csv")
    fato     = _limpar_valor(_ler_csv(pasta, "Fato_Despesas_Edu.csv"))
    df = fato.merge(dim_cal,  on="ID_Data",      how="left")
    df = df.merge(dim_forn,   on="ID_Fornecedor", how="left")
    df = df.merge(dim_item,   on="ID_Item",       how="left")
    df = df.merge(dim_esc,    on="ID_Escola",     how="left")
    return df, dim_cal


@st.cache_data
def carregar_seguranca():
    pasta = os.path.join(BASE_DIR, "cenarios", "seguranca")
    dim_cal  = _limpar_cal(_ler_csv(pasta, "Dim_Calendario.csv"))
    dim_item = _ler_csv(pasta, "Dim_Item_Seg.csv")
    dim_forn = _ler_csv(pasta, "Dim_Fornecedor_Seg.csv")
    dim_uni  = _ler_csv(pasta, "Dim_Unidade.csv")
    fato     = _limpar_valor(_ler_csv(pasta, "Fato_Despesas_Seg.csv"))
    df = fato.merge(dim_cal,  on="ID_Data",      how="left")
    df = df.merge(dim_forn,   on="ID_Fornecedor", how="left")
    df = df.merge(dim_item,   on="ID_Item",       how="left")
    df = df.merge(dim_uni,    on="ID_Unidade",    how="left")
    return df, dim_cal


@st.cache_data
def carregar_urbanismo():
    pasta = os.path.join(BASE_DIR, "cenarios", "urbanismo")
    dim_cal  = _limpar_cal(_ler_csv(pasta, "Dim_Calendario.csv"))
    dim_item = _ler_csv(pasta, "Dim_Item_Urb.csv")
    dim_forn = _ler_csv(pasta, "Dim_Fornecedor_Urb.csv")
    dim_bai  = _ler_csv(pasta, "Dim_Bairro.csv")
    fato     = _limpar_valor(_ler_csv(pasta, "Fato_Obras_Urb.csv"))
    df = fato.merge(dim_cal,  on="ID_Data",      how="left")
    df = df.merge(dim_forn,   on="ID_Fornecedor", how="left")
    df = df.merge(dim_item,   on="ID_Item",       how="left")
    df = df.merge(dim_bai,    on="ID_Bairro",     how="left")
    return df, dim_cal


@st.cache_data
def carregar_arrecadacao():
    """
    STAR SCHEMA — Cenário Arrecadação Municipal MT
    Fato_Arrecadacao ←→ Dim_Calendario, Dim_Municipio, Dim_Tributo, Dim_Orgao
    """
    pasta = os.path.join(BASE_DIR, "cenarios", "arrecadacao")
    dim_cal  = _limpar_cal(_ler_csv(pasta, "Dim_Calendario.csv"))
    dim_mun  = _ler_csv(pasta, "Dim_Municipio.csv")
    dim_tri  = _ler_csv(pasta, "Dim_Tributo.csv")
    dim_org  = _ler_csv(pasta, "Dim_Orgao.csv")
    fato     = _ler_csv(pasta, "Fato_Arrecadacao.csv")
    fato["Valor_Arrecadado"] = (
        fato["Valor_Arrecadado"].astype(str).str.replace(",", ".", regex=False).str.strip()
    )
    fato["Valor_Arrecadado"] = pd.to_numeric(fato["Valor_Arrecadado"], errors="coerce").fillna(0)
    # Renomeia para compatibilidade com as funções de gráfico
    fato = fato.rename(columns={"Valor_Arrecadado": "Valor_Empenhado"})
    df = fato.merge(dim_cal, on="ID_Data",       how="left")
    df = df.merge(dim_mun,   on="ID_Municipio",  how="left")
    df = df.merge(dim_tri,   on="ID_Tributo",    how="left")
    df = df.merge(dim_org,   on="ID_Orgao",      how="left")
    return df, dim_cal


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES DE VISUALIZAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
def linha_mensal(df, dim_cal):
    todos = dim_cal[["Mes", "Nome_Mes"]].drop_duplicates().sort_values("Mes")
    gasto = df.groupby(["Mes", "Nome_Mes"])["Valor_Empenhado"].sum().reset_index()
    gasto = todos.merge(gasto, on=["Mes", "Nome_Mes"], how="left").fillna(0).sort_values("Mes")
    fig = px.line(gasto, x="Nome_Mes", y="Valor_Empenhado", markers=True,
                  template="plotly_dark", color_discrete_sequence=["#4f8ef7"])
    fig.update_traces(line=dict(width=3), marker=dict(size=9, color="#f6ad55"),
                      fill="tozeroy", fillcolor="rgba(79,142,247,0.08)")
    fig.update_layout(**_layout(height=300, xaxis=dict(showgrid=False),
                                yaxis=dict(showgrid=True, gridcolor="#2d3748")))
    return fig


def barras_top5(df, col_grupo):
    top5 = (df.groupby(col_grupo)["Valor_Empenhado"].sum().reset_index()
              .sort_values("Valor_Empenhado", ascending=False).head(5))
    top5[col_grupo] = top5[col_grupo].str.slice(0, 30)
    fig = px.bar(top5, x="Valor_Empenhado", y=col_grupo, orientation="h",
                 template="plotly_dark",
                 color="Valor_Empenhado",
                 color_continuous_scale=["#2b4bab", "#4f8ef7", "#68d391"],
                 text_auto=".2s")
    fig.update_layout(**_layout(height=310, coloraxis_showscale=False,
                                xaxis=dict(showgrid=True, gridcolor="#2d3748"),
                                yaxis=dict(showgrid=False, categoryorder="total ascending")))
    fig.update_traces(textfont_color="white", textposition="outside")
    return fig


def donut(df, col_grupo, cores=None):
    cores = cores or ["#4f8ef7", "#68d391", "#f6ad55", "#fc8181", "#b794f4"]
    gasto = df.groupby(col_grupo)["Valor_Empenhado"].sum().reset_index()
    fig = px.pie(gasto, names=col_grupo, values="Valor_Empenhado", hole=0.52,
                 template="plotly_dark", color_discrete_sequence=cores)
    fig.update_traces(textinfo="percent+label", textfont_size=12,
                      marker=dict(line=dict(color="#1e2130", width=2)))
    fig.update_layout(**_layout(height=310, showlegend=False))
    return fig


def barras_simples(df, col_x, cores=None):
    cores = cores or ["#2b4bab", "#b794f4"]
    gasto = (df.groupby(col_x)["Valor_Empenhado"].sum().reset_index()
               .sort_values("Valor_Empenhado", ascending=True))
    gasto[col_x] = gasto[col_x].str.slice(0, 24)
    fig = px.bar(gasto, x="Valor_Empenhado", y=col_x, orientation="h",
                 template="plotly_dark",
                 color="Valor_Empenhado", color_continuous_scale=cores,
                 text_auto=".2s")
    fig.update_layout(**_layout(height=310, coloraxis_showscale=False,
                                xaxis=dict(showgrid=True, gridcolor="#2d3748"),
                                yaxis=dict(showgrid=False)))
    return fig


def kpis(df, label_dim, valor_dim):
    total  = df["Valor_Empenhado"].sum()
    qtde   = len(df)
    ticket = total / qtde if qtde > 0 else 0
    top    = df.groupby(valor_dim)["Valor_Empenhado"].sum().idxmax() if not df.empty else "N/A"
    top_s  = str(top)[:22] + "…" if len(str(top)) > 22 else str(top)

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
                    f'<div class="kpi-value" style="font-size:14px;">{top_s}</div>'
                    f'<div class="kpi-delta">Maior valor</div></div>', unsafe_allow_html=True)


def sec(titulo):
    st.markdown(f'<div class="section-title">{titulo}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — SELETOR DE CENÁRIO + FILTROS DINÂMICOS
# ─────────────────────────────────────────────────────────────────────────────
CENARIOS = [
    "🏥 Hospital Municipal",
    "🏫 Secretaria de Educação",
    "🚔 Segurança Pública",
    "🏗️ Secretaria de Urbanismo",
    "💰 Arrecadação Municipal - MT",
]

with st.sidebar:
    st.markdown("## 📊 Dashboard BI")
    st.markdown("**Gestão Pública Municipal 2026**")
    st.divider()

    st.subheader("🎯 Cenário")
    cenario = st.radio(label="cenario", options=CENARIOS, label_visibility="collapsed")
    st.divider()

    st.subheader("🔎 Filtros")

    if cenario == "🏥 Hospital Municipal":
        try:
            df_full, dim_cal = carregar_hospital()
        except Exception as e:
            st.error(f"Erro: {e}"); st.stop()
        meses = ["Todos"] + list(dim_cal.sort_values("Mes")["Nome_Mes"].unique())
        f_mes = st.selectbox("📅 Mês", meses)
        f_f2  = st.selectbox("👨‍⚕️ Especialidade",
                             ["Todas"] + sorted(df_full["Especialidade"].dropna().unique().tolist()))
        f_cat = st.selectbox("💊 Categoria",
                             ["Todas"] + sorted(df_full["Categoria"].dropna().unique().tolist()))

    elif cenario == "🏫 Secretaria de Educação":
        try:
            df_full, dim_cal = carregar_educacao()
        except Exception as e:
            st.error(f"Erro: {e}"); st.stop()
        meses = ["Todos"] + list(dim_cal.sort_values("Mes")["Nome_Mes"].unique())
        f_mes = st.selectbox("📅 Mês", meses)
        f_f2  = st.selectbox("🏫 Nível de Ensino",
                             ["Todos"] + sorted(df_full["Nivel_Ensino"].dropna().unique().tolist()))
        f_cat = st.selectbox("📦 Categoria",
                             ["Todas"] + sorted(df_full["Categoria"].dropna().unique().tolist()))

    elif cenario == "🚔 Segurança Pública":
        try:
            df_full, dim_cal = carregar_seguranca()
        except Exception as e:
            st.error(f"Erro: {e}"); st.stop()
        meses = ["Todos"] + list(dim_cal.sort_values("Mes")["Nome_Mes"].unique())
        f_mes = st.selectbox("📅 Mês", meses)
        f_f2  = st.selectbox("🚔 Tipo de Unidade",
                             ["Todos"] + sorted(df_full["Tipo_Unidade"].dropna().unique().tolist()))
        f_cat = st.selectbox("📦 Categoria",
                             ["Todas"] + sorted(df_full["Categoria"].dropna().unique().tolist()))

    elif cenario == "🏗️ Secretaria de Urbanismo":
        try:
            df_full, dim_cal = carregar_urbanismo()
        except Exception as e:
            st.error(f"Erro: {e}"); st.stop()
        meses = ["Todos"] + list(dim_cal.sort_values("Mes")["Nome_Mes"].unique())
        f_mes = st.selectbox("📅 Mês", meses)
        f_f2  = st.selectbox("🗺️ Região",
                             ["Todas"] + sorted(df_full["Regiao"].dropna().unique().tolist()))
        f_cat = st.selectbox("🏗️ Categoria de Obra",
                             ["Todas"] + sorted(df_full["Categoria"].dropna().unique().tolist()))

    else:  # Arrecadação MT
        try:
            df_full, dim_cal = carregar_arrecadacao()
        except Exception as e:
            st.error(f"Erro: {e}"); st.stop()
        meses = ["Todos"] + list(dim_cal.sort_values("Mes")["Nome_Mes"].unique())
        f_mes = st.selectbox("📅 Mês", meses)
        f_f2  = st.selectbox("🗺️ Mesorregião",
                             ["Todas"] + sorted(df_full["Mesorregiao"].dropna().unique().tolist()))
        f_cat = st.selectbox("💰 Categoria do Tributo",
                             ["Todas"] + sorted(df_full["Categoria"].dropna().unique().tolist()))

    st.divider()
    st.caption("Fonte: Empenhos Município 2026 | Star Schema")


# ─────────────────────────────────────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────────────────────────────────────
df = df_full.copy()
if f_mes != "Todos":
    df = df[df["Nome_Mes"] == f_mes]

if cenario == "🏥 Hospital Municipal":
    if f_f2  != "Todas": df = df[df["Especialidade"] == f_f2]
    if f_cat != "Todas": df = df[df["Categoria"]     == f_cat]
elif cenario == "🏫 Secretaria de Educação":
    if f_f2  != "Todos": df = df[df["Nivel_Ensino"] == f_f2]
    if f_cat != "Todas": df = df[df["Categoria"]    == f_cat]
elif cenario == "🚔 Segurança Pública":
    if f_f2  != "Todos": df = df[df["Tipo_Unidade"] == f_f2]
    if f_cat != "Todas": df = df[df["Categoria"]    == f_cat]
elif cenario == "🏗️ Secretaria de Urbanismo":
    if f_f2  != "Todas": df = df[df["Regiao"]    == f_f2]
    if f_cat != "Todas": df = df[df["Categoria"] == f_cat]
else:  # Arrecadação MT
    if f_f2  != "Todas": df = df[df["Mesorregiao"] == f_f2]
    if f_cat != "Todas": df = df[df["Categoria"]   == f_cat]


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARDS
# ─────────────────────────────────────────────────────────────────────────────

# ── Hospital ─────────────────────────────────────────────────────────────────
if cenario == "🏥 Hospital Municipal":
    st.markdown("## 🏥 Hospital Municipal — Empenhos 2026")
    st.markdown(f"Exibindo **{len(df)}** de **{len(df_full)}** registros.")
    st.divider()
    kpis(df, "Top Fornecedor", "Razao_Social")
    st.markdown("<br>", unsafe_allow_html=True)

    sec("📅 Evolução Mensal dos Gastos")
    st.plotly_chart(linha_mensal(df, dim_cal), use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        sec("🏆 Top 5 Fornecedores")
        st.plotly_chart(barras_top5(df, "Razao_Social"), use_container_width=True)
    with c2:
        sec("💊 Gastos por Categoria")
        st.plotly_chart(donut(df, "Categoria"), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        sec("👨‍⚕️ Por Especialidade Médica")
        st.plotly_chart(barras_simples(df, "Especialidade"), use_container_width=True)
    with c4:
        sec("📍 Por Cidade do Fornecedor")
        st.plotly_chart(barras_simples(df, "Cidade", cores=["#2b4bab", "#4f8ef7"]), use_container_width=True)

    with st.expander("📋 Ver dados detalhados"):
        cols = ["Data", "Nome_Mes", "Razao_Social", "Cidade", "Descricao",
                "Categoria", "Nome_Medico", "Especialidade", "Valor_Empenhado"]
        dv = df[cols].copy()
        dv["Data"] = pd.to_datetime(dv["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
        dv["Valor_Empenhado"] = dv["Valor_Empenhado"].apply(lambda x: f"R$ {x:,.2f}")
        dv.columns = ["Data","Mês","Fornecedor","Cidade","Material","Categoria","Médico","Especialidade","Valor"]
        st.dataframe(dv, use_container_width=True, height=300)


# ── Educação ─────────────────────────────────────────────────────────────────
elif cenario == "🏫 Secretaria de Educação":
    st.markdown("## 🏫 Secretaria de Educação — Despesas 2026")
    st.markdown(f"Exibindo **{len(df)}** de **{len(df_full)}** registros.")
    st.divider()
    kpis(df, "Top Fornecedor", "Razao_Social")
    st.markdown("<br>", unsafe_allow_html=True)

    sec("📅 Evolução Mensal das Despesas")
    st.plotly_chart(linha_mensal(df, dim_cal), use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        sec("🏆 Top 5 Fornecedores")
        st.plotly_chart(barras_top5(df, "Razao_Social"), use_container_width=True)
    with c2:
        sec("📦 Gastos por Categoria")
        st.plotly_chart(donut(df, "Categoria",
                              cores=["#4f8ef7","#68d391","#f6ad55","#fc8181","#b794f4"]),
                        use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        sec("🏫 Por Escola")
        st.plotly_chart(barras_simples(df, "Nome_Escola", cores=["#2b4bab","#b794f4"]), use_container_width=True)
    with c4:
        sec("🗺️ Por Região")
        st.plotly_chart(barras_simples(df, "Regiao", cores=["#2b4bab","#68d391"]), use_container_width=True)

    with st.expander("📋 Ver dados detalhados"):
        cols = ["Data","Nome_Mes","Nome_Escola","Regiao","Nivel_Ensino",
                "Razao_Social","Descricao","Categoria","Valor_Empenhado"]
        dv = df[cols].copy()
        dv["Data"] = pd.to_datetime(dv["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
        dv["Valor_Empenhado"] = dv["Valor_Empenhado"].apply(lambda x: f"R$ {x:,.2f}")
        dv.columns = ["Data","Mês","Escola","Região","Nível","Fornecedor","Item","Categoria","Valor"]
        st.dataframe(dv, use_container_width=True, height=300)


# ── Segurança Pública ─────────────────────────────────────────────────────────
elif cenario == "🚔 Segurança Pública":
    st.markdown("## 🚔 Segurança Pública — Despesas 2026")
    st.markdown(f"Exibindo **{len(df)}** de **{len(df_full)}** registros.")
    st.divider()
    kpis(df, "Top Fornecedor", "Razao_Social")
    st.markdown("<br>", unsafe_allow_html=True)

    sec("📅 Evolução Mensal das Despesas")
    st.plotly_chart(linha_mensal(df, dim_cal), use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        sec("🏆 Top 5 Fornecedores")
        st.plotly_chart(barras_top5(df, "Razao_Social"), use_container_width=True)
    with c2:
        sec("🔫 Gastos por Categoria")
        st.plotly_chart(donut(df, "Categoria",
                              cores=["#fc8181","#f6ad55","#4f8ef7","#68d391","#b794f4"]),
                        use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        sec("🏢 Por Tipo de Unidade")
        st.plotly_chart(barras_simples(df, "Tipo_Unidade", cores=["#2b4bab","#fc8181"]), use_container_width=True)
    with c4:
        sec("🏛️ Por Unidade Policial")
        st.plotly_chart(barras_simples(df, "Nome_Unidade", cores=["#2b4bab","#f6ad55"]), use_container_width=True)

    with st.expander("📋 Ver dados detalhados"):
        cols = ["Data","Nome_Mes","Nome_Unidade","Tipo_Unidade","Regiao",
                "Razao_Social","Descricao","Categoria","Valor_Empenhado"]
        dv = df[cols].copy()
        dv["Data"] = pd.to_datetime(dv["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
        dv["Valor_Empenhado"] = dv["Valor_Empenhado"].apply(lambda x: f"R$ {x:,.2f}")
        dv.columns = ["Data","Mês","Unidade","Tipo","Região","Fornecedor","Item","Categoria","Valor"]
        st.dataframe(dv, use_container_width=True, height=300)


# ── Urbanismo ─────────────────────────────────────────────────────────────────
elif cenario == "🏗️ Secretaria de Urbanismo":
    st.markdown("## 🏗️ Secretaria de Urbanismo — Obras 2026 | Cuiabá-MT")
    st.markdown(f"Exibindo **{len(df)}** de **{len(df_full)}** registros.")
    st.divider()
    kpis(df, "Top Fornecedor", "Razao_Social")
    st.markdown("<br>", unsafe_allow_html=True)

    sec("📅 Evolução Mensal das Obras")
    st.plotly_chart(linha_mensal(df, dim_cal), use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        sec("🏆 Top 5 Fornecedores")
        st.plotly_chart(barras_top5(df, "Razao_Social"), use_container_width=True)
    with c2:
        sec("🏗️ Investimento por Categoria de Obra")
        st.plotly_chart(donut(df, "Categoria",
                              cores=["#f6ad55","#4f8ef7","#68d391","#b794f4","#fc8181"]),
                        use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        sec("🏘️ Por Bairro de Cuiabá")
        st.plotly_chart(barras_simples(df, "Nome_Bairro", cores=["#2b4bab","#f6ad55"]), use_container_width=True)
    with c4:
        sec("🗺️ Por Região da Cidade")
        st.plotly_chart(barras_simples(df, "Regiao", cores=["#2b4bab","#68d391"]), use_container_width=True)

    with st.expander("📋 Ver dados detalhados"):
        cols = ["Data","Nome_Mes","Nome_Bairro","Regiao",
                "Razao_Social","Descricao","Categoria","Valor_Empenhado"]
        dv = df[cols].copy()
        dv["Data"] = pd.to_datetime(dv["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
        dv["Valor_Empenhado"] = dv["Valor_Empenhado"].apply(lambda x: f"R$ {x:,.2f}")
        dv.columns = ["Data","Mês","Bairro","Região","Fornecedor","Serviço/Material","Categoria","Valor"]
        st.dataframe(dv, use_container_width=True, height=300)


# ── Arrecadação Municipal MT ──────────────────────────────────────────────────
else:
    st.markdown("## 💰 Arrecadação Municipal — Mato Grosso 2026")
    st.markdown(f"Exibindo **{len(df)}** de **{len(df_full)}** registros.")
    st.divider()
    kpis(df, "Top Município", "Nome_Municipio")
    st.markdown("<br>", unsafe_allow_html=True)

    sec("📅 Evolução Mensal da Arrecadação")
    st.plotly_chart(linha_mensal(df, dim_cal), use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        sec("🏆 Top 5 Municípios por Arrecadação")
        st.plotly_chart(barras_top5(df, "Nome_Municipio"), use_container_width=True)
    with c2:
        sec("💰 Distribuição por Categoria de Tributo")
        st.plotly_chart(donut(df, "Categoria",
                              cores=["#4f8ef7","#68d391","#f6ad55","#fc8181"]),
                        use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        sec("🗺️ Por Mesorregião do MT")
        st.plotly_chart(barras_simples(df, "Mesorregiao", cores=["#2b4bab","#68d391"]), use_container_width=True)
    with c4:
        sec("📋 Por Tipo de Tributo")
        st.plotly_chart(barras_simples(df, "Descricao", cores=["#2b4bab","#f6ad55"]), use_container_width=True)

    with st.expander("📋 Ver dados detalhados"):
        cols = ["Data","Nome_Mes","Nome_Municipio","Mesorregiao","Porte",
                "Descricao","Categoria","Nome_Orgao","Valor_Empenhado"]
        dv = df[cols].copy()
        dv["Data"] = pd.to_datetime(dv["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
        dv["Valor_Empenhado"] = dv["Valor_Empenhado"].apply(lambda x: f"R$ {x:,.2f}")
        dv.columns = ["Data","Mês","Município","Mesorregião","Porte","Tributo","Categoria","Órgão","Valor"]
        st.dataframe(dv, use_container_width=True, height=300)


# ─────────────────────────────────────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.caption("📊 Dashboard BI Multi-Cenário 2026 | Streamlit + Plotly | Modelagem Star Schema | AulaBI Unifacc")
