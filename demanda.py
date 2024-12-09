import pandas as pd
import numpy as np

pd.set_option('future.no_silent_downcasting', True)

# Dicionário dos dias da semana
dias_semana = {
    0: 'segunda',
    1: 'terça',
    2: 'quarta',
    3: 'quinta',
    4: 'sexta',
    5: 'sábado',
    6: 'domingo'
}


def adjust_output(df_in):

    df = df_in.copy()
    df = df.rename(columns={"data": "DATA COMPETÊNCIA", "cod_filial": "CODIGO FILIAL", "tipo_veiculo": "TIPO VEÍCULO",
                            "FAIXA": "JORNADA", "dia_semana": "DIA_DA_SEMANA", "forecast_faixa": "QNT_ROTAS"})
    cols = ['DATA COMPETÊNCIA', 'CODIGO FILIAL', 'TIPO VEÍCULO', 'DIA_DA_SEMANA', 'JORNADA', 'QNT_ROTAS']
    df = df[cols]

    return df


def prep_demand_data(df_prep):

    # Selecionar apenas as colunas necessárias
    df = df_prep.copy()
    df = df[["DATA_COMPETÊNCIA", "CODIGO_FILIAL", "TIPO_VEÍCULO", "TOTAL_HVG_EM_MINUTOS"]]

    # Contar as ocorrências de TOTAL_HVG_EM_MINUTOS
    df["demanda"] = df.groupby(["DATA_COMPETÊNCIA", "CODIGO_FILIAL", "TIPO_VEÍCULO"])["TOTAL_HVG_EM_MINUTOS"].transform("count")

    # Remover duplicados para manter apenas as linhas únicas por combinação de colunas
    df = df.drop_duplicates(subset=["DATA_COMPETÊNCIA", "CODIGO_FILIAL", "TIPO_VEÍCULO"])

    df = df.rename(columns={"DATA_COMPETÊNCIA": "data", "CODIGO_FILIAL": "cod_filial", "TIPO_VEÍCULO": "tipo_veiculo"})

    return df


# Função para remover outliers usando o método IQR
def remover_outliers(group):

    if group['demanda'].empty:
        return group
    q1 = group['demanda'].quantile(0.25)
    q3 = group['demanda'].quantile(0.75)
    iqr = q3 - q1
    filtered = (group['demanda'] >= q1 - 1.5 * iqr) & (group['demanda'] <= q3 + 1.5 * iqr)

    return group.loc[filtered]


# Função para preparar os dados para previsão
def prep_data(inicio_hist, fim_hist, df_demanda, df_feriados):

    # filtrar histórico pelas datas definidas
    min_date = pd.to_datetime(inicio_hist)
    max_date = pd.to_datetime(fim_hist)
    df_filtered = df_demanda[(df_demanda['data'] >= min_date) & (df_demanda['data'] <= max_date)]

    # Agrupa os dados para evitar duplicatas na mesma data, filial e tipo de veículo
    df = df_filtered.groupby(['data', 'cod_filial', 'tipo_veiculo'], as_index=False).agg({'demanda': 'sum'})

    # Garante que todas as datas entre a mínima e a máxima estejam presentes

    todas_datas = pd.date_range(start=inicio_hist, end=fim_hist)

    # Cria um DataFrame com todas as combinações possíveis de datas, filiais e tipos de veículo
    cod_filiais = df['cod_filial'].unique()
    tipos_veiculo = df['tipo_veiculo'].unique()
    todas_combinacoes = pd.MultiIndex.from_product([todas_datas, cod_filiais, tipos_veiculo], names=['data', 'cod_filial', 'tipo_veiculo']).to_frame(index=False)

    # Faz o merge com os dados existentes para preencher datas faltantes
    df = pd.merge(todas_combinacoes, df, on=['data', 'cod_filial', 'tipo_veiculo'], how='left')

    # Preenche valores faltantes de 'demanda' com zero ou outro método apropriado
    df['demanda'] = df['demanda'].fillna(0)

    # Adiciona colunas auxiliares
    df['dia_semana'] = df['data'].dt.weekday.map(dias_semana)

    # Marca os feriados com base no arquivo fornecido
    df = df.merge(df_feriados.assign(is_holiday=True), on=['data', 'cod_filial'], how='left')
    df['is_holiday'] = df['is_holiday'].fillna(False).astype(bool)

    # Remove os feriados antes de remover outliers e calcular a previsão
    df_no_holidays = df[~df['is_holiday']]

    # Remove outliers de cada série temporal
    df_limpo = df_no_holidays.groupby(['cod_filial', 'tipo_veiculo', 'dia_semana'], group_keys=False).apply(remover_outliers).reset_index(drop=True)

    return df_limpo, df


