import pandas as pd
import streamlit as st
import os
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# Configuração inicial da aplicação
st.set_page_config(
    page_title="Análise Tabloide Leve +", page_icon=":bar_chart:", layout="wide"
)


# Função para carregar os arquivos CSV
def carregar_dados():
    caminho_relatorio_tratado = "../files/tratado/relatorio_tratado.csv"
    relatorio_tratado = pd.read_csv(caminho_relatorio_tratado, sep=";")
    return relatorio_tratado


# Função para carregar os arquivos mensais dinamicamente
def carregar_dados_mensais(data_inicial, data_final):
    caminho_pasta = "../files/tratado"
    arquivos_mensais = []
    for mes in pd.date_range(start=data_inicial, end=data_final, freq="MS").strftime(
        "%Y-%m"
    ):
        caminho_arquivo = os.path.join(caminho_pasta, f"{mes}_tratado.csv")
        if os.path.exists(caminho_arquivo):
            arquivos_mensais.append(pd.read_csv(caminho_arquivo, sep=";"))

    if arquivos_mensais:
        return pd.concat(arquivos_mensais, ignore_index=True)
    else:
        return pd.DataFrame()


# Função para filtrar os dados de acordo com o intervalo de datas
def filtrar_por_data(dados, data_inicial, data_final):
    filtrados = dados[
        (dados["Data Inicial"] >= data_inicial) & (dados["Data Final"] <= data_final)
    ]
    return filtrados


# Função para filtrar promoções por período
def filtrar_promocoes_por_periodo(dados, prefixo_periodo):
    filtrados = dados[dados["Nome Promocao"].str.startswith(prefixo_periodo)]
    return filtrados


# Função para correlacionar itens entre os dois relatórios
def correlacionar_vendas(promocoes, vendas):
    vendas["SKU"] = vendas["Item"].astype(str)  # Garantir que o SKU esteja como string
    promocoes["SKU"] = promocoes["SKU"].astype(str)

    # Filtrar vendas para remover itens com "P" na coluna Promoção
    vendas = vendas[vendas["Promoção"] != "P"]

    correlacionados = pd.merge(
        promocoes, vendas, on="SKU", how="inner", suffixes=("_promo", "_venda")
    )
    correlacionados.to_csv("teste.csv", sep=";", index=False)
    correlacionados = correlacionados[
        correlacionados["Quantidade"] >= correlacionados["Ativacao"]
    ]
    correlacionados["Desconto Aplicado"] = (
        correlacionados["Preco Vendido"] - correlacionados["Preco Promocao"]
    ) * correlacionados["Quantidade"]
    correlacionados["Lucro Bruto"] = (
        correlacionados["Preco Promocao"] * correlacionados["Quantidade"]
    )
    return correlacionados


def calcular_custos_encarte(correlacionados, nome_promocao):
    # Identifica o prefixo do período com base na promoção selecionada
    prefixo_periodo = " - ".join(
        nome_promocao.split(" - ")[:-1]
    )  # Pega tudo antes do último " - "

    # Filtra todas as promoções relacionadas ao mesmo período
    filtrados = correlacionados[
        correlacionados["Nome Promocao"].str.startswith(prefixo_periodo)
    ]

    # Dicionário para armazenar os preços por SKU e loja
    preco_por_sku_loja = {}

    for _, linha in filtrados.iterrows():
        sku = linha["SKU"]
        preco_promocional = linha["Preco Promocao"]
        loja = linha["Nome Promocao"].split(" - ")[1]

        if sku not in preco_por_sku_loja:
            preco_por_sku_loja[sku] = {}

        preco_por_sku_loja[sku][loja] = {
            "preco_promocional": preco_promocional,
        }

    # Verifica se todos os SKUs têm preços promocionais iguais entre as lojas
    modelo_unico = True
    for sku, lojas in preco_por_sku_loja.items():
        preco_promocional_comum = list(lojas.values())[0]["preco_promocional"]

        for loja, precos in lojas.items():
            if precos["preco_promocional"] != preco_promocional_comum:
                modelo_unico = False
                break

        if not modelo_unico:
            break

    # Define o custo com base no modelo identificado
    custo = 3600 if modelo_unico else 6400
    return custo


