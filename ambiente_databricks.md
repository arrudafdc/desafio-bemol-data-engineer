# Desafio Bemol - Parte 1: Estruturação de Ambiente Azure Databricks

## 1. Visão Geral da Arquitetura Lakehouse

Para configurar um ambiente Lakehouse profissional do zero, é necessário estabelecer uma arquitetura escalável, governada e segura. A proposta aqui é criar um ambiente que simule um cenário enterprise real, com separação clara entre ambientes de desenvolvimento e produção, controle de acesso por Data Owner e rastreabilidade completa de operações.

A arquitetura será composta por:

1. **Azure Databricks** como plataforma de processamento de dados
2. **Azure Data Lake Storage (ADLS)** como repositório de dados
3. **Azure Data Factory** como orquestrador de pipelines
4. **Azure DevOps** como controle de versão e CI/CD
5. **Unity Catalog** para governança de metadados e permissões

---

## 2. Configuração Inicial do Ambiente

### 2.1 Criação do Workspace Databricks

O primeiro passo é provisionar o workspace Databricks que será o núcleo do ambiente Lakehouse. Este workspace será configurado em nível que seja necessário para ativar o Unity Catalog.

### 2.2 Integração com ADLS Gen2

O ADLS Gen2 será o repositório central onde todos os dados serão armazenados. A integração é feita através de credenciais de Service Principal, permitindo que o Databricks leia e escreva dados com segurança.

Importância:

- Garante que dados persistam mesmo se o cluster for terminado
- Permite que múltiplos clusters acessem os mesmos dados
- Facilita backup e disaster recovery
- Possibilita integração com outras ferramentas Azure

A configuração será feita uma única vez no workspace, e todos os notebooks e pipelines usarão automaticamente essa conexão.

---

## 3. Arquitetura de Clusters

### 3.1 Cluster de Desenvolvimento (bemol-dev-cluster)

O cluster de desenvolvimento será utilizado para experimentação, desenvolvimento de notebooks e testes de pipelines.

**Características:**

- **Instâncias menores**: DS4_v2 (8 cores, 28GB RAM) suficiente para dados de teste
- **Auto-scaling**: Mínimo 2, máximo 8 workers, permitindo economia de custos quando ocioso
- **Auto-termination**: 30 minutos, economizando recursos quando não está em uso
- **Disponibilidade**: SPOT instances para reduzir custos
- **Disco elástico**: Habilitado para garantir performance mesmo com dados temporários

Este cluster será acessível para toda equipe de dados durante desenvolvimento, permitindo testes rápidos e iteração ágil.

### 3.2 Cluster de Produção (bemol-prod-cluster)

O cluster de produção executará apenas pipelines orquestrados pelo Azure Data Factory, garantindo repetibilidade e auditoria.

**Características:**

- **Instâncias maiores**: DS5_v2 (16 cores, 56GB RAM) para processar volumes reais
- **Auto-scaling**: Mínimo 4, máximo 16 workers, sempre pronto para picos de demanda
- **Auto-termination**: 60 minutos, reduzindo custos mas permitindo execução de jobs longos
- **Disponibilidade**: ON-DEMAND instances para garantir estabilidade (custos mais altos justificados por SLA)
- **Configurações Spark otimizadas**: Adaptive Query Execution e Skew Join handling habilitados

**Acesso restrito**: Este cluster será configurado com políticas que permitem execução APENAS através de Azure Data Factory. Usuários não poderão executar notebooks diretamente neste cluster, garantindo que todas as execuções sejam orquestradas, versionadas e auditadas.

### 3.3 Estratégia de Acesso aos Clusters

- **Dev**: Acesso aberto para equipe de dados (Workspace admins e developers)
- **Prod**: Acesso via pipelines do Data Factory apenas, sem acesso direto de usuários

Essa separação garante que código testado e aprovado seja executado de forma controlada em produção.

---

## 4. Estrutura de Armazenamento no ADLS

### 4.1 Organização Física dos Dados

Os dados serão armazenados no ADLS Gen2 em uma estrutura que separa **ambientes de desenvolvimento e produção**, refletindo a separação lógica do Unity Catalog.

```
lakehouse/
├── dev/
│   ├── bronze/
│   │   ├── produtos_vendidos/
│   │   └── usuarios/
│   ├── silver/
│   │   ├── produtos_vendidos/
│   │   └── usuarios/
│   └── gold/
│
└── prod/
    ├── bronze/
    │   ├── produtos_vendidos/
    │   └── usuarios/
    ├── silver/
    │   ├── produtos_vendidos/
    │   └── usuarios/
    └── gold/
```

### 4.2 Justificativa da Separação Dev/Prod

Separar dados em dev e prod garante que:

