import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from io import BytesIO

def mostrar_resultados(resultado: dict):
    """
    Muestra en pantalla el resumen de resultados del modelo optimizado.

    Detecta si el resultado contiene:
    - Una solución general (variables)
    - Una matriz de asignaciones (Asignación)
    - Un modelo de transporte (tabla con múltiples combinaciones)

    Args:
        resultado (dict): Diccionario con claves como 'status', 'valor_objetivo',
                          'solucion' o 'asignaciones'.

    Returns:
        None
    """

    st.success(f"Estado del modelo: {resultado['status']}")
    
    st.markdown("### 🔍 Variables de decisión:")
    df_sol = pd.DataFrame(resultado["solucion"].items(), columns=["Variable", "Valor"])
    st.table(df_sol)

    st.markdown(f"### 📈 Valor óptimo de la función objetivo: `{resultado['valor_objetivo']}`")

def graficar_solucion_lineal(df_modelo, df_restricciones, resultado, tipo="Maximización"):
    """
    Genera y muestra una visualización gráfica para modelos lineales de 2 variables.

    Dibuja:
    - Las restricciones como rectas
    - La región factible sombreada
    - La solución óptima como un punto

    Solo aplicable a problemas de Maximización o Minimización con 2 variables.

    Args:
        df_modelo (pd.DataFrame): Coeficientes de la función objetivo y restricciones.
        df_restricciones (pd.DataFrame): RHS y operadores de las restricciones.
        resultado (dict): Resultado resuelto del modelo.
        tipo (str): Tipo de modelo ('Maximización' o 'Minimización') para el título del gráfico.

    Returns:
        BytesIO: Objeto con la imagen del gráfico en formato PNG (para exportar), o None.
    """

    if df_modelo.shape[0] != 2:
        st.warning("⚠️ Visualización disponible solo para modelos con 2 variables.")
        return

    # Variables
    x1 = np.linspace(0, 50, 500)
    fig, ax = plt.subplots()

    # Graficar restricciones
    for idx, row in df_modelo.iterrows():
        restriccion = df_restricciones.iloc[idx]
        a = row["Coef_R1"]
        b = row["Coef_R2"]
        rhs = restriccion["RHS"]
        tipo_signo = restriccion["Tipo"]

        # Evitar división por cero
        if b != 0:
            y = (rhs - a * x1) / b
        else:
            x1_const = rhs / a
            ax.axvline(x=x1_const, color='gray', linestyle='--', label=f"Restricción {idx+1}")
            continue

        if tipo_signo == "<=":
            ax.fill_between(x1, y, 100, alpha=0.1)
        elif tipo_signo == ">=":
            ax.fill_between(x1, y, 0, alpha=0.1)

        ax.plot(x1, y, label=f"Restricción {idx+1}")

    # Graficar solución
    if resultado.get("status") == "Óptimo":
        x = resultado["solucion"]
        x_val = x.get("X1", 0)
        y_val = x.get("X2", 0)
        ax.plot(x_val, y_val, "ro", label="Solución óptima")
        ax.annotate(f"({x_val:.2f}, {y_val:.2f})", (x_val, y_val), textcoords="offset points", xytext=(10, 10))

    # Ejes y estética
    ax.set_xlabel("X1")
    ax.set_ylabel("X2")
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 50)
    ax.set_title(f"Solución gráfica - {tipo}")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # Mostrar en Streamlit
    st.pyplot(fig)

    # Retornar imagen en memoria
    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer
