import requests
from core.bemol_monitor import BemolMonitor

class BemolLandingReader:
  """
  Classe para leitura de dados da camada landing.
  """

  def __init__(self, logger):
    self.logger = logger
    self.monitor = BemolMonitor(logger)

  def read_api(self, spark, url):
    """
        Lê dados de uma API e retorna um DataFrame.
    """

    # Início do monitoramento e Log de início da escrita
    self.monitor.start(operation_name="read_api")
    self.logger.log_info(f"Lendo dados da API: {url}")
    
    # Leitura dos dados da API
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        rdd = spark.sparkContext.parallelize(data)
        df = spark.read.json(rdd)
        df_count = df.count()
        df_cols = len(df.columns)
        # Mensagem de log e Métricas de monitoramento
        self.logger.log_info(f"Dados lidos com sucesso da API: {df_count} linhas, {df_cols} colunas.")
        self.monitor.end(operation_name="read_api")
        return df
    except Exception as e:
        self.logger.log_error(f"Erro ao ler API: {e}")
        raise e
  
  # Pode-se adicionar mais métodos de leitura conforme necessário, como leitura de arquivos CSV, Parquet...
  