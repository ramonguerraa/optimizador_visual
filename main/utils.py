import pandas as pd
import streamlit as st
from io import BytesIO
import os
from datetime import datetime


def mostrar_ejemplo_excel(ruta_archivo, hojas: dict, titulo: str):
    """
    Muestra la estructura de un archivo Excel de ejemplo y permite su descarga.

    Args:
        ruta_archivo (str): Ruta del archivo .xlsx
        hojas (dict): Diccionario con nombre de hoja como clave y título para mostrar como valor
        titulo (str): Título del panel expandible
    """
    with st.expander(f"📄 {titulo}"):
        try:
            archivo = pd.ExcelFile(ruta_archivo)

            for hoja, titulo_hoja in hojas.items():
                df = archivo.parse(hoja)
                st.markdown(f"#### {titulo_hoja}")
                st.dataframe(df)

            with open(ruta_archivo, "rb") as f:
                st.download_button(
                    "⬇️ Descargar archivo de ejemplo",
                    data=f,
                    file_name=ruta_archivo.split("/")[-1],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Error al cargar el archivo de ejemplo: {e}")


def generar_ejemplo_maximizacion():
    """
    Genera un conjunto de DataFrames de ejemplo para un problema de maximización.

    Returns:
        tuple: (df_modelo, df_restricciones)
    """

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
    """
    Genera un conjunto de DataFrames de ejemplo para un problema de minimización.

    Returns:
        tuple: (df_modelo, df_restricciones)
    """

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

def generar_ejemplo_transporte():
    """
    Genera un DataFrame de ejemplo para un problema de transporte.

    Returns:
        pd.DataFrame: Matriz de transporte con oferta, demanda y costos.
    """

    df_modelo = pd.DataFrame({
        "Origen": ["O1", "O1", "O2", "O2"],
        "Destino": ["D1", "D2", "D1", "D2"],
        "Costo": [5, 8, 4, 3],
        "Oferta": [100, None, 200, None],
        "Demanda": [120, None, None, 180]
    })

    return df_modelo

def exportar_excel(df1, df2, nombre1="modelo", nombre2="restricciones") -> BytesIO:
    """
    Exporta dos DataFrames a un archivo Excel en memoria, con dos hojas separadas.

    Usado para generar archivos de ejemplo que los usuarios pueden descargar.

    Args:
        df1 (pd.DataFrame): Primer DataFrame.
        df2 (pd.DataFrame): Segundo DataFrame.
        nombre1 (str): Nombre de la hoja 1.
        nombre2 (str): Nombre de la hoja 2.

    Returns:
        BytesIO: Objeto en memoria listo para ser descargado como Excel.
    """

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name=nombre1, index=False)
        df2.to_excel(writer, sheet_name=nombre2, index=False)
    output.seek(0)
    return output

def plantilla_modelo(v=2, r=2):
    """
    Genera una plantilla de DataFrame para la carga manual del modelo.

    Args:
        v (int): Número de variables.
        r (int): Número de restricciones.

    Returns:
        pd.DataFrame: Plantilla con columnas para coeficientes de FO y restricciones.
    """

    data = {
        "Variable": [f"X{i+1}" for i in range(v)],
        "Coef_FO": [0] * v
    }
    for j in range(r):
        data[f"Coef_R{j+1}"] = [0] * v

    return pd.DataFrame(data)


def plantilla_restricciones(r=2):
    """
    Genera una plantilla de DataFrame para la carga manual de restricciones.

    Args:
        r (int): Número de restricciones.

    Returns:
        pd.DataFrame: Plantilla con columnas 'Restricción', 'Tipo', 'RHS'.
    """

    return pd.DataFrame({
        "Restriccion": [f"R{i+1}" for i in range(r)],
        "Tipo": ["<="] * r,
        "RHS": [0] * r
    })
    
