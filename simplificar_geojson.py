import geopandas as gpd

# 1. Cargar el archivo original
world = gpd.read_file("static/countries.geojson")

# 2. Simplificar geometrías
# tolerance controla cuánto se reduce:
#   valores bajos = más detalle (archivo más pesado)
#   valores altos = menos detalle (archivo más ligero)
world["geometry"] = world["geometry"].simplify(tolerance=0.05, preserve_topology=True)

# 3. Guardar archivo reducido
world.to_file("static/countries_simplified.geojson", driver="GeoJSON")

print("✅ Archivo simplificado guardado en static/countries_simplified.geojson")
