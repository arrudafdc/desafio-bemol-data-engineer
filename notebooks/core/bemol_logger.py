import os
import logging
from datetime import datetime

class BemolLogger:
  """
   Classe para configuração de logging centralizado.
  """

  # Dicionário para armazenar loggers já inicializados
  _initialized_loggers = {}

  def __init__(self, table_name, log_path = "../logs"):
    # Cria subpasta específica da tabela
    table_log_path = os.path.join(log_path, table_name)
    os.makedirs(table_log_path, exist_ok=True)

    # Se já foi inicializado, reutiliza o logger existente
    if table_name in BemolLogger._initialized_loggers:
      self.logger = BemolLogger._initialized_loggers[table_name]
      return 

    # Gera o nome do arquivo com base na data/hora atual
    log_file = os.path.join(
      table_log_path,
      f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    # Cria o logger
    logger = logging.getLogger(table_name)
    logger.setLevel(logging.INFO)

    # Evita duplicar handlers
    if not logger.handlers:
      formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Handler para o terminal
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Handler para arquivo
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Salva no cache para reutilizar nas próximas instâncias
    BemolLogger._initialized_loggers[table_name] = logger
    self.logger = logger

  def log_info(self, message):
    self.logger.info(message)

  def log_error(self, message):
    self.logger.error(message)  
  
  def log_warning(self, message):
    self.logger.warning(message)