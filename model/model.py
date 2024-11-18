from datetime import datetime, timedelta
import pandas as pd


class model:
    def __init__(self, dataframe, qt_monthly_prediction, window, data_inicio, data_fim):
        self.df = dataframe
        self.qt = qt_monthly_prediction
        self.window = window
        self.start_date = data_inicio
        self.end_date = data_fim

    def predict(self):
        self.start_date = pd.to_datetime(self.start_date, format="%d/%m/%Y")
        self.end_date = pd.to_datetime(self.end_date, format="%d/%m/%Y")
        self.df = self.df.loc[self.df["is_feriado"] == 0]
        df_aggregate = (
            self.df.groupby(
                [
                    "DATA COMPETÊNCIA",
                    "CODIGO FILIAL",
                    "TIPO VEÍCULO",
                    "dia_da_semana",
                    "Category",
                ]
            )
            .size()
            .reset_index(name="count")
        )
        df_teste = df_aggregate[
            ["dia_da_semana", "CODIGO FILIAL", "TIPO VEÍCULO", "Category"]
        ].drop_duplicates()
        last_date_ofc = df_aggregate["DATA COMPETÊNCIA"].max()
        last_date = df_aggregate["DATA COMPETÊNCIA"].max()
        last_sat = last_date - timedelta(days=1)
        last_fri = last_date - timedelta(days=2)
        last_thur = last_date - timedelta(days=3)
        last_wed = last_date - timedelta(days=4)
        last_tue = last_date - timedelta(days=5)
        last_mon = last_date - timedelta(days=6)
        for _, row in df_teste.iterrows():
            for i in range(1, self.qt):
                df_aggregate_loop = (
                    df_aggregate[
                        (df_aggregate["CODIGO FILIAL"] == row["CODIGO FILIAL"])
                        & (df_aggregate["TIPO VEÍCULO"] == row["TIPO VEÍCULO"])
                        & (df_aggregate["dia_da_semana"] == row["dia_da_semana"])
                        & (df_aggregate["Category"] == row["Category"])
                    ]["count"]
                    .dropna()
                    .tail(self.window)
                )
                if row["dia_da_semana"] == "Segunda":
                    x = last_mon
                    df_prediction = pd.DataFrame(
                        [
                            [
                                ((x) + (timedelta(days=7))),
                                row["dia_da_semana"],
                                row["CODIGO FILIAL"],
                                row["TIPO VEÍCULO"],
                                row["Category"],
                                df_aggregate_loop.mean(),
                            ]
                        ],
                        columns=[
                            "DATA COMPETÊNCIA",
                            "dia_da_semana",
                            "CODIGO FILIAL",
                            "TIPO VEÍCULO",
                            "Category",
                            "count",
                        ],
                    )
                    df_aggregate = pd.concat([df_aggregate, df_prediction])
                    last_mon = last_mon + timedelta(days=7)
                elif row["dia_da_semana"] == "Terça":
                    x = last_tue
                    df_prediction = pd.DataFrame(
                        [
                            [
                                ((x) + (timedelta(days=7))),
                                row["dia_da_semana"],
                                row["CODIGO FILIAL"],
                                row["TIPO VEÍCULO"],
                                row["Category"],
                                df_aggregate_loop.mean(),
                            ]
                        ],
                        columns=[
                            "DATA COMPETÊNCIA",
                            "dia_da_semana",
                            "CODIGO FILIAL",
                            "TIPO VEÍCULO",
                            "Category",
                            "count",
                        ],
                    )
                    df_aggregate = pd.concat([df_aggregate, df_prediction])
                    last_tue = last_tue + timedelta(days=7)
                elif row["dia_da_semana"] == "Quarta":
                    x = last_wed
                    df_prediction = pd.DataFrame(
                        [
                            [
                                ((x) + (timedelta(days=7))),
                                row["dia_da_semana"],
                                row["CODIGO FILIAL"],
                                row["TIPO VEÍCULO"],
                                row["Category"],
                                df_aggregate_loop.mean(),
                            ]
                        ],
                        columns=[
                            "DATA COMPETÊNCIA",
                            "dia_da_semana",
                            "CODIGO FILIAL",
                            "TIPO VEÍCULO",
                            "Category",
                            "count",
                        ],
                    )
                    df_aggregate = pd.concat([df_aggregate, df_prediction])
                    last_wed = last_wed + timedelta(days=7)
                elif row["dia_da_semana"] == "Quinta":
                    x = last_thur
                    df_prediction = pd.DataFrame(
                        [
                            [
                                ((x) + (timedelta(days=7))),
                                row["dia_da_semana"],
                                row["CODIGO FILIAL"],
                                row["TIPO VEÍCULO"],
                                row["Category"],
                                df_aggregate_loop.mean(),
                            ]
                        ],
                        columns=[
                            "DATA COMPETÊNCIA",
                            "dia_da_semana",
                            "CODIGO FILIAL",
                            "TIPO VEÍCULO",
                            "Category",
                            "count",
                        ],
                    )
                    df_aggregate = pd.concat([df_aggregate, df_prediction])
                    last_thur = last_thur + timedelta(days=7)
                elif row["dia_da_semana"] == "Sexta":
                    x = last_fri
                    df_prediction = pd.DataFrame(
                        [
                            [
                                ((x) + (timedelta(days=7))),
                                row["dia_da_semana"],
                                row["CODIGO FILIAL"],
                                row["TIPO VEÍCULO"],
                                row["Category"],
                                df_aggregate_loop.mean(),
                            ]
                        ],
                        columns=[
                            "DATA COMPETÊNCIA",
                            "dia_da_semana",
                            "CODIGO FILIAL",
                            "TIPO VEÍCULO",
                            "Category",
                            "count",
                        ],
                    )
                    df_aggregate = pd.concat([df_aggregate, df_prediction])
                    last_fri = last_fri + timedelta(days=7)
                elif row["dia_da_semana"] == "Sábado":
                    x = last_sat
                    df_prediction = pd.DataFrame(
                        [
                            [
                                ((x) + (timedelta(days=7))),
                                row["dia_da_semana"],
                                row["CODIGO FILIAL"],
                                row["TIPO VEÍCULO"],
                                row["Category"],
                                df_aggregate_loop.mean(),
                            ]
                        ],
                        columns=[
                            "DATA COMPETÊNCIA",
                            "dia_da_semana",
                            "CODIGO FILIAL",
                            "TIPO VEÍCULO",
                            "Category",
                            "count",
                        ],
                    )
                    df_aggregate = pd.concat([df_aggregate, df_prediction])
                    last_sat = last_sat + timedelta(days=7)
                elif row["dia_da_semana"] == "Domingo":
                    x = last_date
                    df_prediction = pd.DataFrame(
                        [
                            [
                                ((x) + (timedelta(days=7))),
                                row["dia_da_semana"],
                                row["CODIGO FILIAL"],
                                row["TIPO VEÍCULO"],
                                row["Category"],
                                df_aggregate_loop.mean(),
                            ]
                        ],
                        columns=[
                            "DATA COMPETÊNCIA",
                            "dia_da_semana",
                            "CODIGO FILIAL",
                            "TIPO VEÍCULO",
                            "Category",
                            "count",
                        ],
                    )
                    df_aggregate = pd.concat([df_aggregate, df_prediction])
                    last_date = last_date + timedelta(days=7)
            last_date = last_date_ofc
            last_sat = last_date - timedelta(days=1)
            last_fri = last_date - timedelta(days=2)
            last_thur = last_date - timedelta(days=3)
            last_wed = last_date - timedelta(days=4)
            last_tue = last_date - timedelta(days=5)
            last_mon = last_date - timedelta(days=6)
            df_predictions = df_aggregate.loc[
                (df_aggregate["DATA COMPETÊNCIA"] >= self.start_date)
                & (df_aggregate["DATA COMPETÊNCIA"] <= self.end_date)
            ]
        return df_predictions
