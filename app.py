import streamlit as st
import os
import pandas as pd
from main.problemas import Maximizacion, Minimizacion, Transporte, Asignacion
from main.utils import mostrar_ejemplo_excel
from main.interfaz import manejar_carga_desde_excel, manejar_carga_manual
from PIL import Image

def cargar_estilos():
    with open("assets/estilos.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def mostrar_logo():
    logo_path = "assets/logo.png"
    logo = Image.open(logo_path)
    st.sidebar.image(logo, width=250)

cargar_estilos()

mostrar_logo()

# -----------------------------
# Configuración de la app
# -----------------------------
st.set_page_config(page_title="Optimizador Visual", layout="wide")

# -----------------------------
# Encabezado
# -----------------------------
st.title("📊 Optimizador Visual de Recursos")
st.markdown("Aplicación interactiva para resolver y visualizar modelos de optimización lineal, transporte y asignación de recursos.")

# -----------------------------
# Menú lateral de navegación
# -----------------------------
opcion = st.sidebar.selectbox(
    "Selecciona el tipo de problema a resolver:",
    [
        "Maximización",
        "Minimización",
        "Problema de Transporte",
        "Problema de Asignación",
        "📜 Historial de ejecuciones"
    ]
)

if opcion == "📜 Historial de ejecuciones":
    st.subheader("📜 Historial de ejecuciones anteriores")

    ruta_log = "logs/registro.csv"

    if not os.path.exists(ruta_log):
        st.info("Aún no hay registros guardados.")
    else:
        df_log = pd.read_csv(ruta_log)

        # Opcional: mostrar filtros
        with st.expander("🔍 Filtros avanzados"):
            tipos = df_log["tipo"].unique().tolist()
            tipo_seleccionado = st.selectbox("Filtrar por tipo de problema", ["Todos"] + tipos)
            fecha_busqueda = st.date_input("Filtrar por fecha (opcional)", value=None)

        # Aplicar filtros
        if tipo_seleccionado != "Todos":
            df_log = df_log[df_log["tipo"] == tipo_seleccionado]

        if fecha_busqueda:
            df_log = df_log[df_log["timestamp"].str.contains(str(fecha_busqueda))]

        st.dataframe(df_log.sort_values(by="timestamp", ascending=False))

        # Mostrar JSON de un registro
        st.markdown("### 📋 Ver detalles de un registro")
        idx = st.number_input("Selecciona índice del registro", min_value=0, max_value=len(df_log)-1, step=1)
        st.json(df_log.iloc[idx].to_dict())

# Diccionario central de configuración por tipo de problema
config_problemas = {
    "Maximización": {
        "clase": Maximizacion,
        "archivo_ejemplo": "data/ejemplo_maximizacion.xlsx",
        "hojas": {"modelo": "Hoja 1: modelo", "restricciones": "Hoja 2: restricciones"},
        "nombre_modelo": "Maximización"
    },
    "Minimización": {
        "clase": Minimizacion,
        "archivo_ejemplo": "data/ejemplo_minimizacion.xlsx",
        "hojas": {"modelo": "Hoja 1: modelo", "restricciones": "Hoja 2: restricciones"},
        "nombre_modelo": "Minimización"
    },
    "Problema de Transporte": {
        "clase": Transporte,
        "archivo_ejemplo": "data/ejemplo_transporte.xlsx",
        "hojas": {"costos": "Matriz de costos y capacidades"},
        "nombre_modelo": "Transporte"
    },
    "Problema de Asignación de Recursos": {
    "clase": Asignacion,
    "archivo_ejemplo": "data/ejemplo_asignacion.xlsx",
    "hojas": {"costos": "Matriz de costos de asignación"},
    "nombre_modelo": "Asignación"
    }
}

# Datos de la selección actual
conf = config_problemas[opcion]

# Subtítulo dinámico
st.subheader(f"🔧 Resolución de {opcion}")

# Visualización de ejemplo estructural (formato esperado)
mostrar_ejemplo_excel(
    ruta_archivo=conf["archivo_ejemplo"],
    hojas=conf["hojas"],
    titulo="Ejemplo de estructura de archivo Excel"
)

# Elegir modo de carga
tipo_carga = st.radio("¿Cómo deseas cargar los datos?", ["Desde archivo Excel", "Ingreso manual"])

# Cargar desde archivo Excel
if tipo_carga == "Desde archivo Excel":
    manejar_carga_desde_excel(
        nombre_archivo=conf["nombre_modelo"],
        clase_problema=conf["clase"],
        hojas=conf["hojas"],
        nombre_hoja_modelo="costos" if opcion == "Problema de Transporte" else "modelo",
        nombre_hoja_restricciones=None if opcion == "Problema de Transporte" else "restricciones",
        nombre_modelo=conf["nombre_modelo"]
    )

# Carga manual
elif tipo_carga == "Ingreso manual":
    manejar_carga_manual(conf["nombre_modelo"], conf["clase"])

