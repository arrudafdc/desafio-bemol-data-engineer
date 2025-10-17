from core.bemol_monitor import BemolMonitor

class BemolLakeHouse:
  """
  Classe para gerenciar leitura e escrita de dados nas camadas bronze e silver.
  """

  def __init__(self, spark, logger):
    self.spark = spark
    self.logger = logger
    self.monitor = BemolMonitor(logger)

  def read_bronze(self, path, format="delta"):
    """
    Lê dados da camada bronze.
    """

    # Início do monitoramento e Log de início da escrita
    self.monitor.start(operation_name="read_bronze")
    self.logger.log_info(f"Lendo dados da camada Bronze: {path}")

    # Leitura dos dados
    try:
      df = self.spark.read.format(format).load(path)
      df_count = df.count()
      df_cols = len(df.columns)
      # Mensagem de log e Métricas de monitoramento
      self.logger.log_info(F"Dados lidos com sucesso da camada Bronze: {df_count} linhas, {df_cols} colunas.")
      self.monitor.end(operation_name="read_bronze")
      return df
    except Exception as e:
      self.logger.log_error(f"Erro ao ler dados na camada bronze: {e}")
      self.monitor.end(operation_name="read_bronze")
      raise e
  
  def write_bronze(self, df, path, table_name, format="delta", mode="overwrite"):
    """
    Escreve dados na camada bronze.
    """

    # Início do monitoramento e Log de início da escrita
    self.monitor.start("write_bronze")
    self.logger.log_info(f"Escrevendo dados na camada bronze em {path}")

    # Escrita dos dados
    try:
      df.write.format(format).mode(mode).save(path)
      # Mensagem de log e Métricas de monitoramento
      self.logger.log_info("Dados escritos com sucesso na camada bronze.")
      self.monitor.get_metrics(df, table_name)
      self.monitor.end("write_bronze")
    except Exception as e:
      self.logger.log_error(f"Erro ao escrever dados na camada bronze: {e}")
      self.monitor.end("write_bronze")
      raise e

  def write_silver(self, df, path, table_name, format="delta", mode="overwrite"):
    """
    Escreve dados na camada silver.
    """
    
    # Início do monitoramento e Log de início da escrita
    self.monitor.start("write_silver")
    self.logger.log_info(f"Escrevendo dados na camada silver em {path}")

    # Escrita dos dados
    try:
      df.write.format(format).mode(mode).save(path)
      # Mensagem de log e Métricas de monitoramento
      self.logger.log_info("Dados escritos com sucesso na camada silver.")
      self.monitor.get_metrics(df, table_name)
      self.monitor.end("write_silver")
    except Exception as e:
      self.logger.log_error(f"Erro ao escrever dados na camada silver: {e}")
      self.monitor.end("write_bronze")
      raise e