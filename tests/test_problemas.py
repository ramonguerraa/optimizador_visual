import pytest
import pandas as pd
from main.problemas import Maximizacion, Minimizacion

def test_resolucion_maximizacion():
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

    problema = Maximizacion(df_modelo, df_restricciones)
    problema.construir()
    resultado = problema.resolver()

    assert resultado["status"] == "Optimal"
    assert isinstance(resultado["valor_objetivo"], (int, float))
    assert "X1" in resultado["solucion"]

from main.problemas import Maximizacion, Minimizacion

def test_resolucion_minimizacion():
    # Caso de minimización: minimizar Z = 10·X1 + 5·X2
    # Sujeto a:
    #  X1 + X2 >= 6
    #  X1, X2 >= 0
    df_modelo = pd.DataFrame({
        "Variable": ["X1", "X2"],
        "Coef_FO": [10, 5],
        "Coef_R1": [1, 1]
    })

    df_restricciones = pd.DataFrame({
        "Restriccion": ["R1"],
        "Tipo": [">="],
        "RHS": [6]
    })

    problema = Minimizacion(df_modelo, df_restricciones)
    problema.construir()
    resultado = problema.resolver()

    assert resultado["status"] == "Optimal"
    assert isinstance(resultado["valor_objetivo"], (int, float))
    assert "X1" in resultado["solucion"]
    assert "X2" in resultado["solucion"]

    # Opcional: verificar el valor mínimo esperado
    assert resultado["valor_objetivo"] == 30  # (X1=0, X2=6) o (X1=6, X2=0)
