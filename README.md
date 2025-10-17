# Desafio Técnico Bemol - Data Engineer

## 📋 Sobre o Projeto

Pipeline de ingestão e processamento de dados utilizando arquitetura Lakehouse com camadas Bronze e Silver. O projeto consome dados da [Fake Store API](https://fakestoreapi.com) (users, carts e products) e realiza transformações progressivas para gerar insights sobre vendas por produto.

**Objetivo Principal:** Criar uma tabela de produtos enriquecida com informações de quantidade total vendida e valor total agregado, alimentada pelos dados de carrinho e preços de produtos.

---

## 🎯 Arquitetura do Projeto

### Camada Bronze

Tratamento leve dos dados brutos com foco em limpeza estrutural:

- **Notebook 1 (Carts & Products):** Desaninhamento de carrinho com uma linha por produto, remoção de nulos e tratamentos básicos
- **Notebook 2 (Users):** Padronização e limpeza dos dados de usuários

### Camada Silver

Agregações e transformações de negócio:

- **Notebook 1 (Analytics):** Agregação de quantidade vendida por produto, enriquecimento com preços e cálculo de valor total vendido
- **Notebook 2 (Data Quality):** Validações e monitoramento de qualidade dos dados

---

## 🛠️ Stack Tecnológico

- **Python** 3.12
- **PySpark** 3.4.2
- **Delta Lake** 2.4.0
- **Requests** (para consumo de API)

> **Nota:** Essas versões foram escolhidas por serem as únicas que permitiram rodar Delta Lake localmente sem conflitos.

---

## 📚 Arquitetura de Classes

O projeto utiliza programação orientada a objetos para criar uma solução robusta e extensível:

### **Lakehouse**

Responsável por leitura e escrita de dados nas camadas Bronze e Silver, simulando um cenário real de Data Lake.

### **LandingReader**

Abstração para leitura de dados de fontes externas (atualmente implementado para APIs, extensível para outras fontes).

### **Logging**

Integrada com `Lakehouse` e `LandingReader`, gera arquivo de logs detalhado sobre todas as operações de leitura e escrita.

### **Monitor**

Complementa o logging gerando:

- Mensagens estruturadas no arquivo de logs
- DataFrame com metadados de escrita (count, número de colunas, nome da tabela, timestamp)

### **Controller**

Cria e gerencia colunas de controle com timestamp de processamento, marcando a camada de origem dos dados.

### **Validator**

Realiza validações em dados (validação de email com regex), facilmente extensível para outras regras de negócio.

---

## 🚀 Como Usar

### Pré-requisitos

- Python 3.12 instalado
- pip para gerenciamento de dependências

### Instalação

1. Clone o repositório:

```bash
git clone <seu-repositorio>
cd desafio-tecnico-bemol-data-engineer
```

2. Crie um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

3. Instale as dependências:

```bash
pip install pyspark==3.4.2 delta-spark==2.4.0 requests
```

### Execução

Os notebooks devem ser executados na seguinte ordem:

**Bronze:**

1. `notebooks/bronze/01_carts_products.ipynb` - Desaninhamento e limpeza de carrinho e produtos
2. `notebooks/bronze/02_users.ipynb` - Tratamento de dados de usuários

**Silver:** 3. `notebooks/silver/01_products_analytics.ipynb` - Agregação de vendas por produto 4. `notebooks/silver/02_data_quality.ipynb` - Monitoramento de qualidade

---

## 📊 Saída Principal

A tabela gerada no Silver contém:

| Campo               | Descrição                          |
| ------------------- | ---------------------------------- |
| product_id          | ID do produto                      |
| product_name        | Nome do produto                    |
| price               | Preço unitário                     |
| total_quantity_sold | Quantidade total vendida           |
| total_revenue       | Receita total (preço × quantidade) |

---

## 📁 Estrutura de Diretórios

```
desafio-tecnico-bemol-data-engineer/
├── notebooks/
│   ├── bronze/
│   │   ├── 01_carts_products.ipynb
│   │   └── 02_users.ipynb
│   └── silver/
│       ├── 01_products_analytics.ipynb
│       └── 02_data_quality.ipynb
├── src/
│   ├── lakehouse.py
│   ├── landing_reader.py
│   ├── logging.py
│   ├── monitor.py
│   ├── controller.py
│   └── validator.py
├── data/
│   ├── bronze/
│   └── silver/
├── logs/
├── .venv/
├── README.md
└── requirements.txt
```

---

## 🔍 Destaques Técnicos

✅ **Arquitetura Lakehouse:** Simulação realista de um Data Lake com camadas de refino progressivo

✅ **Código Orientado a Objetos:** Implementação de classes reutilizáveis e testáveis

✅ **Logging e Monitoramento:** Rastreamento completo de operações com DataFrame de auditoria

✅ **Validação de Dados:** Classe Validator com suporte a regex para garantir qualidade

✅ **Desaninhamento Inteligente:** Explode de dados de carrinho mantendo contexto de cada item

✅ **Delta Lake Local:** Demonstração de uso de formato open source para versionamento de dados

---

## 🔧 Próximos Passos (Sugestões)

- Automatizar execução dos notebooks com orquestrador (Airflow, Databricks Workflows)
- Adicionar testes unitários para as classes
- Implementar CI/CD para validação automática
- Expandir LandingReader para suportar múltiplas fontes (CSV, Parquet, Banco de Dados)
- Criar pipeline de testes de qualidade de dados mais robustos

---

## 📝 Licença

[Especifique a licença, ex: MIT, Apache 2.0, etc.]

---

## 📧 Contato

[Seu email ou LinkedIn]