- **Isolamento**: Testes em dev não afetam dados de produção
- **Recuperação**: Se um erro ocorrer em dev, prod está seguro
- **Conformidade**: Muitas regulações exigem separação de ambientes
- **Performance**: Dev pode usar dados comprimidos ou amostrados

### 4.3 Camadas de Dados

Dentro de cada ambiente (dev/prod), os dados são organizados em **camadas**:

- **Bronze**: Dados brutos conforme chegam da fonte, mínimo de tratamento
- **Silver**: Dados limpos, validados e integrados, prontos para análise
- **Gold**: Dados agregados e otimizados para relatórios e dashboards

---

## 5. Azure Data Factory - Orquestração de Pipelines

### 5.1 Papel do Data Factory

O Azure Data Factory (ADF) será responsável por orquestrar todas as execuções dos pipelines de dados. Diferente de executar notebooks manualmente, usar o ADF garante:

- **Agendamento automático**: Pipelines podem rodar em horários específicos
- **Retry automático**: Se falhar, tenta executar novamente com backoff
- **Notificações**: Alertas se um pipeline falha
- **Logging centralizado**: Rastreamento completo de quando, onde e por quê um pipeline rodou
- **Segurança**: Credenciais gerenciadas centralmente via Key Vault

### 5.2 Arquitetura de Pipelines

Os pipelines no ADF seguirão um padrão:

1. **Pipeline pai (Orquestrador principal)**

   - Define a ordem de execução das camadas
   - Bronze → Silver → Gold

2. **Subpipelines especializados**

   - Ingestão Bronze: Produtos_Vendidos
   - Ingestão Bronze: Usuários
   - Transformação Silver: Produtos_Vendidos
   - Transformação Silver: Usuários

3. **Tratamento de erros**
   - Se Bronze falha, Silver não executa
   - Se Silver falha, mantém dados da execução anterior
   - Notificações enviadas para equipe responsável

### 5.3 Variáveis no Data Factory

O ADF utilizará variáveis para parametrizar execuções:

- `ENVIRONMENT`: "dev" ou "prod" (define qual ADLS path será usado)
- `DATA_OWNER`: Nome da equipe proprietária (para logs de auditoria)
- `FORCE_FULL_LOAD`: true/false (controla se faz carregamento incremental ou full)
- `DATE_PARTITION`: Data de execução (para dados particionados por data)

Essas variáveis permitem que **o mesmo pipeline rode em dev e prod com apenas uma mudança de variável**, evitando duplicação de código.

### 5.4 Execução Apenas via Data Factory em Produção

Para garantir conformidade e auditoria:

- **Dev**: Usuários podem executar notebooks diretamente no cluster ou via ADF
- **Prod**: Apenas o ADF pode executar pipelines no cluster de produção

Isso é configurado via políticas Databricks que verificam a identidade do executor. Se uma pessoa tentar executar um notebook diretamente em prod, receberá um erro de permissão.

---

## 6. Azure DevOps - Controle de Versão e CI/CD

### 6.1 Estrutura de Repositório

O Azure DevOps armazenará todo o código em um repositório Git:

```
bemol-data-lake/
├── notebooks/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── src/
│   ├── lakehouse.py
│   ├── landing_reader.py
│   ├── logging.py
│   ├── monitor.py
│   ├── controller.py
│   └── validator.py
├── adf/
│   ├── pipelines/
│   ├── datasets/
│   └── linked_services/
├── tests/
├── docs/
└── .gitignore
```

### 6.2 Fluxo de Desenvolvimento

1. **Feature Branch**: Desenvolvedor cria branch para nova feature
2. **Desenvolvimento Local**: Código desenvolvido e testado em dev
3. **Pull Request**: Código submetido para revisão
4. **Code Review**: Pares revisam código e executam testes
5. **Merge**: Após aprovação, código é mergeado para main
6. **Deploy Automático**: Pipeline CI/CD automaticamente deploy para prod

### 6.3 Automatização com CI/CD

O pipeline CI/CD (via Azure Pipelines):

1. **Na submissão de PR**:

   - Testes unitários executam
   - Linting do código verifica padrões
   - Validação de SQL syntax

2. **No merge para main**:

   - Deploy automático para dev
   - Testes de integração executam
   - Geração de documentação

3. **Em produção** (manual ou agendado):
   - Deploy aprovado é aplicado ao cluster prod
   - Logs de deploy salvos para auditoria
   - Rollback automático se falhar

---

## 7. Unity Catalog - Governança e Separação por Data Owner

### 7.1 Separação por Data Owner

A estrutura proposta separa os dados em dois schemas distintos, cada um gerenciado por uma equipe diferente:

**Schema: produtos_vendidos (Data Owner: Equipe X)**

