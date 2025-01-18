"""Interface en ligne de commande pour l'analyse e-commerce."""

import click
from pathlib import Path
from main import run_analysis

@click.group()
def cli():
    """Outil d'analyse de données e-commerce."""
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument('output_dir', type=click.Path(file_okay=False, path_type=Path))
@click.option('--template-dir', 
              type=click.Path(exists=True, file_okay=False, path_type=Path),
              help='Répertoire contenant les templates Quarto')
@click.option('--debug/--no-debug', default=False, help='Active le mode debug')
def analyze(input_file: Path, output_dir: Path, template_dir: Path, debug: bool):
    """Lance l'analyse complète des données e-commerce.
    
    Args:
        input_file: Chemin vers le fichier CSV de données
        output_dir: Répertoire où sauvegarder les résultats
        template_dir: Répertoire contenant les templates Quarto
    """
    if debug:
        click.echo("Mode debug activé")
    
    if not template_dir:
        template_dir = Path(__file__).parent / "templates" / "quarto"
    
    try:
        report_dir = run_analysis(input_file, output_dir, template_dir)
        click.echo(f"Analyse terminée ! Rapport disponible dans : {report_dir}")
    except Exception as e:
        click.echo(f"Erreur : {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()