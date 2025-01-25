import pandas as pd
from config.config_transform import (
    colunas_csv,
    tipo_dados_csv,
)

arquivo = "../files/2024/desconto/2024.csv"

df = pd.read_csv(
    arquivo,
    sep=";",
    encoding="ISO-8859-1",
    decimal=",",
    usecols=colunas_csv,
    dtype=tipo_dados_csv,
)
print(df.head(5))