Este schema conterá todas as tabelas relacionadas a produtos e vendas:

- `bronze.produtos`: Dados brutos de produtos
- `bronze.vendas`: Dados brutos de transações de venda
- `silver.produtos_vendidos_agregado`: Agregação de vendas por produto (este é o principal output desejado)
- `silver.vendas_por_categoria`: Análise de vendas segmentada por categoria

A Equipe X é proprietária deste schema e tem permissões totais (SELECT, INSERT, UPDATE, DELETE). Outras equipes podem apenas LER dados deste schema.

**Schema: usuarios (Data Owner: Equipe Y)**

Este schema conterá dados relacionados aos usuários da plataforma:

- `bronze.usuarios`: Dados brutos de usuários
- `bronze.perfis`: Dados brutos de perfis de usuários
- `silver.usuarios_limpo`: Dados de usuários já validados e limpos
- `silver.usuarios_agregado`: Agregações e segmentações de usuários

A Equipe Y é proprietária deste schema com permissões totais. Equipe X pode apenas LER os dados conforme necessário.

### 7.4 Benefícios dessa Separação

- **Responsabilidade clara**: Cada equipe é dona de seus dados
- **Segurança**: Acesso é concedido no mínimo necessário
- **Auditoria**: Sabe-se exatamente quem modificou qual dado
- **Escalabilidade**: Novas equipes podem ser adicionadas criando novos schemas
- **Flexibilidade**: Permissões podem evoluir sem afetar outras equipes

---

## 8. Unity Catalog - Permissões e Segurança

### 8.1 Modelo de Permissões

O Unity Catalog utiliza um modelo de permissões baseado em papéis:

**Papel: Data Owner (Equipe X - Produtos_Vendidos)**

- Permissão FULL: SELECT, INSERT, UPDATE, DELETE em `bemol_data.produtos_vendidos.*`
- Permissão SELECT: Apenas leitura em `bemol_data.usuarios.*`
- Permissão ADMIN: Gerenciar schemas e políticas

**Papel: Data Owner (Equipe Y - Usuários)**

- Permissão FULL: SELECT, INSERT, UPDATE, DELETE em `bemol_data.usuarios.*`
- Permissão SELECT: Apenas leitura em `bemol_data.produtos_vendidos.*`
- Permissão ADMIN: Gerenciar schemas e políticas

**Papel: Data Analyst**

- Permissão SELECT: Leitura em todos os schemas
- Permissão EXECUTE: Poder executar notebooks compartilhados

**Papel: Admin**

- Permissão FULL: Controle total sobre todo o catalog

### 8.2 Auditoria e Compliance

O Unity Catalog registra automaticamente:

- Quem acessou qual tabela
- Qual operação foi realizada (SELECT, INSERT, UPDATE, DELETE)
- Quando foi acessado
- Quantas linhas foram afetadas

Esse histórico fica disponível e pode ser consultado para compliance, investigação de incidentes ou auditoria.

---

## 9. Fluxo Completo de Execução

### 9.1 Cenário: Ingestão de Novos Dados

1. **Agendamento**: ADF aguarda hora configurada (ex: 02:00 AM)
2. **Inicialização**: ADF inicia cluster de produção
3. **Execução**: ADF chama notebook de ingestão Bronze no cluster prod
4. **Transformação**: Se Bronze sucesso, ADF chama notebook de transformação Silver
5. **Auditoria**: Cada operação é registrada no Unity Catalog
6. **Notificação**: Ao final, e-mail enviado com status (sucesso/falha)
7. **Cleanup**: Cluster é terminado após 60 min de inatividade

### 9.2 Cenário: Desenvolvimento de Nova Transformação

1. **Dev**: Desenvolvedor cria branch no DevOps
2. **Coding**: Escreve notebook em cluster dev, testa com dados de dev
3. **Push**: Comita código para DevOps
4. **PR**: Abre Pull Request, pares revisam
5. **Testing**: Testes automáticos executam em CI/CD
6. **Merge**: Após aprovação, mescla para main
7. **Deploy**: Automaticamente desfaz em dev para teste
8. **Prod Deploy**: Após validação manual, deploy acontece em prod

---

## 10. Segurança e Melhores Práticas

### 10.1 Credenciais e Secrets

Todas as credenciais são armazenadas em **Azure Key Vault**:

- Client IDs e secrets
- Conexão strings
- Tokens de API

### 10.2 Network Security

Se necessário, os serviços Azure podem estar dentro de uma VNet (Virtual Network), com:

- Acesso limitado a IPs específicos

### 10.3 Compliance e Governança

- **GDPR**: Dados de usuários marcados e com políticas de retenção
- **SOX**: Auditoria completa de todas as operações
- **LGPD**: Conformidade com regulamentações de proteção de dados
