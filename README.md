# Analyse E-commerce avec Polars

Ce projet fournit une suite d'outils pour l'analyse de données e-commerce en utilisant des technologies modernes comme Polars et Plotly. Il permet d'analyser en détail les performances de vente, le comportement client et les tendances temporelles.

## 🎯 Fonctionnalités

* Analyse complète des KPIs e-commerce
* Segmentation client avec analyse RFM
* Analyse des performances produits
* Visualisations interactives avec Plotly
* Génération de rapports automatisés avec Quarto

## 🛠️ Technologies Utilisées

* **Polars**: Pour le traitement efficace des données
* **Plotly**: Pour les visualisations interactives
* **Quarto**: Pour la génération de rapports
* **Click**: Pour l'interface en ligne de commande
* **PyArrow**: Pour l'optimisation des performances

## 📦 Installation

1. Clonez le repository :
```bash
git clone https://github.com/votre-username/polars-ecommerce-analysis.git
cd polars-ecommerce-analysis
```

2. Créez un environnement virtuel et installez les dépendances :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
pip install -e .
```

3. Installez Quarto :
```bash
# Sur Ubuntu/Debian
wget https://quarto.org/download/latest/quarto-linux-amd64.deb
sudo dpkg -i quarto-linux-amd64.deb

# Sur Windows avec winget
winget install --id RProject.quarto
```

## 📊 Structure du Projet

```
polars-ecommerce-analysis/
│
├── src/
│   └── ecommerce_analysis/
│       ├── __init__.py
│       ├── cli.py           # Interface en ligne de commande
│       ├── data_loader.py   # Chargement des données
│       ├── data_cleaner.py  # Nettoyage des données
│       ├── kpi_calculator.py # Calcul des KPIs
│       ├── visualizer.py    # Création des graphiques
│       └── quarto_exporter.py # Export des rapports
│
├── templates/
│   └── quarto/
│       └── template.qmd     # Template de rapport
│
├── tests/                   # Tests unitaires
│
├── main.py                  # Point d'entrée principal
└── pyproject.toml          # Configuration du projet
```

## 🚀 Utilisation

1. Préparez votre fichier de données e-commerce au format CSV
2. Lancez l'analyse via le CLI :
```bash
python -m ecommerce_analysis.cli analyze /chemin/vers/donnees.csv /chemin/sortie --template-dir /chemin/templates
```

3. Consultez le rapport généré dans le dossier de sortie

## 📝 Format des Données

Le fichier CSV doit contenir les colonnes suivantes :
* InvoiceNo
* StockCode
* Description
* Quantity
* InvoiceDate
* UnitPrice
* CustomerID
* Country

## 🔍 Analyses Générées

Le rapport inclut :
* Vue d'ensemble des performances e-commerce
* Analyse produits et catégories de prix
* Segmentation client RFM
* Analyse temporelle des ventes
* Tableaux de bord interactifs
* Recommandations stratégiques

## 📚 Utilisation dans vos Scripts

```python
from ecommerce_analysis import (
    load_retail_data,
    clean_retail_data,
    generate_kpi_report
)

# Chargement et nettoyage des données
df = load_retail_data("data/raw/online_retail.csv")
df_clean = clean_retail_data(df)

# Génération du rapport complet
report = generate_kpi_report(df_clean)
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 🔍 Qualité du Code

Le projet utilise :
- Ruff pour le linting
- pytest pour les tests
- Typage statique avec annotations

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## ✨ Remerciements

Ce projet utilise plusieurs bibliothèques open source remarquables :
* Polars
* Plotly
* Quarto
* Click
* PyArrow

## ✍️ Auteur

Créé avec ❤️ par [Gaël Penessot](https://www.linkedin.com/in/gael-penessot), auteur de [Business Intelligence with Python](https://amzn.to/42jjs1o)