def validar_datos_manual(df_modelo: pd.DataFrame, df_restricciones: pd.DataFrame):
    """
    Valida que los datos del modelo y restricciones cargados manualmente sean correctos.

    Checks:
    - Columnas esperadas
    - Tipos numéricos
    - Correspondencia entre variables y restricciones

    Args:
        df_modelo (pd.DataFrame): DataFrame con coeficientes de la función objetivo y restricciones.
        df_restricciones (pd.DataFrame): DataFrame con los RHS y operadores.

    Raises:
        ValueError: Si alguna estructura no es válida o hay tipos no numéricos.
    """
    
    if "Variable" not in df_modelo.columns or "Coef_FO" not in df_modelo.columns:
        raise ValueError("🧩 La tabla debe incluir las columnas: 'Variable' y 'Coef_FO'.")

    columnas_restr = [col for col in df_modelo.columns if col.startswith("Coef_R")]
    if not columnas_restr:
        raise ValueError("🧩 Debes incluir al menos una columna de restricciones (Coef_R#).")

    # Imputar valores vacíos con cero
    df_modelo[columnas_restr + ["Coef_FO"]] = df_modelo[columnas_restr + ["Coef_FO"]].fillna(0)

    # Validar tipos numéricos
    for col in columnas_restr + ["Coef_FO"]:
        try:
            df_modelo[col] = pd.to_numeric(df_modelo[col])
        except:
            raise ValueError(f"❌ La columna '{col}' debe contener solo valores numéricos.")

    if df_restricciones is not None:
        if not {"Restriccion", "Tipo", "RHS"}.issubset(df_restricciones.columns):
            raise ValueError("🧩 La tabla de restricciones debe tener las columnas: 'Restriccion', 'Tipo' y 'RHS'.")

        df_restricciones["RHS"] = df_restricciones["RHS"].fillna(0)
        try:
            df_restricciones["RHS"] = pd.to_numeric(df_restricciones["RHS"])
        except:
            raise ValueError("❌ La columna 'RHS' debe contener solo números.")

        if not df_restricciones["Tipo"].isin({"<=", ">=", "="}).all():
            raise ValueError("❌ La columna 'Tipo' debe contener solo: <=, >= o =.")
        
def validar_datos_transporte(df_costos: pd.DataFrame):
    """
    Valida los datos cargados para un problema de transporte.

    Requiere que existan columnas 'Origen', 'Destino', 'Costo', 'Oferta', 'Demanda'
    y que todos los valores necesarios sean numéricos.

    Args:
        df (pd.DataFrame): DataFrame con la matriz de transporte.

    Raises:
        ValueError: Si faltan columnas o hay valores no numéricos.
    """

    columnas = {"Origen", "Destino", "Costo", "Oferta", "Demanda"}
    if not columnas.issubset(df_costos.columns):
        raise ValueError("🧩 Faltan columnas obligatorias: Origen, Destino, Costo, Oferta, Demanda.")

    df_costos["Costo"] = df_costos["Costo"].fillna(0)
    try:
        df_costos["Costo"] = pd.to_numeric(df_costos["Costo"])
    except:
        raise ValueError("❌ La columna 'Costo' debe contener solo números.")

    # Validación general: al menos una oferta por origen y demanda por destino
    if df_costos["Oferta"].notna().sum() == 0:
        raise ValueError("⚠️ Debes indicar al menos una 'Oferta' para cada origen.")
    if df_costos["Demanda"].notna().sum() == 0:
        raise ValueError("⚠️ Debes indicar al menos una 'Demanda' para cada destino.")
    
def validar_datos_asignacion(df: pd.DataFrame):
    """
    Valida una matriz de asignación para el método húngaro.

    La matriz debe ser cuadrada y numérica.

    Args:
        df (pd.DataFrame): Matriz de costos entre agentes y tareas.

    Raises:
        ValueError: Si la matriz no es cuadrada o contiene valores no numéricos.
    """

    if df.shape[0] != df.shape[1]:
        raise ValueError("❌ La matriz debe ser cuadrada.")
    if not all(df.dtypes.apply(lambda t: pd.api.types.is_numeric_dtype(t))):
        raise ValueError("❌ Todos los valores deben ser numéricos.")
    
