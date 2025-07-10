import pandas as pd
from io import BytesIO

def generar_ejemplo_maximizacion():
    # Ejemplo para 2 variables y 2 restricciones
    df_modelo = pd.DataFrame({
        "Variable": ["X1", "X2"],
        "Coef_FO": [40, 30],
        "Coef_R1": [2, 1],
        "Coef_R2": [3, 2]
    })

    df_restricciones = pd.DataFrame({
        "Restriccion": ["R1", "R2"],
        "Tipo": ["<=", "<="],
        "RHS": [100, 80]
    })

    return df_modelo, df_restricciones

def generar_ejemplo_minimizacion():
    # Ejemplo para 2 variables y 2 restricciones
    df_modelo = pd.DataFrame({
        "Variable": ["X1", "X2"],
        "Coef_FO": [2, 3],
        "Coef_R1": [5, 10],
        "Coef_R2": [4, 3],
        "Coef_R3": [0.5, 0]
    })

    df_restricciones = pd.DataFrame({
        "Restriccion": ["R1", "R2", "R3"],
        "Tipo": [">=", ">=", ">="],
        "RHS": [90, 48, 1.5]
    })

    return df_modelo, df_restricciones


def exportar_excel(df1, df2, nombre1="modelo", nombre2="restricciones"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name=nombre1, index=False)
        df2.to_excel(writer, sheet_name=nombre2, index=False)
    output.seek(0)
    return output

def plantilla_modelo(v=2, r=2):
    # Plantilla de variables por defecto (v variables, r restricciones)
    data = {
        "Variable": [f"X{i+1}" for i in range(v)],
        "Coef_FO": [0] * v
    }
    for j in range(r):
        data[f"Coef_R{j+1}"] = [0] * v

    return pd.DataFrame(data)


def plantilla_restricciones(r=2):
    return pd.DataFrame({
        "Restriccion": [f"R{i+1}" for i in range(r)],
        "Tipo": ["<="] * r,
        "RHS": [0] * r
    })

def validar_datos_modelo(modelo_df, restricciones_df):
    # Validar columnas básicas
    if "Variable" not in modelo_df.columns or "Coef_FO" not in modelo_df.columns:
        raise ValueError("La tabla de variables debe tener columnas 'Variable' y 'Coef_FO'.")

    columnas_restriccion = [col for col in modelo_df.columns if col.startswith("Coef_R")]
    if not columnas_restriccion:
        raise ValueError("Debe haber al menos una columna 'Coef_R#' para restricciones.")

    if not {"Restriccion", "Tipo", "RHS"}.issubset(restricciones_df.columns):
        raise ValueError("La tabla de restricciones debe tener las columnas: 'Restriccion', 'Tipo' y 'RHS'.")

    # Convertir celdas vacías a 0
    modelo_df[columnas_restriccion + ["Coef_FO"]] = modelo_df[columnas_restriccion + ["Coef_FO"]].fillna(0)
    restricciones_df["RHS"] = restricciones_df["RHS"].fillna(0)

    # Validar tipo numérico
    for col in columnas_restriccion + ["Coef_FO"]:
        try:
            modelo_df[col] = pd.to_numeric(modelo_df[col])
        except:
            raise ValueError(f"Columna '{col}' debe tener solo valores numéricos.")

    try:
        restricciones_df["RHS"] = pd.to_numeric(restricciones_df["RHS"])
    except:
        raise ValueError("La columna 'RHS' debe contener solo números.")

    # Validar signos
    tipos_validos = {"<=", ">=", "="}
    if not restricciones_df["Tipo"].isin(tipos_validos).all():
        raise ValueError("La columna 'Tipo' debe contener solo: <=, >= o =.")

