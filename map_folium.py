import folium
from folium.plugins import HeatMap
import pandas as pd

# --- Étape 1 : Générer des données simulées ---
def generate_sample_data():
    data = {
        'parcelle': ['Parcelle A', 'Parcelle B', 'Parcelle C', 'Parcelle D'],
        'latitude': [15.0, 15.1, 15.2, 15.3],
        'longitude': [-10.0, -10.1, -10.2, -10.3],
        'yield': [8, 5, 7, 6],  # Rendements en tonnes/ha
        'risk_score': [0.3, 0.7, 0.6, 0.9]  # Scores de risque (0-1)
    }
    return pd.DataFrame(data)

data = generate_sample_data()

# --- Étape 2 : Créer une carte de base ---
def create_base_map(lat=15.0, lon=-10.0, zoom_start=10):
    """Crée une carte de base centrée sur les coordonnées fournies."""
    base_map = folium.Map(location=[lat, lon], zoom_start=zoom_start, control_scale=True)
    return base_map

# --- Étape 3 : Ajouter une couche des rendements ---
def add_yield_layer(base_map, data):
    """Ajoute une couche de cercles proportionnels pour les rendements."""
    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=row['yield'],  # Proportional to yield
            color="green",
            fill=True,
            fill_color="green",
            fill_opacity=0.6,
            popup=f"Parcelle: {row['parcelle']}<br>Rendement: {row['yield']} t/ha"
        ).add_to(base_map)
    return base_map

# --- Étape 4 : Ajouter une carte de chaleur pour les risques ---
def add_risk_heatmap(base_map, data):
    """Ajoute une carte de chaleur pour visualiser les scores de risque."""
    heat_data = [[row['latitude'], row['longitude'], row['risk_score']] for _, row in data.iterrows()]
    HeatMap(heat_data, radius=15).add_to(base_map)
    return base_map

# --- Étape 5 : Générer la carte complète ---
def generate_interactive_map(data):
    """Crée une carte interactive avec plusieurs couches."""
    base_map = create_base_map()
    base_map = add_yield_layer(base_map, data)
    base_map = add_risk_heatmap(base_map, data)
    return base_map

# --- Étape 6 : Afficher ou sauvegarder la carte ---
map_result = generate_interactive_map(data)

# Sauvegarder la carte dans un fichier HTML
map_result.save("agricultural_dashboard.html")
print("La carte a été sauvegardée dans le fichier 'agricultural_dashboard.html'.")

# Si vous utilisez Jupyter Notebook, vous pouvez afficher la carte directement :
# from IPython.display import display
# display(map_result)