def adjust_holidays(df_semifinal, df):
    # Agrupa por 'cod_filial', 'tipo_veiculo' e 'is_holiday' para calcular a média de demanda
    demand_stats = (
        df.groupby(['cod_filial', 'tipo_veiculo', 'is_holiday'])['demanda']
        .mean()
        .reset_index()
        .pivot(index=['cod_filial', 'tipo_veiculo'], columns='is_holiday', values='demanda')
        .reset_index()
    )

    # Renomeia colunas, preenchendo valores ausentes com 0
    demand_stats = demand_stats.rename(columns={False: 'avg_non_holiday_demand', True: 'avg_holiday_demand'})
    if 'avg_non_holiday_demand' not in demand_stats.columns:
        demand_stats['avg_non_holiday_demand'] = 0
    if 'avg_holiday_demand' not in demand_stats.columns:
        demand_stats['avg_holiday_demand'] = 0

    # Calcula a redução percentual apenas quando os dados são válidos
    demand_stats['percentage_reduction'] = 0
    valid_mask = (demand_stats['avg_non_holiday_demand'] > 0) & (demand_stats['avg_holiday_demand'] > 0)
    demand_stats['percentage_reduction'] = demand_stats['percentage_reduction'].astype('float64')
    demand_stats.loc[valid_mask, 'percentage_reduction'] = (
        1 - (demand_stats.loc[valid_mask, 'avg_holiday_demand'] / demand_stats.loc[valid_mask, 'avg_non_holiday_demand'])
    ).clip(0, 1)

    # Junta as estatísticas calculadas ao DataFrame principal
    df_final = df_semifinal.merge(
        demand_stats[['cod_filial', 'tipo_veiculo', 'percentage_reduction']],
        on=['cod_filial', 'tipo_veiculo'],
        how='left'
    )

    # Ajusta a previsão para feriados
    holiday_mask = df_final['is_holiday'] & df_final['forecast'].notna()
    reduction_available_mask = df_final['percentage_reduction'].notna()

    df_final.loc[holiday_mask & reduction_available_mask, 'forecast'] *= (
        1 - df_final.loc[holiday_mask & reduction_available_mask, 'percentage_reduction']
    )

    # Remove a coluna 'percentage_reduction' se não for necessária
    df_final = df_final.drop(columns=['percentage_reduction'])

    return df_final


def make_prediction(inicio_prev, fim_prev, inicio_hist, fim_hist, window_size, df_demanda, df_feriados):

    df_limpo, df = prep_data(inicio_hist, fim_hist, df_demanda, df_feriados)

    # Lista para armazenar previsões
    lista_previsoes = []

    # Loop através de cada grupo para calcular a previsão usando médias móveis
    for nome, grupo in df_limpo.groupby(['cod_filial', 'tipo_veiculo', 'dia_semana']):
        # Ordena o grupo por data
        grupo = grupo.sort_values('data')
        # Calcula a média móvel
        grupo['media_movel'] = grupo['demanda'].rolling(window=window_size, min_periods=1).mean()
        # Obtém o último valor da média móvel
        ultima_media = grupo['media_movel'].iloc[-1]
        # Cria as datas de previsão para o dia da semana específico dentro do período especificado
        datas_previsao = pd.date_range(start=inicio_prev, end=fim_prev)
        dia_semana_num = list(dias_semana.keys())[list(dias_semana.values()).index(nome[2])]
        datas_previsao = datas_previsao[datas_previsao.weekday == dia_semana_num]
        # Cria o DataFrame de previsão
        previsao = pd.DataFrame({
            'data': datas_previsao,
            'cod_filial': nome[0],
            'tipo_veiculo': nome[1],
            'dia_semana': nome[2],
            'forecast': ultima_media
        })
        lista_previsoes.append(previsao)

    # Concatena todas as previsões
    df_previsao = pd.concat(lista_previsoes, ignore_index=True)

    # Marca os feriados na previsão usando o arquivo de feriados
    df_previsao = df_previsao.merge(df_feriados.assign(is_holiday=True), on=['data', 'cod_filial'], how='left')
    df_previsao['is_holiday'] = df_previsao['is_holiday'].fillna(False).astype(bool)

    # Adiciona a coluna 'dia_semana' na previsão
    df_previsao['dia_semana'] = df_previsao['data'].dt.weekday.map(dias_semana)

    # Preenche a coluna 'demanda' na previsão com NaN
    df_previsao['demanda'] = np.nan

    # Preenche a coluna 'forecast' nos dados históricos com NaN
    df['forecast'] = np.nan

    # Seleciona as colunas relevantes
    colunas = ['data', 'cod_filial', 'tipo_veiculo', 'dia_semana', 'demanda', 'forecast', 'is_holiday']

    # Concatena os dados históricos e previstos
    df_semifinal = pd.concat([df[colunas], df_previsao[colunas]], ignore_index=True)

    # Ordena o DataFrame final
    df_semifinal = df_semifinal.sort_values(['cod_filial', 'tipo_veiculo', 'data'])

    # AJUSTA FERIADOS
    df_final = adjust_holidays(df_semifinal, df)

    return df_final


