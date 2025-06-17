import streamlit as st
import pandas as pd
from datetime import datetime
import os

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
st.title("🧠 Calculadora de Puntaje Estandarizado con Historial")

# Cargar todas las referencias
archivos = {
    "Puntaje General": "referencias.csv",
    "Aprendizaje Serial": "AprendizajeSerial.csv",
    "Rec. Clave Semántica": "RecConClaveSemantica.csv",
    "Recuerdo Serial": "RecuerdoSerial.csv"
}

referencias = {}
error = False

for nombre, archivo in archivos.items():
    try:
        referencias[nombre] = pd.read_csv(archivo)
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo: `{archivo}`")
        error = True

if error:
    st.stop()

# Formulario de ingreso
with st.form("formulario_paciente"):
    nombre = st.text_input("Nombre del paciente")
    edad = st.number_input("Edad del paciente", min_value=1, max_value=120, step=1)
    puntaje_bruto = st.number_input("Puntaje bruto", format="%.2f")
    submit = st.form_submit_button("Calcular y guardar")

if submit:
    # Calcular resultados
    resultados = {}
    for nombre_prueba, df in referencias.items():
        resultado = calcular_estandarizado(edad, puntaje_bruto, df)
        resultados[nombre_prueba] = resultado

    # Mostrar resultados
    st.subheader(f"🧾 Resultados para {nombre} (edad {edad}):")
    for prueba, resultado in resultados.items():
        if resultado is not None:
            st.markdown(f"**{prueba}**: {resultado}")
        else:
            st.markdown(f"**{prueba}**: ⚠️ No hay referencia o la desviación es 0")

    # Guardar en CSV
    registro = {
        "Nombre": nombre,
        "Edad": edad,
        "Puntaje Bruto": puntaje_bruto,
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    registro.update(resultados)

    archivo_resultados = "resultados.csv"
    existe = os.path.isfile(archivo_resultados)

    df_resultados = pd.DataFrame([registro])

    if existe:
        df_resultados.to_csv(archivo_resultados, mode='a', header=False, index=False)
    else:
        df_resultados.to_csv(archivo_resultados, mode='w', header=True, index=False)

    st.success("✅ Resultados guardados en `resultados.csv`")

    # Mostrar historial guardado
if os.path.exists(archivo_resultados):
    st.subheader("📋 Historial de cálculos anteriores")
    historial = pd.read_csv(archivo_resultados)
    st.dataframe(historial)