def exportar_resultado_excel(resultado: dict, datos_entrada: dict = None, grafico_img=None) -> BytesIO:
    """
    Exporta los resultados del modelo a un archivo Excel, incluyendo datos originales y gráfico opcional.

    Crea un archivo con varias hojas:
    - Resumen del resultado
    - Solución o asignaciones
    - Datos de entrada (modelo, restricciones, costos)
    - Imagen del gráfico (si se provee)

    Args:
        resultado (dict): Diccionario con claves como 'status', 'valor_objetivo', 'solucion', etc.
        datos_entrada (dict, optional): Diccionario con DataFrames de entrada.
        grafico_img (BytesIO, optional): Imagen en memoria (PNG) con la visualización gráfica.

    Returns:
        BytesIO: Archivo Excel en memoria listo para ser descargado.
    """

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: resumen del resultado
        resumen = pd.DataFrame({
            "Estado": [resultado.get("status", "")],
            "Valor óptimo": [resultado.get("valor_objetivo", "")]
        })
        resumen.to_excel(writer, sheet_name="Resumen", index=False)

        # Hoja 2: resultados detallados
        if "solucion" in resultado:
            df_sol = pd.DataFrame(resultado["solucion"].items(), columns=["Variable", "Valor"])
            df_sol.to_excel(writer, sheet_name="Solución", index=False)
        elif "asignaciones" in resultado:
            df_asig = pd.DataFrame(resultado["asignaciones"], columns=["Agente", "Tarea"])
            df_asig.to_excel(writer, sheet_name="Asignaciones", index=False)

        # Hoja 3+: datos de entrada (opcional)
        if datos_entrada:
            if "modelo" in datos_entrada:
                datos_entrada["modelo"].to_excel(writer, sheet_name="Entrada - Modelo", index=False)
            if "restricciones" in datos_entrada:
                datos_entrada["restricciones"].to_excel(writer, sheet_name="Entrada - Restricciones", index=False)
            if "costos" in datos_entrada:
                datos_entrada["costos"].to_excel(writer, sheet_name="Entrada - Costos", index=False)

        if grafico_img:
            from openpyxl.drawing.image import Image
            from openpyxl.utils import get_column_letter

            # Acceder al workbook abierto
            ws = writer.book.create_sheet("Gráfico")
            img = Image(grafico_img)
            img.width = 600
            img.height = 400
            ws.add_image(img, "B2")


    output.seek(0)
    return output

def registrar_log(tipo_problema, resultado: dict, datos_entrada: dict, ruta="logs/registro.csv"):
    """
    Registra los datos de una ejecución del modelo en un archivo CSV de historial.

    Cada registro incluye:
    - Fecha y hora
    - Tipo de problema
    - Estado de la solución
    - Valor óptimo
    - Datos de entrada (como JSON)
    - Solución encontrada

    Args:
        tipo_problema (str): Nombre del tipo de modelo resuelto.
        resultado (dict): Resultado del modelo con solución.
        datos_entrada (dict): Diccionario con los DataFrames originales.
        ruta (str): Ruta al archivo CSV donde se acumulan los registros.

    Returns:
        None
    """

    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo_problema,
        "estado": resultado.get("status", ""),
        "valor_objetivo": resultado.get("valor_objetivo", ""),
        "entrada_modelo": "",
        "entrada_restricciones": "",
        "entrada_costos": "",
        "solucion": ""
    }

    if "modelo" in datos_entrada:
        log["entrada_modelo"] = datos_entrada["modelo"].to_json()
    if "restricciones" in datos_entrada:
        log["entrada_restricciones"] = datos_entrada["restricciones"].to_json()
    if "costos" in datos_entrada:
        log["entrada_costos"] = datos_entrada["costos"].to_json()

    if "solucion" in resultado:
        log["solucion"] = pd.Series(resultado["solucion"]).to_json()
    elif "asignaciones" in resultado:
        log["solucion"] = pd.DataFrame(resultado["asignaciones"]).to_json()

    df_log = pd.DataFrame([log])

    # Adjuntar si existe, crear si no
    if os.path.exists(ruta):
        df_existente = pd.read_csv(ruta)
        df_log = pd.concat([df_existente, df_log], ignore_index=True)

    df_log.to_csv(ruta, index=False)






