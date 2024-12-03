import pandas as pd
import streamlit as st


class DataPostprocessor:
    def __init__(self, dataframe_original, dataframe, df_weights, df_feriados):
        self.df1 = dataframe_original
        self.df = dataframe
        self.df_weights = df_weights
        self.df_feriados = df_feriados

    def apply_ufs(self, df1, df):
        x = df1.groupby(["CODIGO FILIAL", "UF", "NOME FILIAL"]).size().reset_index()
        ufs = {
            "CODIGO FILIAL": x["CODIGO FILIAL"].tolist(),
            "UF": x["UF"].tolist(),
            "NOME FILIAL": x["NOME FILIAL"].tolist(),
        }
        testando = pd.DataFrame(ufs)
        df = pd.merge(df, testando, on="CODIGO FILIAL", how="left")

        return df

    def apply_feriados(self, df, df_feriados):
        df_feriados["Data_feriado"] = pd.to_datetime(df_feriados["Data_feriado"])
        df["is_feriado"] = 0

        for index, row in df_feriados.iterrows():
            if row["Motivo"] == "FERIADO NACIONAL":
                df.loc[df["DATA COMPETÊNCIA"] == row["Data_feriado"], "is_feriado"] = 1
            elif row["Motivo"] == "FERIADO ESTADUAL":
                df.loc[
                    (df["DATA COMPETÊNCIA"] == row["Data_feriado"])
                    & (df["UF"] == row["UF"]),
                    "is_feriado",
                ] = 1
            elif row["Motivo"] == "FERIADO MUNICIPAL":
                df.loc[
                    (df["DATA COMPETÊNCIA"] == row["Data_feriado"])
                    & (df["NOME FILIAL"] == row["Nome_Municipio"]),
                    "is_feriado",
                ] = 1

        return df

    def apply_weights(self, df, df_weight):
        df = pd.merge(
            df,
            df_weight,
            on=["CODIGO FILIAL", "TIPO VEÍCULO", "dia_da_semana", "Category"],
            how="left",
        )
        df = df.fillna(1)
        df["count"] = (df["count"] * df["weight"]).where(
            df["is_feriado"] == 1, other=df["count"]
        )
        df["count"] = df["count"].astype(int)

        return df

    def postprocessing(self):
        self.df = self.apply_ufs(self.df1, self.df)
        self.df = self.apply_feriados(self.df, self.df_feriados)
        self.df = self.apply_weights(self.df, self.df_weights)
        self.df.sort_values(by=["DATA COMPETÊNCIA"], inplace=True)
        self.df.drop(
            ["UF", "NOME FILIAL", "is_feriado", "weight"], axis=1, inplace=True
        )
        self.df = self.df.rename(columns={"dia_da_semana": "DIA_DA_SEMANA"})
        self.df = self.df.rename(columns={"Category": "JORNADA"})
        self.df = self.df.rename(columns={"count": "QNT_ROTAS"})
        self.df.to_csv("data/predictions.csv")
        return self.df
