import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import uuid
import re
from datetime import datetime
from model.model import model
from data_preprocessing.data_preprocessor import DataPreprocessor
from post_processing.data_postprocessor import DataPostprocessor
from weights import calcular_pesos

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
    "<h1 style='color: #007BFF;'>Previsão de Dados</h1>", unsafe_allow_html=True
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
        "[Clique aqui](http://54.211.109.72:8501/)", unsafe_allow_html=True
    )

elif menu_option == "Modelo de Simulação":
    st.sidebar.write("Redirecionando para Modelo de Simulação")
    st.sidebar.markdown(
        "[Clique aqui](https://sua-aplicacao-streamlit-cloud.com)",
        unsafe_allow_html=True,
    )


@st.cache_data
def carregar_arquivo(file):
    return pd.read_csv(file)


# Carregar os dados
st.markdown(
    "<h5 style='color: #007BFF;'>Por favor, selecione o arquivo de histórico de dados no formato CSV.</h5>",
    unsafe_allow_html=True,
)
df_file_path = st.file_uploader(
    "Selecione o arquivo de previsão de histórico:",
    type="csv",
    key="df_file_path",
    label_visibility="collapsed",
)

st.markdown(
    "<h5 style='color: #007BFF;'>Por favor, selecione o arquivo de feriados no formato CSV.</h5>",
    unsafe_allow_html=True,
)
df_feriados_file_path = st.file_uploader(
    "Selecione o arquivo de feriados:",
    type="csv",
    key="df_feriados_file_path",
    label_visibility="collapsed",
)

# Inputs do historico
st.markdown(
    "<h2 style='color: #007BFF;'>Período de Histórico</h2>", unsafe_allow_html=True
)
col1, col2 = st.columns(2)
historico_data_inicial = col1.date_input("Data Inicial", value=datetime.today())
historico_data_final = col2.date_input("Data Final", value=datetime.today())

# Inputs da previsao
st.markdown(
    "<h2 style='color: #007BFF;'>Período de Previsão</h2>", unsafe_allow_html=True
)
col3, col4 = st.columns(2)
previsao_data_inicial = col3.date_input(
    "Data Inicial da Previsão", value=datetime.today()
)
previsao_data_final = col4.date_input("Data Final da Previsão", value=datetime.today())

# Calculando a data da previsao para semanas
qt_monthly_prediction = ((previsao_data_final - previsao_data_inicial).days // 7) + 2
st.markdown(f"**Número de semanas de previsão calculado:** {qt_monthly_prediction}")


# Tamanho da janela do modelo

st.markdown(
    "<h2 style='color: #007BFF;'>Tamanho da Janela do Modelo</h2>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='color:#007BFF '>Representa o número de semanas do histórico usado para prever cada semana futura, ajustando-se dinamicamente conforme novas semanas são previstas.</p>",
    unsafe_allow_html=True,
)

# Tamanho da janela
window = st.number_input(
    " Tamanho da Janela do Modelo", min_value=1, max_value=100, value=5
)

st.markdown(
    "<p style='color:#007BFF '>O cálculo da previsão utiliza o histórico informado e projeta o mesmo período para o futuro.</p>",
    unsafe_allow_html=True,
)
# Botão para processar
if st.button("Processar Dados"):
    if df_file_path is not None and df_feriados_file_path is not None:
        try:
            progress = st.progress(0)
            total_etapas = 10
            progress_contador = 0
            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            # Carregar dados
            df = carregar_arquivo(df_file_path)

            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            df_feriados = carregar_arquivo(df_feriados_file_path)

            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            # Processar dados
            processor = DataPreprocessor(
                df_file_path,
                df_feriados_file_path,
                historico_data_inicial,
                historico_data_final,
            )
            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            df_cleaned = processor.clean_transform_data()

            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            df_weights = calcular_pesos(df_cleaned)
            st.write("Dados do Histórico(5 primeiras colunas:)")
            st.write(df_cleaned.head())

            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            # Modelo e previsão
            modelo = model(
                df_cleaned,
                qt_monthly_prediction,
                window,
                previsao_data_inicial,
                previsao_data_final,
            )

            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            predictions = modelo.predict()

            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            # Pós-processamento
            postprocessor = DataPostprocessor(
                df_cleaned, predictions, df_weights, df_feriados
            )

            final = postprocessor.postprocessing()

            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            df = postprocessor.df

            progress_contador += 1
            progress.progress(progress_contador / total_etapas)

            st.write("Resultados Finais(Primeiras 5 linhas)")
            st.write(df.head())
            st.success("Processamento concluído!")

            # Armazenar no estado
            st.session_state["df"] = df

        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
    else:
        st.error("Por favor, carregue os arquivos CSV necessários.")

# Gráficos após o processamento
if "df" in st.session_state:
    df = st.session_state["df"]

    st.markdown(
        "<h2 style='color: #007BFF;'>Filtros para o gráfico</h2>",
        unsafe_allow_html=True,
    )
    filial = st.multiselect("Selecione a(s) Filial(is)", df["CODIGO FILIAL"].unique())
    tipo_veiculo = st.multiselect(
        "Selecione o(s) Tipo(s) de Veículo", df["TIPO VEÍCULO"].unique()
    )
    faixa_horario = st.multiselect(
        "Selecione a(s) Faixa(s) de Horário", df["JORNADA"].unique()
    )
    dia_da_semana = st.multiselect(
        "Selecione o(s) Dia(s) da Semana", df["DIA_DA_SEMANA"].unique()
    )

    # Filtrar os dados
    df_filtrado = df.copy()
    if filial:
        df_filtrado = df_filtrado[df_filtrado["CODIGO FILIAL"].isin(filial)]
    if tipo_veiculo:
        df_filtrado = df_filtrado[df_filtrado["TIPO VEÍCULO"].isin(tipo_veiculo)]
    if faixa_horario:
        df_filtrado = df_filtrado[df_filtrado["JORNADA"].isin(faixa_horario)]
    if dia_da_semana:
        df_filtrado = df_filtrado[df_filtrado["DIA_DA_SEMANA"].isin(dia_da_semana)]

    # Gráfico
    df_grouped = (
        df_filtrado.groupby("DATA COMPETÊNCIA").agg({"QNT_ROTAS": "sum"}).reset_index()
    )

    plt.figure(figsize=(10, 6))
    plt.plot(
        df_grouped["DATA COMPETÊNCIA"],
        df_grouped["QNT_ROTAS"],
        label="Previsão de Veículos",
        marker="o",
    )
    plt.xlabel("Data de Competência")
    plt.ylabel("Contagem de Veículos")
    plt.title("Previsão de Veículos ao Longo do Tempo")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

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

    st.subheader("Download dos Resultados")
    download_link = download_button_csv(
        "data/predictions.csv",
        "previsoes_resultado.csv",
        "Baixar CSV com os Resultados",
    )
    st.markdown(download_link, unsafe_allow_html=True)
