import pytest
import pandas as pd
from main.utils import validar_datos_modelo

def test_validacion_correcta():
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

    # No debería lanzar excepción
    validar_datos_modelo(df_modelo, df_restricciones)

def test_variable_invalida():
    df_modelo = pd.DataFrame({
        "Var": ["X1", "X2"],  # Mal nombre de columna
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
        validar_datos_modelo(df_modelo, df_restricciones)

