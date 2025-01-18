"""Module pour le calcul des KPIs e-commerce avec Polars.

Ce module utilise l'API Polars pour calculer efficacement différents KPIs e-commerce.
Il suit les conventions Polars pour une meilleure performance et lisibilité.
"""

import polars as pl
from typing import Dict, Any, Tuple

def calculate_global_kpis(df: pl.DataFrame) -> Dict[str, float]:
    """
    Calcule les KPIs globaux de l'activité e-commerce avec Polars.
    """
    # Création d'une LazyFrame pour optimiser les calculs
    lf = df.lazy()
    
    # Calcul du panier moyen et des articles par commande
    order_metrics = (
        lf.group_by("InvoiceNo")  # Notez group_by au lieu de groupby
        .agg([
            pl.sum("Revenue").alias("OrderValue"),
            pl.sum("Quantity").alias("ItemCount")
        ])
        .select([
            pl.mean("OrderValue").alias("avg_order_value"),
            pl.mean("ItemCount").alias("avg_items_per_order")
        ])
        .collect()
    )
    
    # Calcul des autres métriques globales
    global_metrics = {
        "total_revenue": float(df["Revenue"].sum()),
        "total_orders": len(df["InvoiceNo"].unique()),
        "total_customers": len(df["CustomerID"].unique()),
        "total_products": len(df["StockCode"].unique()),
        "average_order_value": float(order_metrics["avg_order_value"][0]),
        "average_items_per_order": float(order_metrics["avg_items_per_order"][0])
    }
    
    return global_metrics

def analyze_products(df: pl.DataFrame) -> Tuple[pl.DataFrame, pl.DataFrame]:
    """
    Analyse détaillée des produits avec Polars.
    
    Cette fonction réalise deux analyses distinctes :
    1. Une analyse des top produits par chiffre d'affaires
    2. Une analyse des performances par catégorie de prix
    
    Args:
        df: DataFrame avec les données nettoyées incluant PriceCategory
        
    Returns:
        Tuple contenant:
        - DataFrame des top produits
        - DataFrame des statistiques par catégorie de prix
    """
    print("Analyse des top produits...")
    # Analyse des top produits
    top_products = (
        df.lazy()
        .group_by(["StockCode", "Description", "PriceCategory"])  # Ajout de PriceCategory
        .agg([
            pl.sum("Revenue").alias("TotalRevenue"),
            pl.sum("Quantity").alias("TotalQuantity"),
            pl.n_unique("InvoiceNo").alias("NumberOrders"),
            pl.mean("UnitPrice").alias("AveragePrice")
        ])
        .sort("TotalRevenue", descending=True)
        .collect()
    )
    
    print("Analyse des catégories de prix...")
    # Analyse par catégorie de prix
    price_stats = (
        df.lazy()
        .group_by("PriceCategory")
        .agg([
            pl.sum("Revenue").alias("TotalRevenue"),
            pl.mean("UnitPrice").alias("AveragePrice"),
            pl.n_unique("StockCode").alias("NumberProducts"),
            pl.sum("Quantity").alias("TotalQuantity"),
            pl.n_unique("InvoiceNo").alias("NumberOrders")
        ])
        .sort("TotalRevenue", descending=True)
        .collect()
    )
    
    return top_products, price_stats

