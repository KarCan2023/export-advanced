
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import unicodedata
from datetime import datetime
import pandas as pd
import streamlit as st
import pytz
from dateutil.relativedelta import relativedelta

def normalize(s: str) -> str:
    s = str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return " ".join(s.strip().lower().replace("_", " ").split())

def guess_added_cols(cols):
    cands = []
    for c in cols:
        n = normalize(c)
        if ("added" in n and "list" in n and ("on" in n or "fecha" in n)) or ("anad" in n and "lista" in n):
            cands.append(c)
        if n in {"added to list on", "added to list", "fecha agregado a lista", "fecha de agregado a lista"}:
            cands.append(c)
    # keep order but unique
    seen = set()
    out = []
    for c in cands:
        if c not in seen:
            out.append(c); seen.add(c)
    return out

def excel_serial_to_datetime(series: pd.Series) -> pd.Series:
    base = pd.Timestamp("1899-12-30")
    return base + pd.to_timedelta(series, unit="D")

def parse_datetime_col(series: pd.Series, tz_name: str) -> pd.Series:
    s = series.copy()
    if pd.api.types.is_numeric_dtype(s):
        dt = excel_serial_to_datetime(s)
    else:
        dt = pd.to_datetime(s, errors="coerce", dayfirst=True, infer_datetime_format=True)
    tz = pytz.timezone(tz_name)
    if hasattr(dt, "dt"):
        try:
            if dt.dt.tz is None:
                dt = dt.dt.tz_localize(tz, nonexistent="shift_forward", ambiguous="NaT")
            else:
                dt = dt.dt.tz_convert(tz)
        except Exception:
            dt = pd.to_datetime(s.astype(str), errors="coerce", dayfirst=True)
            dt = dt.dt.tz_localize(tz, nonexistent="shift_forward", ambiguous="NaT")
    return dt

def filter_range(df: pd.DataFrame, date_col: str, start, end, tz_name: str):
    dt = parse_datetime_col(df[date_col], tz_name)
    mask = (dt >= start) & (dt < end)
    return df.loc[mask].copy(), dt

st.set_page_config(page_title="Siigo • Avanzados por mes (HubSpot)", page_icon="📤", layout="wide")
st.title("📤 Avanzados del mes — HubSpot ➜ Siigo")
st.caption("Sube tu export de HubSpot y obtén solo los contactos que **avanzaron** (columna *Added To List On*) en el **periodo** seleccionado.")

uploaded = st.file_uploader("Archivo **.xlsx** o **.csv** exportado de HubSpot", type=["xlsx", "csv"])

tz_name = st.selectbox("Zona horaria", ["America/Bogota", "UTC"], index=0)

# Defaults: último mes completo
now = datetime.now(pytz.timezone(tz_name))
last_full_month_first = (now.replace(day=1) - relativedelta(months=1))

period_mode = st.radio("Periodo", ["Mes único", "Últimos 2 meses", "Últimos 3 meses"], index=0, horizontal=True)

if period_mode == "Mes único":
    year = st.number_input("Año", min_value=2018, max_value=2100, value=last_full_month_first.year, step=1)
    meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    month_idx = last_full_month_first.month - 1
    month = st.selectbox("Mes", list(range(1,13)), index=month_idx, format_func=lambda i: meses[i-1])
    start = pd.Timestamp(year=int(year), month=int(month), day=1, tz=tz_name)
    end = start + relativedelta(months=1)
else:
    months_back = 2 if "2" in period_mode else 3
    # últimos N meses completos (si hoy es 2025-09, N=2 => 2025-07..2025-08)
    start = last_full_month_first - relativedelta(months=months_back-1)
    end = last_full_month_first + relativedelta(months=1)

