"""Module pour charger les données e-commerce."""
import polars as pl
from pathlib import Path
from typing import Union

def get_retail_schema() -> dict:
    """
    Définit le schéma pour les données retail.
    
    Returns:
        Dictionnaire définissant les types de colonnes
    """
    return {
        "InvoiceNo": pl.Utf8,
        "StockCode": pl.Utf8,
        "Description": pl.Utf8,
        "Quantity": pl.Int32,
        "InvoiceDate": pl.Utf8,
        "UnitPrice": pl.Utf8,
        "CustomerID": pl.Float64,
        "Country": pl.Utf8
    }

def load_retail_data(file_path: Union[str, Path]) -> pl.DataFrame:
    """
    Charge les données brutes depuis un fichier CSV.
    
    Args:
        file_path: Chemin vers le fichier de données
        
    Returns:
        DataFrame Polars contenant les données brutes
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
        
    if not file_path.exists():
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
    
    # Chargement avec le schéma prédéfini
    return pl.read_csv(
        file_path,
        schema=get_retail_schema(),
        separator=",",
        try_parse_dates=False,
        encoding="utf8"
    )