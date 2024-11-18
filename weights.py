from data_preprocessing.data_preprocessor import DataPreprocessor
import pandas as pd
import streamlit as st


def calcular_pesos(df):
    # processor = DataPreprocessor()
    # df = processor.clean_transform_data()
    df_aggregate = (
        df.groupby(
            [
                "DATA COMPETÊNCIA",
                "CODIGO FILIAL",
                "TIPO VEÍCULO",
                "dia_da_semana",
                "NOME FILIAL",
                "is_feriado",
                "Category",
            ]
        )
        .size()
        .reset_index(name="count")
    )

    x = df.groupby(["CODIGO FILIAL", "UF"]).size().reset_index()
    ufs = {"CODIGO FILIAL": x["CODIGO FILIAL"].tolist(), "UF": x["UF"].tolist()}
    testando = pd.DataFrame(ufs)
    df = pd.merge(df, testando, on="CODIGO FILIAL", how="left")
    y = df.sort_values(by="CODIGO FILIAL")
    df_codigos = y["CODIGO FILIAL"].drop_duplicates().tolist()

    df_weight = pd.DataFrame()
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    tipo = ["FORTE", "LEVE"]
    categoria = [
        "till 8",
        "till 9",
        "til 10",
        "till 11",
        "till 12",
        "till 13",
        "till 14",
        "greater than 14",
    ]
    for i in df_codigos:
        f = []
        x = []
        for t in tipo:
            for p in categoria:
                for j in dias:
                    data1 = df_aggregate.loc[
                        (df_aggregate["TIPO VEÍCULO"] == t)
                        & (df_aggregate["CODIGO FILIAL"] == i)
                        & (df_aggregate["is_feriado"] == 1)
                        & (df_aggregate["dia_da_semana"] == j)
                        & (df_aggregate["Category"] == p)
                    ]
                    data0 = df_aggregate.loc[
                        (df_aggregate["TIPO VEÍCULO"] == t)
                        & (df_aggregate["CODIGO FILIAL"] == i)
                        & (df_aggregate["is_feriado"] == 0)
                        & (df_aggregate["dia_da_semana"] == j)
                        & (df_aggregate["Category"] == p)
                    ]
                    l = data0["count"].mean()
                    k = data1["count"].mean()
                    weight = 1 - ((l - k) / l)
                    df_weight_prediction = pd.DataFrame(
                        [[i, j, t, p, weight]],
                        columns=[
                            "CODIGO FILIAL",
                            "dia_da_semana",
                            "TIPO VEÍCULO",
                            "Category",
                            "weight",
                        ],
                    )
                    df_weight = pd.concat([df_weight, df_weight_prediction])

    df_weight.dropna(inplace=True)
    df_weight.to_csv("data/df_weights.csv", index=False)
    return df_weight
