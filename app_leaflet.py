import streamlit as st
from pathlib import Path
from streamlit.components.v1 import html
from geopy.distance import geodesic
import geopandas as gpd
import random
import json
import unicodedata
from paises_es import paises_es  # asegúrate de tener paises_es.py junto a este archivo


# --- Funciones auxiliares ---
def normalizar(texto: str) -> str:
    """Quita acentos y pasa a minúsculas para comparar mejor."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.strip().lower())
        if unicodedata.category(c) != 'Mn'
    )

def es_desde_en(nombre_en: str) -> str:
    """Devuelve el nombre en español con capitalización correcta (desde diccionario)."""
    for es, en in paises_es.items():
        if normalizar(en) == normalizar(nombre_en):
            return es
    return nombre_en

def en_desde_es(nombre_es: str) -> str:
    """Devuelve el nombre en inglés desde un nombre en español."""
    for es, en in paises_es.items():
        if normalizar(es) == normalizar(nombre_es):
            return en
    return nombre_es

# Diccionarios normalizados (para búsqueda rápida)
paises_es_norm = {normalizar(k): v for k, v in paises_es.items()}   # es → en
en_a_es_norm   = {normalizar(v): k for k, v in paises_es.items()}   # en → es

# --- Inicialización ---
if "pais_misterioso" not in st.session_state:
    st.session_state.pais_misterioso = None   # en inglés
if "intentos" not in st.session_state:
    st.session_state.intentos = []
if "incorrectos" not in st.session_state:
    st.session_state.incorrectos = []
if "pais_revelado" not in st.session_state:
    st.session_state.pais_revelado = False
if "pais_input" not in st.session_state:
    st.session_state.pais_input = ""     # valor del text_input
if "last_guess" not in st.session_state:
    st.session_state.last_guess = ""     # último intento enviado
if "trigger" not in st.session_state:
    st.session_state.trigger = False     # bandera para procesar intento

# Configuración
st.set_page_config(layout="wide")

# --- Reducir padding superior de la página ---
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Encabezado con contador ---
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🌍 País Misterioso")
with col2:
    st.metric("Intentos", len(st.session_state.intentos))

# --- Cargar datos base ---
geojson_path = Path("static/countries_simplified.geojson")
world = gpd.read_file(geojson_path).to_crs(epsg=4326)
world["centroid"] = world.geometry.centroid
coords_dict = {
    row["name"]: (row["centroid"].y, row["centroid"].x) for _, row in world.iterrows()
}

# --- Lista de prioridad alta ---
prioritarios = [
    # Hispanoamérica
    "Argentina","Bolivia","Chile","Colombia","Costa Rica","Cuba","Ecuador","El Salvador","Guatemala",
    "Honduras","Mexico","Nicaragua","Panama","Paraguay","Peru","Dominican Republic","Uruguay","Venezuela",
    "Puerto Rico","Equatorial Guinea",
    # Europa
    # Europa
    "Spain","France","Germany","Italy","Portugal","Netherlands","Belgium","Poland","Sweden","Norway","Finland","United Kingdom",
    "Switzerland","Austria","Denmark","Ireland","Czech Republic","Hungary","Greece","Turkey","Ukraine","Romania","Bulgaria","Croatia","Serbia",

    # Otros
    "Japan","China","Australia","South Africa","Morocco","Algeria","Tunisia","Egypt", "Libya"
]

todos_los_paises = list(coords_dict.keys())
pesos = [40 if p in prioritarios else 1 for p in todos_los_paises]

# --- Botón para nuevo país ---
if st.button("🎯 Nuevo país misterioso"):
    elegido = random.choices(todos_los_paises, weights=pesos, k=1)[0]  # en inglés
    st.session_state.pais_misterioso = elegido
    st.session_state.intentos = []
    st.session_state.incorrectos = []
    st.session_state.pais_revelado = False
    st.session_state.pais_input = ""
    st.session_state.last_guess = ""
    st.session_state.trigger = False
    st.success("✅ Nuevo país misterioso elegido (oculto para ti).")

# --- Callback para enviar intento (enter o botón) ---
def enviar_intento():
    texto = st.session_state.pais_input.strip()
    if not texto:
        return
    st.session_state.last_guess = texto   # guardamos lo escrito
    st.session_state.pais_input = ""      # limpiamos el input
    st.session_state.trigger = True       # marcamos para procesar en el cuerpo

# --- Entrada de intentos (sin form): enter y botón comparten callback ---
cols_in = st.columns([4, 1])
with cols_in[0]:
    st.text_input(
        "✍️ Escribe un país (en español o inglés):",
        key="pais_input",
        on_change=enviar_intento
    )
with cols_in[1]:
    st.button("📨 Enviar", on_click=enviar_intento)

# Variables para mensajes
msg_idioma, msg_dist, msg_result = "", "", ""

# --- Procesamiento del intento si hay trigger ---
if st.session_state.trigger:
    st.session_state.trigger = False
    pais_input = st.session_state.last_guess

    if not st.session_state.pais_misterioso:
        msg_result = "Primero elige un país misterioso."
    else:
        clave = normalizar(pais_input)
        nombre_en = None
        nombre_es_visto = None

        # Intento en español
        if clave in paises_es_norm:
            nombre_en = paises_es_norm[clave]
            nombre_es_visto = en_a_es_norm.get(normalizar(nombre_en), es_desde_en(nombre_en))
            msg_idioma = f"Has escrito en español: **{nombre_es_visto}**"
        # Intento en inglés
        elif clave in en_a_es_norm:
            for es, en in paises_es.items():
                if normalizar(en) == clave:
                    nombre_en = en
                    nombre_es_visto = es
                    break
            msg_idioma = f"Has escrito en inglés, en español sería: **{nombre_es_visto}**"

        # --- Validar ---
        if nombre_en and nombre_en in coords_dict:
            misterioso = st.session_state.pais_misterioso  # en inglés
            if nombre_en == misterioso:
                # ¡Acierto!
                color = [0, 180, 0, 0.9]  # verde intenso
                msg_dist = "Distancia: 0 km"
                msg_result = "¡Correcto!"
                st.session_state.intentos.append({"name": nombre_en, "color": color})
                st.balloons()
            else:
                # Distancia y color por tramos
                dist = geodesic(coords_dict[nombre_en], coords_dict[misterioso]).km
                max_dist = 11000
                ratio = dist / max_dist
                if ratio > 0.8:
                    color = [255, 255, 255, 0.8]
                elif ratio > 0.6:
                    color = [255, 200, 120, 0.8]
                elif ratio > 0.4:
                    color = [255, 160, 60, 0.8]
                elif ratio > 0.2:
                    color = [200, 100, 30, 0.8]
                elif ratio > 0.05:
                    color = [150, 75, 0, 0.8]
                else:
                    color = [255, 0, 0, 0.9]

                msg_dist = f"Distancia: {int(dist)} km"
                msg_result = "No es correcto."
                st.session_state.intentos.append({"name": nombre_en, "color": color})

                if nombre_es_visto:
                    dist_km = int(dist)  # ya tienes la variable dist calculada
                    # guardamos como (nombre, distancia)
                    if not any(nombre_es_visto == x[0] for x in st.session_state.incorrectos):
                        st.session_state.incorrectos.append((nombre_es_visto, dist_km))

        else:
            msg_result = "Ese país no está en el mapa o en el diccionario."

# --- Mensajes en una fila ---
cols_msg = st.columns(3)
if msg_idioma:
    cols_msg[0].info(msg_idioma)
if msg_dist:
    cols_msg[1].info(msg_dist)
if msg_result:
    if "correcto" in msg_result.lower():
        cols_msg[2].success(msg_result)
    elif "no es correcto" in msg_result.lower():
        cols_msg[2].error(msg_result)
    else:
        cols_msg[2].warning(msg_result)

# --- Preparar HTML con colores ---
html_base = Path("static/map.html").read_text(encoding="utf-8")

# 1) Qué geometrías mostramos (sin mutar estado):
paises_mostrados = [i["name"] for i in st.session_state.intentos]
if st.session_state.pais_revelado and st.session_state.pais_misterioso:
    paises_mostrados.append(st.session_state.pais_misterioso)

subset = world[world["name"].isin(paises_mostrados)]
geojson_data = subset.drop(columns=["centroid"]).to_json()

# 2) Qué colores usamos en esta vista (sin mutar estado):
colores_vista = list(st.session_state.intentos)
if st.session_state.pais_revelado and st.session_state.pais_misterioso:
    colores_vista = [i for i in colores_vista if i["name"] != st.session_state.pais_misterioso]
    colores_vista.append({"name": st.session_state.pais_misterioso, "color": [0, 180, 0, 0.85]})

html_final = html_base.replace(
    "// AQUÍ IRA GEOJSON",
    f"const geoData = {geojson_data};\nconst colores = {json.dumps(colores_vista)};"
)

st.subheader("🗺️ Mapa Mundial")
html(html_final, height=650, scrolling=False)

# --- Lista de incorrectos ---
if st.session_state.incorrectos:
    st.subheader("❌ Lista de países incorrectos (ordenados por cercanía):")

    # ordenamos por distancia (más cercano primero)
    ordenados = sorted(st.session_state.incorrectos, key=lambda x: x[1])

    cols = st.columns(4)
    for idx, (pais, dist) in enumerate(ordenados):
        cols[idx % 4].write(f"{pais} — {dist} km")


# --- Botones al final ---
if st.session_state.pais_misterioso:
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("👀 Mostrar / Ocultar respuesta correcta"):
            st.session_state.pais_revelado = not st.session_state.pais_revelado
            # Si ocultamos y por alguna razón quedó en intentos, lo sacamos
            if not st.session_state.pais_revelado and st.session_state.pais_misterioso:
                st.session_state.intentos = [
                    i for i in st.session_state.intentos
                    if i["name"] != st.session_state.pais_misterioso
                ]

        if st.session_state.pais_revelado:
            misterioso_en = st.session_state.pais_misterioso
            misterioso_es = es_desde_en(misterioso_en)
            st.success(f"✅ El país misterioso era: **{misterioso_es}**")

    with col2:
        if st.button("🔄 Reiniciar juego"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
