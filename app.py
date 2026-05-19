import streamlit as st
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import pandas as pd
import numpy as np

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="WebGIS | Crédito Rural",
    page_icon="🗺️",
    layout="wide"
)

# ── CSS personalizado ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Reset geral */
* { font-family: 'Inter', sans-serif; }

/* Fundo da página */
.stApp {
    background: #0f1117;
    color: #e2e8f0;
}

/* Cabeçalho principal */
.main-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #0f1117 100%);
    border-bottom: 1px solid #2d3748;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}
.main-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f7fafc;
    letter-spacing: -0.5px;
    margin: 0;
}
.main-header p {
    font-size: 0.85rem;
    color: #718096;
    margin: 0.3rem 0 0 0;
}

/* Painel de filtros */
.filter-panel {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
}
.filter-panel-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #4a90d9;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.filter-panel-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #2d3748;
}

/* Cards de métricas */
.metric-card {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #4a90d9; }
.metric-label {
    font-size: 0.72rem;
    font-weight: 500;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-size: 1.35rem;
    font-weight: 700;
    color: #f7fafc;
    font-family: 'JetBrains Mono', monospace;
}
.metric-value.green { color: #68d391; }
.metric-value.blue  { color: #63b3ed; }
.metric-value.yellow{ color: #f6e05e; }
.metric-value.teal  { color: #81e6d9; }

/* Subtítulos de seção */
.section-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    padding: 0.6rem 0;
    border-bottom: 1px solid #2d3748;
    margin-bottom: 1rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #13161f !important;
    border-right: 1px solid #2d3748;
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: #a0aec0;
    font-size: 0.85rem;
}

/* Sliders */
.stSlider > div > div > div { background: #4a90d9 !important; }

/* Dataframe */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Esconder elementos padrão do Streamlit */
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🗺️ WebGIS · Crédito Rural</h1>
    <p>Visualização e análise de operações de crédito rural — Ji-Paraná, Rondônia</p>
</div>
""", unsafe_allow_html=True)

# ── Carregar dados ──────────────────────────────────────────────────────────
@st.cache_data
def load_jipa():
    return gpd.read_file("data/Jipa.geojson")

@st.cache_data
def load_credi():
    gdf = gpd.read_file("data/Credi_geo.geojson")
    gdf['dt_emissao'] = pd.to_datetime(gdf['dt_emissao'])
    return gdf

gdf_jipa  = load_jipa()
gdf_credi = load_credi()

# ── Sidebar: resumo geral ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Resumo Geral")
    st.markdown(f"**Total de registros:** {len(gdf_credi):,}")
    st.markdown(f"**Crédito total:** R$ {gdf_credi['vl_parc_cr'].sum():,.2f}")
    st.markdown(f"**Área total:** {gdf_credi['vl_area_in'].sum():,.2f} ha")
    st.markdown("---")
    st.markdown("**Período coberto**")
    st.markdown(f"{gdf_credi['dt_emissao'].min().strftime('%d/%m/%Y')} → {gdf_credi['dt_emissao'].max().strftime('%d/%m/%Y')}")

# ── Painel de filtros ────────────────────────────────────────────────────────
st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
st.markdown('<div class="filter-panel-title">⚙ Filtros</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.2, 1, 1])

with col1:
    min_date = gdf_credi['dt_emissao'].min().date()
    max_date = gdf_credi['dt_emissao'].max().date()

    st.markdown("📅 **Período de Emissão**")
    c_ini, c_fim = st.columns(2)
    with c_ini:
        data_inicio = st.date_input(
            "Data Inicial",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="data_inicio",
            label_visibility="visible"
        )
    with c_fim:
        data_fim = st.date_input(
            "Data Final",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="data_fim",
            label_visibility="visible"
        )
    selected_date = (data_inicio, data_fim)
    
with col2:
    min_valor = float(gdf_credi['vl_parc_cr'].min())
    max_valor = float(gdf_credi['vl_parc_cr'].max())
    valor_range = st.slider(
        "💰 Valor do Crédito (R$)",
        min_value=min_valor,
        max_value=max_valor,
        value=(min_valor, max_valor),
        format="R$ %.0f",
        help="Filtre pelo valor da parcela de crédito"
    )

with col3:
    min_area = float(gdf_credi['vl_area_in'].min())
    max_area = float(gdf_credi['vl_area_in'].max())
    area_range = st.slider(
        "🌿 Área (hectares)",
        min_value=min_area,
        max_value=max_area,
        value=(min_area, max_area),
        format="%.1f ha",
        help="Filtre pelo tamanho da área financiada"
    )

st.markdown('</div>', unsafe_allow_html=True)

# ── Aplicar filtros ──────────────────────────────────────────────────────────
if len(selected_date) == 2:
    mask = (
        (gdf_credi['dt_emissao'].dt.date >= selected_date[0]) &
        (gdf_credi['dt_emissao'].dt.date <= selected_date[1]) &
        (gdf_credi['vl_parc_cr'] >= valor_range[0]) &
        (gdf_credi['vl_parc_cr'] <= valor_range[1]) &
        (gdf_credi['vl_area_in'] >= area_range[0]) &
        (gdf_credi['vl_area_in'] <= area_range[1])
    )
    gdf_credi_filtered = gdf_credi[mask].copy()
else:
    gdf_credi_filtered = gdf_credi.copy()

# ── Mapa ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🗺 Mapa Interativo</div>', unsafe_allow_html=True)

def create_map():
    centroid = gdf_jipa.geometry.to_crs(epsg=3857).centroid.to_crs(epsg=4326).iloc[0]
    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=10,
        tiles="CartoDB dark_matter"
    )

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satélite',
        overlay=False,
        control=True
    ).add_to(m)

    folium.GeoJson(
        gdf_jipa,
        name="Ji-Paraná",
        style_function=lambda x: {
            'fillColor': 'none',
            'color': '#f6ad55',
            'weight': 2.5,
            'fillOpacity': 0
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["NM_MUN", "AREA_KM2"],
            aliases=["Município:", "Área (km²):"]
        )
    ).add_to(m)

    if not gdf_credi_filtered.empty:
        gdf_plot = gdf_credi_filtered.copy()
        for col in gdf_plot.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
            gdf_plot[col] = gdf_plot[col].dt.strftime('%Y-%m-%d')

        folium.GeoJson(
            gdf_plot.to_json(),
            name="Crédito Rural",
            style_function=lambda x: {
                'fillColor': '#4a90d9',
                'color': '#63b3ed',
                'weight': 1.5,
                'fillOpacity': 0.4
            },
            popup=folium.GeoJsonPopup(
                fields=["dt_emissao", "vl_parc_cr", "vl_area_in"],
                aliases=["📅 Emissão:", "💰 Valor (R$):", "🌿 Área (ha):"]
            )
        ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m

m = create_map()
folium_static(m, width=1400, height=650)

# ── Métricas ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Indicadores — Seleção Atual</div>', unsafe_allow_html=True)

total_valor  = gdf_credi_filtered["vl_parc_cr"].sum()
total_area   = gdf_credi_filtered["vl_area_in"].sum()
num_op       = len(gdf_credi_filtered)
media_credito = gdf_credi_filtered["vl_parc_cr"].mean() if num_op > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 Total de Crédito</div>
        <div class="metric-value green">R$ {total_valor:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🌿 Área Total</div>
        <div class="metric-value teal">{total_area:,.1f} ha</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📋 Operações</div>
        <div class="metric-value blue">{num_op:,}</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📊 Média por Operação</div>
        <div class="metric-value yellow">R$ {media_credito:,.0f}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gráfico de evolução ────────────────────────────────────────────────────
st.markdown('<div class="section-title">📉 Evolução do Crédito Rural</div>', unsafe_allow_html=True)

if not gdf_credi_filtered.empty:
    evolucao = (
        gdf_credi_filtered
        .assign(dt=gdf_credi_filtered['dt_emissao'].dt.strftime('%Y-%m-%d'))
        .groupby("dt")["vl_parc_cr"]
        .sum()
        .reset_index()
        .sort_values("dt")
        .set_index("dt")
        .rename(columns={"vl_parc_cr": "Valor (R$)"})
    )
    st.line_chart(evolucao, height=220)
else:
    st.info("Nenhum dado encontrado para os filtros selecionados.")

# ── Tabela ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🗃 Registros Filtrados</div>', unsafe_allow_html=True)

if not gdf_credi_filtered.empty:
    tabela = gdf_credi_filtered[["dt_emissao", "vl_parc_cr", "vl_area_in"]].copy()
    tabela["dt_emissao"] = tabela["dt_emissao"].dt.strftime('%d/%m/%Y')
    tabela.columns = ["Data de Emissão", "Valor do Crédito (R$)", "Área (hectares)"]
    tabela["Valor do Crédito (R$)"] = tabela["Valor do Crédito (R$)"].map("R$ {:,.2f}".format)
    tabela["Área (hectares)"] = tabela["Área (hectares)"].map("{:,.2f} ha".format)
    st.dataframe(tabela, use_container_width=True, hide_index=True, height=320)

# ── Rodapé ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#4a5568;font-size:0.78rem;'>"
    "Desenvolvido com Streamlit · Folium · GeoPandas</p>",
    unsafe_allow_html=True
)
