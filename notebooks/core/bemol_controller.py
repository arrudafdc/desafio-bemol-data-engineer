from pyspark.sql.functions import current_timestamp

class BemolController:
  """
  Classe para controle de inserção de dados nas camadas do Lakehouse.
  """

  @staticmethod
  def control_field(df, layer):
    """
    Adiciona um campo de controle de inserção baseado na camada. 
    """

    if layer == "bronze":
      df = df.withColumn("insertion_bronze", current_timestamp())
    elif layer == "silver":
      df = df.withColumn("insertion_silver", current_timestamp())
    elif layer == "gold":
      df = df.withColumn("insertion_gold", current_timestamp())
    else:
      raise ValueError("Layer inválida. Use 'bronze', 'silver' ou 'gold'.")
    return df