# WebGIS de Crédito Rural

Este é um WebGIS interativo desenvolvido com Streamlit para visualização e análise de dados de crédito rural no município de Ji-Paraná.

## Funcionalidades

- Visualização interativa de dados de crédito rural
- Mapa com camadas de satélite e polígono do município
- Filtros dinâmicos por data, valor e área
- Estatísticas em tempo real
- Gráfico de evolução do crédito rural
- Tabela com dados detalhados

## Requisitos

- Python 3.11 ou superior
- Bibliotecas listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute o aplicativo:
```bash
python -m streamlit run app.py
```

2. O WebGIS será aberto automaticamente no seu navegador padrão.

## Estrutura de Arquivos

- `app.py`: Código principal do WebGIS
- `data/`: Diretório contendo os arquivos GeoJSON
  - `Jipa.geojson`: Polígono do município de Ji-Paraná
  - `Credi_geo.geojson`: Dados de crédito rural

## Tecnologias Utilizadas

- Streamlit
- Folium
- GeoPandas
- Pandas
- NumPy

## Desenvolvido por

[Seu Nome/Organização] 

http://localhost:8501 