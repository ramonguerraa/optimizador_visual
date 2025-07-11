# 🧠 Optimizador Visual Interactivo

Una aplicación construida con **Python** y **Streamlit** para resolver y visualizar problemas de:

- 🔼 **Maximización**
- 🔽 **Minimización**
- 🚚 **Problemas de Transporte**
- 🧮 **Asignación de Recursos** (Método Húngaro)

---

## 🎯 Funcionalidades

- ✅ Carga de datos por archivo Excel o ingreso manual
- ✅ Visualización gráfica para modelos de 2 variables
- ✅ Exportación de resultados a Excel (con gráficos)
- ✅ Registro automático de todas las ejecuciones
- ✅ Historial navegable y filtrable desde la app

---

## 🛠️ Requisitos

Instala los paquetes necesarios con:

```bash
pip install -r requirements.txt
```
Requiere Python 3.11 o superior.

## 🚀 Uso
Ejecutá la app desde la raíz del proyecto:

```bash
streamlit run app.py
```
## 📁 Estructura del proyecto

```bash
optimizador_visual/
├── app.py
├── main/
│   ├── __init__.py
│   ├── problemas.py
│   ├── utils.py
│   ├── interfaz.py
│   └── visualizacion.py
├── data/
│   ├── ejemplo_maximizacion.xlsx
│   ├── ejemplo_minimizacion.xlsx
│   ├── ejemplo_transporte.xlsx
│   └── ejemplo_asignacion.xlsx
├── logs/
│   └── registro.csv
├── requirements.txt
└── README.md
```

## 🧪 Testing
Usamos pytest para pruebas unitarias. Ejecuta:

```bash
pytest tests/ --import-mode=importlib
```


## 📄 Licencia
Este proyecto es de código abierto y se publica bajo licencia MIT.

## 🤝 Autor
### ![GitHub](https:github.com/ramonguerraa)
### 📧 Contacto: ![Mail](ramonguerraa@gmail.com)

