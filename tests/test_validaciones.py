import pytest
import pandas as pd
from main.utils import validar_datos_manual, validar_datos_transporte

# 🔹 Pruebas para validar_datos_manual()
def test_validacion_manual_correcta():
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

    validar_datos_manual(df_modelo, df_restricciones)  # No debe lanzar error

def test_validacion_manual_columna_invalida():
    df_modelo = pd.DataFrame({
        "Var": ["X1", "X2"],  # ❌ mal nombre
        "Coef_FO": [40, 30],
        "Coef_R1": [2, 1],
        "Coef_R2": [3, 2]
    })
    df_restricciones = pd.DataFrame({
        "Restriccion": ["R1", "R2"],
        "Tipo": ["<=", "<="],
        "RHS": [100, 80]
    })

    with pytest.raises(ValueError):
        validar_datos_manual(df_modelo, df_restricciones)

def test_validacion_manual_tipo_invalido():
    df_modelo = pd.DataFrame({
        "Variable": ["X1", "X2"],
        "Coef_FO": ["a", 30],  # ❌ valor no numérico
        "Coef_R1": [2, 1],
        "Coef_R2": [3, 2]
    })
    df_restricciones = pd.DataFrame({
        "Restriccion": ["R1", "R2"],
        "Tipo": ["<=", "<="],
        "RHS": [100, 80]
    })

    with pytest.raises(ValueError):
        validar_datos_manual(df_modelo, df_restricciones)

def test_validacion_transporte_correcta():
    df = pd.DataFrame({
        "Origen": ["O1", "O1", "O2", "O2"],
        "Destino": ["D1", "D2", "D1", "D2"],
        "Costo": [4, 6, 5, 2],
        "Oferta": [20, None, 30, None],
        "Demanda": [25, 35, None, None]
    })
    validar_datos_transporte(df)  # No debe lanzar error

def test_validacion_transporte_columnas_faltantes():
    df = pd.DataFrame({
        "Origen": ["O1"], "Destino": ["D1"], "Costo": [4]
    })
    with pytest.raises(ValueError):
        validar_datos_transporte(df)

def test_validacion_transporte_costo_invalido():
    df = pd.DataFrame({
        "Origen": ["O1"],
        "Destino": ["D1"],
        "Costo": ["caro"],  # ❌ inválido
        "Oferta": [20],
        "Demanda": [25]
    })
    with pytest.raises(ValueError):
        validar_datos_transporte(df)
