import streamlit as st
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
import json

# Configuração da página
st.set_page_config(
    page_title="WebGIS Interativo",
    page_icon="🗺️",
    layout="wide"
)

# Título e descrição
st.title("🗺️ WebGIS Interativo")
st.markdown("""
    Bem-vindo ao seu WebGIS interativo! Aqui você pode visualizar e analisar dados geoespaciais.
""")

# Carregar polígono do município de Ji-Paraná
@st.cache_data
def load_jipa():
    gdf = gpd.read_file("data/Jipa.geojson")
    return gdf

gdf_jipa = load_jipa()

# Carregar camada adicional: Credi_geo.geojson
@st.cache_data
def load_credi():
    gdf = gpd.read_file("data/Credi_geo.geojson")
    return gdf

gdf_credi = load_credi()

# Sidebar para controles
st.sidebar.header("Estatísticas de Crédito Rural")
total_valor = gdf_credi["vl_parc_cr"].sum()
total_area = gdf_credi["vl_area_in"].sum()
st.sidebar.write(f"Total de Crédito: R$ {total_valor:,.2f}")
st.sidebar.write(f"Área Total: {total_area:,.2f} hectares")

# Criar dados de exemplo (pontos aleatórios no Brasil)
@st.cache_data
def generate_sample_data():
    # Coordenadas aproximadas do Brasil
    lat_min, lat_max = -33.0, 5.0
    lon_min, lon_max = -74.0, -34.0
    
    # Gerar 100 pontos aleatórios
    n_points = 100
    lats = np.random.uniform(lat_min, lat_max, n_points)
    lons = np.random.uniform(lon_min, lon_max, n_points)
    
    # Criar DataFrame com os pontos
    data = {
        'latitude': lats,
        'longitude': lons,
        'valor': np.random.uniform(100, 1000, n_points),
        'categoria': np.random.choice(['A', 'B', 'C'], n_points)
    }
    
    return pd.DataFrame(data)

# Carregar dados
df = generate_sample_data()

# Criar mapa base
def create_map():
    # Centralizar no polígono de Ji-Paraná
    centroid = gdf_jipa.geometry.centroid.iloc[0]
    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=10,
        tiles="OpenStreetMap"
    )
    
    # Adicionar camada de satélite (Esri)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satélite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Adicionar polígono de Ji-Paraná
    folium.GeoJson(
        gdf_jipa,
        name="Ji-Paraná",
        style_function=lambda x: {
            'fillColor': 'none',
            'color': 'orange',
            'weight': 2,
            'fillOpacity': 0
        },
        tooltip=folium.GeoJsonTooltip(fields=["NM_MUN", "AREA_KM2"], aliases=["Município:", "Área (km²):"])
    ).add_to(m)

    # Adicionar camada Credi_geo.geojson com dados filtrados
    if not gdf_credi_filtered.empty:
        folium.GeoJson(
            gdf_credi_filtered,
            name="CrediGeo",
            style_function=lambda x: {
                'fillColor': 'blue',
                'color': 'blue',
                'weight': 2,
                'fillOpacity': 0.3
            },
            popup=folium.GeoJsonPopup(
                fields=["dt_emissao", "vl_parc_cr", "vl_area_in"],
                aliases=["Data de Emissão:", "Valor da Parcela:", "Área:"]
            )
        ).add_to(m)
    
    folium.LayerControl().add_to(m)
    return m

# Layout: mapa em cima, estatísticas e gráfico abaixo
st.subheader("Mapa Interativo")

# Filtros dinâmicos
col1, col2, col3 = st.columns(3)
with col1:
    # Converter datas para datetime
    gdf_credi['dt_emissao'] = pd.to_datetime(gdf_credi['dt_emissao'])
    min_date = gdf_credi['dt_emissao'].min()
    max_date = gdf_credi['dt_emissao'].max()
    selected_date = st.date_input(
        "Filtrar por Data",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

with col2:
    min_valor = float(gdf_credi['vl_parc_cr'].min())
    max_valor = float(gdf_credi['vl_parc_cr'].max())
    valor_range = st.slider(
        "Filtrar por Valor (R$)",
        min_value=min_valor,
        max_value=max_valor,
        value=(min_valor, max_valor)
    )

with col3:
    min_area = float(gdf_credi['vl_area_in'].min())
    max_area = float(gdf_credi['vl_area_in'].max())
    area_range = st.slider(
        "Filtrar por Área (hectares)",
        min_value=min_area,
        max_value=max_area,
        value=(min_area, max_area)
    )

# Aplicar filtros
mask = (
    (gdf_credi['dt_emissao'].dt.date >= selected_date[0]) &
    (gdf_credi['dt_emissao'].dt.date <= selected_date[1]) &
    (gdf_credi['vl_parc_cr'] >= valor_range[0]) &
    (gdf_credi['vl_parc_cr'] <= valor_range[1]) &
    (gdf_credi['vl_area_in'] >= area_range[0]) &
    (gdf_credi['vl_area_in'] <= area_range[1])
)
gdf_credi_filtered = gdf_credi[mask].copy()
# Converter data para string para evitar erro de serialização
gdf_credi_filtered['dt_emissao'] = gdf_credi_filtered['dt_emissao'].dt.strftime('%Y-%m-%d')

# Criar mapa com dados filtrados
m = create_map()
folium_static(m, width=1400, height=700)

# Estatísticas de Crédito Rural
st.subheader("Estatísticas de Crédito Rural")

# Criar colunas para estatísticas
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_valor = gdf_credi_filtered["vl_parc_cr"].sum()
    st.metric("Total de Crédito", f"R$ {total_valor:,.2f}")

with col2:
    total_area = gdf_credi_filtered["vl_area_in"].sum()
    st.metric("Área Total", f"{total_area:,.2f} hectares")

with col3:
    num_operacoes = len(gdf_credi_filtered)
    st.metric("Número de Operações", f"{num_operacoes:,}")

with col4:
    media_credito = gdf_credi_filtered["vl_parc_cr"].mean()
    st.metric("Média por Operação", f"R$ {media_credito:,.2f}")

# Gráficos
st.subheader("Evolução do Crédito Rural")
evolucao = gdf_credi_filtered.groupby("dt_emissao")["vl_parc_cr"].sum().reset_index()
evolucao = evolucao.sort_values("dt_emissao")
st.line_chart(evolucao.set_index("dt_emissao"))

# Tabela de dados
st.subheader("Dados de Crédito Rural")
# Selecionar e renomear colunas para exibição
tabela = gdf_credi_filtered[["dt_emissao", "vl_parc_cr", "vl_area_in"]].copy()
tabela.columns = ["Data de Emissão", "Valor do Crédito (R$)", "Área (hectares)"]
# Formatar valores
tabela["Valor do Crédito (R$)"] = tabela["Valor do Crédito (R$)"].map("R$ {:,.2f}".format)
tabela["Área (hectares)"] = tabela["Área (hectares)"].map("{:,.2f}".format)
# Exibir tabela com paginação
st.dataframe(
    tabela,
    use_container_width=True,
    hide_index=True
)

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido com Streamlit, Folium e GeoPandas") 