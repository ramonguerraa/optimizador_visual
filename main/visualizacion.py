import streamlit as st
import pandas as pd

def mostrar_resultados(resultado):
    st.success(f"Estado del modelo: {resultado['status']}")
    
    st.markdown("### 🔍 Variables de decisión:")
    df_sol = pd.DataFrame(resultado["solucion"].items(), columns=["Variable", "Valor"])
    st.table(df_sol)

    st.markdown(f"### 📈 Valor óptimo de la función objetivo: `{resultado['valor_objetivo']}`")
