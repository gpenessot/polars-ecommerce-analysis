"""Package d'analyse e-commerce utilisant Polars et Plotly.

Ce package fournit des outils pour :
- Charger et nettoyer des données e-commerce
- Calculer des KPIs business
- Créer des visualisations interactives
- Générer des rapports d'analyse détaillés
"""

from .data_loader import load_retail_data
from .data_cleaner import clean_retail_data
from .kpi_calculator import (
    generate_kpi_report,
    calculate_global_kpis,
    analyze_products,
    calculate_customer_metrics,
    calculate_temporal_kpis
)
from .visualizer import EcommerceVisualizer
from .quarto_exporter import QuartoExporter

# Définition explicite des éléments publics du package
__all__ = [
    'load_retail_data',
    'clean_retail_data',
    'generate_kpi_report',
    'calculate_global_kpis',
    'analyze_products',
    'calculate_customer_metrics',
    'calculate_temporal_kpis',
    'EcommerceVisualizer',
    'QuartoExporter'
]