## Coverage Mapbiomas Área Calculator (Python & GEE Batch)

---

## Visão Geral do Projeto

Este projeto é uma solução de automação desenvolvida em Python para processar grandes volumes de dados geoespaciais. Ele calcula a área (em hectares) de todas as classes de Uso e Cobertura da Terra (LULC) do MapBiomas Coleção 10 para múltiplos Shapefiles ou feições em lote, utilizando o poder de processamento em nuvem do Google Earth Engine (GEE).

O script foi criado para resolver gargalos de escalabilidade e precisão em projetos que demandam o cruzamento rápido de limites personalizados com os dados raster do MapBiomas.

---

## Fluxo de Trabalho

1. O script Python itera sobre a pasta de Shapefiles de entrada;

2. Carrega as geometrias (via GeoPandas) e as envia para o GEE;

3. O GEE executa o cálculo geodésico de área pixel a pixel (30m);

4. O resultado, uma tabela no formato longo/tidy, é exportado diretamente para o Google Drive.

---

## Funcionalidades Chave:

- Processamento em Lote (Batch): Automação completa para iterar e processar todos os arquivos Shapefile dentro da pasta de entrada;

- Cálculo Geodésico Preciso: Utiliza `ee.Image.pixelArea()` para garantir que a área (em m², convertida para hectares) seja calculada com precisão, considerando a curvatura da Terra e a resolução de 30m do MapBiomas;

- Alto Desempenho: Todo o processamento intensivo é realizado nos servidores do GEE, liberando recursos locais;

- Limpeza de Metadados: O script traduz os códigos numéricos brutos do MapBiomas para nomes legíveis e padronizados (e.g., "3. AGROPECUÁRIA / Pastagem");

- Saída Standard: Exportação direta para o Google Drive no formato CSV (padrão `ee.batch.Export.table.toDrive`).

---

## Stack Técnico e Configuração de Uso:

Pré-requesitos:

- Linguagem **Python 3+**;
- Conta ativa no **Google Earth Engine (GEE)**;
- Acesso ao **Google Drive**.

1. Instalação das bibliotecas

```python

pip install earthengine-api geopandas pandas unidecode

```

2. Autenticação GEE

Antes de rodar o script, deve-se configurar uma conta no Google Earth Engine e autenticar para uso via API Pyhton:

