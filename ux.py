import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA (Identidad Institucional) ---
st.set_page_config(page_title="Portal de Resultados ONPE 2021", layout="wide")

# Estilo CSS para mejorar la estética institucional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 1. TÍTULO INSTITUCIONAL
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/ONPE_Logo.svg/1200px-ONPE_Logo.svg.png", width=200)
st.title("Plataforma Electoral: Resultados Presidenciales 2021")
st.markdown("**Oficina Nacional de Procesos Electorales (ONPE)** | *Información oficial al ciudadano*")
st.divider()

# CARGA DE DATOS
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\carra\Desktop\Curso_emergentes\PC1\Resultados_por_mesa_2021.csv",sep=";", encoding="latin1")
    cols = ["VOTOS_P1", "VOTOS_P2", "VOTOS_VB", "VOTOS_VN", "VOTOS_VI"]
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# 2. USER FLOW: PASO 1 - SELECCIÓN DE REGIÓN (Filtros)
st.sidebar.header("Consulta Ciudadana")
st.sidebar.write("Siga el flujo para consultar resultados:")

departamentos = sorted(df["DEPARTAMENTO"].unique())
region_sel = st.sidebar.selectbox("1. Seleccione su Región:", ["TODO EL PERÚ"] + departamentos)

# Lógica de filtrado
if region_sel == "TODO EL PERÚ":
    df_filtered = df
    alcance = "Nacional"
else:
    df_filtered = df[df["DEPARTAMENTO"] == region_sel]
    alcance = region_sel

# 3. USER FLOW: PASO 2 - VISUALIZACIÓN CLARA DE RESULTADOS
st.subheader(f"Reporte de Resultados: {alcance}")

# Métricas destacadas
v1 = int(df_filtered["VOTOS_P1"].sum())
v2 = int(df_filtered["VOTOS_P2"].sum())
total_v = v1 + v2

m1, m2, m3 = st.columns(3)
m1.metric("Candidato P1", f"{v1:,} votos", f"{ (v1/total_v*100 if total_v > 0 else 0):.2f}%")
m2.metric("Candidato P2", f"{v2:,} votos", f"{ (v2/total_v*100 if total_v > 0 else 0):.2f}%")
m3.metric("Mesas Procesadas", f"{len(df_filtered):,}")

# Gráfico Principal
fig_res = px.bar(
    x=["Candidato P1", "Candidato P2"],
    y=[v1, v2],
    color=["Candidato P1", "Candidato P2"],
    color_discrete_map={"Candidato P1": "#D32F2F", "Candidato P2": "#1976D2"},
    labels={'x': 'Candidato', 'y': 'Total de Votos'},
    title=f"Votación Detallada - {alcance}"
)
st.plotly_chart(fig_res, use_container_width=True)

# 4. USER FLOW: PASO 3 - INTERPRETACIÓN
st.subheader("Interpretación de los Datos")
with st.expander("Haz clic para ver el análisis de transparencia"):
    diferencia = abs(v1 - v2)
    ganador = "P1" if v1 > v2 else "P2"
    
    st.write(f"""
    - En la región **{alcance}**, el candidato con mayor votación es **{ganador}**.
    - La brecha electoral es de **{diferencia:,}** votos entre ambos contendientes.
    - Se registra un total de **{int(df_filtered['VOTOS_VB'].sum()):,}** votos en blanco, lo que representa un dato clave para el análisis de la participación ciudadana.
    """)
    st.info("💡 Este reporte se genera automáticamente a partir de las actas contabilizadas por la ONPE.")

st.divider()
st.caption("© 2021 ONPE - Sistema de Visualización de Resultados Electorales.")

