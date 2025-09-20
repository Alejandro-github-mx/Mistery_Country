# Mistery_Country
Juego interactivo en Streamlit para adivinar un país misterioso. Incluye un mapa mundial dinámico con Leaflet, cálculo de distancias y soporte para respuestas en español e inglés./Interactive Streamlit game to guess a mystery country. Features a dynamic world map with Leaflet, distance calculation, and support for answers in Spanish and English.

# 🌍 País Misterioso / Mystery Country

Juego interactivo en **Streamlit** para adivinar un país misterioso.  
Incluye un mapa mundial dinámico con **Leaflet**, cálculo de distancias y soporte para respuestas en **español** e **inglés**.

Interactive **Streamlit** game to guess a mystery country.  
Features a dynamic world map with **Leaflet**, distance calculation, and support for answers in **Spanish** and **English**.

---

## 🚀 Cómo ejecutar / How to run

### Español
1. Clona este repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/mystery-country.git
   cd mystery-country
python -m venv venv
source venv/bin/activate   # en Linux/Mac
venv\Scripts\activate      # en Windows

pip install -r requirements.txt
streamlit run app_leaflet.py


# Clone this repository

git clone https://github.com/YOUR_USERNAME/mystery-country.git
cd mystery-country
python -m venv venv
source venv/bin/activate   # on Linux/Mac
venv\Scripts\activate      # on Windows

pip install -r requirements.txt
streamlit run app_leaflet.py

mystery-country/
│── app_leaflet.py        # Código principal / Main code
│── paises_es.py          # Diccionario español-inglés / Spanish-English dictionary
│── requirements.txt      # Dependencias / Dependencies
│── README.md             # Este archivo / This file
└── static/
    ├── map.html
    └── countries_simplified.geojson

📜 Licencia / License

Este proyecto usa la licencia MIT.
This project uses the MIT License.


---

### 📄 `requirements.txt`
Las dependencias mínimas para que cualquiera lo ejecute:

streamlit
geopandas
geopy
shapely


(Se pueden añadir más si las necesitas, pero esas son las claves).


