import pandas as pd
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.seasonal import seasonal_decompose
import warnings

warnings.filterwarnings('ignore')


class AgriculturalDataManager:
    def __init__(self):
        """Initialise le gestionnaire de données agricoles."""
        self.monitoring_data = None
        self.weather_data = None
        self.soil_data = None
        self.yield_history = None
        self.scaler = StandardScaler()

    def load_data(self):
        """
        Charge l'ensemble des données nécessaires au système.
        """
        self.monitoring_data = pd.read_csv(r'C:/Users/hp/Desktop/Data Science/Ahnouch/data/monitoring_cultures.csv', parse_dates=['date'])
        self.weather_data = pd.read_csv(r'C:/Users/PC/Desktop/Data Science/Ahnouch/data/meteo_detaillee.csv', parse_dates=['date'])
        self.soil_data = pd.read_csv(r'C:/Users/PC/Desktop/Data Science/Ahnouch/data/sols.csv')
        self.yield_history = pd.read_csv(r'C:/Users/PC/Desktop/Data Science/Ahnouch/data/historique_rendements.csv', parse_dates=['date'])

    def get_parcelle_ids(self):
        """
        Retourne une liste des identifiants des parcelles.
        """
        if 'parcelle_id' not in self.monitoring_data.columns:
            raise ValueError("La colonne 'parcelle_id' est manquante dans les données.")
        return sorted(self.monitoring_data['parcelle_id'].unique())
    
    def get_yield_history(self, parcelle_id):
        """
        Retourne l'historique des rendements pour une parcelle donnée.
        """
        if self.yield_history is None:
            raise ValueError("Les données d'historique des rendements ne sont pas chargées.")

        # Filtrer les données pour la parcelle
        return self.yield_history[self.yield_history["parcelle_id"] == parcelle_id]

    def prepare_features(self):
        """
        Prépare les caractéristiques pour l'analyse en fusionnant
        les différentes sources de données.
        """
        # Assurez-vous que les dates sont au bon format
        self.monitoring_data['date'] = pd.to_datetime(self.monitoring_data['date'])
        self.weather_data['date'] = pd.to_datetime(self.weather_data['date']).dt.normalize()

        # Fusion des données météo
        merged_data = pd.merge(
            self.monitoring_data,
            self.weather_data[['date', 'precipitation']],
            on='date',
            how='left'
        )

        # Fusion avec les données de sol
        merged_data = pd.merge(merged_data, self.soil_data, on='parcelle_id', how='left')

        # Standardisation des colonnes numériques
        numeric_cols = merged_data.select_dtypes(include=['float64', 'int64']).columns
        merged_data[numeric_cols] = self.scaler.fit_transform(merged_data[numeric_cols])

        return merged_data

    def enrich_yield_history(self, data):
        """
        Enrichit les données actuelles avec l'historique des rendements.
        """
        enriched_data = pd.merge(
            data,
            self.yield_history[['parcelle_id', 'date', 'culture', 'rendement_final', 'progression']],
            on=['parcelle_id', 'date'],
            how='left'
        )
        return enriched_data

    def get_temporal_patterns(self, parcelle_id):
        """
        Analyse les patterns temporels pour une parcelle donnée.
        """
        parcelle_data = self.yield_history[self.yield_history['parcelle_id'] == parcelle_id]

        if parcelle_data.empty:
            raise ValueError(f"Aucune donnée disponible pour la parcelle {parcelle_id}.")

        # Vérifier le nombre d'observations
        if len(parcelle_data) < 24:
            parcelle_data['trend'] = parcelle_data['rendement_final'].rolling(window=3, min_periods=1).mean()
            return parcelle_data['trend'], None, None

        # Décomposition saisonnière
        result = seasonal_decompose(parcelle_data['rendement_final'], model='additive', period=12)
        return result.trend, result.seasonal, result.resid

    def calculate_risk_metrics(self, data):
        """
        Calcule les métriques de risque basées sur les conditions
        actuelles et l'historique.
        """
        data['risk_metric'] = (data['stress_hydrique'] + data['precipitation'] * 0.1) / (data['biomasse_estimee'] + 1)
        return data

    def analyze_yield_patterns(self, parcelle_id):
        """
        Réalise une analyse approfondie des patterns de rendement pour une parcelle donnée.
        """
        parcelle_data = self.yield_history[self.yield_history['parcelle_id'] == parcelle_id].copy()

        if parcelle_data.empty:
            raise ValueError(f"Aucune donnée disponible pour la parcelle {parcelle_id}.")

        if len(parcelle_data) < 24:
            parcelle_data['trend'] = parcelle_data['rendement_final'].rolling(window=3, min_periods=1).mean()
            return {
                'trend': parcelle_data['trend'],
                'seasonality': None,
                'residuals': None
            }

        parcelle_data.set_index('date', inplace=True)
        result = seasonal_decompose(parcelle_data['rendement_final'], model='additive', period=12)

        return {
            'trend': result.trend,
            'seasonality': result.seasonal,
            'residuals': result.resid
        }
        
    import json


    '''def get_geojson_data(self):
        """
        Génère des données GeoJSON pour les parcelles.
        """
        geojson_features = []

        # Parcourez les parcelles uniques dans soil_data
        for _, row in self.soil_data.iterrows():
            feature = {
                "type": "Feature",
                "properties": {
                    "parcelle_id": row["parcelle_id"],
                    "surface_ha": row.get("surface_ha", None),  # Exemple de propriété additionnelle
                    "type_sol": row.get("type_sol", None)
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [row["longitude"], row["latitude"]],
                }
            }
            geojson_features.append(feature)

        geojson_data = {
            "type": "FeatureCollection",
            "features": geojson_features
        }

        return geojson_data
'''