def adjust_prediction_journey(df_previsao, df_demanda):
    """
    Ajusta as previsões para considerar faixas de horário com base no histórico.

    Args:
        df_previsao (DataFrame): DataFrame com as previsões no nível (data, cod_filial, tipo_veiculo).
        df_demanda (DataFrame): DataFrame com o histórico no nível (data, cod_filial, tipo_veiculo, TOTAL_HVG_EM_MINUTOS).

    Returns:
        DataFrame: Previsões ajustadas no nível (data, cod_filial, tipo_veiculo, faixa).
    """

    bins = [0, 8, 9, 10, 11, 12, np.inf]
    labels = ["Até 8", "De 8 a 9", "De 9 a 10", "De 10 a 11", "De 11 a 12", "Mais que 12"]

    # Adicionar coluna de faixas no histórico
    df_hist = df_demanda.copy()
    df_hist = df_hist[["DATA_COMPETÊNCIA", "CODIGO_FILIAL", "TIPO_VEÍCULO", "TOTAL_HVG_EM_MINUTOS"]]
    df_hist['HORAS'] = pd.to_numeric(df_hist["TOTAL_HVG_EM_MINUTOS"], errors="coerce")
    df_hist['HORAS'] = df_hist['HORAS'].fillna(0)
    df_hist['HORAS'] = df_hist["HORAS"] / 60
    df_hist['FAIXA'] = pd.cut(df_hist['HORAS'], bins=bins, labels=labels, right=False)
    df_hist["demanda"] = df_hist.groupby(["DATA_COMPETÊNCIA", "CODIGO_FILIAL", "TIPO_VEÍCULO", "FAIXA"])[
        "TOTAL_HVG_EM_MINUTOS"].transform("count")
    df_hist = df_hist[["DATA_COMPETÊNCIA", "CODIGO_FILIAL", "TIPO_VEÍCULO", "FAIXA", "demanda"]]
    df_hist = df_hist.drop_duplicates()
    df_hist['dia_semana'] = df_hist['DATA_COMPETÊNCIA'].dt.weekday.map(dias_semana)

    # Calcular o percentual da demanda por faixa em relação ao total
    demanda_total_por_faixa = df_hist.groupby(['dia_semana', 'CODIGO_FILIAL', 'TIPO_VEÍCULO', 'FAIXA']).agg(
        {'demanda': 'sum'})
    demanda_total_por_faixa = demanda_total_por_faixa.reset_index()

    demanda_total = df_hist.groupby(['dia_semana', 'CODIGO_FILIAL', 'TIPO_VEÍCULO']).agg({'demanda': 'sum'})
    demanda_total = demanda_total.reset_index()

    demanda_total_por_faixa = demanda_total_por_faixa.merge(demanda_total,
                                                            on=['dia_semana', 'CODIGO_FILIAL', 'TIPO_VEÍCULO'],
                                                            suffixes=('_faixa', '_total'))
    demanda_total_por_faixa['percentual'] = demanda_total_por_faixa['demanda_faixa'] / demanda_total_por_faixa[
        'demanda_total']

    # Gerar todas as combinações possíveis de (data, cod_filial, tipo_veiculo, faixa)
    faixas = pd.DataFrame({'FAIXA': labels})
    combinacoes = (
        df_previsao[['data', 'cod_filial', 'tipo_veiculo', 'dia_semana']]
            .drop_duplicates()
            .merge(faixas, how='cross')
    )

    # Mesclar
    historico = combinacoes.merge(
        df_hist,
        left_on=['data', 'dia_semana', 'cod_filial', 'tipo_veiculo', 'FAIXA'],
        right_on=['DATA_COMPETÊNCIA', 'dia_semana', 'CODIGO_FILIAL', 'TIPO_VEÍCULO', 'FAIXA'],
        how='left'
    )
    previsao = historico.merge(
        df_previsao[['data', 'cod_filial', 'tipo_veiculo', 'dia_semana', 'forecast']],
        left_on=['data', 'dia_semana', 'cod_filial', 'tipo_veiculo'],
        right_on=['data', 'dia_semana', 'cod_filial', 'tipo_veiculo'],
        how='left'
    )
    previsao_ajustada = previsao.merge(
        demanda_total_por_faixa,
        left_on=['dia_semana', 'cod_filial', 'tipo_veiculo', 'FAIXA'],
        right_on=['dia_semana', 'CODIGO_FILIAL', 'TIPO_VEÍCULO', 'FAIXA'],
        how='left'
    )

    # Ajustar a previsão para cada faixa de horário
    previsao_ajustada['forecast_faixa'] = previsao_ajustada['forecast'] * previsao_ajustada['percentual']

    # Preencher NaN (caso faltem proporções) com 0 para não deixar combinações sem valor
    previsao_ajustada['forecast_faixa'] = previsao_ajustada['forecast_faixa'].fillna(0)

    # Selecionar colunas relevantes
    cols = ['data', 'dia_semana', 'cod_filial', 'tipo_veiculo', 'FAIXA', 'demanda', 'forecast_faixa']
    previsao_ajustada = previsao_ajustada[cols]

    return previsao_ajustada
