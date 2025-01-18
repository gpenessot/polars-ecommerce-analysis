"""Point d'entrée principal pour l'analyse e-commerce."""

import logging
import sys
from pathlib import Path
from datetime import datetime

from ecommerce_analysis.data_loader import load_retail_data
from ecommerce_analysis.data_cleaner import clean_retail_data
from ecommerce_analysis.kpi_calculator import generate_kpi_report
from ecommerce_analysis.quarto_exporter import QuartoExporter

def setup_logging(log_file: Path = None):
    """Configure le logging pour écrire dans un fichier et la console."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger

def run_analysis(input_file: Path, output_dir: Path, template_dir: Path):
    """
    Exécute l'analyse complète des données e-commerce.
    
    Args:
        input_file: Chemin vers le fichier de données brutes
        output_dir: Répertoire pour sauvegarder les résultats
        template_dir: Répertoire contenant les templates Quarto
    """
    print(f"Démarrage de l'analyse...")
    print(f"Fichier d'entrée: {input_file}")
    print(f"Répertoire de sortie: {output_dir}")
    
    try:
        # Vérification du fichier d'entrée
        if not input_file.exists():
            raise FileNotFoundError(f"Le fichier {input_file} n'existe pas!")
        
        # 1. Chargement des données
        print("Chargement des données en cours...")
        df = load_retail_data(input_file)
        print(f"Données chargées: {df.shape[0]} lignes et {df.shape[1]} colonnes")
        
        # 2. Nettoyage des données
        print("Nettoyage des données en cours...")
        df_clean = clean_retail_data(df)
        print(f"Données nettoyées: {df_clean.shape[0]} lignes restantes")
        
        # 3. Calcul des KPIs
        print("Calcul des KPIs en cours...")
        kpi_report = generate_kpi_report(df_clean)
        
        # 4. Export des résultats au format Quarto
        print("Préparation du rapport Quarto...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = output_dir / f"report_{timestamp}"
        
        # Initialisation de l'exporteur Quarto
        exporter = QuartoExporter(template_dir, report_dir)
        
        # Préparation des répertoires et copie des templates
        print("Configuration des répertoires...")
        exporter.setup_directories()
        
        # Export des résultats
        print("Export des résultats...")
        exporter.export_results(kpi_report)
        
        # Génération du rapport
        print("Génération du rapport Quarto...")
        try:
            exporter.render_report()
            print(f"Rapport généré avec succès dans : {report_dir}")
        except Exception as e:
            print(f"Attention : {str(e)}")
            print("Le rapport devra être généré manuellement avec 'quarto render'")
        
        return report_dir
        
    except Exception as e:
        print(f"Erreur lors de l'analyse: {str(e)}", file=sys.stderr)
        raise

def main():
    """Fonction principale."""
    # Définition des chemins par défaut
    root_dir = Path(__file__).parent
    input_file = root_dir / "data" / "raw" / "online_retail.csv"
    output_dir = root_dir / "data" / "processed"
    template_dir = root_dir / "templates" / "quarto"
    log_file = root_dir / "logs" / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Création du répertoire des logs
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configuration du logging
    logger = setup_logging(log_file)
    
    try:
        run_analysis(input_file, output_dir, template_dir)
    except Exception as e:
        logger.error(f"L'analyse a échoué: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()