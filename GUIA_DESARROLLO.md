# Guía de Desarrollo - TPI Análisis de Datos Académicos

Este documento contiene las directrices, restricciones y la estructura para el desarrollo del Trabajo Práctico Integrador (TPI) de Diagnóstico de Desempeño Académico.

---

## 📌 Visión General del Proyecto
* **Objetivo:** Desarrollar un sistema de análisis y visualización de datos para diagnosticar el desempeño académico, identificar factores de riesgo y proponer soluciones basadas en evidencia.
* **Meta Final:** Crear un Informe de Gestión Interactivo donde un usuario final (no programador) pueda entender la situación de su clase de forma intuitiva.

---

## 🛠️ Requisitos Técnicos y Fases (Hitos)

### Hito 1: Adquisición y Planteo
* **Dataset:** Mínimo 5000 registros de datos educativos (reales, abiertos o simulados).
* **Preguntas de Negocio:** Definir 3 preguntas pedagógicas de alta complejidad (ej: patrones que preceden al abandono).

### Hito 2: ETL y Calidad de Datos (EDA)
* **Limpieza Avanzada:** Tratamiento de nulos, eliminación de outliers mediante métodos estadísticos y normalización de strings.
* **Feature Engineering:** Creación de variables calculadas (ej: Índices de constancia basados en fechas).

### Hito 3: Visualización Dinámica y Análisis
* **Gráficos:** Mínimo 4 gráficos profesionales usando **Matplotlib** y **Seaborn**.
* **Requisitos:** Deben incluir títulos, leyendas, escalas correctas y un análisis escrito explicativo de cada uno.

### Hito 4: Interfaz Gráfica (Dashboard Interactivo)
* **Tecnología:** Uso de **Streamlit**.
* **Interactividad:** Filtros dinámicos que actualicen los gráficos en tiempo real.

### Hito 5: Informe de Gestión y Propuesta
* **Diagnóstico:** Redactar conclusiones basadas puramente en la evidencia de los datos.
* **Propuestas:** Proponer al menos 2 soluciones de mejora académica factibles y justificadas estadísticamente.

---

## ⚖️ Criterios de Evaluación (Prioridades de Código)
El código y la solución serán evaluados bajo la siguiente ponderación:
1. **Análisis Crítico (30%):** Capacidad de transformar datos en propuestas coherentes.
2. **Lógica Pandas (25%):** Eficiencia en filtrado y transformación de grandes volúmenes de datos.
3. **UX/Dashboard (25%):** Interactividad, facilidad de uso y claridad visual de la interfaz.
4. **Calidad de Código (20%):** Uso de funciones, modularización y manejo de errores (`try-except`).

---

## 💻 Estándares de Codificación (Reglas para la IA)

### 1. Estilo y Arquitectura de Código
* **Modularización:** El proceso de ETL, la lógica de negocio y la interfaz deben estar estrictamente separados en módulos/archivos independientes (ej: `etl.py`, `plots.py`, `app.py`).
* **Buenas Prácticas:** Escribir funciones claras, con nombres descriptivos (snake_case) y tipado de datos en lo posible.
* **Manejo de Errores:** Bloques `try-except` obligatorios en las etapas críticas de carga de datos y transformaciones de Pandas para evitar que la app crashee.

### 2. Uso de Pandas y Rendimiento
* Evitar bucles iterativos (`for`) sobre DataFrames; priorizar la vectorización de Pandas y el uso de `.apply()` o `.loc` para transformaciones masivas.
* Asegurar que los filtros por comisión, fecha o estado sean eficientes.

### 3. Diseño de Interfaz (UX)
* Recordar que el usuario final **no sabe programar**. La interfaz debe ser limpia, autoexplicativa y visualmente organizada.

---

## 🚀 Comandos Útiles (A adaptar según el entorno)
* **Instalación de dependencias:** `pip install pandas matplotlib seaborn streamlit`
* **Correr la aplicación (Streamlit):** `streamlit run app.py`