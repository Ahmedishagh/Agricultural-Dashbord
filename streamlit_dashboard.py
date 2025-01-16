import streamlit as st
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.embed import components
import folium
from streamlit_folium import folium_static

# --- Étape 1 : Générer des données simulées ---
def generate_sample_data():
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    parcelles = ['Parcelle A', 'Parcelle B', 'Parcelle C']

    data = {
        'date': np.tile(dates, len(parcelles)),
        'parcelle': np.repeat(parcelles, len(dates)),
        'yield': np.random.uniform(2, 10, len(dates) * len(parcelles)),
        'ndvi': np.random.uniform(0.4, 0.9, len(dates) * len(parcelles)),
        'latitude': np.random.uniform(15.0, 15.3, len(dates) * len(parcelles)),
        'longitude': np.random.uniform(-10.3, -10.0, len(dates) * len(parcelles)),
        'risk_score': np.random.uniform(0.1, 1.0, len(dates) * len(parcelles)),
    }
    return pd.DataFrame(data)

data = generate_sample_data()

# Convertir la colonne 'date' en datetime.datetime pour éviter l'erreur
data['date'] = data['date'].dt.to_pydatetime()

# --- Étape 2 : Créer des visualisations avec Bokeh ---
def create_yield_plot(data, parcelle):
    """Créer un graphique Bokeh pour les rendements."""
    filtered_data = data[data['parcelle'] == parcelle]
    source = ColumnDataSource(filtered_data)

    p = figure(
        title=f"Évolution des rendements pour {parcelle}",
        x_axis_type="datetime",
        height=400,
        tools="pan,box_zoom,reset,save",
    )
    p.line('date', 'yield', source=source, line_width=2, color='blue', legend_label='Rendement')
    p.circle('date', 'yield', source=source, size=5, color='blue')
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Rendement (t/ha)"
    p.legend.location = "top_left"
    return p

# --- Étape 3 : Créer une carte interactive avec Folium ---
def create_map(data, parcelle):
    """Créer une carte Folium pour afficher les parcelles."""
    filtered_data = data[data['parcelle'] == parcelle]
    base_map = folium.Map(location=[15.15, -10.15], zoom_start=10)

    for _, row in filtered_data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=7,
            color="green",
            fill=True,
            fill_color="green",
            fill_opacity=0.6,
            popup=f"Rendement: {row['yield']} t/ha<br>Score de risque: {row['risk_score']:.2f}"
        ).add_to(base_map)

    return base_map

# --- Étape 4 : Interface utilisateur avec Streamlit ---
def main():
    st.title("Tableau de Bord Agricole Interactif")

    # Sélecteur de parcelle
    parcelle_options = list(data['parcelle'].unique())
    selected_parcelle = st.selectbox("Choisissez une parcelle :", parcelle_options)

    # Intervalle de dates
    min_date = data['date'].min()
    max_date = data['date'].max()
    date_range = st.slider(
        "Sélectionnez un intervalle de dates :", 
        min_value=min_date, 
        max_value=max_date, 
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )

    # Filtrer les données
    filtered_data = data[
        (data['parcelle'] == selected_parcelle) &
        (data['date'] >= date_range[0]) &
        (data['date'] <= date_range[1])
    ]

    # Graphique des rendements avec Bokeh
    st.subheader("Graphique des rendements")
    bokeh_plot = create_yield_plot(filtered_data, selected_parcelle)
    st.bokeh_chart(bokeh_plot, use_container_width=True)

    # Carte interactive avec Folium
    st.subheader("Carte interactive")
    folium_map = create_map(filtered_data, selected_parcelle)
    folium_static(folium_map)

# --- Lancer l'application Streamlit ---
if __name__ == "__main__":
    main()