# Função para gerar insights
def gerar_insights(correlacionados, custo_encarte):
    total_itens = correlacionados["Quantidade"].sum()
    total_desconto = correlacionados["Desconto Aplicado"].sum()
    lucro_bruto = correlacionados["Lucro Bruto"].sum()
    lucro_liquido = lucro_bruto - custo_encarte - total_desconto
    custo_total = total_desconto + custo_encarte
    return total_itens, total_desconto, lucro_bruto, lucro_liquido, custo_total


# Funções de formatação
def formatar_moeda(valor, simbolo=True):
    return locale.currency(valor, grouping=True, symbol=simbolo)


def formatar_numero(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Interface do Streamlit
st.title("Análise de Tabloide - Leve Mais")
col1, col2, col3, col4, col5, col6, col7 = st.columns([0.7, 0.7, 1.5, 0.7, 0.5, 1, 2])

# Carregar dados de promoções
relatorio_tratado = carregar_dados()
data_minima = pd.to_datetime(relatorio_tratado["Data Inicial"]).min()
data_maxima = pd.to_datetime(relatorio_tratado["Data Final"]).max()

st.subheader("Seleção de Período de Promoção")
data_inicial = col1.date_input(
    "Data Inicial",
    value=None,
    min_value=data_minima,
    max_value=data_maxima,
    format="DD/MM/YYYY",
)
data_final = col2.date_input(
    "Data Final",
    value=None,
    min_value=data_minima,
    max_value=data_maxima,
    format="DD/MM/YYYY",
)

dados_filtrados_por_data = filtrar_por_data(
    relatorio_tratado, str(data_inicial), str(data_final)
)

if not dados_filtrados_por_data.empty:
    nomes_promocoes = dados_filtrados_por_data["Nome Promocao"].unique()
    nome_promocao = col3.selectbox("Selecione a Promoção", nomes_promocoes)

    # Obter o prefixo do período da promoção selecionada
    prefixo_periodo = " - ".join(nome_promocao.split(" - ")[:-1])

    # Filtrar promoções do mesmo período
    promocoes_filtradas = filtrar_promocoes_por_periodo(
        dados_filtrados_por_data, prefixo_periodo
    )

    st.subheader("Promoções Selecionadas")
    promocoes_filtradas["SKU"] = promocoes_filtradas["SKU"].astype(str)
    st.dataframe(
        promocoes_filtradas,
        use_container_width=True,
        hide_index=True,
    )

    if not promocoes_filtradas.empty:
        historico_vendas = carregar_dados_mensais(data_inicial, data_final)
        if not historico_vendas.empty:
            vendas_correlacionadas = correlacionar_vendas(
                promocoes_filtradas, historico_vendas
            )
            custo_encarte = calcular_custos_encarte(
                vendas_correlacionadas, nome_promocao
            )
            total_itens, total_desconto, lucro_bruto, lucro_liquido, custo_total = (
                gerar_insights(vendas_correlacionadas, custo_encarte)
            )

            st.subheader("Insights da Promoção")
            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
            col1.metric("Total de Itens Vendidos", formatar_numero(total_itens))
            col2.metric("Total de Descontos Concedidos", formatar_moeda(total_desconto))
            col3.metric("Lucro Bruto", formatar_moeda(lucro_bruto))
            col4.metric("Lucro Líquido", formatar_moeda(lucro_liquido))
            col5.metric("Custo de Impressão do Encarte", formatar_moeda(custo_encarte))
            col6.metric("Custo da Promoção", formatar_moeda(custo_total))

            if lucro_liquido >= custo_total:
                st.success(
                    f"O lucro líquido cobriu o custo total da promoção ({(lucro_liquido / custo_total) * 100:.2f}%)."
                )
            else:
                deficit = custo_total - lucro_liquido
                st.error(
                    f"O lucro líquido não cobriu o custo total. Faltaram {formatar_moeda(deficit)} ({(lucro_liquido / custo_total) * 100:.2f}%)."
                )
        else:
            st.warning("Nenhum dado de vendas encontrado para o período selecionado.")
    else:
        st.warning("Nenhuma promoção encontrada para os filtros selecionados.")
else:
    st.warning("Nenhuma promoção disponível para o período selecionado.")
