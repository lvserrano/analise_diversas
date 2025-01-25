import os

# Definir caminhos dos arquivos e diretórios
caminho_arquivos_csv = "../files/2024/desconto"
caminho_arquivos_xlsx = "../files/2024/cupons"
caminho_relatorio = "../files/2024/relatorios/rel_2024.csv"
diretorio_saida = "../files/tratado"

# Garantir que o diretório de saída exista
os.makedirs(diretorio_saida, exist_ok=True)

# Definir colunas e tipos de dados para o CSV
colunas_csv = [
    "Lj",
    "Data",
    "Docum",
    "CX",
    "Valor",
    "Desconto",
    "Tipo",
    "Cliente",
    "Operador",
]
tipo_dados_csv = {
    "Lj": "category",
    "Data": "string",
    "Hora": "string",
    "Docum": "category",
    "CX": "category",
    "Valor": "float64",
    "Desconto": "float64",
    "Tipo": "category",
    "Cliente": "category",
    "Operador": "category",
}
tipo_dados_relatorio = {
    "Descricao": "string",
    "Dt.Valid.Ini": "string",
    "Dt.Valid.Fin": "string",
    "Item": "string",
    "Descricao.1": "string",
    "Pr.Un": "float64",
    "Quant.": "float64",
    "Pr.Total": "float64",
}

# Definir colunas do Excel
colunas_excel = [
    "Loja",
    "Num.Cupom",
    "Data",
    "PDV",
    "Item",
    "Desc.Item",
    "Quantidade",
    "Pr.Venda.Un",
    "Pr.Venda Total",
    "Promoção",
]

colunas_relatorio = [
    "Descricao",
    "Dt.Valid.Ini",
    "Dt.Valid.Fin",
    "Item",
    "Descricao.1",
    "Pr.Un",
    "Quant.",
    "Pr.Total",
]
colunas_finais_relatorio = [
    "Nome Promocao",
    "Data Inicial",
    "Data Final",
    "SKU",
    "Nome Item",
    "Preco Vendido",
    "Preco Promocao",
    "Ativacao",
]
