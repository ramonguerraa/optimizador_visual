import pandas as pd
import numpy as np
import pulp

def leer_datos_excel(archivo):
    try:
        # Leer todas las hojas
        xls = pd.ExcelFile(archivo)
        if 'modelo' not in xls.sheet_names or 'restricciones' not in xls.sheet_names:
            raise ValueError("El archivo debe contener dos hojas llamadas 'modelo' y 'restricciones'.")

        df_modelo = xls.parse('modelo')
        df_restricciones = xls.parse('restricciones')

        # Validar columnas obligatorias
        columnas_obligatorias_modelo = {'Variable', 'Coef_FO'}
        if not columnas_obligatorias_modelo.issubset(df_modelo.columns):
            raise ValueError("La hoja 'modelo' debe contener las columnas: Variable y Coef_FO.")

        columnas_restriccion = [col for col in df_modelo.columns if col.startswith("Coef_R")]
        if len(columnas_restriccion) == 0:
            raise ValueError("La hoja 'modelo' debe incluir al menos una columna Coef_R#.")

        columnas_obligatorias_restricciones = {'Restriccion', 'Tipo', 'RHS'}
        if not columnas_obligatorias_restricciones.issubset(df_restricciones.columns):
            raise ValueError("La hoja 'restricciones' debe contener las columnas: Restriccion, Tipo y RHS.")

        # Rellenar celdas vacías con cero en columnas numéricas
        columnas_numericas_modelo = ['Coef_FO'] + columnas_restriccion
        df_modelo[columnas_numericas_modelo] = df_modelo[columnas_numericas_modelo].fillna(0)

        df_restricciones['RHS'] = df_restricciones['RHS'].fillna(0)

        # Validar que sean numéricos (convertibles)
        for col in columnas_numericas_modelo:
            if not pd.api.types.is_numeric_dtype(df_modelo[col]):
                try:
                    df_modelo[col] = pd.to_numeric(df_modelo[col])
                except:
                    raise ValueError(f"La columna '{col}' debe contener solo valores numéricos.")

        if not pd.api.types.is_numeric_dtype(df_restricciones['RHS']):
            try:
                df_restricciones['RHS'] = pd.to_numeric(df_restricciones['RHS'])
            except:
                raise ValueError("La columna 'RHS' en 'restricciones' debe ser numérica.")

        # Validar valores en columna Tipo
        tipos_validos = {"<=", "=", ">="}
        if not df_restricciones['Tipo'].isin(tipos_validos).all():
            raise ValueError("La columna 'Tipo' solo puede contener: <=, =, >=.")

        return {
            "modelo": df_modelo,
            "restricciones": df_restricciones
        }

    except Exception as e:
        raise ValueError(f"Error al leer el archivo: {e}")


def resolver_maximizacion(datos):
    df_modelo = datos["modelo"]
    df_restricciones = datos["restricciones"]

    # Crear el problema
    prob = pulp.LpProblem("MaximizarBeneficio", pulp.LpMaximize)

    # Crear variables
    variables = {
        row["Variable"]: pulp.LpVariable(row["Variable"], lowBound=0)
        for _, row in df_modelo.iterrows()
    }

    # Función objetivo
    prob += pulp.lpSum([
        row["Coef_FO"] * variables[row["Variable"]]
        for _, row in df_modelo.iterrows()
    ])

    # Restricciones
    for i, restr in df_restricciones.iterrows():
        coeficientes = df_modelo[f"Coef_R{i+1}"]
        expr = pulp.lpSum([
            coeficientes[j] * variables[row["Variable"]]
            for j, row in df_modelo.iterrows()
        ])

        if restr["Tipo"] == "<=":
            prob += expr <= restr["RHS"], restr["Restriccion"]
        elif restr["Tipo"] == ">=":
            prob += expr >= restr["RHS"], restr["Restriccion"]
        elif restr["Tipo"] == "=":
            prob += expr == restr["RHS"], restr["Restriccion"]

    # Resolver
    prob.solve()

    solucion = {v.name: v.varValue for v in prob.variables()}
    resultado = {
        "solucion": solucion,
        "valor_objetivo": pulp.value(prob.objective),
        "status": pulp.LpStatus[prob.status]
    }
    return resultado
