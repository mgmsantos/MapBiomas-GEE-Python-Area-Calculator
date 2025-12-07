# -*- coding: utf-8 -*-

# --- DOCUMENTAÇÃO COMPLETA DO SCRIPT DE ANÁLISE MAPBIOMAS ---

# OBJETIVO: Automatizar o cálculo da área de classes de Uso e Ocupação do Solo
# (MapBiomas Collection 10) para múltiplas áreas de interesse (Shapefiles locais).
#
# O script itera sobre uma pasta de Shapefiles, converte cada feição para o
# Google Earth Engine (GEE), calcula a área (em hectares) de cada classe
# MapBiomas e exporta os resultados em:
#
# 1. Tabela (CSV) no formato Longo (uma linha por feição por classe).
#
# REQUISITOS: Python 3+, Google Earth Engine API, geopandas, re, unidecode.
# --------------------------------------------------------------------------------

# %%

# ------------------------------------------------------------------------
# 1. INSTALAÇÃO E IMPORTAÇÃO DE BIBLIOTECAS NECESSÁRIAS
# ------------------------------------------------------------------------

# Instale as dependências se necessário:
# pip install earthengine-api geopandas unidecode

import ee                       # Google Earth Engine Python API.
import geopandas as gpd         # Usado para ler, manipular e reprojetar Shapefiles locais.
import pandas as pd             # Usado internamente pelo GeoPandas.
import re                       # Módulo de Expressões Regulares para limpeza de strings.
from unidecode import unidecode # Usado para remover acentos e caracteres especiais (e.g., 'á' -> 'a').
import os                       # Módulo para interação com o sistema operacional (listagem e manipulação de caminhos).

# %%

# ------------------------------------------------------------------------
# 2. AUTENTICAÇÃO E INICIALIZAÇÃO
# ------------------------------------------------------------------------

# Necessário se estiver rodando pela primeira vez na sessão.
# ee.Authenticate() # Comando para autenticação inicial do usuário.

# Inicializa a conexão com o servidor GEE (DEVE SER EXECUTADO)
try:
    ee.Initialize()
    print("Conexão com Google Earth Engine inicializada com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o GEE: {e}. Verifique a autenticação.")

# %%

# ------------------------------------------------------------------------
# 2.2 PARÂMETROS GLOBAIS DE ENTRADA
# ------------------------------------------------------------------------

diretorio_shapes = 'shapes' # Nome da pasta onde os shapefiles de entrada estão localizados.
id_coluna = 'fid' # Nome da coluna que identifica unicamente cada polígono (Feature) no shapefile.

# CONFIGURAÇÕES MAPBIOMAS
mapbiomas_asset = 'projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_coverage_v2'
ano = '2024'  # Ano da classificação MapBiomas a ser utilizada (define a banda 'classification_2024').

# Define a pasta de saída do seu Google Drive para salvar todos os arquivos .csv
folder_drive_export = f'GEE_MapBiomas_Batch_Export_{ano}'

# Lista de arquivos .shp no diretório
arquivos_shp = [f for f in os.listdir(diretorio_shapes) if f.endswith('.shp')]
if not arquivos_shp:
    # Levanta um erro e interrompe o script se nenhum arquivo for encontrado.
    raise FileNotFoundError(f'Nenhum arquivo .shp encontrado em: {diretorio_shapes}')

print("**Arquivos shapefile Encontrados:**")
print("----------------------------")
for arquivo in arquivos_shp:
    print(arquivo) 
print("----------------------------")

# %%

# ------------------------------------------------------------------------
# 2.3. LEGENDAS (DICIONÁRIO MAPBIOMAS)
# ------------------------------------------------------------------------

