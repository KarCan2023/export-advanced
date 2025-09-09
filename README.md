# 📤 Avanzados del mes — HubSpot ➜ Siigo (Streamlit)

Pequeña herramienta para **cargar un export de HubSpot** y obtener **solo los contactos que avanzaron en un mes**, usando la columna **"Added To List On"** (o equivalente). Permite **descargar** el resultado en **XLSX** o **CSV** listo para usar en tu flujo con **Siigo**.

## 🚀 Uso local

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py
```

## 🧭 ¿Cómo funciona?
1. **Sube** tu archivo `.xlsx` o `.csv` exportado desde HubSpot.
2. La app detecta la columna de fecha para *avanzados* (p. ej. **Added To List On**). Si hay varias, puedes **elegir**.
3. Selecciona la **zona horaria** (por defecto *America/Bogota*) y el **mes** (por defecto, el **último mes completo**).
4. El sistema **filtra** las filas cuya fecha cae dentro del mes seleccionado.
5. **Quita duplicados** por la clave que elijas (recomendado: *ID de registro - Contact* o *Correo*).
6. **Elige** las columnas a exportar.
7. **Descarga** el resultado en **XLSX** o **CSV**.

## 🧱 Soporte de encabezados en español
- La detección de la columna funciona con variantes comunes (**Added To List On**, *Añadido a la lista*, etc.).
- Si tu export trae la columna repetida (p. ej. `Added To List On` y `Added To List On.1`), puedes **seleccionar** la correcta.

## 🕒 Zonas horarias
- Las fechas se **convierten o localizan** a la zona seleccionada antes de aplicar el filtro mensual.
- Si tu archivo usa **seriales de Excel**, se convierten automáticamente.

## 📦 Estructura
```
siigo_hs_avanzados/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
└── sample_data/
    └── hs_export_ejemplo.xlsx
```

## ☁️ Despliegue rápido (Streamlit Community Cloud)
1. Sube este proyecto a **GitHub**.
2. Entra a **share.streamlit.io** y conéctalo a tu repo.
3. *Main file path*: `app.py` — *Python version*: 3.10+
4. La app se construye e inicia sola.

## ✅ Buenas prácticas
- Mantén el nombre de la columna **Added To List On** en tu export de HubSpot para una detección más confiable.
- Revisa la **zona horaria** y el **mes** antes de exportar.
- Si quieres un formato especial para Siigo, ajusta la selección de columnas desde la app.

---

Hecho para un flujo mensual **simple, estable y auditable**. Cualquier mejora/ajuste, abre un issue o edita `app.py`.
