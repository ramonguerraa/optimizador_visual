import pandas as pd
from io import BytesIO
import pytest
from main.modelo import leer_datos_excel

def crear_excel_valido():
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

    archivo = BytesIO()
    with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
        df_modelo.to_excel(writer, sheet_name="modelo", index=False)
        df_restricciones.to_excel(writer, sheet_name="restricciones", index=False)
    archivo.seek(0)
    return archivo

def test_leer_excel_valido():
    archivo = crear_excel_valido()
    datos = leer_datos_excel(archivo)

    assert "modelo" in datos
    assert "restricciones" in datos
    assert datos["modelo"].shape == (2, 4)
    assert datos["restricciones"].shape == (2, 3)

def test_excel_sin_hoja_modelo():
    archivo = BytesIO()
    with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
        pd.DataFrame({"a": [1]}).to_excel(writer, sheet_name="restricciones", index=False)
    archivo.seek(0)

    with pytest.raises(ValueError) as excinfo:
        leer_datos_excel(archivo)

    assert "modelo" in str(excinfo.value).lower()

def test_excel_columna_invalida():
    df_modelo = pd.DataFrame({
        "Variable": ["X1", "X2"],
        "FO": [40, 30],  # ❌ debería ser 'Coef_FO'
        "Coef_R1": [2, 1],
        "Coef_R2": [3, 2]
    })
    df_restricciones = pd.DataFrame({
        "Restriccion": ["R1", "R2"],
        "Tipo": ["<=", "<="],
        "RHS": [100, 80]
    })

    archivo = BytesIO()
    with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
        df_modelo.to_excel(writer, sheet_name="modelo", index=False)
        df_restricciones.to_excel(writer, sheet_name="restricciones", index=False)
    archivo.seek(0)

    with pytest.raises(ValueError) as excinfo:
        leer_datos_excel(archivo)

    assert "Coef_FO" in str(excinfo.value)
