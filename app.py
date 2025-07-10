import streamlit as st
from main import modelo, visualizacion
from main.utils import generar_ejemplo_maximizacion, exportar_excel, generar_ejemplo_minimizacion
from main.problemas import Maximizacion, Minimizacion
from main.utils import plantilla_modelo, plantilla_restricciones, validar_datos_modelo

# -----------------------------
# Configuración de la app
# -----------------------------
st.set_page_config(page_title="Optimizador Visual", layout="wide")

# -----------------------------
# Encabezado
# -----------------------------
st.title("📊 Optimizador Visual de Recursos")
st.markdown("Versión inicial - módulo de **Maximización** activado.")

# -----------------------------
# Menú lateral de navegación
# -----------------------------
opcion = st.sidebar.selectbox(
    "Selecciona el tipo de problema a resolver:",
    [
        "Maximización",
        "Minimización",
        "Problema de Transporte (próximamente)",
        "Problema de Asignación (próximamente)"
    ]
)
# -----------------------------
# Flujo visual para Maximización
# -----------------------------
if opcion == "Maximización":
    st.subheader("🔼 Modelo de Maximización")
    
    tipo_carga = st.radio("¿Cómo deseas cargar los datos?", ["Desde archivo Excel", "Ingreso manual"])
    
    # Mostrar ejemplo de estructura de Maximizacion
    st.markdown("### ℹ️ Formato esperado para la carga de datos:")

    with st.expander("📄 Ver ejemplo de estructura de archivo Excel"):
        df_modelo_ex, df_rest_ex = generar_ejemplo_maximizacion()

        st.markdown("#### Hoja 1: modelo")
        st.dataframe(df_modelo_ex)

        st.markdown("#### Hoja 2: restricciones")
        st.dataframe(df_rest_ex)

        excel_bytes = exportar_excel(df_modelo_ex, df_rest_ex)
        st.download_button("⬇️ Descargar archivo de ejemplo", data=excel_bytes, file_name="ejemplo_maximizacion.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


    if tipo_carga == "Desde archivo Excel":
        archivo = st.file_uploader("📁 Sube tu archivo Excel con el modelo", type=["xlsx"])
        
        if archivo is not None:
            try:
                datos = modelo.leer_datos_excel(archivo)
                st.success("Datos cargados correctamente.")

                st.markdown("### 📌 Función Objetivo y Variables:")
                st.dataframe(datos["modelo"])

                st.markdown("### 📌 Restricciones:")
                st.dataframe(datos["restricciones"])

                if st.button("🚀 Ejecutar modelo"):
                    try:
                        problema = Maximizacion(datos["modelo"], datos["restricciones"])
                        problema.construir()
                        resultado = problema.resolver()
                        visualizacion.mostrar_resultados(resultado)
                    except Exception as e:
                        st.error(f"❌ Error al resolver el modelo: {e}")


            except Exception as e:
                st.error(f"❌ Error al procesar el archivo: {e}")

    elif tipo_carga == "Ingreso manual":
        st.markdown("### ✍️ Ingreso manual de datos del modelo")

        # Definir número de variables y restricciones
        cols = st.columns(2)
        num_vars = cols[0].number_input("Número de variables", min_value=1, max_value=10, value=2)
        num_restr = cols[1].number_input("Número de restricciones", min_value=1, max_value=10, value=2)

        # Mostrar editor para cada tabla
        modelo_df = st.data_editor(
            plantilla_modelo(num_vars, num_restr),
            num_rows="fixed",
            key="editor_modelo",
            use_container_width=True
        )

        restricciones_df = st.data_editor(
            plantilla_restricciones(num_restr),
            num_rows="fixed",
            key="editor_restricciones",
            use_container_width=True
        )

        # Botón para ejecutar modelo
        if st.button("🚀 Ejecutar modelo con datos ingresados"):
            try:
                validar_datos_modelo(modelo_df, restricciones_df)
                problema = Maximizacion(modelo_df, restricciones_df)
                problema.construir()
                resultado = problema.resolver()
                visualizacion.mostrar_resultados(resultado)
            except Exception as e:
                st.error(f"❌ Error: {e}")

elif opcion == "Minimización":
    st.subheader("🔽 Modelo de Minimización")

    tipo_carga = st.radio("¿Cómo deseas cargar los datos?", ["Desde archivo Excel", "Ingreso manual"])

    # Mostrar ejemplo de estructura de Minimizacion
    st.markdown("### ℹ️ Formato esperado para la carga de datos:")

    with st.expander("📄 Ver ejemplo de estructura de archivo Excel"):
        df_modelo_ex, df_rest_ex = generar_ejemplo_minimizacion()

        st.markdown("#### Hoja 1: modelo")
        st.dataframe(df_modelo_ex)

        st.markdown("#### Hoja 2: restricciones")
        st.dataframe(df_rest_ex)

        excel_bytes = exportar_excel(df_modelo_ex, df_rest_ex)
        st.download_button("⬇️ Descargar archivo de ejemplo", data=excel_bytes, file_name="ejemplo_minimizacion.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if tipo_carga == "Desde archivo Excel":
        archivo = st.file_uploader("📁 Sube tu archivo Excel con el modelo", type=["xlsx"])
        
        if archivo is not None:
            try:
                datos = modelo.leer_datos_excel(archivo)
                st.success("Datos cargados correctamente.")
                st.dataframe(datos["modelo"])
                st.dataframe(datos["restricciones"])

                if st.button("🚀 Ejecutar modelo"):
                    problema = Minimizacion(datos["modelo"], datos["restricciones"])
                    problema.construir()
                    resultado = problema.resolver()
                    visualizacion.mostrar_resultados(resultado)
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

    elif tipo_carga == "Ingreso manual":
        st.markdown("### ✍️ Ingreso manual de datos del modelo")

        # Definir número de variables y restricciones
        cols = st.columns(2)
        num_vars = cols[0].number_input("Número de variables", min_value=1, max_value=10, value=2)
        num_restr = cols[1].number_input("Número de restricciones", min_value=1, max_value=10, value=2)

        # Mostrar editor para cada tabla
        modelo_df = st.data_editor(
            plantilla_modelo(num_vars, num_restr),
            num_rows="fixed",
            key="editor_modelo",
            use_container_width=True
        )

        restricciones_df = st.data_editor(
            plantilla_restricciones(num_restr),
            num_rows="fixed",
            key="editor_restricciones",
            use_container_width=True
        )

        # Botón para ejecutar modelo
        if st.button("🚀 Ejecutar modelo con datos ingresados"):
            try:
                validar_datos_modelo(modelo_df, restricciones_df)
                problema = Minimizacion(modelo_df, restricciones_df)
                problema.construir()
                resultado = problema.resolver()
                visualizacion.mostrar_resultados(resultado)
            except Exception as e:
                st.error(f"❌ Error: {e}")
# -----------------------------
# Mensaje para opciones no activas
# -----------------------------
else:
    st.warning("🚧 Esta sección estará disponible en futuras versiones.")

