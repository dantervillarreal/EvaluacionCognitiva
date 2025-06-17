import streamlit as st
import pandas as pd
from datetime import datetime
import os
import csv

# Archivo de resultados
archivo_resultados = "resultados.csv"

# Función para calcular z-score
def calcular_estandarizado(edad, puntaje_bruto, df_referencia):
    ref = df_referencia[df_referencia["Edad"] == edad]
    if not ref.empty:
        media = ref["Media"].values[0]
        desv = ref["DesviacionEstandar"].values[0]
        if desv != 0:
            return round((puntaje_bruto - media) / desv, 2)
    return None

# Archivos de referencia por prueba
archivos = {
    "Recuerdo Lógico Inmediato": "RecuerdoLogicoInmediato.csv",
    "Recuerdo Lógico Diferido": "RecuerdoLogicoDiferido.csv",
    "Aprendizaje Serial": "AprendizajeSerial.csv",
    "Rec. Clave Semántica": "RecConClaveSemantica.csv",
    "Recuerdo Serial": "RecuerdoSerial.csv",
    "Reconocimiento": "Reconocimiento.csv"
}

# Cargar CSVs
referencias = {}
error = False
for nombre_prueba, archivo_csv in archivos.items():
    try:
        df = pd.read_csv(archivo_csv)
        df.columns = df.columns.str.strip()
        referencias[nombre_prueba] = df
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo: `{archivo_csv}`")
        error = True
if error:
    st.stop()

# ---------------------
# 🧍 Datos del paciente
# ---------------------
st.title("🧠 Evaluación Cognitiva - Puntajes Estandarizados")

st.subheader("🧍 Datos del paciente")
with st.form("formulario_paciente"):
    col1, col2 = st.columns([2, 1])
    with col1:
        nombre = st.text_input("Nombre")
    with col2:
        edad = st.number_input("Edad", min_value=1, max_value=120, step=1)

    st.divider()

    # ---------------------
    # 📝 Puntajes brutos
    # ---------------------
    st.subheader("📝 Puntajes brutos por prueba")
    # Orden fijo y correcto para todas las plataformas
    nombres_pruebas = [
        "Recuerdo Lógico Inmediato",
        "Recuerdo Lógico Diferido",
        "Aprendizaje Serial",
        "Recuerdo Serial",
        "Rec. Clave Semántica",
        "Reconocimiento"
    ]
    puntajes_brutos = {}
    for i in range(0, len(nombres_pruebas), 2):
        col1, col2 = st.columns(2)
        with col1:
            prueba1 = nombres_pruebas[i]
            puntajes_brutos[prueba1] = st.number_input(prueba1, format="%.2f", key=f"bruto_{prueba1}")
        if i + 1 < len(nombres_pruebas):
            with col2:
                prueba2 = nombres_pruebas[i + 1]
                puntajes_brutos[prueba2] = st.number_input(prueba2, format="%.2f", key=f"bruto_{prueba2}")

    st.divider()
    submit = st.form_submit_button("✅ Calcular y guardar resultados")

# ---------------------
# 📊 Resultados
# ---------------------
if submit:
    resultados = {}
    for nombre_prueba, df_ref in referencias.items():
        bruto = puntajes_brutos[nombre_prueba]
        z = calcular_estandarizado(edad, bruto, df_ref)
        resultados[nombre_prueba] = z

    st.subheader("📊 Puntajes estandarizados")
    col1, col2 = st.columns(2)
    for i, (prueba, z) in enumerate(resultados.items()):
        col = col1 if i % 2 == 0 else col2
        with col:
            if z is not None:
                st.metric(label=prueba, value=f"{z:.2f}")
            else:
                st.warning(f"{prueba}: sin datos para esta edad")

    # Guardar resultado
    registro = {
        "Nombre": nombre,
        "Edad": edad,
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    for nombre_prueba in archivos.keys():
        registro[f"{nombre_prueba} - Bruto"] = puntajes_brutos[nombre_prueba]
        registro[f"{nombre_prueba} - Z"] = resultados[nombre_prueba]

    df_resultados = pd.DataFrame([registro])
    if os.path.exists(archivo_resultados):
        df_resultados.to_csv(archivo_resultados, mode='a', header=False, index=False, quoting=csv.QUOTE_MINIMAL)
    else:
        df_resultados.to_csv(archivo_resultados, mode='w', header=True, index=False, quoting=csv.QUOTE_MINIMAL)

    st.success("✅ Resultados guardados correctamente.")

# ---------------------
# 📋 Historial
# ---------------------
if os.path.exists(archivo_resultados):
    st.divider()
    with st.expander("📋 Ver historial de cálculos anteriores"):
        historial = pd.read_csv(archivo_resultados)
        st.dataframe(historial, use_container_width=True)
        st.download_button("⬇️ Descargar historial CSV", data=historial.to_csv(index=False), file_name="resultados.csv", mime="text/csv")