# Dicionário de mapeamento GEE: Código numérico da classe -> Nome do Grupo/Classe (formato longo)
# Este formato facilita a separação das colunas 'Grande Grupo' e 'Classe Detalhada' no pós-processamento.
mapbiomas_legend = ee.Dictionary({
    
    # 1. FLORESTA (Nível 1: Código 1)
    1:  '1. FLORESTA / (Nível 1)', 
    3:  '1. FLORESTA / Formação Florestal',
    4:  '1. FLORESTA / Formação Savânica',
    5:  '1. FLORESTA / Mangue',
    6:  '1. FLORESTA / Floresta Alagável (Várzea)',
    49: '1. FLORESTA / Restinga Arbórea',
    
    # 2. VEGETAÇÃO HERBÁCEA E ARBUSTIVA (Nível 1: Código 2)
    10: '2. VEGETAÇÃO HERBÁCEA E ARBUSTIVA / (Nível 1)', 
    11: '2. VEGETAÇÃO HERBÁCEA E ARBUSTIVA / Campo Alagado e Área Pantanosa',
    12: '2. VEGETAÇÃO HERBÁCEA E ARBUSTIVA / Formação Campestre',
    32: '2. VEGETAÇÃO HERBÁCEA E ARBUSTIVA / Apicum',
    29: '2. VEGETAÇÃO HERBÁCEA E ARBUSTIVA / Afloramento Rochoso',
    50: '2. VEGETAÇÃO HERBÁCEA E ARBUSTIVA / Restinga Herbácea',

    # 3. AGROPECUÁRIA (Nível 1: Código 3)
    14: '3. AGROPECUÁRIA / (Nível 1)', 
    15: '3. AGROPECUÁRIA / Pastagem (Nível 2)',
    # 3.1. Agricultura
    18: '3. AGROPECUÁRIA / Agricultura (Nível 2)',
    19: '3. AGROPECUÁRIA / Lavoura Temporária (Nível 3)',
    39: '3. AGROPECUÁRIA / Soja', 
    20: '3. AGROPECUÁRIA / Cana (Cana-de-Açúcar)',
    40: '3. AGROPECUÁRIA / Arroz',
    62: '3. AGROPECUÁRIA / Algodão',
    41: '3. AGROPECUÁRIA / Outras Lavouras Temporárias',
    36: '3. AGROPECUÁRIA / Lavoura Perene (Nível 3)',
    46: '3. AGROPECUÁRIA / Café',
    47: '3. AGROPECUÁRIA / Citrus',
    35: '3. AGROPECUÁRIA / Dendê',
    48: '3. AGROPECUÁRIA / Outras Lavouras Perenes',
    # 3.2. Silvicultura
    9:  '3. AGROPECUÁRIA / Silvicultura (Nível 2)', 
    21: '3. AGROPECUÁRIA / Mosaico de Usos (Nível 2)', 
    
    # 4. ÁREA NÃO VEGETADA (Nível 1: Código 4)
    22: '4. ÁREA NÃO VEGETADA / (Nível 1)', 
    23: '4. ÁREA NÃO VEGETADA / Praia, Duna e Areal',
    24: '4. ÁREA NÃO VEGETADA / Área Urbanizada',
    30: '4. ÁREA NÃO VEGETADA / Mineração',
    75: '4. ÁREA NÃO VEGETADA / Usina Fotovoltaica',
    25: '4. ÁREA NÃO VEGETADA / Outras Áreas Não Vegetadas',

    # 5. CORPO D'ÁGUA (Nível 1: Código 5)
    33: '5. CORPO D\'ÁGUA / Rio, Lago e Oceano',
    31: '5. CORPO D\'ÁGUA / Aquicultura',
    
    # 6. OUTROS / NÃO OBSERVADO (Nível 1: Código 6)
    27: '6. OUTROS / Não Observado'
})

# %%

# ------------------------------------------------------------------------
# 3. CARREGAMENTO DO RASTER MAPBIOMAS (DEFINIÇÃO)
# ------------------------------------------------------------------------

# Seleciona a banda do ano desejado (ex: 'classification_2024')
mapbiomas_banda = f'classification_{ano}'
mapbiomas_image = ee.Image(mapbiomas_asset).select(mapbiomas_banda)
print(f'Raster MapBiomas {mapbiomas_banda} carregado.')

# %%

# ------------------------------------------------------------------------
# 4. FUNÇÃO PRINCIPAL DE CÁLCULO DE ÁREA (DEFINIÇÃO)
# ------------------------------------------------------------------------

