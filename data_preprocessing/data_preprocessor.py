import pandas as pd


class DataPreprocessor:
    def __init__(self, df_file_path, df_feriados_file_path, data_inicio, data_fim):
        self.df = pd.read_csv(df_file_path)
        self.df_feriados = pd.read_csv(df_feriados_file_path)
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.padronizar_colunas()

    def padronizar_colunas(self):

        column_mappings = {
            "DATA COMPETÊNCIA": ["DATA_COMPETÊNCIA", "DATA COMPETÊNCIA"],
            "NOME FILIAL": ["NOME_FILIAL", "NOME_FILIAL1"],
            "CÓD CLIENTE": ["CÓD_CLIENTE"],
            "NOME CLIENTE": ["NOME_CLIENTE"],
            "TIPO VEÍCULO": ["TIPO_VEÍCULO"],
            "TOTAL HVG EM NUMERO": ["TOTAL_HVG_EM_NUMERO"],
            "TOTAL HVG EM PESO": ["TOTAL_HVG_EM_PESO"],
            "TOTAL HVG EM VOLUME": ["TOTAL_HVG_EM_VOLUME"],
            "TOTAL HVG EM CUBATURA": ["TOTAL_HVG_EM_CUBATURA"],
            "CODIGO FILIAL":["CODIGO_FILIAL"],
            # Adicione mais mapeamentos aqui conforme necessário
        }

        for padrao, alternativas in column_mappings.items():
            for alt in alternativas:
                if alt in self.df.columns:
                    self.df.rename(columns={alt: padrao}, inplace=True)
                    break

    def filter_historico(self, df, data_inicio_historico, data_fim_historico):
        data_inicio_historico = pd.to_datetime(data_inicio_historico, format="%d/%m/%Y")
        data_fim_historico = pd.to_datetime(data_fim_historico, format="%d/%m/%Y")
        df = df.loc[
            (df["DATA COMPETÊNCIA"] >= data_inicio_historico)
            & (df["DATA COMPETÊNCIA"] <= data_fim_historico)
        ]

        return df

    def dropnul_col(self, df):
        df.drop(columns=["CÓD CLIENTE", "NOME CLIENTE"], inplace=True)
        df.dropna(inplace=True)

        return df

    def apply_date(self, df):
        df["DATA COMPETÊNCIA"] = pd.to_datetime(
            df["DATA COMPETÊNCIA"], format="%d/%m/%Y"
        )
        df = df.sort_values(by="DATA COMPETÊNCIA")
        df = df.reset_index()
        df = df.drop(columns="index")

        return df

    def apply_faixa_horario(self, df):
        def categorize(df):
            if df["TOTAL HVG EM NUMERO"] <= 8:
                return "till 8"
            elif df["TOTAL HVG EM NUMERO"] <= 9:
                return "till 9"
            elif df["TOTAL HVG EM NUMERO"] <= 10:
                return "till 10"
            elif df["TOTAL HVG EM NUMERO"] <= 11:
                return "till 11"
            elif df["TOTAL HVG EM NUMERO"] <= 12:
                return "till 12"
            elif df["TOTAL HVG EM NUMERO"] <= 13:
                return "till 13"
            elif df["TOTAL HVG EM NUMERO"] <= 14:
                return "till 14"
            elif df["TOTAL HVG EM NUMERO"] > 14:
                return "greater than 14"

        df["TOTAL HVG EM NUMERO"] = (
            df["TOTAL HVG EM NUMERO"].astype(str).str.replace(",", ".").astype(float)
        )
        df["Category"] = df.apply(categorize, axis=1)

        return df

    def apply_municipios(self, df):
        data = {
            "municipio": [
                "PICOS",
                "RIO DE JANEIRO",
                "BRASILIA",
                "BAURU",
                "BACABAL",
                "JOINVILLE",
                "MARABA",
                "RIBEIRÃO PRETO",
                "TERESINA",
                "MANAUS",
                "SÃO PAULO - BARRA FUNDA",
                "SALVADOR",
                "SANTA MARIA",
                "SJ DO RIO PRETO",
                "LAGES",
                "URUGUAIANA",
                "BELEM",
                "BLUMENAU",
                "NATAL",
                "CAMPOS",
                "BELO HORIZONTE",
                "GOIÂNIA",
                "SAO LUIS",
                "ITAJAÍ",
                "CASTANHAL",
                "SÃO JOSE DOS CAMPOS",
                "CAMPINAS",
                "BARREIRAS",
                "SANTOS",
                "RIO BRANCO",
                "CARUARU",
                "CAMPO GRANDE",
                "CUIABÁ",
                "CURITIBA",
                "PORTO ALEGRE",
                "MACAPA",
                "VITORIA DA CONQUISTA",
                "OLINDA",
                "IRECE",
                "LONDRINA",
                "RIO VERDE",
                "FLORIANÓPOLIS",
                "IMPERATRIZ",
                "FORTALEZA",
                "CRICIÚMA",
                "FEIRA DE SANTANA",
                "PARAUAPEBAS",
                "JACOBINA",
                "PASSO FUNDO",
                "SETE LAGOAS",
                "BOM JESUS DA LAPA",
                "PAULO AFONSO",
                "SANTA CRUZ DO SUL",
                "PELOTAS",
                "JEQUIE",
                "JOAO PESSOA",
                "PARNAIBA",
                "GUANAMBI",
                "TUBARÃO",
                "POÇOS DE CALDAS",
                "EUNAPOLIS",
                "POUSO ALEGRE",
                "ITABUNA",
                "PETROLINA",
                "JOAÇABA",
                "ARACAJU",
                "ARAPIRACA",
                "MACEIO",
                "MOSSORO",
                "CHAPECÓ",
                "SANTANA LIVRAMENTO",
                "PATOS",
                "SANTO ANGELO",
                "CAMPINA GRANDE",
                "SERRA",
                "PORTO VELHO",
                "UBERLÂNDIA",
                "FLORIANO",
                "OURINHOS",
                "PRESIDENTE PRUDENTE",
                "CORONEL FABRICIANO",
                "TEÓFILO OTONI",
                "VARGINHA",
                "MARINGÁ",
                "CAXIAS DO SUL",
                "CACHOEIRO DO ITAPEMIRIM",
                "BOA VISTA",
                "MONTES CLAROS",
                "FOZ DO IGUAÇU",
                "CASCAVEL",
                "IGUATU",
                "SANTAREM",
                "DIVINÓPOLIS",
                "PALMAS",
                "CERES",
                "REDENCAO",
                "LINHARES",
                "ITAITUBA",
                "TUCURUI",
                "GURUPI",
                "MANHUAÇU",
                "ALTAMIRA",
                "VOLTA REDONDA",
                "ARAGUAINA",
                "ITUMBIARA",
                "PASSOS",
                "ALEGRETE",
                "GOVERNADOR VALADARES",
                "BAGÉ",
            ],
            "UF": [
                "PI",
                "RJ",
                "DF",
                "SP",
                "MA",
                "SC",
                "PA",
                "SP",
                "PI",
                "AM",
                "SP",
                "BA",
                "RS",
                "SP",
                "SC",
                "RS",
                "RS",
                "PA",
                "SC",
                "RN",
                "RJ",
                "MG",
                "GO",
                "MA",
                "SC",
                "PA",
                "SP",
                "SP",
                "BA",
                "SP",
                "AC",
                "PE",
                "MS",
                "MT",
                "PR",
                "RS",
                "AP",
                "BA",
                "PE",
                "BA",
                "BA",
                "PR",
                "GO",
                "SC",
                "MA",
                "CE",
                "SC",
                "BA",
                "PA",
                "BA",
                "RS",
                "MG",
                "BA",
                "BA",
                "RS",
                "RS",
                "BA",
                "PB",
                "PI",
                "BA",
                "SC",
                "MG",
                "BA",
                "MG",
                "BA",
                "PE",
                "SC",
                "SE",
                "AL",
                "AL",
                "RN",
                "SC",
                "RS",
                "PB",
                "RO",
                "MG",
                "MG",
                "PI",
                "SP",
                "SP",
                "MG",
                "MG",
                "MG",
                "PR",
                "RS",
                "ES",
                "RR",
                "MG",
                "PR",
                "PR",
                "CE",
                "PA",
                "MG",
                "TO",
                "GO",
                "PA",
                "ES",
                "PA",
                "PA",
                "PA",
                "MG",
                "PA",
                "RJ",
                "TO",
                "GO",
                "MG",
                "RS",
                "MG",
                "RS",
            ],
        }

        df.rename(columns={"NOME FILIAL": "municipio"}, inplace=True)
        df_municipios = pd.DataFrame(data)
        df["municipio"] = df["municipio"].str.strip().str.upper()
        df_municipios["municipio"] = df_municipios["municipio"].str.strip().str.upper()
        df = df.merge(df_municipios, on="municipio", how="left")
        df.rename(columns={"municipio": "NOME FILIAL"}, inplace=True)

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

    def apply_dias_da_semana(self, df):
        dias_da_semana = {
            "Monday": "Segunda",
            "Tuesday": "Terça",
            "Wednesday": "Quarta",
            "Thursday": "Quinta",
            "Friday": "Sexta",
            "Saturday": "Sábado",
            "Sunday": "Domingo",
        }

        df["dia_da_semana"] = df["DATA COMPETÊNCIA"].dt.day_name().map(dias_da_semana)

        return df

    def clean_transform_data(self):
        self.df = self.apply_date(self.df)
        self.df = self.filter_historico(self.df, self.data_inicio, self.data_fim)
        self.df = self.dropnul_col(self.df)
        self.df = self.apply_faixa_horario(self.df)
        self.df = self.apply_municipios(self.df)
        self.df = self.apply_feriados(self.df, self.df_feriados)
        self.df = self.apply_dias_da_semana(self.df)

        return self.df
