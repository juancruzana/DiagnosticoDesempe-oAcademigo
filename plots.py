# -*- coding: utf-8 -*-
"""
plots.py - Funciones de visualizacion del TPI.

Cada funcion recibe un DataFrame (potencialmente filtrado por el dashboard) y
devuelve una figura de Matplotlib. No usan plt.show(): el caller decide que hacer
(st.pyplot en el dashboard, savefig en el informe).
"""
import matplotlib.pyplot as plt
import seaborn as sns

from etl import ORDEN_RISK, ORDEN_USO

sns.set_theme(style="whitegrid", palette="muted")

PAL_RISK = {"Bajo": "#2ca02c", "Medio": "#ff7f0e", "Alto": "#d62728"}
_NUM_CORR = ["Avg_Daily_Usage_Hours", "Daily_Unlocks", "Study_Hours",
             "Physical_Activity_Hours", "Sleep_Hours_Per_Night",
             "Mental_Health_Score", "Stress_Num", "Risk_Index"]


def _sin_datos(msg="Sin datos para los filtros seleccionados"):
    """Figura de aviso cuando el filtrado deja el DataFrame vacio."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, msg, ha="center", va="center", fontsize=13, color="grey")
    ax.axis("off")
    return fig


def fig_correlaciones(df):
    """G1 - Mapa de correlaciones (contexto general)."""
    if df.empty:
        return _sin_datos()
    fig, ax = plt.subplots(figsize=(8, 6.5))
    sns.heatmap(df[_NUM_CORR].corr(), annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, vmin=-1, vmax=1, square=True, linewidths=.5, ax=ax,
                cbar_kws={"label": "Coef. de correlacion"})
    ax.set_title("Correlaciones entre habitos, bienestar y riesgo", fontweight="bold")
    fig.tight_layout()
    return fig


def fig_huella_q1(df):
    """G2 (Q1) - La huella digital del riesgo academico."""
    if df.empty:
        return _sin_datos()
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    metricas = [("Avg_Daily_Usage_Hours", "Horas diarias de uso"),
                ("Daily_Unlocks", "Desbloqueos diarios (total)"),
                ("Study_Usage_Ratio", "Ratio estudio / uso")]
    for ax, (col, lab) in zip(axes, metricas):
        sns.boxplot(data=df, x="Risk_Level", y=col, order=ORDEN_RISK,
                    hue="Risk_Level", palette=PAL_RISK, legend=False, ax=ax)
        ax.set_xlabel("Nivel de riesgo academico")
        ax.set_ylabel(lab)
        ax.set_title(lab)
    fig.suptitle("Q1 - La huella digital del riesgo academico",
                 fontweight="bold", fontsize=14)
    fig.tight_layout()
    return fig


def fig_umbral_q2(df):
    """G3 (Q2) - Umbral: uso vs sueno y estudio."""
    if df.empty:
        return _sin_datos()
    agg = (df.assign(Uso_round=df["Avg_Daily_Usage_Hours"].round())
             .groupby("Uso_round")[["Sleep_Hours_Per_Night", "Study_Hours"]].mean())
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(agg.index, agg["Sleep_Hours_Per_Night"], marker="o", label="Horas de sueno")
    ax.plot(agg.index, agg["Study_Hours"], marker="s", label="Horas de estudio")
    ax.axhline(7, ls=":", color="steelblue", alpha=.7)
    ax.axvline(5, ls="--", color="grey", alpha=.8)
    ax.text(5.1, agg.values.max() * 0.95, "Umbral ~5 h/dia", color="grey")
    ax.set_xlabel("Horas diarias de uso de redes sociales")
    ax.set_ylabel("Horas promedio (sueno por noche / estudio por dia)")
    ax.set_title("Q2 - Umbral de uso: caida del sueno y del estudio", fontweight="bold")
    ax.legend()
    fig.tight_layout()
    return fig


def fig_mecanismo_q2(df):
    """G4 (Q2 - mecanismo) - % deficit de sueno por nivel de uso."""
    if df.empty:
        return _sin_datos()
    defi = (df.groupby("Usage_Level", observed=True)["Sleep_Deficit"]
              .mean().mul(100).reindex(ORDEN_USO))
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=defi.index, y=defi.values, hue=defi.index,
                palette="flare", legend=False, ax=ax)
    for i, v in enumerate(defi.values):
        if v == v:  # ignora NaN (categorias sin datos tras filtrar)
            ax.text(i, v + 1, f"{v:.0f}%", ha="center", fontweight="bold")
    ax.set_xlabel("Nivel de uso de redes (cuartiles)")
    ax.set_ylabel("% de estudiantes con deficit de sueno (< 7 h)")
    ax.set_ylim(0, 110)
    ax.set_title("Q2 - El mecanismo: el uso alto roba horas de sueno", fontweight="bold")
    fig.tight_layout()
    return fig


def fig_segmentos_q3(df):
    """G5 (Q3) - % en riesgo por nivel academico x proposito de uso."""
    if df.empty:
        return _sin_datos()
    piv = df.pivot_table(index="Academic_Level", columns="Purpose_Of_Use",
                         values="En_Riesgo", aggfunc="mean").mul(100)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(piv, annot=True, fmt=".0f", cmap="Reds", linewidths=.5, ax=ax,
                cbar_kws={"label": "% en riesgo"})
    ax.set_xlabel("Proposito de uso")
    ax.set_ylabel("Nivel academico")
    ax.set_title("Q3 - Segmentos mas expuestos (% en riesgo)", fontweight="bold")
    fig.tight_layout()
    return fig