def calculate_customer_metrics(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calcule les métriques clients (RFM) avec Polars.
    
    Cette fonction utilise les capacités natives de Polars pour l'analyse RFM :
    - Récence (R) : Calculée en jours à partir des dates de commande
    - Fréquence (F) : Nombre de commandes
    - Montant (M) : Valeur totale des achats
    
    Args:
        df: DataFrame avec les données nettoyées
        
    Returns:
        DataFrame avec les métriques RFM et la segmentation client
    """
    print("\nCalcul des métriques RFM de base...")

    # Calcul de la date de référence (dernier jour du dataset)
    reference_date = df["OrderDate"].dt.date().max()
    print(f"Date de référence pour le calcul de récence : {reference_date}")
    
    # Calcul des métriques RFM de base
    customer_metrics = (
        df.lazy()
        .group_by("CustomerID")
        .agg([
            # La récence est calculée en jours
            ((pl.lit(reference_date) - pl.col("OrderDate").dt.date().max())\
             .cast(pl.Duration("ns")) / pl.duration(days=1)).alias("Recency"),
            pl.n_unique("InvoiceNo").alias("Frequency"),
            pl.sum("Revenue").alias("MonetaryValue")
        ])
        .collect()
    )

    
    print("\nCalcul des scores RFM...")
    # Configuration des métriques pour le scoring
    metrics_config = [
        ("Recency", True),       # Plus petit = meilleur
        ("Frequency", False),    # Plus grand = meilleur
        ("MonetaryValue", False) # Plus grand = meilleur
    ]
    
    # Calcul des scores pour chaque dimension
    for metric, reverse in metrics_config:
        print(f"\nTraitement de la métrique: {metric}")
        # Calcul des quartiles
        q1 = float(customer_metrics[metric].quantile(0.25))
        q2 = float(customer_metrics[metric].quantile(0.50))
        q3 = float(customer_metrics[metric].quantile(0.75))
        
        print(f"Seuils pour {metric}:")
        print(f"- Q1 (25%): {q1:.2f}")
        print(f"- Q2 (50%): {q2:.2f}")
        print(f"- Q3 (75%): {q3:.2f}")
        
        # Attribution des scores selon le sens de la métrique
        if reverse:
            score_expr = (
                pl.when(pl.col(metric) >= q3).then(1)
                .when(pl.col(metric) >= q2).then(2)
                .when(pl.col(metric) >= q1).then(3)
                .otherwise(4)
            )
        else:
            score_expr = (
                pl.when(pl.col(metric) <= q1).then(1)
                .when(pl.col(metric) <= q2).then(2)
                .when(pl.col(metric) <= q3).then(3)
                .otherwise(4)
            )
        
        customer_metrics = customer_metrics.with_columns([
            score_expr.alias(f"{metric}_Score")
        ])
    
    print("\nCalcul du score RFM combiné...")
    # Création du score RFM combiné (format : RFM)
    customer_metrics = customer_metrics.with_columns([
        pl.concat_str([
            pl.col("Recency_Score").cast(pl.Utf8),
            pl.col("Frequency_Score").cast(pl.Utf8),
            pl.col("MonetaryValue_Score").cast(pl.Utf8)
        ]).alias("RFM_Score")
    ])
    
    print("Attribution des segments RFM...")
    # Segmentation des clients selon leur score RFM
    customer_metrics = customer_metrics.with_columns([
        pl.when(pl.col("RFM_Score").str.contains("^[34][34][34]$"))
        .then(pl.lit("Champions"))
        .when(pl.col("RFM_Score").str.contains("^[12][34][34]$"))
        .then(pl.lit("Clients Loyaux"))
        .when(pl.col("RFM_Score").str.contains("^[12][12][34]$"))
        .then(pl.lit("Clients Potentiels"))
        .otherwise(pl.lit("Clients à Réactiver"))
        .alias("RFM_Segment")
    ])
    
    # Analyse des segments
    segment_stats = (
        customer_metrics
        .group_by("RFM_Segment")
        .agg([
            pl.count("CustomerID").alias("Nombre_Clients"),
            pl.mean("MonetaryValue").round(2).alias("Panier_Moyen")
        ])
        .sort("Nombre_Clients", descending=True)
    )
    
    print("\nStatistiques par segment RFM :")
    print(segment_stats)
    
    return customer_metrics

def calculate_temporal_kpis(df: pl.DataFrame) -> dict[str, pl.DataFrame]:
    """
    Calcule les KPIs temporels avec Polars.
    """
    # Analyse des ventes quotidiennes
    daily_sales = (
        df.lazy()
        .group_by("OrderDate")  # Syntaxe Polars
        .agg([
            pl.sum("Revenue").alias("Revenue"),
            pl.n_unique("InvoiceNo").alias("Orders"),
            pl.sum("Quantity").alias("Items")
        ])
        .sort("OrderDate")
        .collect()
    )
    
    # Analyse par jour de la semaine
    weekday_sales = (
        df.lazy()
        .group_by("WeekDay")  # Syntaxe Polars
        .agg([
            pl.sum("Revenue").alias("Revenue"),
            pl.mean("Revenue").alias("AverageRevenue")
        ])
        .sort("WeekDay")
        .collect()
    )
    
    # Analyse par heure
    hourly_sales = (
        df.lazy()
        .group_by("Hour")  # Syntaxe Polars
        .agg([
            pl.sum("Revenue").alias("Revenue"),
            pl.mean("Revenue").alias("AverageRevenue")
        ])
        .sort("Hour")
        .collect()
    )
    
    return {
        "daily": daily_sales,
        "weekday": weekday_sales,
        "hourly": hourly_sales
    }

def generate_kpi_report(df: pl.DataFrame) -> dict[str, Any]:
    """
    Génère un rapport complet avec tous les KPIs.
    """
    print("Calcul des KPIs globaux...")
    global_kpis = calculate_global_kpis(df)
    
    print("Analyse des produits...")
    top_products, price_stats = analyze_products(df)
    
    print("Calcul des métriques clients...")
    customer_metrics = calculate_customer_metrics(df)
    
    print("Analyse temporelle...")
    temporal_kpis = calculate_temporal_kpis(df)
    
    return {
        "global_kpis": global_kpis,
        "top_products": top_products,
        "price_analysis": price_stats,
        "customer_metrics": customer_metrics,
        "temporal_analysis": temporal_kpis
    }