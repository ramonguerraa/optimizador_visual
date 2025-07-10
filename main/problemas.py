import pulp
import pandas as pd

class Problema:
    def __init__(self, modelo_df: pd.DataFrame, restricciones_df: pd.DataFrame):
        self.modelo_df = modelo_df
        self.restricciones_df = restricciones_df
        self.variables = {}
        self.modelo = None
        self.resultado = None

    def crear_variables(self):
        self.variables = {
            row["Variable"]: pulp.LpVariable(row["Variable"], lowBound=0)
            for _, row in self.modelo_df.iterrows()
        }

    def construir(self):
        raise NotImplementedError("Este método debe ser implementado por la subclase.")

    def resolver(self):
        self.modelo.solve()
        solucion = {v.name: v.varValue for v in self.modelo.variables()}
        self.resultado = {
            "solucion": solucion,
            "valor_objetivo": pulp.value(self.modelo.objective),
            "status": pulp.LpStatus[self.modelo.status]
        }
        return self.resultado
    
class Maximizacion(Problema):
    def construir(self):
        self.modelo = pulp.LpProblem("Modelo_de_Maximizacion", pulp.LpMaximize)
        self.crear_variables()

        # Función objetivo
        self.modelo += pulp.lpSum(
            row["Coef_FO"] * self.variables[row["Variable"]]
            for _, row in self.modelo_df.iterrows()
        )

        # Restricciones dinámicas
        columnas_restriccion = [col for col in self.modelo_df.columns if col.startswith("Coef_R")]
        for i, restr in self.restricciones_df.iterrows():
            expr = pulp.lpSum(
                self.modelo_df[col].iloc[j] * self.variables[row["Variable"]]
                for j, row in self.modelo_df.iterrows()
                for col in [columnas_restriccion[i]]
            )

            if restr["Tipo"] == "<=":
                self.modelo += expr <= restr["RHS"], restr["Restriccion"]
            elif restr["Tipo"] == ">=":
                self.modelo += expr >= restr["RHS"], restr["Restriccion"]
            elif restr["Tipo"] == "=":
                self.modelo += expr == restr["RHS"], restr["Restriccion"]

class Minimizacion(Problema):
    def construir(self):
        self.modelo = pulp.LpProblem("Modelo_de_Minimizacion", pulp.LpMinimize)
        self.crear_variables()

        # Función objetivo (mínima)
        self.modelo += pulp.lpSum(
            row["Coef_FO"] * self.variables[row["Variable"]]
            for _, row in self.modelo_df.iterrows()
        )

        # Restricciones
        columnas_restriccion = [col for col in self.modelo_df.columns if col.startswith("Coef_R")]
        for i, restr in self.restricciones_df.iterrows():
            expr = pulp.lpSum(
                self.modelo_df[columnas_restriccion[i]].iloc[j] * self.variables[row["Variable"]]
                for j, row in self.modelo_df.iterrows()
            )

            if restr["Tipo"] == "<=":
                self.modelo += expr <= restr["RHS"], restr["Restriccion"]
            elif restr["Tipo"] == ">=":
                self.modelo += expr >= restr["RHS"], restr["Restriccion"]
            elif restr["Tipo"] == "=":
                self.modelo += expr == restr["RHS"], restr["Restriccion"]

class Transporte(Problema):
    def construir(self):
        self.modelo = pulp.LpProblem("Problema_de_Transporte", pulp.LpMinimize)

        df = self.modelo_df  # en este caso contiene costos, oferta y demanda

        # Crear variables de decisión: X_origen_destino
        self.variables = {
            (row["Origen"], row["Destino"]): pulp.LpVariable(f"X_{row['Origen']}_{row['Destino']}", lowBound=0)
            for _, row in df.iterrows()
        }

        # Función objetivo: minimizar suma de costo * cantidad
        self.modelo += pulp.lpSum(
            row["Costo"] * self.variables[(row["Origen"], row["Destino"])]
            for _, row in df.iterrows()
        )

        # Restricción de oferta por origen
        oferta_por_origen = df.dropna(subset=["Oferta"]).groupby("Origen").first()["Oferta"]
        for origen, oferta in oferta_por_origen.items():
            self.modelo += (
                pulp.lpSum(
                    self.variables[(origen, d)] for d in df[df["Origen"] == origen]["Destino"]
                ) <= oferta,
                f"Oferta_{origen}"
            )

        # Restricción de demanda por destino
        demanda_por_destino = df.dropna(subset=["Demanda"]).groupby("Destino").first()["Demanda"]
        for destino, demanda in demanda_por_destino.items():
            self.modelo += (
                pulp.lpSum(
                    self.variables[(o, destino)] for o in df[df["Destino"] == destino]["Origen"]
                ) >= demanda,
                f"Demanda_{destino}"
            )


