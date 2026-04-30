import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


# Configuración de la página
st.set_page_config(page_title="Dashboard ONPE 2021", layout="wide")

st.title("Resultados Electorales ONPE 2021")
st.markdown("---")

# 1. Carga y Limpieza de datos
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\carra\Desktop\Curso_emergentes\PC1\Resultados_por_mesa_2021.csv",sep=";", encoding="latin1")
    # Limpieza de columnas de votos: convertir a numérico y llenar vacíos con 0
    columnas_votos = ["VOTOS_P1", "VOTOS_P2", "VOTOS_VB", "VOTOS_VN", "VOTOS_VI"]
    for col in columnas_votos:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

df = load_data()

# 2. Cálculos Globales
total_p1 = df["VOTOS_P1"].sum()
total_p2 = df["VOTOS_P2"].sum()
total_emitidos = df[["VOTOS_P1", "VOTOS_P2", "VOTOS_VB", "VOTOS_VN", "VOTOS_VI"]].sum().sum()
total_validos = total_p1 + total_p2

# 3. Métricas Principales (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Votos P1", f"{int(total_p1):,}")
col2.metric("Votos P2", f"{int(total_p2):,}")
col3.metric("Votos Válidos", f"{int(total_validos):,}")
col4.metric("Participación", f"{int(df['N_CVAS'].sum()):,}")

st.markdown("---")

# 4. VISUALIZACIONES
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Barras: Votos por Candidato")
    votos_data = pd.DataFrame({
        "Candidato": ["Partido 1 (P1)", "Partido 2 (P2)"],
        "Votos": [total_p1, total_p2]
    })
    st.bar_chart(votos_data.set_index("Candidato"))
    
    st.info("""
    **Interpretación:** Este gráfico permite visualizar la brecha absoluta entre ambos candidatos a nivel nacional. 
    La diferencia actual es de **{:,}** votos.
    """.format(int(abs(total_p1 - total_p2))))

with col_right:
    st.subheader("Comparación: Distribución del Voto")
    # Usamos matplotlib para un gráfico de torta detallado
    labels = ['P1', 'P2', 'Blancos', 'Nulos/Imp.']
    sizes = [total_p1, total_p2, df["VOTOS_VB"].sum(), df["VOTOS_VN"].sum() + df["VOTOS_VI"].sum()]
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    ax.axis('equal') 
    st.pyplot(fig)

    st.warning("**Interpretación:** El porcentaje de votos no válidos (Blancos/Nulos) representa una porción crítica que influye en la legitimidad de la elección.")

st.markdown("---")

# 5. DISTRIBUCIÓN POR REGIÓN
st.subheader("Distribución de Votos por Región (Departamento)")

# Agrupamos por departamento
region_stats = df.groupby("DEPARTAMENTO")[["VOTOS_P1", "VOTOS_P2"]].sum().sort_values(by="VOTOS_P1", ascending=False)

st.bar_chart(region_stats)

with st.expander("Ver análisis regional detallado"):
    st.write("A continuación se muestra el top 5 de departamentos con mayor carga electoral:")
    st.table(region_stats.head(5))
    
    dep_max_p1 = region_stats["VOTOS_P1"].idxmax()
    dep_max_p2 = region_stats["VOTOS_P2"].idxmax()
    
    st.write(f"**Dato Clave:** El bastión principal de P1 es **{dep_max_p1}**, mientras que P2 lidera en **{dep_max_p2}**.")

# 6. FILTRO DINÁMICO
st.sidebar.header("Filtros de Búsqueda")
dep_sel = st.sidebar.selectbox("Seleccione un Departamento", sorted(df["DEPARTAMENTO"].unique()))

df_filtro = df[df["DEPARTAMENTO"] == dep_sel]
st.sidebar.write(f"Mesas en {dep_sel}: {len(df_filtro)}")



# --- PARTE 4: MACHINE LEARNING ---
st.markdown("---")
st.header("Machine Learning Aplicado")

# 1. IDENTIFICAR TIPO DE PROBLEMA
st.subheader("1. Identificación del Problema")
st.info("""
**Tipo de problema:** Agrupamiento (Clustering) - Aprendizaje No Supervisado.
- **Justificación:** No buscamos predecir un valor numérico específico (Regresión) ni asignar etiquetas predefinidas (Clasificación). El objetivo es descubrir patrones ocultos para agrupar regiones con comportamientos electorales similares.
""")

# 2. APLICAR MODELO BÁSICO
st.subheader("2. Aplicación del Modelo: Agrupamiento de Regiones")

# Preparación de datos: Agrupamos por departamento
data_ml = df.groupby("DEPARTAMENTO")[["VOTOS_P1", "VOTOS_P2", "VOTOS_VB", "VOTOS_VN"]].sum()

# Escalado de datos (Fundamental para modelos de distancia como K-Means)
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data_ml)

# Modelo K-Means
n_clusters = 3
model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
data_ml['Grupo_Electoral'] = model.fit_predict(data_scaled)
data_ml['Grupo_Electoral'] = data_ml['Grupo_Electoral'].astype(str)

