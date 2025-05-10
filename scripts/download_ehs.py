"""
Script pour télécharger les directives EHS de l'IFC.
"""
import os
import requests
from tqdm import tqdm
from loguru import logger

# URL de base pour les directives EHS
IFC_EHS_BASE_URL = "https://www.ifc.org/wps/wcm/connect/topics_ext_content/ifc_external_corporate_site/sustainability-at-ifc/company-resources/ehs-guidelines/"

# Liste des directives EHS à télécharger
EHS_GUIDELINES = [
    "2007-mining-ehs-guidelines-en.pdf",
    "2007-onshore-oil-gas-development-ehs-guidelines-en.pdf",
    "2015-offshore-oil-gas-development-ehs-guidelines-en.pdf",
    "2017-lng-ehs-guidelines-en.pdf",
    "2015-wind-energy-ehs-guidelines-en.pdf",
    "2008-thermal-power-ehs-guidelines-en.pdf",
    "2007-geothermal-power-generation-ehs-guidelines-en.pdf",
    "2007-electric-transmission-distribution-ehs-guidelines-en.pdf",
    "2007-water-and-sanitation-ehs-guidelines-en.pdf",
    "2007-waste-management-facilities-ehs-guidelines-en.pdf",
    "2007-tourism-hospitality-development-ehs-guidelines-en.pdf",
    "2007-toll-roads-ehs-guidelines-en.pdf",
    "2007-telecommunications-ehs-guidelines-en.pdf",
    "2007-shipping-ehs-guidelines-en.pdf",
    "2007-retail-petroleum-networks-ehs-guidelines-en.pdf",
    "2007-railways-ehs-guidelines-en.pdf",
    "2017-ports-harbors-terminals-ehs-guidelines-en.pdf",
    "2007-health-care-facilities-ehs-guidelines-en.pdf",
    "2007-gas-distribution-systems-ehs-guidelines-en.pdf",
    "2007-crude-petroleum-products-terminals-ehs-guidelines-en.pdf",
    "2007-airports-ehs-guidelines-en.pdf",
    "2007-airlines-ehs-guidelines-en.pdf",
    "2007-textiles-manufacturing-ehs-guidelines-en.pdf",
    "2007-tanning-leather-finishing-ehs-guidelines-en.pdf",
    "2007-semiconductors-electronic-ehs-guidelines-en.pdf",
    "2007-printing-ehs-guidelines-en.pdf",
    "2007-metal-plastic-rubber-products-ehs-guidelines-en.pdf",
    "2007-integrated-steel-mills-ehs-guidelines-en.pdf",
    "2007-glass-manufacturing-ehs-guidelines-en.pdf",
    "2007-foundries-ehs-guidelines-en.pdf",
    "2007-construction-materials-extraction-ehs-guidelines-en.pdf",
    "2007-ceramic-tile-sanitary-ware-ehs-guidelines-en.pdf",
    "2022-cement-lime-manufacturing-ehs-guidelines-en.pdf",
    "2007-metal-smelting-refining-ehs-guidelines-en.pdf",
    "2007-sawmilling-wood-products-ehs-guidelines-en.pdf",
    "2007-pulp-and-paper-mills-ehs-guidelines-en.pdf",
    "2007-forest-harvesting-operations-ehs-guidelines-en.pdf",
    "2007-board-and-particle-based-products-ehs-guidelines-en.pdf",
    "2007-phosphate-fertilizer-ehs-guidelines-en.pdf",
    "2007-pharma-biotech-ehs-guidelines-en.pdf",
    "2007-petroleum-polymers-ehs-guidelines-en.pdf",
    "2016-petroleum-refining-ehs-guidelines-en.pdf",
    "2007-pesticides-ehs-guidelines-en.pdf",
    "2007-oleochemicals-manufacturing-ehs-guidelines-en.pdf",
    "2007-nitrogenous-fertilizers-ehs-guidelines-en.pdf",
    "2007-natural-gas-processing-ehs-guidelines-en.pdf",
    "2007-large-vol-petro-organic-chemcials-ehs-guidelines-en.pdf",
    "2007-large-vol-inorganic-compounds-coaltar-ehs-guidelines-en.pdf",
    "2007-coal-processing-ehs-guidelines-en.pdf",
    "2015-vegetable-oil-processing-ehs-guidelines-en.pdf",
    "2007-sugar-manufacturing-ehs-guidelines-en.pdf",
    "2007-poultry-production-ehs-guidelines-en.pdf",
    "2007-poultry-processing-ehs-guidelines-en.pdf",
    "2016-perennial-crop-production-ehs-guidelines-en.pdf",
    "2007-meat-processing-ehs-guidelines-en.pdf",
    "2007-mammalian-livestock-production-ehs-guidelines-en.pdf",
    "2007-food-and-beverage-processing-ehs-guidelines-en.pdf",
    "2007-fish-processing-ehs-guidelines-en.pdf",
    "2007-dairy-processing-ehs-guidelines-en.pdf",
    "2007-breweries-ehs-guidelines-en.pdf",
    "2007-aquaculture-ehs-guidelines-en.pdf",
    "2016-annual-crop-production-ehs-guidelines-en.pdf"
]

def download_file(url: str, filename: str, output_dir: str) -> bool:
    """Télécharge un fichier avec une barre de progression."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(output_dir, filename)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                pbar.update(size)
        return True
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de {filename}: {str(e)}")
        return False

def main():
    """Télécharge tous les fichiers EHS."""
    # Créer le dossier ifc-ehs s'il n'existe pas
    output_dir = "ifc-ehs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Télécharger chaque fichier
    success_count = 0
    for filename in EHS_GUIDELINES:
        url = IFC_EHS_BASE_URL + filename
        if download_file(url, filename, output_dir):
            success_count += 1
    
    logger.info(f"Téléchargement terminé : {success_count}/{len(EHS_GUIDELINES)} fichiers téléchargés avec succès")

if __name__ == "__main__":
    main() 