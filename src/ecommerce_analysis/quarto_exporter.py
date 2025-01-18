"""Module pour l'export des résultats au format Quarto."""

import json
import shutil
import os
from pathlib import Path
from typing import Dict, Any
import polars as pl

class QuartoExporter:
    """Classe pour exporter les résultats d'analyse au format Quarto."""
    
    def __init__(self, template_dir: Path, output_dir: Path):
        """
        Initialise l'exporteur Quarto.
        
        Args:
            template_dir: Répertoire contenant les templates Quarto
            output_dir: Répertoire de sortie pour le rapport
        """
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.results_dir = self.output_dir / "results"
        
    def setup_directories(self):
        """Prépare les répertoires pour l'export."""
        # Création des répertoires nécessaires
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Copie du template principal
        template_qmd = self.template_dir / "template.qmd"
        if not template_qmd.exists():
            raise FileNotFoundError(f"Template Quarto non trouvé: {template_qmd}")
            
        # Copie et modification du template avec les bons chemins
        with open(template_qmd, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Remplacer le chemin des résultats dans le template
        template_content = template_content.replace(
            'results_dir = os.getenv(\'RESULTS_DIR\', \'results\')',
            f'results_dir = "{str(self.results_dir)}"'
        )
        
        # Écrire le template modifié
        with open(self.output_dir / "report.qmd", 'w', encoding='utf-8') as f:
            f.write(template_content)
        
    def export_results(self, results: Dict[str, Any]):
        """
        Exporte les résultats au format approprié pour Quarto.
        
        Args:
            results: Dictionnaire contenant tous les résultats d'analyse
        """
        print(f"Export des résultats vers {self.results_dir}")
        
        # Export des KPIs globaux en JSON
        with open(self.results_dir / "global_kpis.json", "w", encoding='utf-8') as f:
            json.dump(results["global_kpis"], f, indent=2, ensure_ascii=False)
        
        # Export des analyses produits
        results["top_products"].write_csv(self.results_dir / "top_products.csv")
        results["price_analysis"].write_csv(self.results_dir / "price_analysis.csv")
        
        # Export des métriques clients
        results["customer_metrics"].write_csv(self.results_dir / "customer_metrics.csv")
        
        # Export des analyses temporelles
        for key, df in results["temporal_analysis"].items():
            df.write_csv(self.results_dir / f"temporal_{key}.csv")
            
    def render_report(self):
        """Lance le rendu du rapport Quarto."""
        import subprocess
        
        try:
            print("Génération du rapport Quarto...")
            print(f"Répertoire de travail : {self.output_dir}")
            print(f"Fichiers disponibles : {list(self.results_dir.glob('*'))}")
            
            # Définir les variables d'environnement pour Quarto
            env = os.environ.copy()
            env["RESULTS_DIR"] = str(self.results_dir)
            
            # Exécuter quarto dans le bon répertoire
            subprocess.run([
                "quarto", "render", 
                "report.qmd",
                "--embed-resources"
            ], check=True, cwd=self.output_dir, env=env)
            
            print(f"Rapport généré avec succès: {self.output_dir}/report.html")
            
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du rendu Quarto: {str(e)}")
            raise
        except FileNotFoundError:
            print("Quarto n'est pas installé ou n'est pas dans le PATH")
            print("Rendez le rapport manuellement avec: quarto render report.qmd")