import streamlit as st
import pandas as pd
from main.utils import plantilla_modelo, plantilla_restricciones, exportar_resultado_excel
from main.utils import validar_datos_manual, validar_datos_transporte, registrar_log
from main.visualizacion import graficar_solucion_lineal

def manejar_carga_manual(nombre_modelo, clase_problema):
    """
    Permite al usuario ingresar manualmente los datos del modelo, resolverlo y exportar resultados.

    La interfaz varía según el tipo de problema (Maximización, Minimización, Transporte, Asignación),
    mostrando plantillas editables y ejecutando el modelo con los valores ingresados.

    Args:
        nombre_modelo (str): Etiqueta del tipo de problema.
        clase_problema (class): Clase correspondiente al modelo a resolver.

    Returns:
        None
    """

    st.markdown(f"### ✍️ Ingreso manual de datos para {nombre_modelo}")

    if nombre_modelo == "Transporte":
        num_origenes = st.number_input("Número de orígenes", min_value=1, max_value=10, value=2)
        num_destinos = st.number_input("Número de destinos", min_value=1, max_value=10, value=2)

        # Crear plantilla de transporte
        data = []
        for i in range(num_origenes):
            for j in range(num_destinos):
                data.append({
                    "Origen": f"O{i+1}",
                    "Destino": f"D{j+1}",
                    "Costo": 0,
                    "Oferta": 20 if j == 0 else None,
                    "Demanda": 30 if i == 0 else None
                })
        df_costos = pd.DataFrame(data)

        editado = st.data_editor(df_costos, use_container_width=True, num_rows="fixed", key="editor_transporte")

        if st.button("🚀 Ejecutar modelo"):
            validar_datos_transporte(editado)
            try:
                problema = clase_problema(editado, pd.DataFrame())
                problema.construir()
                resultado = problema.resolver()
                from main import visualizacion
                visualizacion.mostrar_resultados(resultado)
            except Exception as e:
                st.error(f"❌ Error: {e}")

        registrar_log(nombre_modelo, resultado, datos_entrada)

        datos_entrada = {
            "costos": df_editado
        }
        excel_resultado = exportar_resultado_excel(resultado, datos_entrada)


    elif nombre_modelo == "Asignación":
        st.markdown("Ingrese una matriz de costos o utilidades para el problema de asignación.")
        num = st.number_input("Tamaño de la matriz cuadrada", min_value=2, max_value=10, value=3)

        # Crear DataFrame cuadrado con valores por defecto
        df = pd.DataFrame([[0]*num for _ in range(num)], 
                        columns=[f"Tarea {j+1}" for j in range(num)],
                        index=[f"Agente {i+1}" for i in range(num)])

        df_editado = st.data_editor(df, key="editor_asignacion")

        if st.button("🚀 Ejecutar modelo"):
            from main.utils import validar_datos_asignacion
            from main.problemas import Asignacion
            validar_datos_asignacion(df_editado)

            problema = Asignacion(df_editado)
            problema.construir()
            resultado = problema.resolver()

            from main import visualizacion
            visualizacion.mostrar_resultados(resultado)

        registrar_log(nombre_modelo, resultado, datos_entrada)

        datos_entrada = {
            "costos": df_editado
        }
        excel_resultado = exportar_resultado_excel(resultado, datos_entrada)


    else:  # Para Max y Min
        col1, col2 = st.columns(2)
        num_vars = col1.number_input("Número de variables", min_value=1, max_value=10, value=2)
        num_restr = col2.number_input("Número de restricciones", min_value=1, max_value=10, value=2)

        df_modelo = plantilla_modelo(num_vars, num_restr)
        df_restricciones = plantilla_restricciones(num_restr)

        edit_modelo = st.data_editor(df_modelo, use_container_width=True, num_rows="fixed", key=f"editor_modelo_{nombre_modelo}")
        edit_restr = st.data_editor(df_restricciones, use_container_width=True, num_rows="fixed", key=f"editor_restricciones_{nombre_modelo}")

        if st.button("🚀 Ejecutar modelo"):
            validar_datos_manual(edit_modelo, edit_restr)
            try:
                problema = clase_problema(edit_modelo, edit_restr)
                problema.construir()
                resultado = problema.resolver()
                from main import visualizacion
                visualizacion.mostrar_resultados(resultado)
                # Solo graficar si es Max/Min y tiene 2 variables
                grafico_buffer = None
                if edit_modelo.shape[0] == 2:
                    grafico_buffer = graficar_solucion_lineal(edit_modelo, edit_restr, resultado, tipo=nombre_modelo)
            except Exception as e:
                st.error(f"❌ Error: {e}")

        registrar_log(nombre_modelo, resultado, datos_entrada)

        datos_entrada = {
            "modelo": edit_modelo,
            "restricciones": edit_restr
        }
        excel_resultado = exportar_resultado_excel(resultado, datos_entrada, grafico_img=grafico_buffer)

    st.download_button(
        label="⬇️ Descargar resultados con datos originales",
        data=excel_resultado,
        file_name="resultado_completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def manejar_carga_desde_excel(nombre_archivo, clase_problema, hojas,
                               nombre_hoja_modelo="modelo",
                               nombre_hoja_restricciones="restricciones",
                               nombre_modelo=""):
    """
    Maneja la carga de datos desde un archivo Excel y ejecuta el modelo.

    Soporta distintos tipos de problema (Maximización, Minimización, Transporte, Asignación),
    leyendo las hojas correspondientes y validando sus contenidos.

    Args:
        nombre_archivo (str): Texto descriptivo del tipo de archivo (para mostrar al usuario).
        clase_problema (class): Clase del modelo a instanciar.
        hojas (dict): Diccionario con nombres de hojas a mostrar en la vista previa.
        nombre_hoja_modelo (str): Nombre de la hoja con el modelo base.
        nombre_hoja_restricciones (str): Nombre de la hoja con restricciones (si aplica).
        nombre_modelo (str): Etiqueta del tipo de problema (usada para exportación/logs).

    Returns:
        None
    """

    archivo = st.file_uploader(f"📁 Sube tu archivo Excel de {nombre_archivo}", type=["xlsx"])

    if archivo is not None:
        try:
            xls = pd.ExcelFile(archivo)
            st.success("✅ Archivo cargado correctamente")

            for hoja, titulo in hojas.items():
                df = xls.parse(hoja)
                st.markdown(f"#### {titulo}")
                st.dataframe(df)

            if st.button("🚀 Ejecutar modelo"):
                # 🔁 Lógica para Asignación
                if clase_problema.__name__ == "Asignacion":
                    df_costos = xls.parse("costos")
                    from main.utils import validar_datos_asignacion
                    validar_datos_asignacion(df_costos)

                    problema = clase_problema(df_costos)
                    problema.construir()
                    resultado = problema.resolver()

                    from main import visualizacion
                    visualizacion.mostrar_resultados(resultado)

                    datos_entrada = {"costos": df_costos}
                    excel_resultado = exportar_resultado_excel(resultado, datos_entrada)

                # 🔁 Lógica para Transporte
                elif nombre_hoja_modelo == "costos":
                    df_costos = xls.parse("costos")
                    from main.utils import validar_datos_transporte
                    validar_datos_transporte(df_costos)

                    problema = clase_problema(df_costos, pd.DataFrame())
                    problema.construir()
                    resultado = problema.resolver()

                    from main import visualizacion
                    visualizacion.mostrar_resultados(resultado)

                    datos_entrada = {"costos": df_costos}
                    excel_resultado = exportar_resultado_excel(resultado, datos_entrada)

                # 🔁 Lógica para Max y Min
                else:
                    df_modelo = xls.parse(nombre_hoja_modelo)
                    df_restricciones = xls.parse(nombre_hoja_restricciones)

                    from main.utils import validar_datos_manual
                    validar_datos_manual(df_modelo, df_restricciones)

                    problema = clase_problema(df_modelo, df_restricciones)
                    problema.construir()
                    resultado = problema.resolver()

                    # Solo graficar si hay 2 variables
                    grafico_buffer = None
                    if clase_problema.__name__ in ["Maximizacion", "Minimizacion"] and df_modelo.shape[0] == 2:
                        grafico_buffer = graficar_solucion_lineal(df_modelo, df_restricciones, resultado, tipo=nombre_modelo)

                    datos_entrada = {"modelo": df_modelo, "restricciones": df_restricciones}
                    excel_resultado = exportar_resultado_excel(resultado, datos_entrada, grafico_img=grafico_buffer)


                    from main import visualizacion
                    visualizacion.mostrar_resultados(resultado)


                registrar_log(nombre_modelo, resultado, datos_entrada)

                # ✅ Botón para descargar resultados
                st.download_button(
                    label="⬇️ Descargar resultados en Excel",
                    data=excel_resultado,
                    file_name="resultado_completo.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")
