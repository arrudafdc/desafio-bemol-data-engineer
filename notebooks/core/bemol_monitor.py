import time
import os

class BemolMonitor:
  """Classe para monitoramento de métricas das operações."""

  def __init__(self, logger):
    self.logger = logger
    self.start_time = {}
    self.df_metrics = []

  def start(self, operation_name):
    """Inicia o cronômetro de uma operação."""

    # Armazena o tempo de início
    self.start_time[operation_name] = time.time()
    # Log de início da operação
    self.logger.log_info(f"Iniciando operação: {operation_name}")

  def end(self, operation_name):
    """Finaliza o cronômetro de uma operação e registra métricas."""

    # Verifica se a operação foi iniciada
    if operation_name not in self.start_time:
      self.logger.log_warning(f"Operação {operation_name} não foi iniciada.")
      return None
    
    # Calcula a duração
    duration = time.time() - self.start_time[operation_name]
    
    # Log de fim da operação
    self.logger.log_info(f"Operação {operation_name} finalizada em {round(duration, 2)} segundos.")
    return duration
  
  def get_metrics(self, df, table_name):
    """Registra métricas coletadas do Data Frame."""
    
    # Coleta métricas básicas do DataFrame e realiza append das informações
    try:
      row_count = df.count()
      col_count = len(df.columns)
      record = {
        "table_name": table_name,
        "row_count": row_count,
        "col_count": col_count,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
      }
      self.df_metrics.append(record)
      # Log das métricas coletadas
      self.logger.log_info(f"Métricas {table_name}: {row_count} linhas, {col_count} colunas.")
      return record
    except Exception as e:
      self.logger.log_error(f"Erro ao coletar métricas do DataFrame {table_name}: {str(e)}")
      return None
    
  def export_delta(self, spark, path):
    """Exporta as métricas acumuladas para um Delta Table."""

    # Verifica se há métricas para exportar
    if not self.df_metrics:
      self.logger.log_warning("Nenhuma métrica para exportar.")
      return None
    
    # Cria DataFrame Spark a partir das métricas
    df_spark = spark.createDataFrame(self.df_metrics)
    df_spark = df_spark.select("table_name", "row_count", "col_count", "timestamp")

    # Garante que o diretório existe
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Exporta para Delta Table
    try:
      df_spark.write.format("delta").mode("append").save(path)
      self.logger.log_info(f"Métricas exportadas com sucesso para {path}")
      return df_spark
    except Exception as e:
      self.logger.log_error(f"Erro ao exportar métricas para {path}: {str(e)}")
      raise e