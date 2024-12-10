import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import uuid
import re
from demanda import (
    make_prediction,
    prep_demand_data,
    adjust_output,
    adjust_prediction_journey,
)

# Configurações de layout
st.set_page_config(page_title="Demanda Previsão", page_icon="assets/cog.png")
st.markdown(
    """
    <style>

    div.stButton > button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #0056b3;
        color: white;
    }

    div.stDownloadButton > button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
    }

    div.stDownloadButton > button:hover {
        background-color: #0056b3;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='color: #007BFF;'>Modelo Previsão de Demanda</h1>", unsafe_allow_html=True
)
# sidebar para o menu de navegação
st.sidebar.title("Menu de Navegação")
menu_option = st.sidebar.radio(
    "Navegue para:",
    [
        "Previsão de Demanda",
        "Modelo de Otimização",
        "Modelo de Simulação",
    ],

)

if menu_option == "Previsão de Demanda":
    st.sidebar.write("Redirecionando para Previsão de Demanda ")
    st.sidebar.markdown(
        "[Clique aqui](https://prossegurprevisao-cognitivo.streamlit.app/)",
        unsafe_allow_html=True,
    )

elif menu_option == "Modelo de Otimização":
    st.sidebar.write("Redirecionando para Modelo de Otimização")
    st.sidebar.markdown(
        "[Clique aqui](http://54.211.109.72/)", unsafe_allow_html=True
    )

elif menu_option == "Modelo de Simulação":
    st.sidebar.write("Redirecionando para Modelo de Simulação")
    st.sidebar.markdown(
        "[Clique aqui](http://54.211.109.72:8080/)",
        unsafe_allow_html=True,
    )


# Salvando os arquivos em cache
@st.cache_data
def load_file(file, date_column):
    return pd.read_csv(file, parse_dates=[date_column], dayfirst=True)


# Função para converter o arquivo CSV em Base64 e gerar o link de download
def download_button_csv(file_path, download_filename, button_text):
    with open(file_path, "rb") as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    button_uuid = str(uuid.uuid4()).replace("-", "")
    button_id = re.sub("\d+", "", button_uuid)

    # Estiliza o botão de Download
    custom_css = f"""
        <style>
            #{button_id} {{
                background-color: #007BFF;
                color: white;
                padding: 0.5em 0.8em;
                text-decoration: none;
                border-radius: 4px;
                border: 1px solid #007BFF;
                display: inline-block;
            }}
            #{button_id}:hover {{
                background-color: #0056b3;
                color: white;
                border-color: #0056b3;
            }}
            #{button_id}:active {{
                background-color: #002299;
                color: white;
                border-color: #002299;
            }}
        </style>
        """

    # Cria o link de download
    dl_link = (
        custom_css
        + f'<a download="{download_filename}" id="{button_id}" href="data:text/csv;base64,{b64}">{button_text}</a><br><br>'
    )

    return dl_link


# Carregar os dados
st.markdown(
    "<h5 style='color: #007BFF;'>Por favor, selecione o arquivo de histórico de dados no formato CSV.</h5>",
    unsafe_allow_html=True,
)
df_file_path = st.file_uploader("Histórico:", type="csv")

st.markdown(
    "<h5 style='color: #007BFF;'>Por favor, selecione o arquivo de feriados no formato CSV.</h5>",
    unsafe_allow_html=True,
)
df_feriados_file_path = st.file_uploader("Feriados:", type="csv")


# Definição de datas
if df_file_path is not None:
    # Inputs do historico
    st.markdown(
        "<h2 style='color: #007BFF;'>Período de Histórico</h2>", unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
    df = load_file(df_file_path, "DATA_COMPETÊNCIA")
    valor_min = df["DATA_COMPETÊNCIA"].min()
    valor_max = df["DATA_COMPETÊNCIA"].max()
    historico_data_inicial = col1.date_input("Data Inicial", value=valor_min)
    historico_data_final = col2.date_input("Data Final", value=valor_max)
    # Inputs da previsao
    st.markdown(
        "<h2 style='color: #007BFF;'>Período de Previsão</h2>", unsafe_allow_html=True
    )
    col3, col4 = st.columns(2)
    valor_min = valor_max + pd.Timedelta(days=1)
    valor_max = valor_max + pd.Timedelta(days=30)
    previsao_data_inicial = col3.date_input("Data Inicial da Previsão", value=valor_min)
    previsao_data_final = col4.date_input("Data Final da Previsão", value=valor_max)

# Tamanho da janela
st.markdown(
    "<h2 style='color: #007BFF;'>Tamanho da Janela do Modelo</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#007BFF '>Representa o número de semanas do histórico usado para prever cada semana "
    "futura, ajustando-se dinamicamente conforme novas semanas são previstas.</p>",
    unsafe_allow_html=True,
)
window = st.number_input(
    " Tamanho da Janela do Modelo", min_value=1, max_value=100, value=5
)
st.markdown(
    "<p style='color:#007BFF '>O cálculo da previsão utiliza o histórico informado e projeta o "
    "mesmo período para o futuro.</p>",
    unsafe_allow_html=True,
)

# Botão para processar
if st.button("Processar Dados"):
    if df_file_path is not None and df_feriados_file_path is not None:
        # try:
        # Carregar dados
        df = load_file(df_file_path, "DATA_COMPETÊNCIA")
        df_feriados = load_file(df_feriados_file_path, "data")

        # consolida dados
        df_cleaned = prep_demand_data(df)

        st.write("Dados do Histórico (5 primeiras linhas):")
        st.write(df_cleaned.head())

        # Modelo e previsão
        predictions_daily = make_prediction(
            previsao_data_inicial,
            previsao_data_final,
            historico_data_inicial,
            historico_data_final,
            window,
            df_cleaned,
            df_feriados,
        )

        # Ajuste de faixas
        predictions = adjust_prediction_journey(predictions_daily, df)

        df = predictions.loc[
            (predictions["data"].dt.date >= previsao_data_inicial)
            & (predictions["data"].dt.date <= previsao_data_final)
        ]
        df["forecast_faixa"] = df["forecast_faixa"].map(
            lambda value: int(round(value, 0))
        )
        st.write(df.head())

        # save file
        predictions_daily.to_csv("data/predictions_daily.csv", index=False)
        predictions.to_csv("data/predictions_faixa.csv", index=False)
        df_save = adjust_output(df)
        df_save.to_csv("data/predictions.csv", index=False)

        min_date = pd.to_datetime(historico_data_inicial)
        max_date = pd.to_datetime(previsao_data_final)
        df_final = predictions[
            (predictions["data"] >= min_date) & (predictions["data"] <= max_date)
        ]

        st.write("Resultados Finais (5 Primeiras linhas):")
        st.write(df.head())
        st.success("Processamento concluído!")

        # Armazenar no estado
        st.session_state["df"] = df_final


    # except Exception as e:
    # st.error(f"Ocorreu um erro: {e}")
    else:
        st.error("Por favor, carregue os arquivos CSV necessários.")

# Gráficos após o processamento
if "df" in st.session_state:
    df = st.session_state["df"]

    st.markdown(
        "<h2 style='color: #007BFF;'>Filtros para o gráfico</h2>",
        unsafe_allow_html=True,
    )
    filial = st.multiselect("Selecione a(s) Filial(is)", df["cod_filial"].unique())
    tipo_veiculo = st.multiselect(
        "Selecione o(s) Tipo(s) de Veículo", df["tipo_veiculo"].unique()
    )
    faixa_horario = st.multiselect(
        "Selecione a(s) Faixa(s) de Horário", df["FAIXA"].unique()
    )
    dia_da_semana = st.multiselect(
        "Selecione o(s) Dia(s) da Semana", df["dia_semana"].unique()
    )
    min_date = pd.to_datetime(historico_data_inicial)
    data_inicio = st.date_input("Data Inicio Gráfico", value=min_date)

    # Filtrar os dados
    df_filtrado = df.copy()
    df_filtrado = df_filtrado[(df_filtrado["data"] >= pd.to_datetime(data_inicio))]
    if filial:
        df_filtrado = df_filtrado[df_filtrado["cod_filial"].isin(filial)]
    if tipo_veiculo:
        df_filtrado = df_filtrado[df_filtrado["tipo_veiculo"].isin(tipo_veiculo)]
    if faixa_horario:
        df_filtrado = df_filtrado[df_filtrado["FAIXA"].isin(faixa_horario)]
    if dia_da_semana:
        df_filtrado = df_filtrado[df_filtrado["dia_semana"].isin(dia_da_semana)]

    # Gráfico
    df_grouped = (
        df_filtrado.groupby("data")
        .agg({"forecast_faixa": "sum", "demanda": "sum"})
        .reset_index()
    )

    plt.figure(figsize=(16, 7))
    # Linha para 'forecast'
    plt.plot(
        df_grouped["data"],
        df_grouped["forecast_faixa"],
        label="Previsão de Rotas",
        marker="o",
        linestyle="-",
    )
    # Linha para 'demanda'
    plt.plot(
        df_grouped["data"],
        df_grouped["demanda"],
        label="Demanda de Rotas",
        marker="s",
        linestyle="--",
    )
    # configuração gráfico
    plt.xlabel("Data de Competência")
    plt.ylabel("Contagem")
    plt.title("Previsão ao Longo do Tempo")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

    st.subheader("Download dos Resultados")
    download_link = download_button_csv(
        "data/predictions.csv",
        "previsoes_resultado.csv",
        "Baixar CSV com os Resultados",
    )
    st.markdown(download_link, unsafe_allow_html=True)
