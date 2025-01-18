"""Module pour la création de visualisations e-commerce interactives.

Ce module fournit des fonctions spécialisées pour créer des visualisations
pertinentes pour l'analyse e-commerce. Il utilise Plotly pour générer des
graphiques interactifs et professionnels qui peuvent être utilisés dans
des dashboards ou des rapports.

Les visualisations sont organisées en trois catégories principales :
1. Analyse temporelle (tendances des ventes, patterns saisonniers)
2. Analyse produits (top produits, catégories, prix)
3. Analyse clients (segmentation, comportement d'achat)
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl
from typing import Dict, Any
import numpy as np


class EcommerceVisualizer:
    """Classe pour la création de visualisations e-commerce."""
    
    def __init__(self, template: str = "plotly_white"):
        """
        Initialise le visualizer avec un template spécifique.
        
        Args:
            template: Template Plotly à utiliser pour tous les graphiques
        """
        self.template = template
        self.colors = px.colors.qualitative.Set3
    
    def create_temporal_dashboard(self, df: pl.DataFrame) -> go.Figure:
        """
        Crée un dashboard d'analyse temporelle complet.
        
        Ce dashboard combine plusieurs visualisations temporelles :
        - Évolution du CA quotidien
        - Répartition par jour de la semaine
        - Distribution horaire des ventes
        
        Args:
            df: DataFrame avec les données temporelles
            
        Returns:
            Figure Plotly avec le dashboard complet
        """
        # Création d'un dashboard avec sous-graphiques
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Évolution du chiffre d'affaires",
                "Ventes par jour de la semaine",
                "Distribution horaire des ventes"
            ),
            specs=[[{"colspan": 2}, None],
                  [{}, {}]],
            vertical_spacing=0.12
        )
        
        # 1. Évolution du CA quotidien
        daily_revenue = (df.group_by("OrderDate")
                          .agg(pl.sum("Revenue"))
                          .sort("OrderDate")
                          .to_pandas())
        
        fig.add_trace(
            go.Scatter(
                x=daily_revenue["OrderDate"],
                y=daily_revenue["Revenue"],
                mode="lines",
                name="CA quotidien",
                line=dict(color=self.colors[0])
            ),
            row=1, col=1
        )
        
        # 2. Répartition par jour de la semaine
        weekday_data = (df.group_by("WeekDay")
                         .agg(pl.sum("Revenue"))
                         .sort("WeekDay")
                         .to_pandas())
        
        fig.add_trace(
            go.Bar(
                x=weekday_data["WeekDay"],
                y=weekday_data["Revenue"],
                name="CA par jour",
                marker_color=self.colors[1]
            ),
            row=2, col=1
        )
        
        # 3. Distribution horaire
        hourly_data = (df.group_by("Hour")
                        .agg(pl.sum("Revenue"))
                        .sort("Hour")
                        .to_pandas())
        
        fig.add_trace(
            go.Bar(
                x=hourly_data["Hour"],
                y=hourly_data["Revenue"],
                name="CA par heure",
                marker_color=self.colors[2]
            ),
            row=2, col=2
        )
        
        # Mise en forme globale
        fig.update_layout(
            height=800,
            title_text="Analyse temporelle des ventes",
            showlegend=True,
            template=self.template
        )
        print('create_temporal_dashboard Done')
        return fig
    
    def create_product_dashboard(self, df: pl.DataFrame) -> go.Figure:
        """
        Crée un dashboard d'analyse produits.
        
        Combine plusieurs visualisations sur les produits :
        - Top 10 des produits
        - Matrice prix/quantité
        - Distribution des prix
        
        Args:
            df: DataFrame avec les données produits
            
        Returns:
            Figure Plotly avec le dashboard produits
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Top 10 des produits",
                "Matrice prix/quantité",
                "Distribution des prix"
            ),
            specs=[[{"colspan": 2}, None],
                  [{}, {}]],
            vertical_spacing=0.12
        )
        
        # 1. Top 10 des produits
        top_products = (df.group_by(["StockCode", "Description"])
                         .agg(pl.sum("Revenue").alias("TotalRevenue"))
                         .sort("TotalRevenue", descending=True)
                         .limit(10)
                         .to_pandas())
        
        fig.add_trace(
            go.Bar(
                x=top_products["Description"],
                y=top_products["TotalRevenue"],
                marker_color=self.colors[0]
            ),
            row=1, col=1
        )
        
        # 2. Matrice prix/quantité
        fig.add_trace(
            go.Scatter(
                x=df["UnitPrice"].to_pandas(),
                y=df["Quantity"].to_pandas(),
                mode="markers",
                marker=dict(
                    size=8,
                    color=self.colors[1],
                    opacity=0.6
                ),
                name="Produits"
            ),
            row=2, col=1
        )
        
        # 3. Distribution des prix
        fig.add_trace(
            go.Histogram(
                x=df["UnitPrice"].to_pandas(),
                nbinsx=30,
                marker_color=self.colors[2]
            ),
            row=2, col=2
        )
        
        # Mise en forme
        fig.update_layout(
            height=800,
            title_text="Analyse des produits",
            template=self.template
        )
        
        fig.update_xaxes(tickangle=45, row=1, col=1)
        print('create_product_dashboard Done')
        return fig
    
    def create_customer_dashboard(self, df: pl.DataFrame) -> go.Figure:
        """
        Crée un dashboard d'analyse clients avec segmentation RFM.
        
        Cette fonction calcule et visualise :
        1. Une segmentation RFM (Recency, Frequency, Monetary) des clients
        2. La distribution des paniers moyens
        3. L'analyse de la fréquence d'achat
        
        Le score RFM est calculé en divisant chaque métrique en quartiles :
        - R4 = clients les plus récents à R1 = clients les moins récents
        - F4 = clients les plus fréquents à F1 = clients les moins fréquents
        - M4 = clients à plus haute valeur à M1 = clients à plus faible valeur
        """
        # Calcul des métriques clients
        reference_date = df["OrderDate"].dt.date().max()

        customer_metrics = (df.group_by("CustomerID")
                            .agg([
                                pl.sum("Revenue").alias("TotalRevenue"),
                                pl.count("InvoiceNo").alias("Frequency"),
                                ((pl.lit(reference_date) - pl.col("OrderDate")
                                  .dt.date()
                                  .max())
                                  .cast(pl.Duration("ns")) / pl.duration(days=1))
                                  .alias("LastOrder")
                            ]))
        

        print(customer_metrics.head())
        # Attribution des scores RFM
        r_labels = ["R4", "R3", "R2", "R1"]
        f_labels = ["F1", "F2", "F3", "F4"]
        m_labels = ["M1", "M2", "M3", "M4"]
        
        r_quantiles = [customer_metrics["LastOrder"].quantile(i) for i in [.25, 0.5, 0.75]]
        f_quantiles = [customer_metrics["Frequency"].quantile(i) for i in [.25, 0.5, 0.75]]
        m_quantiles = [customer_metrics["TotalRevenue"].quantile(i) for i in [.25, 0.5, 0.75]]
        
        print(r_quantiles)
        print(f_quantiles)
        print(m_quantiles)

        # Fonction auxiliaire pour attribuer les scores
        def assign_score(value, quantiles, labels):
            if value <= quantiles[0]:
                return labels[0]
            elif value <= quantiles[1]:
                return labels[1]
            elif value <= quantiles[2]:
                return labels[2]
            else:
                return labels[3]

        # Attribution des scores RFM
        customer_metrics = customer_metrics.with_columns([
            pl.col("LastOrder").map_elements(
                lambda x: assign_score(x, r_quantiles, r_labels)
            ).alias("R_Score"),
            pl.col("Frequency").map_elements(
                lambda x: assign_score(x, f_quantiles, f_labels)
            ).alias("F_Score"),
            pl.col("TotalRevenue").map_elements(
                lambda x: assign_score(x, m_quantiles, m_labels)
            ).alias("M_Score")
        ])
        
        # Création du dashboard avec les scores RFM
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Segmentation RFM",
                "Distribution des paniers moyens",
                "Fréquence d'achat"
            ),
            specs=[[{"colspan": 2, "type": "scene"}, None],
                [{"type": "xy"}, {"type": "xy"}]],
            vertical_spacing=0.12
        )
        
        # 1. Visualisation 3D avec couleurs basées sur le score RFM
        customer_data = customer_metrics.to_pandas()
        
        # Calcul d'un score composite pour la couleur
        customer_data["RFM_Score"] = (
            customer_data["R_Score"].str[1].astype(int) + 
            customer_data["F_Score"].str[1].astype(int) + 
            customer_data["M_Score"].str[1].astype(int)
        )

        fig.add_trace(
            go.Scatter3d(
                x=customer_metrics["LastOrder"].to_pandas(),
                y=customer_metrics["Frequency"].to_pandas(),
                z=customer_metrics["TotalRevenue"].to_pandas(),
                mode="markers",
                marker=dict(
                    size=5,
                    color=customer_data["RFM_Score"],
                    colorscale="Viridis",
                    opacity=0.7,
                    colorbar=dict(
                        title="Score RFM",
                        ticktext=["Faible", "Moyen", "Élevé"],
                        tickvals=[3, 6, 9]
                    )
                ),
                text=[f"R:{r} F:{f} M:{m}" for r, f, m in 
                    zip(customer_data["R_Score"], 
                        customer_data["F_Score"], 
                        customer_data["M_Score"])],
                hovertemplate="R:%{text}<br>Freq.:%{y}<br>Rev.:%{z}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # 2. Distribution des paniers moyens
        avg_basket = (df.group_by("InvoiceNo")
                       .agg(pl.sum("Revenue"))
                       .to_pandas())
        
        fig.add_trace(
            go.Histogram(
                x=avg_basket["Revenue"],
                nbinsx=50,
                marker_color=self.colors[1]
            ),
            row=2, col=1
        )
        
        # 3. Fréquence d'achat
        fig.add_trace(
            go.Histogram(
                x=customer_metrics["Frequency"].to_pandas(),
                nbinsx=50,
                marker_color=self.colors[2]
            ),
            row=2, col=2
        )
        
        # Mise en forme
        fig.update_layout(
            height=800,
            title_text="Analyse des clients",
            template=self.template,
            scene=dict(
                xaxis_title="Récence",
                yaxis_title="Fréquence",
                zaxis_title="Montant"
            )
        )
        
        return fig
    
    def create_full_report(self, df: pl.DataFrame) -> dict[str, go.Figure]:
        """
        Crée un rapport complet avec tous les dashboards.
        
        Args:
            df: DataFrame avec toutes les données
            
        Returns:
            Dictionnaire contenant tous les dashboards
        """
        return {
            "temporal_analysis": self.create_temporal_dashboard(df),
            "product_analysis": self.create_product_dashboard(df),
            "customer_analysis": self.create_customer_dashboard(df)
        }
    
    def save_report(self, report: dict[str, go.Figure], output_dir: str):
        """
        Sauvegarde tous les graphiques du rapport au format HTML.
        
        Args:
            report: Dictionnaire des figures à sauvegarder
            output_dir: Répertoire de destination
        """
        import os
        
        for name, fig in report.items():
            output_path = os.path.join(output_dir, f"{name}.html")
            fig.write_html(output_path)