if uploaded is not None:
    # Cargar dataframe
    try:
        if uploaded.name.lower().endswith(".xlsx"):
            df = pd.read_excel(uploaded, dtype=str, engine="openpyxl")
        else:
            df = pd.read_csv(uploaded, dtype=str, encoding="utf-8")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    st.success(f"Archivo cargado: **{uploaded.name}** — Filas: **{len(df)}** — Columnas: **{len(df.columns)}**")
    with st.expander("Vista previa (primeras 50 filas)"):
        st.dataframe(df.head(50), use_container_width=True)

    # Detectar columna de fecha
    candidates = guess_added_cols(df.columns)
    if not candidates:
        candidates = [c for c in df.columns if "added" in normalize(c) and "list" in normalize(c)]
        if not candidates:
            candidates = list(df.columns)

    date_col = st.selectbox("Columna de fecha para **Avanzados**", candidates, index=0)

    # Clave para deduplicar
    def_cols = []
    for c in df.columns:
        n = normalize(c)
        if ("id" in n and "contact" in n) or ("id de registro - contact" in n):
            def_cols.append(c)
        if "correo" in n or "email" in n:
            def_cols.append(c)
    dedup_col = st.selectbox("Eliminar duplicados por", def_cols if def_cols else list(df.columns), index=0 if def_cols else 0)

    # Filtrar por rango
    filtered, dt_series = filter_range(df, date_col, start, end, tz_name)

    # Insertar columnas de auditoría al inicio
    if not filtered.empty:
        parsed_col = f"{date_col} (parsed)"
        month_col = "Mes (YYYY-MM)"
        filtered.insert(0, month_col, dt_series.loc[filtered.index].dt.strftime("%Y-%m"))
        filtered.insert(0, parsed_col, dt_series.loc[filtered.index].dt.strftime("%Y-%m-%d %H:%M:%S %Z"))

    # Deduplicar conservando el más reciente
    if not filtered.empty and dedup_col in filtered.columns:
        filtered = filtered.sort_values(by=filtered.columns[0], ascending=False).drop_duplicates(subset=[dedup_col])

    total = len(filtered)
    label_start = start.strftime("%Y-%m")
    label_end = (end - relativedelta(days=1)).strftime("%Y-%m")
    periodo_text = f"{label_start}" if period_mode == "Mes único" else f"{label_start} a {label_end}"
    st.metric("Total filtrados", total, help=f"Periodo: {periodo_text}")

    # Selección de columnas a exportar
    default_export = []
    prefer = [
        "ID de registro - Contact","Nombre","Apellidos","Correo","Número de teléfono",
        "ID de registro - Company","Nombre de la empresa","Ciudad","País/región","Sector",
        date_col,"Mes (YYYY-MM)"
    ]
    for p in prefer:
        if p in filtered.columns and p not in default_export:
            default_export.append(p)
    if filtered.columns[0] not in default_export:
        default_export = [filtered.columns[0]] + default_export

    export_cols = st.multiselect("Columnas a exportar", list(filtered.columns), default=default_export)

    out = filtered[export_cols] if export_cols else filtered

    with st.expander("Muestra del resultado (hasta 100 filas)"):
        st.dataframe(out.head(100), use_container_width=True)

    # Botones de descarga
    if period_mode == "Mes único":
        fname_base = f"avanzados_{label_start}"
    else:
        fname_base = f"avanzados_{label_start}_a_{label_end}"

    buf_xlsx = io.BytesIO()
    with pd.ExcelWriter(buf_xlsx, engine="openpyxl") as writer:
        out.to_excel(writer, index=False)
    st.download_button("⬇️ Descargar **XLSX**", data=buf_xlsx.getvalue(),
                       file_name=f"{fname_base}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    csv_bytes = out.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar **CSV (UTF-8)**", data=csv_bytes,
                       file_name=f"{fname_base}.csv", mime="text/csv")

    info_text = "Se filtran fechas desde **el 1** hasta antes del **1 del mes siguiente** del periodo seleccionado."
    if period_mode != "Mes único":
        info_text += " Modo: últimos meses **completos** (no incluye el mes en curso)."
    st.info(info_text)
else:
    st.warning("Sube un archivo para continuar.")
