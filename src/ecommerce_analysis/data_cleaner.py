"""Module pour le nettoyage et la préparation des données e-commerce."""
import polars as pl
from datetime import datetime

def format_numeric_columns(df: pl.DataFrame) -> pl.DataFrame:
    """
    Formate les colonnes numériques (conversion des séparateurs décimaux).
    
    Cette fonction gère la conversion des nombres au format européen (virgule)
    vers le format standard (point).
    
    Args:
        df: DataFrame avec les données brutes
        
    Returns:
        DataFrame avec colonnes numériques formatées
    """
    return df.with_columns([
        pl.col("UnitPrice")
          .str.replace(",", ".")
          .cast(pl.Float64)
          .alias("UnitPrice")
    ])

def parse_dates(df: pl.DataFrame) -> pl.DataFrame:
    """
    Parse les dates en format datetime avec gestion robuste des formats.
    
    Cette fonction gère intelligemment différents formats de dates possibles,
    notamment avec ou sans secondes. Elle inclut également une validation
    des données pour détecter d'éventuelles anomalies.
    
    Args:
        df: DataFrame avec dates en format texte
        
    Returns:
        DataFrame avec dates converties en datetime
        
    Example:
        Formats gérés :
        - "DD/MM/YYYY HH:MM:SS"
        - "DD/MM/YYYY HH:MM"
    """
    # Affichage d'exemples pour le diagnostic
    sample_dates = df["InvoiceDate"].head(5)
    print("\nExemples de dates à parser :")
    for date in sample_dates:
        print(f"- {date}")
    
    try:
        # Première tentative : format avec secondes
        return df.with_columns([
            pl.col("InvoiceDate")
              .str.strptime(
                  pl.Datetime,
                  format="%d/%m/%Y %H:%M:%S"
              )
              .alias("OrderDate")
        ])
    except Exception as e1:
        print(f"\nTentative avec format HH:MM:SS échouée: {str(e1)}")
        try:
            print("Tentative avec format HH:MM...")
            # Deuxième tentative : format sans secondes
            return df.with_columns([
                pl.col("InvoiceDate")
                  .str.strptime(
                      pl.Datetime,
                      format="%d/%m/%Y %H:%M"
                  )
                  .alias("OrderDate")
            ])
        except Exception as e2:
            print(f"\nErreur lors du parsing des dates : {str(e2)}")
            print("\nAnalyse des formats de date présents dans le dataset :")
            
            # Extraction d'un échantillon de dates problématiques
            sample_problematic = (
                df.select(pl.col("InvoiceDate"))
                  .sample(n=5)
                  .collect()
            )
            
            print("\nÉchantillon de dates problématiques :")
            for date in sample_problematic["InvoiceDate"]:
                print(f"- {date}")
            
            raise Exception("Impossible de parser les dates avec les formats connus")

def create_price_categories(df: pl.DataFrame) -> pl.DataFrame:
    """
    Crée les catégories de prix basées sur les quartiles.
    
    Cette fonction utilise une approche en trois étapes :
    1. Calcul des seuils de prix (33% et 66%)
    2. Création des catégories (bas, moyen, premium)
    3. Attribution des catégories aux produits
    
    Args:
        df: DataFrame nettoyé avec prix unitaires
        
    Returns:
        DataFrame avec la nouvelle colonne PriceCategory
    """
    # Calcul des seuils de prix
    try:
        # Calcul des quantiles individuellement
        low_threshold = df.select(
            pl.col("UnitPrice").quantile(0.33)
        ).item()
        
        high_threshold = df.select(
            pl.col("UnitPrice").quantile(0.66)
        ).item()
        
        print(f"Seuils de prix - Bas: {low_threshold:.2f}, Haut: {high_threshold:.2f}")
        
        # Attribution des catégories
        return df.with_columns([
            pl.when(pl.col("UnitPrice") <= low_threshold)
              .then(pl.lit("bas"))
              .when(pl.col("UnitPrice") <= high_threshold)
              .then(pl.lit("moyen"))
              .otherwise(pl.lit("premium"))
              .alias("PriceCategory")
        ])
        
    except Exception as e:
        print(f"Erreur lors de la création des catégories de prix: {str(e)}")
        raise

