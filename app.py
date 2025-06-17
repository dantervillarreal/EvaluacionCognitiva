import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Archivo donde se guarda el historial
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

# Título
st.title("🧠 Evaluación Cognitiva - Múltiples Pruebas")

# Archivos de referencia (1 por prueba)
archivos = {
    "Recuerdo Logico Inmediato": "RecuerdoLogicoInmediato.csv",
    "Recuerdo Logico Diferido": "RecuerdoLogicoDiferido.csv",
    "Aprendizaje Serial": "AprendizajeSerial.csv",
    "Rec. Clave Semántica": "RecConClaveSemantica.csv",
    "Recuerdo Serial": "RecuerdoSerial.csv",
    "Reconocimiento": "Reconocimiento.csv"
}

# Cargar referencias
referencias = {}
error = False

for nombre_prueba, archivo_csv in archivos.items():
    try:
        referencias[nombre_prueba] = pd.read_csv(archivo_csv)
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo: `{archivo_csv}`")
        error = True

if error:
    st.stop()

# Formulario de ingreso
with st.form("formulario_paciente"):
    nombre = st.text_input("Nombre del paciente")
    edad = st.number_input("Edad del paciente", min_value=1, max_value=120, step=1)

    puntajes_brutos = {}
    for nombre_prueba in archivos.keys():
        puntajes_brutos[nombre_prueba] = st.number_input(
            f"Puntaje bruto - {nombre_prueba}",
            format="%.2f"
        )

    submit = st.form_submit_button("Calcular y guardar")

# Procesamiento
if submit:
    st.subheader(f"🧾 Resultados para {nombre} (edad {edad}):")

    resultados = {}
    for nombre_prueba, df_ref in referencias.items():
        bruto = puntajes_brutos[nombre_prueba]
        resultado = calcular_estandarizado(edad, bruto, df_ref)
        resultados[nombre_prueba] = resultado
        if resultado is not None:
            st.markdown(f"**{nombre_prueba}**: {resultado}")
        else:
            st.markdown(f"**{nombre_prueba}**: ⚠️ No hay referencia o desviación 0")

    # Guardar resultados
    registro = {
        "Nombre": nombre,
        "Edad": edad,
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Guardar todos los puntajes brutos y estandarizados
    for nombre_prueba in archivos.keys():
        registro[f"{nombre_prueba} - Bruto"] = puntajes_brutos[nombre_prueba]
        registro[f"{nombre_prueba} - Z"] = resultados[nombre_prueba]

    df_resultados = pd.DataFrame([registro])

    if os.path.exists(archivo_resultados):
        df_resultados.to_csv(archivo_resultados, mode='a', header=False, index=False)
    else:
        df_resultados.to_csv(archivo_resultados, mode='w', header=True, index=False)

    st.success("✅ Resultados guardados correctamente.")

# Mostrar historial si existe
if os.path.exists(archivo_resultados):
    st.subheader("📋 Historial de cálculos anteriores")
    # historial = pd.read_csv(archivo_resultados)
    # st.dataframe(historial)
    try:
        historial = pd.read_csv(archivo_resultados)
        st.subheader("📋 Historial de cálculos anteriores")
        st.dataframe(historial)
    except pd.errors.ParserError:
        st.error("⚠️ El archivo resultados.csv está corrupto o mal formateado. Abrilo manualmente y revisá las filas.")
else:
    st.info("No hay historial guardado todavía.")
