import pulp
import pandas as pd
from scipy.optimize import linear_sum_assignment

class Problema:
    """
    Clase base abstracta para representar un problema de optimización.

    Esta clase define la estructura común para cualquier tipo de modelo:
    maximizaciones, minimizaciones, transporte o asignación. Debe ser
    extendida por subclases que implementen métodos específicos.

    Args:
        df_modelo (pd.DataFrame): DataFrame que contiene los coeficientes del modelo.
        df_restricciones (pd.DataFrame): DataFrame que contiene las restricciones del problema.

    Attributes:
        df_modelo (pd.DataFrame): Datos del modelo.
        df_restricciones (pd.DataFrame): Datos de restricciones.
        modelo (pulp.LpProblem): Modelo de optimización creado con PuLP.
        variables (dict): Diccionario con las variables de decisión.

    Methods:
        crear_variables(): Crea las variables del modelo. Debe ser sobreescrito.
        construir(): Construye el modelo en PuLP. Debe ser sobreescrito.
        resolver(): Resuelve el modelo con el solver de PuLP.
    """

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
        """
        Resuelve el modelo de optimización usando el solver de PuLP.

        Este método aplica a problemas de:

        - Maximización
        - Minimización
        - Transporte (formulado como PL)

        Returns:
            dict: Contiene 'status', 'valor_objetivo' y 'solucion' (diccionario de variables).
        """
        self.modelo.solve()
        solucion = {v.name: v.varValue for v in self.modelo.variables()}
        self.resultado = {
            "solucion": solucion,
            "valor_objetivo": pulp.value(self.modelo.objective),
            "status": pulp.LpStatus[self.modelo.status]
        }
        return self.resultado
    
class Maximizacion(Problema):
    """
    Modelo de programación lineal para problemas de maximización.

    Construye una función objetivo lineal a maximizar, sujeta a un conjunto
    de restricciones lineales.

    Métodos:
        construir(): Define la función objetivo y restricciones.
    """

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
    """
    Modelo de programación lineal para problemas de minimización.

    Construye una función objetivo lineal a minimizar, sujeta a un conjunto
    de restricciones lineales.

    Métodos:
        construir(): Define la función objetivo y restricciones.
    """
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
    """
    Modelo clásico de transporte para minimizar costos de distribución.

    Toma como entrada una tabla de costos unitarios entre orígenes y destinos,
    junto con la oferta y demanda de cada nodo.

    Métodos:
        construir(): Crea las variables, restricciones de oferta/demanda y función objetivo.
    """

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


class Asignacion:
    """
    Problema de asignación de recursos usando el Método Húngaro.

    Este modelo busca asignar recursos a tareas minimizando el costo total
    (o maximizando la utilidad) en una matriz cuadrada.

    Args:
        df_costos (pd.DataFrame): Matriz de costos entre agentes y tareas.

    Métodos:
        construir(): Verifica formato y prepara la matriz.
        resolver(): Ejecuta el método Húngaro y devuelve asignaciones óptimas.
    """

    def __init__(self, df_costos):
        self.df_costos = df_costos
        self.resultado = {}

    def construir(self):
        self.matriz = self.df_costos.to_numpy()
        if self.matriz.shape[0] != self.matriz.shape[1]:
            raise ValueError("⚠️ La matriz de asignación debe ser cuadrada para el método húngaro.")

    def resolver(self):
        """
        Ejecuta el método Húngaro (scipy.optimize.linear_sum_assignment) para resolver el problema.

        Returns:
            dict: Contiene 'status', 'valor_objetivo' y lista de 'asignaciones' óptimas.
        """

        fila, columna = linear_sum_assignment(self.matriz)
        asignaciones = [(self.df_costos.index[i], self.df_costos.columns[j]) for i, j in zip(fila, columna)]
        total = self.matriz[fila, columna].sum()

        self.resultado = {
            "status": "Óptimo",
            "valor_objetivo": total,
            "asignaciones": asignaciones
        }
        return self.resultado