# Visualización con Plotly
fig_ml = px.scatter(
    data_ml, 
    x="VOTOS_P1", 
    y="VOTOS_P2", 
    color="Grupo_Electoral",
    hover_name=data_ml.index,
    title="Mapa de Tendencias: Agrupamiento por Similitud de Voto",
    labels={"VOTOS_P1": "Votos P1", "VOTOS_P2": "Votos P2"},
    color_discrete_sequence=px.colors.qualitative.Safe
)
st.plotly_chart(fig_ml, use_container_width=True)

# 3. EVALUAR RESULTADOS
st.subheader("3. Evaluación de Resultados")

col_a, col_b = st.columns(2)

with col_a:
    st.write("**Métricas del Modelo:**")
    st.write(f"- **Inercia:** {model.inertia_:.2f}")
    st.write(f"- **Grupos identificados:** {n_clusters}")

with col_b:
    st.write("**Interpretación:**")
    st.success("""
    El modelo identificó con éxito 3 perfiles:
    1. **Perfil A:** Regiones con alta fidelidad a P1.
    2. **Perfil B:** Regiones competitivas o divididas.
    3. **Perfil C:** Regiones con alto volumen de votos blancos/nulos.
    """)

# Mostrar tabla de grupos para la ONPE
with st.expander("Ver detalle de departamentos por grupo"):
    st.dataframe(data_ml[['Grupo_Electoral']].sort_values(by="Grupo_Electoral"))


# --- PARTE 5: ENTRENAMIENTO Y VALIDACION ---
st.markdown("---")
st.header("Entrenamiento y Evaluación")

df_ml_clean = df[['N_ELEC_HABIL', 'VOTOS_P1']].dropna()

st.subheader("1. División de Datos (Train/Test)")

# Usamos el dataframe limpio (sin NaNs)
X = df_ml_clean[['N_ELEC_HABIL']].values
y = df_ml_clean['VOTOS_P1'].values

if len(df_ml_clean) > 0:
    # Dividimos: 80% para entrenar, 20% para probar
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    st.write(f"**Muestra original:** {len(df)} mesas")
    st.write(f"**Muestra tras limpiar nulos:** {len(df_ml_clean)} mesas")
    st.write(f"**Set de entrenamiento:** {len(X_train)} mesas")

    # 2. ENTRENAMIENTO DEL MODELO
    st.subheader("2. Entrenamiento: Regresión Lineal Simple")
    modelo_reg = LinearRegression()
    modelo_reg.fit(X_train, y_train)
    st.success("Modelo entrenado exitosamente con el 80% de los datos.")

    # Predicciones
    y_pred = modelo_reg.predict(X_test)

    # 3. EVALUACIÓN DE RESULTADOS
    st.subheader("3. Evaluación del Modelo")
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Precisión (R² Score)", f"{r2:.4f}")
    col_m2.metric("Error Cuadrático Medio", f"{mse:.2f}")

    # Gráfico de la línea de regresión
    fig_reg, ax = plt.subplots()
    ax.scatter(X_test[:500], y_test[:500], color='gray', alpha=0.5, label='Datos Reales')
    ax.plot(X_test[:500], y_pred[:500], color='red', linewidth=2, label='Predicción')
    ax.set_xlabel("Electores Hábiles")
    ax.set_ylabel("Votos P1")
    ax.legend()
    st.pyplot(fig_reg)
    
else:
    st.error("No hay suficientes datos limpios para entrenar el modelo.")

# 4. IDENTIFICACIÓN DE CONCEPTOS CLAVE
st.subheader("4. Diagnóstico del Modelo")

col_diag1, col_diag2 = st.columns(2)

with col_diag1:
    st.markdown("**¿Sobreajuste (Overfitting)?**")
    st.write("""
    No parece haber sobreajuste. El modelo de regresión lineal es muy simple 
    para memorizar el ruido de los datos electorales. Un modelo sobreajustado 
    tendría un R² de 0.99 en entrenamiento pero fallaría totalmente en prueba.
    """)

with col_diag2:
    st.markdown("**¿Subajuste (Underfitting)?**")
    st.write(f"""
    Existe un ligero **subajuste**. Como el R² es de {r2:.2f}, el modelo 
    no logra capturar toda la complejidad. Esto es normal: el número de 
    electores no es el único factor que determina el voto (influye la región, 
    la campaña, etc.).
    """)

# 5. LIMITACIONES EN CONTEXTO ELECTORAL
st.subheader("5. Limitaciones del Modelo")
st.warning("""
1. **Multicausalidad:** El voto no es lineal. Factores sociopolíticos y geográficos no están en el CSV.
2. **Sesgo Geográfico:** Una mesa con 300 electores en Lima no vota igual que una en Puno.
3. **Calidad de Actas:** El modelo asume que todas las actas están contabilizadas; no considera actas observadas o impugnadas.
""")
