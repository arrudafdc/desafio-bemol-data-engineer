from pyspark.sql.functions import col, when, regexp_extract, lit

class BemolValidator:
  """
    Classe centralizada de validações de dados da Bemol.
  """

  # Regex para validação de e-mails
  EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

  @staticmethod
  def validate_email(df, column):
    """
    Adiciona uma coluna booleana 'is_valid_email' indicando se o e-mail é válido.
    """

    # Adiciona a coluna de validação
    df_validated = df.withColumn(
        "is_valid_email",
        when(
            regexp_extract(col(column), BemolValidator.EMAIL_REGEX, 0) != "", lit(True)
        ).otherwise(lit(False))
    )
    
    return df_validated
  
  # Futuras validações podem ser adicionadas aqui...