# Desafio Técnico Bemol - Data Engineer

## Sobre o Projeto

Pipeline de ingestão e processamento de dados utilizando arquitetura Lakehouse com camadas Bronze e Silver. O projeto consome dados da [Fake Store API](https://fakestoreapi.com) (users, carts e products) e realiza transformações progressivas para gerar insights sobre vendas por produto.

**Objetivo Principal:** Criar uma tabela de produtos enriquecida com informações de quantidade total vendida e valor total agregado, alimentada pelos dados de carrinho e preços de produtos.

---

## Arquitetura do Projeto

### Camada Bronze

A camada Bronze realiza o mínimo de processamento necessário para estruturar os dados brutos:

- **Remoção de nulos críticos:** Remove linhas onde campos de chave primária estão vazios
- **Renomeação de colunas:** Padroniza nomes para melhor compreensão (ex: `title` → `product_title`)
- **Extração de campos aninhados:** Converte estruturas JSON nested em colunas planas
- **Desaninhamento (Explode):** Transforma arrays em múltiplas linhas (ex: carrinho com N produtos vira N linhas)
- **Adição de colunas técnicas:** como timestamp de ingestão

### Camada Silver

A camada Silver aplica transformações de negócio e prepara dados para análise:

- **Agregações:** Agrupa dados por dimensões (ex: total de produtos vendidos por item)
- **Joins:** Combina dados de múltiplas tabelas Bronze (ex: carrinho + produtos para obter preços)
- **Enriquecimento:** Adiciona informações contextuais aos dados (ex: nome do produto em cada venda)
- **Seleção de colunas:** Remove colunas desnecessárias, mantendo apenas as relevantes
- **Substituição de valores:** Trata valores específicos conforme regras de negócio
- **Cálculos simples:** Realiza operações básicas (ex: receita = quantidade × preço)
- **Validações:** Cria flags e colunas de validação (ex: validação de email com regex)

---

## Arquitetura de Classes

O projeto utiliza programação orientada a objetos para criar uma solução robusta e extensível:

### **BemolLakeStorage**

Classe principal que gerencia leitura e escrita de dados nas camadas Bronze e Silver. Integra automaticamente as classes de logging e monitoramento, garantindo que todas as operações sejam rastreadas e auditadas.

### **BemolLandingReader**

Abstração para leitura de dados de fontes externas (atualmente implementado para APIs, extensível para outras fontes).

### **BemolLogging**

Sistema centralizado de logs que registra todas as operações de leitura e escrita. Gera arquivo de log com timestamp e outros detalhes da operação.

### **BemolMonitor**

Complementa o logging gerando métricas estruturadas sobre as operações de escrita. Fornece visibilidade sobre volume de dados processados.

### **BemolController**

Gerencia colunas de controle adicionadas aos dados durante o processamento. Marca a camada de origem e timestamp de processamento.

### **BemolValidator**

Realiza validações de dados conforme regras de negócio. Atualmente implementa validação de email com regex, mas facilmente extensível para outras validações.

---

## Fluxo de Transformação de Dados

### De Bronze para Silver: Exemplo Prático

O pipeline transforma dados brutos em informações de negócio através de transformações progressivas.

#### 1. Desaninhamento (Bronze)

```python
# Carrinho com array de produtos
# {id: 5, products: [{productId: 1, quantity: 3}, {productId: 2, quantity: 1}]}

df_carts_bronze = df_carts_bronze.withColumn("products", explode("products"))

# Resultado: 2 linhas (uma por produto)
# cart_id=5, product_id=1, quantity=3
# cart_id=5, product_id=2, quantity=1
```

#### 2. Extração e Renomeação (Bronze)

```python
df_carts_bronze = df_carts_bronze.select(
    col("id").alias("cart_id"),
    col("userId").alias("user_id"),
    col("date").alias("cart_date"),
    col("products.productId").alias("product_id"),
    col("products.quantity").alias("product_quantity")
)

# Transforma estrutura aninhada em colunas planas e claras
```

#### 3. Agregação (Silver)

```python
df_sales = df_carts.groupBy("product_id").agg(
    sum("product_quantity").alias("total_quantity_sold")
)

# Resultado: total de quantidade vendida por produto
# product_id=1, total_quantity_sold=150
# product_id=2, total_quantity_sold=87
```

#### 4. Enriquecimento com Join (Silver)

```python
df_products_silver = df_products.join(
    df_sales,
    df_products.id == df_sales.product_id,
    "left"
).drop(df_sales.product_id)

# Combina informações de produtos com dados de vendas
# Agora cada produto tem sua quantidade vendida
```

#### 5. Tratamento de Nulos (Silver)

```python
df_products_silver = df_products_silver.fillna(0, subset=["total_quantity_sold"])

# Produtos sem vendas recebem 0 em vez de NULL
```

#### 6. Cálculo Final (Silver)

```python
df_products_silver = df_products_silver.withColumn(
    "total_revenue",
    col("price") * col("total_quantity_sold")
)

# Resultado final: tabela com produtos e suas métricas de vendas
# product_id | product_name | price | total_quantity_sold | total_revenue
# 1          | Fjallraven   | 109.95| 150                 | 16492.50
```

### Resultado Final

A tabela Silver `products_sales` contém todas as informações necessárias para análise de vendas por produto, com dados limpos, validados e enriquecidos.

---

# Como Usar

## Pré-requisitos

- Python 3.11 ou anterior
- Java 8+ instalado

### Instalar Python 3.11

**Mac:**

```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install python3.11 python3.11-venv
```

**Windows:**
Baixe em https://www.python.org/downloads/ e instale a versão 3.11.

### Instalar Java

**Mac:**

```bash
brew install java
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install default-jdk
```

**Windows:**
Baixe em https://www.oracle.com/java/technologies/downloads/ e instale a versão LTS.

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/desafio-bemol-data-engineer.git
cd desafio-bemol-data-engineer
```

2. Crie um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução

### Nota Importante: Ambiente de Desenvolvimento

Durante o desenvolvimento, encontrei muitos problemas de incompatibilidades ao tentar executar PySpark + Delta Lake no ambiente Windows e no Google Colab.

**Solução encontrada:** Usar **WSL2 (Windows Subsystem for Linux)** com as versões específicas definidas no `requirements.txt`.

O código funciona perfeitamente em WSL2 ou Linux/Mac com as seguintes versões:

- Python 3.11
- PySpark 3.4.2
- Delta Lake 2.4.0

**Se você estiver no Windows:**

1. Instale WSL2: https://learn.microsoft.com/pt-br/windows/wsl/install
2. Instale Python 3.11 no WSL2
3. Clone o repositório e execute normalmente

---

### Opção 1: Pipeline Automático (Instável)

```bash
python run_pipeline.py
```

O script executará os 4 notebooks em sequência. **Nota:** Este método é instável e pode quebrar no meio da operação, especialmente com grandes volumes de dados.

### Opção 2: Execução Segura (Recomendado)

Execute os notebooks individualmente no Jupyter/VSCode, respeitando a ordem:

**Camada Bronze (executar primeiro):**

1. `notebooks/bronze_products_carts.ipynb`
2. `notebooks/bronze_users.ipynb`

**Camada Silver (executar depois):**

3. `notebooks/silver_products_sales.ipynb`
4. `notebooks/silver_users.ipynb`

## Outputs

Os notebooks executados geram arquivos Delta em:

- Bronze: `data/bronze/`
- Silver: `data/silver/`

Se usar `python run_pipeline.py`, os notebooks executados também serão salvos em `output/`.

## Estrutura do Projeto

```
desafio-bemol-data-engineer/
├── notebooks/
│   ├── core/
│   │   ├── bemol_lake_storage.py
│   │   ├── bemol_controller.py
│   │   ├── bemol_landing_reader.py
│   │   ├── bemol_logging.py
│   │   ├── bemol_monitor.py
│   │   └── bemol_validator.py
│   ├── bronze_products_carts.ipynb
│   ├── bronze_users.ipynb
│   ├── silver_products_sales.ipynb
│   └── silver_users.ipynb
├── data/
│   ├── bronze/
│   │   ├── products_carts/
│   │   └── users/
│   ├── silver/
│   │   ├── products_sales/
│   │   └── users/
│   └── monitor/
├── logs/
│   ├── bronze_products_carts/
│   ├── bronze_users/
│   ├── silver_products_sales/
│   └── silver_users/
├── output/
├── run_pipeline.py
├── requirements.txt
└── README.md
```

---

## Stack

- **Python** 3.11 ou anterior
- **PySpark** 3.4.2
- **Delta Lake** 2.4.0
- **Papermill** (orquestração de notebooks)
- **Requests** (consumo de API)

**Nota sobre as versões:** Após diversos testes de compatibilidade, esta foi a única combinação de versões que permitiu escrever dados em Delta Lake localmente sem problemas. Versões mais recentes apresentaram incompatibilidades ao tentar fazer operações de escrita com Delta.

---
