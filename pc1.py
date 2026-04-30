import streamlit as st
import pandas as pd
#import plotly.express as px

st.title("Resultados Electorales ONPE 2021")

# PARTE 2: Cargar dataset
df = pd.read_csv(r"C:\Users\carra\Desktop\Curso_emergentes\PC1\Resultados_por_mesa_2021.csv",sep=";", encoding="latin1")

st.subheader("Vista inicial del dataset")
st.dataframe(df.head())

st.subheader("Información general")

numero_mesas = df["MESA_DE_VOTACION"].nunique()
st.write("Número de mesas:", numero_mesas)

st.write("Columnas del dataset:")
st.write(df.columns.tolist())

# Limpieza básica
columnas_votos = ["VOTOS_P1", "VOTOS_P2", "VOTOS_VB", "VOTOS_VN", "VOTOS_VI"]

for col in columnas_votos:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

st.subheader("Datos limpiados")
st.write("Valores nulos reemplazados por 0 en columnas de votos.")

# Totales
total_p1 = df["VOTOS_P1"].sum()
total_p2 = df["VOTOS_P2"].sum()
total_blancos = df["VOTOS_VB"].sum()
total_nulos = df["VOTOS_VN"].sum()
total_impugnados = df["VOTOS_VI"].sum()

st.subheader("Resumen de votos")
st.write("Votos candidato P1:", int(total_p1))
st.write("Votos candidato P2:", int(total_p2))
st.write("Votos en blanco:", int(total_blancos))
st.write("Votos nulos:", int(total_nulos))
st.write("Votos impugnados:", int(total_impugnados))

# PARTE 3: Visualizaciones
st.subheader("Votos por candidato")

votos_candidatos = pd.DataFrame({
    "Candidato": ["P1", "P2"],
    "Votos": [total_p1, total_p2]
})

st.bar_chart(votos_candidatos.set_index("Candidato"))

st.subheader("Distribución de votos por región")

region = df.groupby("DEPARTAMENTO")[["VOTOS_P1", "VOTOS_P2"]].sum()
st.bar_chart(region)

st.subheader("Filtro por departamento")

departamentos = sorted(df["DEPARTAMENTO"].dropna().unique())
departamento_seleccionado = st.selectbox("Seleccione un departamento", departamentos)

df_filtrado = df[df["DEPARTAMENTO"] == departamento_seleccionado]

st.write("Resultados para:", departamento_seleccionado)
st.dataframe(df_filtrado.head())

resumen_dep = df_filtrado[["VOTOS_P1", "VOTOS_P2", "VOTOS_VB", "VOTOS_VN"]].sum()
st.bar_chart(resumen_dep)