def clean_retail_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Nettoie les données retail en appliquant plusieurs transformations.
    
    Cette fonction applique une série de transformations dans un ordre précis :
    1. Formatage des colonnes numériques
    2. Filtrage des valeurs invalides
    3. Conversion des dates
    4. Calcul des revenus
    5. Ajout de features temporelles
    6. Création des catégories de prix
    
    Args:
        df: DataFrame Polars brut
        
    Returns:
        DataFrame nettoyé avec colonnes additionnelles
    """
    try:
        # 1. Formatage des colonnes numériques
        print("1. Formatage des colonnes numériques...")
        cleaned = format_numeric_columns(df)
        
        # 2. Filtrage des valeurs invalides
        print("2. Filtrage des valeurs invalides...")
        cleaned = cleaned.filter(
            (pl.col("Quantity") > 0) &
            (pl.col("UnitPrice") > 0)
        )
        
        # 3. Conversion des dates
        print("3. Conversion des dates...")
        cleaned = parse_dates(cleaned)
        
        # 4. Calcul du revenu par ligne
        print("4. Calcul des revenus...")
        cleaned = cleaned.with_columns([
            (pl.col("Quantity") * pl.col("UnitPrice")).alias("Revenue")
        ])
        
        # 5. Extraction de features temporelles
        print("5. Extraction des features temporelles...")
        cleaned = cleaned.with_columns([
            pl.col("OrderDate").dt.month().alias("Month"),
            pl.col("OrderDate").dt.weekday().alias("WeekDay"),
            pl.col("OrderDate").dt.hour().alias("Hour")
        ])
        
        # 6. Création des catégories de prix
        print("6. Création des catégories de prix...")
        cleaned = create_price_categories(cleaned)
        
        # 7. Suppression des lignes avec CustomerID manquant
        print("7. Nettoyage final...")
        cleaned = cleaned.filter(pl.col("CustomerID").is_not_null())
        
        print(f"Nettoyage terminé : {cleaned.shape[0]} lignes conservées")
        return cleaned
        
    except Exception as e:
        print(f"Erreur lors du nettoyage des données: {str(e)}")
        raise


def add_advanced_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Ajoute des features avancées pour l'analyse.
    
    Features ajoutées :
    - Catégorie de prix (bas, moyen, premium)
    - Flag pour les commandes importantes
    - Segment horaire (matin, après-midi, soir)

    Args:
        df: DataFrame nettoyé

    Returns:
        DataFrame avec features additionnelles
    """
    # Calcul des seuils de prix (quartiles)
    price_quantiles = df.select(pl.col("UnitPrice").quantile([0.33, 0.66]))
    low_threshold = price_quantiles[0, 0]
    high_threshold = price_quantiles[0, 1]
    
    # Ajout des features
    return df.with_columns([
        # Catégorie de prix
        pl.when(pl.col("UnitPrice") <= low_threshold).then("bas")
        .when(pl.col("UnitPrice") <= high_threshold).then("moyen")
        .otherwise("premium")
        .alias("PriceCategory"),
        
        # Flag pour commandes importantes
        (pl.col("Quantity") > df.select(pl.col("Quantity").mean())[0, 0])
        .alias("IsLargeOrder"),
        
        # Segment horaire
        pl.when(pl.col("Hour").is_between(6, 11)).then("matin")
        .when(pl.col("Hour").is_between(12, 17)).then("après-midi")
        .otherwise("soir")
        .alias("TimeSegment")
    ])


def validate_data(df: pl.DataFrame) -> bool:
    """
    Valide la qualité des données nettoyées.
    
    Vérifie :
    - Absence de valeurs négatives pour Quantity et UnitPrice
    - Présence des colonnes calculées
    - Cohérence des dates
    
    Args:
        df: DataFrame à valider

    Returns:
        True si les données sont valides, False sinon
    """
    try:
        # Vérification des colonnes requises
        required_columns = ["Revenue", "OrderDate", "Month", "WeekDay"]
        if not all(col in df.columns for col in required_columns):
            print("Colonnes manquantes")
            return False
            
        # Vérification des valeurs négatives
        if df.filter(
            (pl.col("Quantity") <= 0) | (pl.col("UnitPrice") <= 0)
        ).height > 0:
            print("Valeurs négatives détectées")
            return False
            
        # Vérification des dates
        if df.filter(pl.col("OrderDate").is_null()).height > 0:
            print("Dates invalides détectées")
            return False
            
        return True
        
    except Exception as e:
        print(f"Erreur lors de la validation : {str(e)}")
        return False