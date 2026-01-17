# GORE_OS Model Viewer

Visor interactivo para explorar el modelo de datos de User Stories.

## Instalación

```bash
cd visor_model
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

## Funcionalidades

- **📋 User Stories**: Navegar y filtrar las 818 US por dominio, prioridad, búsqueda
- **👤 Roles**: Explorar los 297 roles y ver qué US los usan
- **📦 Entidades**: Buscar entidades y ver en qué US aparecen
- **⚙️ Procesos**: Navegar los 289 procesos y sus referencias
- **🏷️ Tags**: Explorar los 2002 tags y su distribución

## Requisitos

- Python 3.9+
- El archivo `us_model_complete.yml` debe existir (ejecutar primero el ETL)
