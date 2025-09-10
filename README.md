# 📤 Avanzados del mes — HubSpot ➜ Siigo (Streamlit)

Pequeña herramienta para **cargar un export de HubSpot** y obtener **solo los contactos que avanzaron** en el **periodo** elegido, usando la columna **“Added To List On”** (o equivalente). Descarga el resultado en **XLSX** o **CSV**.

## ☁️ Despliegue en Streamlit Cloud (con GitHub)
1. Crea un repositorio en **GitHub** (por ejemplo `siigo_hs_avanzados`) y sube estos archivos:
   - `app.py`
   - `requirements.txt`
   - `runtime.txt`  ← fija Python **3.10**
   - `README.md`
   - `.streamlit/config.toml`
   - (Opcional) `sample_data/hs_export_ejemplo.xlsx`

2. Ve a **streamlit.io** → **Deploy app** → Conecta tu cuenta de GitHub y selecciona el repo.
   - **Main file path**: `app.py`
   - **Branch**: `main` (o el que uses)
   - **Python version**: **3.10** (en *App Settings → Advanced → Python version* o usando `runtime.txt`)
   - **Secrets**: no se requieren para este flujo.

3. Pulsa **Deploy**. La app quedará accesible desde una URL pública.

> Cada mes, entra a la app, sube el export de HubSpot y descarga el archivo filtrado para ese periodo.

## 🧭 ¿Cómo funciona?
1. **Subes** tu archivo `.xlsx` o `.csv` exportado desde HubSpot.
2. La app detecta la columna de fecha para *avanzados* (p. ej. **Added To List On**). Si hay varias, puedes **elegir**.
3. Seleccionas la **zona horaria** (por defecto *America/Bogota*) y el **periodo**:
   - **Mes único** (por defecto: el **último mes completo**).
   - **Últimos 2 meses** (meses completos, sin incluir el mes en curso).
   - **Últimos 3 meses** (meses completos, sin incluir el mes en curso).
4. El sistema **filtra** las filas cuya fecha cae dentro del periodo seleccionado.
5. **Quita duplicados** por la clave que elijas (recomendado: *ID de registro - Contact* o *Correo*).
6. **Eliges** las columnas a exportar.
7. **Descargas** el resultado en **XLSX** o **CSV**.

## 🧱 Soporte de encabezados en español
- La detección de la columna funciona con variantes comunes (**Added To List On**, *Añadido a la lista*, etc.).
- Si tu export trae la columna repetida (p. ej. `Added To List On` y `Added To List On.1`), puedes **seleccionar** la correcta.

## 🕒 Zonas horarias
- Las fechas se **convierten o localizan** a la zona seleccionada antes de aplicar el filtro.
- Si tu archivo usa **seriales de Excel**, se convierten automáticamente.

## 📦 Estructura
```
siigo_hs_avanzados/
├── app.py
├── requirements.txt
├── runtime.txt
├── README.md
├── .streamlit/
│   └── config.toml
└── sample_data/
    └── hs_export_ejemplo.xlsx
```

## ✅ Buenas prácticas
- Mantén el nombre de la columna **Added To List On** en tu export de HubSpot para una detección más confiable.
- Revisa la **zona horaria** y el **periodo** antes de exportar.
- Si quieres un formato especial para Siigo, ajusta la selección de columnas desde la app.

---

Hecho para un flujo mensual **simple, estable y auditable**.
