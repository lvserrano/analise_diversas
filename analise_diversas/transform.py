import logging
import pandas as pd
import os
from tqdm import tqdm
from config.config_transform import (
    caminho_arquivos_csv,
    caminho_arquivos_xlsx,
    caminho_relatorio,
    diretorio_saida,
    colunas_csv,
    tipo_dados_csv,
    colunas_excel,
    colunas_relatorio,
    tipo_dados_relatorio,
    colunas_finais_relatorio,
)

# Configuração do logging para salvar em arquivo e console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("processamento.log", encoding="utf-8"),  # Salva no arquivo
        logging.StreamHandler(),  # Exibe no console
    ],
)
# Garantir que o diretório de saída existe
os.makedirs(diretorio_saida, exist_ok=True)


# Função para processar o único arquivo CSV
def processar_arquivo_csv():
    logging.info("Iniciando processamento do arquivo CSV.")
    arquivo_csv = os.path.join(caminho_arquivos_csv, "2024.csv")
    if not os.path.exists(arquivo_csv):
        logging.warning("Arquivo CSV 2024 não encontrado. Finalizando...")
        return

    # Ler o arquivo CSV
    df_csv = pd.read_csv(
        arquivo_csv,
        sep=";",
        decimal=",",
        usecols=colunas_csv,
        # dtype=tipo_dados_csv,
    )

    df_csv["Data"] = pd.to_datetime(df_csv["Data"], format="%d/%m/%Y")

    # Obter todos os arquivos Excel disponíveis
    arquivos_xlsx = [
        os.path.join(caminho_arquivos_xlsx, f)
        for f in os.listdir(caminho_arquivos_xlsx)
        if f.startswith("CUPOM_") and f.endswith(".xlsx")
    ]

    for arquivo_xlsx in tqdm(arquivos_xlsx, desc="Processando arquivos Excel"):
        ano_mes = os.path.basename(arquivo_xlsx).split("_")[1].split(".")[0]

        # Ler o arquivo Excel
        df_xlsx = pd.read_excel(arquivo_xlsx, decimal=",", usecols=colunas_excel)

        # Padronizar valores para o merge
        df_csv["Docum"] = df_csv["Docum"].astype(str).str.strip()
        df_csv["CX"] = df_csv["CX"].astype(str).str.strip()
        df_csv["Lj"] = df_csv["Lj"].astype(str).str.zfill(2)
        df_csv["Data"] = pd.to_datetime(df_csv["Data"], format="%d/%m/%y")

        df_xlsx["Num.Cupom"] = df_xlsx["Num.Cupom"].astype(str).str.strip()
        df_xlsx["PDV"] = df_xlsx["PDV"].astype(str).str.strip()
        df_xlsx["Loja"] = df_xlsx["Loja"].astype(str).str.zfill(2)
        df_xlsx["Data"] = pd.to_datetime(df_xlsx["Data"], format="%d/%m/%y")

        # Realizar o merge
        df_combinado = pd.merge(
            df_csv,
            df_xlsx,
            left_on=["Docum", "CX", "Lj", "Data"],
            right_on=["Num.Cupom", "PDV", "Loja", "Data"],
            how="inner",
        )

        # Contar valores únicos na coluna 'Docum'
        valores_unicos_docum = df_combinado["Docum"].nunique()
        logging.info(f"{ano_mes}: {valores_unicos_docum} Cupons.")

        # Salvar os resultados
        arquivo_saida_csv = os.path.join(diretorio_saida, f"{ano_mes}_tratado.csv")
        arquivo_saida_parquet = os.path.join(
            diretorio_saida, f"{ano_mes}_tratado.parquet"
        )

        df_combinado.to_csv(arquivo_saida_csv, index=False, encoding="utf-8", sep=";")
        df_combinado.to_parquet(arquivo_saida_parquet, index=False)
    logging.info("Processamento do arquivo CSV concluído.")


def processar_relatorio():
    logging.info("Iniciando processamento do relatório.")
    df = pd.read_csv(
        caminho_relatorio,
        sep=";",
        usecols=colunas_relatorio,
        decimal=",",
        dtype=tipo_dados_relatorio,
    )

    # Padronizar valores
    df["Nome Promocao"] = df["Descricao"].astype(str).str.strip()
    df["Data Inicial"] = pd.to_datetime(df["Dt.Valid.Ini"], format="%d/%m/%y")
    df["Data Final"] = pd.to_datetime(df["Dt.Valid.Fin"], format="%d/%m/%y")
    df["SKU"] = df["Item"].astype(str).str.strip()
    df["Nome Item"] = df["Descricao.1"].astype(str).str.strip()
    df["Preco Vendido"] = pd.to_numeric(df["Pr.Un"], errors="coerce").round(2)
    df["Preco Promocao"] = pd.to_numeric(df["Pr.Total"], errors="coerce").round(2)
    df["Ativacao"] = df["Quant."].fillna(0).astype(int)

    # Filtrar linhas que contenham a palavra "TABLOIDE" na coluna "Nome Promocao"
    df = df[df["Nome Promocao"].str.contains("TABLOIDE", case=False, na=False)]

    # Remover linhas que contenham a palavra "RAIZ" na coluna "Nome Promocao"
    df = df[~df["Nome Promocao"].str.contains("RAIZ", case=False, na=False)]

    arquivo_saida_csv = os.path.join(diretorio_saida, "relatorio_tratado.csv")
    df.to_csv(
        arquivo_saida_csv,
        index=False,
        encoding="utf-8",
        sep=";",
        columns=colunas_finais_relatorio,
    )
    logging.info("Processamento do relatório concluído.")


if __name__ == "__main__":
    logging.info("Início do script.")
    try:
        processar_relatorio()
        processar_arquivo_csv()
        logging.info("Processamento finalizado com sucesso.")
    except Exception as e:
        logging.error(f"Erro durante a execução: {e}")