def calculate_area_per_class(feature):

    """
    Função a ser mapeada sobre a FeatureCollection.
    Calcula a área geodésica de cada classe MapBiomas dentro de uma feature (polígono).
    Utiliza ee.Image.pixelArea() para garantir precisão geodésica.
    Retorna uma ee.FeatureCollection aninhada (uma coleção de resultados).
    """
    
    # 4.1. Obtém o ID da feição (chave primária)
    feature_id = feature.get(id_coluna) 
    
    # 4.2. Cria a imagem de área (m²) e adiciona o raster MapBiomas
    # Banda 0: pixelArea (m²). Banda 1: classification_2024 (código da classe).
    areaImage = ee.Image.pixelArea().addBands(mapbiomas_image) 
    
    # 4.3. Reduz a imagem dentro da geometria da feição
    areas = areaImage.reduceRegion(**{
        'reducer': ee.Reducer.sum().group(**{
            'groupField': 1, # Agrupa pelo índice da banda de classificação (MapBiomas)
            'groupName': 'class'
        }),
        'geometry': feature.geometry(),
        'scale': 30, # Resolução de processamento (MapBiomas é 30m)
        'maxPixels': 1e10 # Permite cálculo em geometrias grandes
    })
    
    # 4.4 Extrai a lista de áreas e classes (ee.List de ee.Dictionary)
    classAreas = ee.List(areas.get('groups')) 

    # 4.4. Função de Mapeamento para criar Features no formato Longo
    def format_results_long(item):
        item = ee.Dictionary(item)
        
        classNumber = ee.Number(item.get('class')).toInt()
        # Conversão de m² para ha (dividir por 10.000)
        area_ha = ee.Number(item.get('sum')).divide(1e4) 

        class_name = mapbiomas_legend.get(classNumber, 'Código de Classe Desconhecido')
        
        # Retorna um Feature para CADA CLASSE:
        return ee.Feature(None, {
            id_coluna: feature_id, 
            'Classe_ID': classNumber, 
            'Nome_Classe': class_name,
            'Area_ha': area_ha
        })

    # Mapeia a Lista de Dicionários para uma Lista de Features GEE
    features_list = classAreas.map(format_results_long)
    
    # Retorna o resultado como uma FeatureCollection aninhada
    return ee.FeatureCollection(features_list)

# %%

# ------------------------------------------------------------------------
# 5. ITINERÁRIO (LOOP) PARA PROCESSAR TODOS OS ARQUIVOS (EXECUÇÃO)
# ------------------------------------------------------------------------

print("\n========================================================")
print(f"INICIANDO PROCESSAMENTO DE {len(arquivos_shp)} SHAPEFILES")
print(f"========================================================")

# Loop principal que itera sobre cada shapefile encontrado.
for arquivo in arquivos_shp:
    shapefile_path = os.path.join(diretorio_shapes, arquivo)
    nome_base = os.path.splitext(arquivo)[0] # Obtém o nome do arquivo sem a extensão .shp
    
    print(f"\n---> Processando: **{arquivo}**")

    try:
        # 5.1. Carregar o Shapefile local usando GeoPandas
        gdf = gpd.read_file(shapefile_path)
        
        # Reprojetar para WGS 84 (EPSG:4326), formato exigido pelo GEE
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        
        # 5.2. Converter GeoDataFrame para FeatureCollection GEE
        features = []
        for index, row in gdf.iterrows():
            geom_json = row.geometry.__geo_interface__
            # Cria a Feature GEE, propagando o ID LOCAL
            features.append(ee.Feature(geom_json, {id_coluna: row[id_coluna]}))
        
        feature_collection = ee.FeatureCollection(features)
        print(f"   - Sucesso: {len(features)} feições convertidas para GEE.")

        # 5.3. Limpeza de nome para a exportação
        nome_limpo = unidecode(nome_base)
        nome_limpo = re.sub(r'[^\w.-]', '_', nome_limpo).replace('__', '_').strip('_')
        
        descricao_tarefa = f'Mapbiomas_Area_{nome_limpo}_{ano}'

        # 5.4. Execução do cálculo e início da exportação para o Google Drive
        # O .map() aplica o cálculo a cada feição. O .flatten() transforma a coleção aninhada em uma tabela longa.
        task = ee.batch.Export.table.toDrive(
            collection = feature_collection.map(calculate_area_per_class).flatten(),
            description = descricao_tarefa,
            folder = folder_drive_export, # Pasta de destino no Google Drive
            fileNamePrefix = f'areas_{nome_limpo.lower()}_c{ano}',
            fileFormat = 'CSV'
        )

        task.start() 
        print(f"   - **Tarefa Iniciada.** Nome: '{descricao_tarefa}'. Salvo em: {folder_drive_export}")

    except Exception as e:
        # Captura e imprime erros específicos de carregamento ou conversão.
        print(f"   Erro ao processar {arquivo}: {e}")
        
print("\n========================================================")
print(f"Todos os {len(arquivos_shp)} shapefiles foram processados.")
print(f"Monitore as {len(arquivos_shp)} tarefas na aba 'Tasks' do GEE.")