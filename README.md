# Optimizador Visual de Recursos

**Versión inicial del proyecto | En desarrollo 🚧**

---

## 📌 Descripción

Este proyecto es una aplicación interactiva construida con **Python y Streamlit** que permite resolver problemas clásicos de **optimización lineal** de forma visual e intuitiva. Está diseñado para facilitar la carga de datos desde archivos Excel o formularios, ejecutar distintos tipos de modelos de optimización, y visualizar los resultados de manera clara y comprensible.

### Problemas que se pueden resolver:

- ✅ **Maximización** de beneficios o utilidades
- ✅ **Minimización** de costos o tiempos
- ✅ **Problemas de transporte** (asignación óptima de rutas, costos logísticos)
- ✅ **Problemas de asignación** (método húngaro)

---

## 🧮 Tecnologías utilizadas

- Python 3.10+
- [Streamlit](https://streamlit.io/) – Interfaz visual
- [PuLP](https://coin-or.github.io/pulp/) – Optimización lineal
- Pandas, NumPy – Manejo de datos
- Matplotlib / Plotly – Visualizaciones
- OpenPyXL / XlsxWriter – Lectura y escritura de Excel

---

## 🏁 Cómo ejecutar el proyecto

1. Clona el repositorio:

```bash
git clone https://github.com/tu_usuario/optimizador-visual.git
cd optimizador-visual
```

2. Crea y activa un entorno virtual:

```bash
python -m venv .venv
# Activación:
# En Windows:
.venv\Scripts\activate
# En Mac/Linux:
source .venv/bin/activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecuta la aplicación:

```bash
streamlit run app.py
```

## 📂 Estructura del proyecto

```bash
optimizador-visual/
│
├── app.py                   # Punto de entrada de Streamlit
├── requirements.txt         # Librerías necesarias
├── README.md
├── .gitignore
│
├── main/                    # Lógica del modelo
│   ├── modelo.py
│   ├── visualizacion.py
│   └── utils.py
│
├── data/                    # Datos de entrada y salida
│   └── resultados/
│
├── tests/                   # Pruebas unitarias
├── assets/                  # Recursos visuales (logos, CSS)
└── .streamlit/              # Configuración de la app
```
## 📌 Estado actual
### 🔧 En desarrollo – módulo de maximización listo en versión preliminar.
### 🚀 Próximamente: módulos de transporte y asignación con visualización dinámica.

## 📄 Licencia
Este proyecto es de código abierto y se publica bajo licencia MIT.

## 🤝 Autor
### ![GitHub](https:github.com/ramonguerraa)
### 📧 Contacto: ![Mail](ramonguerraa@gmail.com)

