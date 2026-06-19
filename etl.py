# -*- coding: utf-8 -*-
"""
etl.py - Carga, limpieza y feature engineering del TPI.

Migra la logica validada en el notebook (Hitos 1-2) a funciones reutilizables
por el dashboard (app.py). Cada funcion es pura: recibe un DataFrame y devuelve
uno nuevo, sin efectos colaterales.
"""
import numpy as np
import pandas as pd

# --- Constantes de dominio ---------------------------------------------------
CSV_CRUDO = "Student Social Media And Mental Health Impact.csv"
CSV_PROCESADO = "dataset_procesado.csv"

CAT_COLS = ["Gender", "Country", "Academic_Level",
            "Most_Used_Platform", "Purpose_Of_Use", "Stress_Level"]
ORDEN_ESTRES = ["Low", "Medium", "High", "Very High"]
ORDEN_RISK = ["Bajo", "Medio", "Alto"]
ORDEN_USO = ["Bajo", "Moderado", "Alto", "Muy alto"]


# --- 1) Carga ----------------------------------------------------------------
def cargar_datos(path=CSV_CRUDO):
    """Lee el CSV crudo. Lanza un error claro si no existe."""
    try:
        return pd.read_csv(path)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"No se encontro '{path}'. Verifica que el CSV este junto a etl.py."
        ) from e


# --- 2) Limpieza -------------------------------------------------------------
def winsorize_iqr(serie, k=1.5):
    """Acota una serie a los limites IQR (winsorizacion). No elimina filas."""
    q1, q3 = serie.quantile([.25, .75])
    iqr = q3 - q1
    return serie.clip(q1 - k * iqr, q3 + k * iqr)


def limpiar_datos(df):
    """Limpieza justificada (ver notebook, Hito 2). Devuelve un DataFrame nuevo."""
    try:
        df = df.copy()

        # 1) Duplicados exactos -> eliminar
        df = df.drop_duplicates().reset_index(drop=True)

        # 2) Normalizacion defensiva de strings
        for c in CAT_COLS:
            df[c] = df[c].astype(str).str.strip()

        # 3) Estres como categorica ORDENADA (orden natural del riesgo)
        df["Stress_Level"] = pd.Categorical(df["Stress_Level"],
                                            categories=ORDEN_ESTRES, ordered=True)

        # 4) Horas de actividad fisica negativas (imposibles) -> acotar a 0
        df["Physical_Activity_Hours"] = df["Physical_Activity_Hours"].clip(lower=0)

        # 5) Outliers IQR -> winsorizar (preservar filas y senal de riesgo)
        for c in ["Study_Hours", "Physical_Activity_Hours"]:
            df[c] = winsorize_iqr(df[c])

        return df
    except KeyError as e:
        raise KeyError(f"Falta una columna esperada durante la limpieza: {e}") from e


# --- 3) Feature Engineering --------------------------------------------------
def _minmax(serie):
    """Normaliza a rango 0-1 (robusto porque los extremos ya fueron winsorizados)."""
    return (serie - serie.min()) / (serie.max() - serie.min())


def agregar_features(df):
    """Crea las variables calculadas que responden las 3 preguntas de negocio."""
    df = df.copy()

    # Encoding ordinal del estres: Low=0 ... Very High=3
    df["Stress_Num"] = df["Stress_Level"].cat.codes

    # A) Indice de Riesgo Academico (pesos iguales 1/3)
    r_estudio = 1 - _minmax(df["Study_Hours"])          # poco estudio -> mas riesgo
    r_estres = df["Stress_Num"] / 3                      # mas estres   -> mas riesgo
    r_salud = 1 - _minmax(df["Mental_Health_Score"])    # baja salud   -> mas riesgo
    df["Risk_Index"] = ((r_estudio + r_estres + r_salud) / 3).round(3)
    df["Risk_Level"] = pd.qcut(df["Risk_Index"], 3, labels=ORDEN_RISK)
    df["En_Riesgo"] = df["Risk_Level"].eq("Alto")

    # B) Features para la Q2 (umbral y mecanismo)
    df["Usage_Level"] = pd.qcut(df["Avg_Daily_Usage_Hours"], 4,
                                labels=ORDEN_USO, duplicates="drop")
    df["Sleep_Deficit"] = df["Sleep_Hours_Per_Night"] < 7   # recomendacion 7-9 h

    # C) Features para la Q1 (huella digital)
    df["Unlocks_Per_Hour"] = (df["Daily_Unlocks"] / df["Avg_Daily_Usage_Hours"]).round(1)
    df["Study_Usage_Ratio"] = (df["Study_Hours"] / df["Avg_Daily_Usage_Hours"]).round(2)

    return df


# --- 4) Orquestador ----------------------------------------------------------
def preparar_dataset(path=CSV_CRUDO):
    """Pipeline completo: carga -> limpia -> agrega features. Lo usa el dashboard."""
    return agregar_features(limpiar_datos(cargar_datos(path)))


def aplicar_orden_categorico(df):
    """Reaplica el orden de las categoricas (util al leer el CSV procesado)."""
    df = df.copy()
    for col, orden in [("Stress_Level", ORDEN_ESTRES),
                       ("Risk_Level", ORDEN_RISK),
                       ("Usage_Level", ORDEN_USO)]:
        if col in df.columns:
            df[col] = pd.Categorical(df[col], categories=orden, ordered=True)
    return df


if __name__ == "__main__":
    datos = preparar_dataset()
    datos.to_csv(CSV_PROCESADO, index=False)
    print(f"Dataset procesado guardado en '{CSV_PROCESADO}': "
          f"{datos.shape[0]} filas x {datos.shape[1]} columnas")
