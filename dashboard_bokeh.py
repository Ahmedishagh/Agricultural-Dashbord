from bokeh.plotting import figure, show, curdoc
from bokeh.models import ColumnDataSource, Select, DateRangeSlider
from bokeh.layouts import column, row
from bokeh.models.tools import HoverTool
import pandas as pd
import numpy as np
from datetime import datetime

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
        'stress': np.random.uniform(0, 1, len(dates) * len(parcelles))
    }
    return pd.DataFrame(data)

data = generate_sample_data()

# Assurez-vous que la colonne 'date' est bien en datetime64[ns]
data['date'] = pd.to_datetime(data['date'])

# Créez une source de données initiale pour Bokeh
source = ColumnDataSource(data)

# --- Étape 2 : Créer les visualisations ---
def create_yield_plot(source):
    p = figure(
        title="Évolution des rendements",
        x_axis_type="datetime",
        height=400,
        tools="pan,box_zoom,reset,save",
    )
    p.line('date', 'yield', source=source, line_width=2, color='blue', legend_label='Rendement')
    p.circle('date', 'yield', source=source, size=5, color='blue')
    p.add_tools(HoverTool(tooltips=[("Date", "@date{%F}"), ("Rendement", "@yield")],
                          formatters={'@date': 'datetime'}))
    p.legend.location = "top_left"
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Rendement (t/ha)"
    return p

def create_ndvi_plot(source):
    p = figure(
        title="Évolution du NDVI",
        x_axis_type="datetime",
        height=400,
        tools="pan,box_zoom,reset,save",
    )
    p.line('date', 'ndvi', source=source, line_width=2, color='green', legend_label='NDVI')
    p.add_tools(HoverTool(tooltips=[("Date", "@date{%F}"), ("NDVI", "@ndvi")],
                          formatters={'@date': 'datetime'}))
    p.legend.location = "top_left"
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "NDVI"
    return p

def create_stress_plot(source):
    p = figure(
        title="Matrice de stress hydrique",
        height=400,
        tools="hover,pan,box_zoom,reset,save",
    )
    p.scatter('ndvi', 'stress', source=source, size=8, color='orange', alpha=0.6)
    p.add_tools(HoverTool(tooltips=[("NDVI", "@ndvi"), ("Stress", "@stress")]))
    p.xaxis.axis_label = "NDVI"
    p.yaxis.axis_label = "Stress hydrique"
    return p

# --- Étape 3 : Ajouter des widgets interactifs ---
def update_plot(attr, old, new):
    selected_parcelle = parcelle_select.value
    start_date, end_date = date_range.value_as_datetime

    # Convertir les dates en tz-naive pour correspondre au format des données
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    # Filtrer les données en fonction de la parcelle et de la plage de dates
    filtered_data = data[
        (data['parcelle'] == selected_parcelle) &
        (data['date'] >= start_date) &
        (data['date'] <= end_date)
    ]
    source.data = ColumnDataSource.from_df(filtered_data)

parcelle_select = Select(title="Sélectionnez une parcelle :", value="Parcelle A", options=list(data['parcelle'].unique()))
date_range = DateRangeSlider(title="Intervalle de dates", start=data['date'].min(), end=data['date'].max(),
                             value=(data['date'].min(), data['date'].max()))

parcelle_select.on_change('value', update_plot)
date_range.on_change('value', update_plot)

# --- Étape 4 : Construire la mise en page ---
yield_plot = create_yield_plot(source)
ndvi_plot = create_ndvi_plot(source)
stress_plot = create_stress_plot(source)

layout = column(
    row(parcelle_select, date_range),
    yield_plot,
    ndvi_plot,
    stress_plot
)

# --- Étape 5 : Exécuter le tableau de bord ---
curdoc().add_root(layout)
curdoc().title = "Tableau de Bord Agricole"

# Si vous exécutez localement, utilisez :
# show(layout)