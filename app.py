# -*- coding: utf-8 -*-
"""
app.py - Dashboard interactivo del TPI (Hito 4).

Informe de gestion para un usuario NO programador: filtros dinamicos en la barra
lateral que actualizan KPIs y graficos en tiempo real. La logica de datos vive en
etl.py y la de graficos en plots.py (separacion estricta de responsabilidades).

Ejecutar con:  streamlit run app.py
"""
import os
import pandas as pd
import streamlit as st

import etl
import plots

st.set_page_config(page_title="Diagnostico de Desempeno Academico",
                   page_icon="📊", layout="wide")


# --- Carga de datos (cacheada) ----------------------------------------------
@st.cache_data
def cargar():
    """Usa el CSV procesado si existe; si no, corre el pipeline desde el crudo."""
    try:
        if os.path.exists(etl.CSV_PROCESADO):
            df = pd.read_csv(etl.CSV_PROCESADO)
            return etl.aplicar_orden_categorico(df)
        return etl.preparar_dataset()
    except (FileNotFoundError, KeyError) as e:
        st.error(f"No se pudieron cargar los datos: {e}")
        st.stop()


df = cargar()

# --- Barra lateral: filtros dinamicos ---------------------------------------
st.sidebar.header("🔎 Filtros")
st.sidebar.caption("Los graficos y KPIs se actualizan en tiempo real.")


def multiselect_col(label, col):
    """Multiselect que por defecto selecciona todas las categorias de la columna."""
    opciones = sorted(df[col].dropna().unique().tolist())
    return st.sidebar.multiselect(label, opciones, default=opciones)

niveles = multiselect_col("Nivel academico", "Academic_Level")
propositos = multiselect_col("Proposito de uso", "Purpose_Of_Use")
plataformas = multiselect_col("Plataforma principal", "Most_Used_Platform")
generos = multiselect_col("Genero", "Gender")

# Slider para controlar "a igualdad de uso" (clave para la Q3)
uso_min, uso_max = float(df["Avg_Daily_Usage_Hours"].min()), float(df["Avg_Daily_Usage_Hours"].max())
rango_uso = st.sidebar.slider("Horas diarias de uso", uso_min, uso_max,
                              (uso_min, uso_max), step=0.5)

solo_riesgo = st.sidebar.checkbox("Mostrar solo estudiantes en riesgo (nivel Alto)")

# --- Aplicacion de filtros (vectorizado) ------------------------------------
mask = (
    df["Academic_Level"].isin(niveles)
    & df["Purpose_Of_Use"].isin(propositos)
    & df["Most_Used_Platform"].isin(plataformas)
    & df["Gender"].isin(generos)
    & df["Avg_Daily_Usage_Hours"].between(*rango_uso)
)
if solo_riesgo:
    mask &= df["En_Riesgo"]

dff = df[mask]

# --- Encabezado --------------------------------------------------------------
st.title("📊 Diagnostico de Desempeno Academico")
st.markdown("Impacto de los habitos digitales y de bienestar en el riesgo academico "
            "de los estudiantes. Use los filtros de la izquierda para explorar segmentos.")

if dff.empty:
    st.warning("Ningun estudiante cumple los filtros seleccionados. "
               "Ajuste los criterios en la barra lateral.")
    st.stop()

# --- KPIs --------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Estudiantes", f"{len(dff):,}")
c2.metric("% en riesgo (Alto)", f"{dff['En_Riesgo'].mean() * 100:.1f}%")
c3.metric("Uso diario promedio", f"{dff['Avg_Daily_Usage_Hours'].mean():.1f} h")
c4.metric("Deficit de sueno", f"{dff['Sleep_Deficit'].mean() * 100:.1f}%")

st.divider()

# --- Pestanas: una por pregunta de negocio ----------------------------------
tab1, tab2, tab3, tab0 = st.tabs([
    "Q1 · Huella del riesgo",
    "Q2 · Umbral y mecanismo",
    "Q3 · Segmentos",
    "Contexto · Correlaciones",
])

with tab1:
    st.subheader("Q1 - ¿Que habitos digitales caracterizan al estudiante en riesgo?")
    st.pyplot(plots.fig_huella_q1(dff))
    st.caption("A mayor riesgo: mas horas de uso, mas desbloqueos diarios y menor "
               "priorizacion del estudio frente a la pantalla.")

with tab2:
    st.subheader("Q2 - ¿Existe un umbral de uso? ¿Por que mecanismo dana?")
    col_a, col_b = st.columns(2)
    with col_a:
        st.pyplot(plots.fig_umbral_q2(dff))
    with col_b:
        st.pyplot(plots.fig_mecanismo_q2(dff))
    st.caption("El sueno cae bajo las 7 h saludables alrededor de las ~5 h/dia de uso; "
               "la via principal de dano es la perdida de sueno.")

with tab3:
    st.subheader("Q3 - ¿Que segmentos concentran mas riesgo?")
    st.info("Sugerencia: fije un rango estrecho en 'Horas diarias de uso' (barra lateral) "
            "para comparar segmentos **a igualdad de uso**, como plantea la pregunta.")
    st.pyplot(plots.fig_segmentos_q3(dff))

with tab0:
    st.subheader("Mapa de correlaciones")
    st.pyplot(plots.fig_correlaciones(dff))

st.divider()
with st.expander("Ver datos filtrados (muestra)"):
    st.dataframe(dff.head(50), use_container_width=True)