- **Criar e ativar conta GEE:** caso ainda não haja acesso, solicitar e ativar a conta no [site oficial do Google Earth Engine](https://earthengine.google.com/). O acesso é gratuito para fins não comerciais;

- **Gerar as credenciais:** é necessário rodar o comando de auteticação na primeira vez para gerar e armazenar o *token* de acesso em ambiente local.

```python

# Comando para autenticação inicial do usuário. 
# Será abertouma janela do navegador para você fazer login e obter o código de autenticação.
ee.Authenticate() 

```

```python

# Após a autenticação bem-sucedida, o script deve inicializar a conexão:
ee.Initialize()

```

Nota: talvez possa ser necessário gerar outro *token* e autenticar novamente caso o código seja expirado. Não é necessário autenticar novamente após inserir o *token*, apenas inicializar.

3. Organização da estrutura

```

/MapBiomas-GEE-Python-Area-Calculator/
├── shapes/
│   ├── bacia_contas.cpg
│   ├── bacia_contas.dbf
│   ├── bacia_contas.prj
│   ├── bacia_contas.shp
│   ├── bacia_contas.shx
│   ├── ... (todos os arquivos complementares ou mais arquivos shapefile)
│   
├── LICENSE
├── README.md
├── mapbio_geepy_area_calculator.py

```

**Observação:** foi adicionado o shapefile da bacia hidrográfica do Rio de Contas para teste.

4. Execução

- Verificar e ajustar as variáveis `ano` (ano de classificação do MapBiomas) e `id_coluna` (chave primária necessária para identificação da feição no shapefile);

- Se possível realizar a simplificação da geometria dos shapefiles antes de executar o script, visto que o GEE permite apenas requisições de geometria vetorial com tamanho
próximo a 10MB;

- Executar o script;

- Monitorar o status das tarefas na aba **Tasks** do GEE (Opcional, porém recomendado);

- O resultado será salvo na pasta padrão `GEE_MapBiomas_Batch_Export_XXXX` caso não seja renomeada.

## Estrutura de Saída

O arquivo .CSV final é exportado no formato *longo/tidy data*, sendo a chave principal o ID da feição (`id_coluna`).

| Coluna | Descrição | Exemplo |
| :--- | :--- | :--- |
| **(id_coluna)** | ID único da feição original processada | `1001` |
| **Classe_ID** | Código numérico da classe MapBiomas (Coleção 10) | `15` |
| **Nome_Classe** | Nome legível e hierárquico da classe (Grupo / Detalhe) | `3. AGROPECUÁRIA / Pastagem (Nível 2)` |
| **Area_ha** | Área total calculada (em hectares) para aquela classe na feição | `125.756` |

---

## Aplicações e Versatilidade

O **Coverage Mapbiomas Área Calculator** não se limita a um único uso; sua automação em nuvem o torna versátil para diversas áreas que dependem de dados de Uso e Cobertura da Terra (LULC):

### 1. Monitoramento e Conformidade Ambiental

- **Validação de CAR (Cadastro Ambiental Rural):** rápida verificação da proporção de vegetação nativa, áreas de preservação permanente (APP) e reservas legais em grandes volumes de propriedades rurais;

- **Auditoria de Desmatamento:** rastreamento eficiente das mudanças de uso do solo em múltiplas áreas de interesse ao longo dos anos (ajustando a variável `ano`), crucial para relatórios de **compliance**.

### 2. Agricultura e Planejamento Territorial

- **Análise de Expansão Agrícola:** quantificação de pastagens e lavouras em novas fronteiras agrícolas ou dentro de bacias hidrográficas;

- **Gestão de Fazendas/Portfólios:** cálculos precisos de áreas de produção e áreas de conservação para portfólios de terras com centenas de glebas, fornecendo dados prontos para **modelagem financeira**.

### 3. Pesquisa Acadêmica e Setor Público

- **Estudos de Bacias Hidrográficas:** análise rápida da matriz de uso e ocupação do solo em grandes regiões hidrograficamente definidas, essencial para modelos hidrológicos;

- **Validação de Modelos:** o CSV de saída é um dataset limpo e estruturado que pode ser facilmente usado para treinar modelos de Machine Learning ou validação de classificações próprias.

### 4. Consultoria e Relatórios de Sustentabilidade (ESG)

- **Inventários de LULC:** geração automática de inventários detalhados para relatórios de Sustentabilidade e critérios **ESG (Ambiental, Social e Governança)**, provando o uso responsável da terra;

- **Substituição do Uso Manual:** elimina a necessidade de abrir Shapefiles e rasters em softwares GIS locais para realizar o cruzamento, economizando horas de trabalho do analista.

---

## Conecte-se Comigo

*Siga os links abaixo para saber mais sobre minha trajetória profissional e me contatar:*

<div> 
  <a href="mailto:miguel.gms31@gmail.com"><img src="https://img.shields.io/badge/-Gmail-%23333?style=for-the-badge&logo=gmail&logoColor=white" target="_blank"></a>
  <a href="https://www.linkedin.com/in/miguelgms31/" target="_blank"><img src="https://img.shields.io/badge/-LinkedIn-%230077B5?style=for-the-badge&logo=linkedin&logoColor=white" target="_blank"></a>
  <a href="http://lattes.cnpq.br/2943203054995050" target="_blank"><img src="https://img.shields.io/badge/-Lattes-%230077B5?style=for-the-badge&logo=google-scholar&logoColor=white" target="_blank"></a>
</div>

---

## Próximos Passos, Contribuições e Licença

O projeto foi projetado para ser modular e expansível. Existem várias direções que a aplicação pode tomar para aumentar sua versatilidade e robustez:

1. Próximos Passos:

- Implementação de Filtro Temporal: adicionar um parâmetro opcional para processar dados de coleções MapBiomas de anos anteriores (ex: Coleção 8 ou 9), permitindo análises de séries temporais de LULC;

- Exportação para GeoTIFF (Raster): implementar a funcionalidade ee.batch.Export.image.toDrive para que, além do CSV, o usuário possa exportar o recorte rasterizado da área processada para visualização em GIS;

- Integração com a biblioteca geobr: introduzir um modo de entrada que use a biblioteca geobr para buscar limites oficiais (municípios, estados) como alternativa ao Shapefile local;

- Geração de Relatório Resumo: após o download do CSV, gerar um gráfico simples (usando Matplotlib ou Plotly) que summarize as áreas calculadas por classe.

2. Como Contribuir:

- Contribuições, sugestões de melhorias e bug reports são muito bem-vindos! Se você deseja contribuir para o projeto, siga o fluxo de trabalho padrão do GitHub:

 - Faça um Fork do repositório;

 - Crie uma nova branch para sua funcionalidade (git checkout -b feature/minha-melhoria);

 - Implemente suas alterações e teste-as cuidadosamente;

 - Comite suas alterações (git commit -m 'Adiciona funcionalidade X');

 - Faça o push para a branch (git push origin feature/minha-melhoria);

 - Abra um Pull Request detalhado explicando o objetivo e o escopo da sua contribuição.

---

## Licença

Este projeto está sob a Licença MIT – consulte o arquivo LICENSE para mais detalhes.

---