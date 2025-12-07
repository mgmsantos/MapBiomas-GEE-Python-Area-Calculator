## Coverage Mapbiomas Área Calculator (Python & GEE Batch)

---

## Visão Geral do Projeto

Este projeto é uma solução de automação desenvolvida em Python para processar grandes volumes de dados geoespaciais. Ele calcula a área exata (em hectares) de todas as classes de Uso e Cobertura da Terra (LULC) do MapBiomas Coleção 10 para múltiplos Shapefiles ou feições em lote, utilizando o poder de processamento em nuvem do Google Earth Engine (GEE).

O script foi criado para resolver gargalos de escalabilidade e precisão em projetos que demandam o cruzamento rápido de limites personalizados com os dados raster do MapBiomas.

---

## Fluxo de Trabalho

1. O script Python itera sobre a pasta de Shapefiles de entrada;
2. Carrega as geometrias (via GeoPandas) e as envia para o GEE;
3. O GEE executa o cálculo geodésico de área pixel a pixel ($30\text{m}$);
4. O resultado, uma tabela no formato longo/tidy, é exportado diretamente para o Google Drive.

---

## Funcionalidades Chave:

- Processamento em Lote (Batch): Automação completa para iterar e processar todos os arquivos Shapefile dentro da pasta de entrada;
- Cálculo Geodésico Preciso: Utiliza ee.Image.pixelArea() para garantir que a área (em $\text{m}^2$, convertida para hectares) seja calculada com precisão, considerando a curvatura da Terra e a resolução de $30\text{m}$ do MapBiomas;
- Alto Desempenho: Todo o processamento intensivo é realizado nos servidores do GEE, liberando recursos locais;
- Limpeza de Metadados: O script traduz os códigos numéricos brutos do MapBiomas para nomes legíveis e padronizados (e.g., "3. AGROPECUÁRIA / Pastagem");
- Saída Standard: Exportação direta para o Google Drive no formato CSV (padrão ee.batch.Export.table.toDrive).

---

## Stack Técnico e Configuração de Uso:

Pré-requesitos:

- Linguagem **Python 3+**;
- Conta ativa no **Google Earth Engine (GEE)**;
- Acesso ao **Google Drive**.

1. Instalação das bibliotecas

```python

pip install earthegine-api geopandas pandas unidecode 

```

2. Autenticação GEE

Antes de rodar o script, deve-se configurar uma conta no Google Earth Engine e autenticar para uso via API Pyhton:

- **Criar e ativar conta GEE:** caso ainda não haja acesso, solicitar e ativar a conta no ['site oficial do Google Earth Engine'](https://earthengine.google.com/). O acesso é gratuito para fins não comerciais;
- **Gerar as credenciais:** é necessário rodar o comando de auteticação na primeira vez para gerar e armazenar o *token* de acesso em ambiente local.

```python

# Comando para autenticação inicial do usuário. 
# Será abertouma janela do navegador para você fazer login e obter o código de autenticação.
ee.Authenticate() 

# Após a autenticação bem-sucedida, o script deve inicializar a conexão:
ee.Initialize()

```

Nota: talvez possa ser necessário gerar outro *token* e autenticar novamente caso o código seja expirado. Não é necessário autenticar novamente após inserir o *token*, apenas inicializar.

3. Organização da estrutura

```
/MapBiomas-GEE-Python-Area-Calculator/
├── shapes/
│   ├── belem-pa.shp
│   ├── belem-pa.shx
│   ├── belem-pa.dbf
│   ├── ... (todos os arquivos complementares do Shapefile)
│   
├── seu_script_aqui.py
├── README.md
```

4. Execução

- Verificar e ajustar as variáveis `ano` (ano de classificação do MapBiomas) e `id_coluna` (chave primária necessária para identificação da feição no shapefile);
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

## Conecte-se Comigo

---

## Contribuição e Licença

