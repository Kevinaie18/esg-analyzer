"""
Module de traitement des directives EHS IFC.
"""
import os
import PyPDF2
from typing import Dict, List, Optional
import re
from loguru import logger

class EHSProcessor:
    def __init__(self, ehs_dir: str = "ifc-ehs"):
        self.ehs_dir = ehs_dir
        if not os.path.exists(self.ehs_dir):
            logger.warning(f"Le dossier {self.ehs_dir} n'existe pas. Création du dossier...")
            os.makedirs(self.ehs_dir, exist_ok=True)
            logger.info(f"Le dossier {self.ehs_dir} a été créé. Veuillez y placer les fichiers PDF des directives EHS.")
        
        self.ehs_files = self._get_ehs_files()
        self.sector_mapping = self._create_sector_mapping()
        
    def _get_ehs_files(self) -> Dict[str, str]:
        """Récupère la liste des fichiers EHS disponibles."""
        files = {}
        if not os.path.exists(self.ehs_dir):
            logger.error(f"Le dossier {self.ehs_dir} n'existe pas.")
            return files
            
        for file in os.listdir(self.ehs_dir):
            if file.endswith('.pdf'):
                # Extraire le secteur du nom de fichier
                sector = file.replace('-ehs-guidelines-en.pdf', '').replace('2007-', '').replace('2015-', '').replace('2016-', '').replace('2017-', '')
                files[sector] = os.path.join(self.ehs_dir, file)
        
        if not files:
            logger.warning(f"Aucun fichier PDF trouvé dans le dossier {self.ehs_dir}")
            
        return files
    
    def _create_sector_mapping(self) -> Dict[str, List[str]]:
        """Crée un mapping entre les secteurs principaux et les fichiers EHS correspondants."""
        mapping = {
            'Mining': ['mining'],
            'Oil & Gas': ['onshore-oil-gas-development', 'offshore-oil-gas-development', 'lng', 'natural-gas-processing'],
            'Power': ['thermal-power', 'wind-energy', 'geothermal-power-generation', 'electric-transmission-distribution'],
            'Manufacturing': [
                'cement-lime-manufacturing', 'metal-smelting-refining', 'integrated-steel-mills',
                'metal-plastic-rubber-products', 'textiles-manufacturing', 'semiconductors-electronic'
            ],
            'Infrastructure': [
                'airports', 'ports-harbors-terminals', 'railways', 'toll-roads',
                'water-and-sanitation', 'waste-management-facilities'
            ],
            'Agriculture': [
                'annual-crop-production', 'perennial-crop-production', 'mammalian-livestock-production',
                'poultry-production', 'aquaculture'
            ],
            'Food Processing': [
                'food-and-beverage-processing', 'meat-processing', 'poultry-processing',
                'dairy-processing', 'fish-processing', 'sugar-manufacturing'
            ]
        }
        return mapping
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrait le texte d'un PDF."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {pdf_path}: {str(e)}")
        return text
    
    def get_relevant_ehs_guidelines(self, sector: str, subsector: Optional[str] = None) -> List[str]:
        """Récupère les directives EHS pertinentes pour un secteur donné."""
        relevant_files = []
        
        if not self.ehs_files:
            logger.warning("Aucun fichier EHS disponible")
            return relevant_files
        
        # Vérifier le secteur principal
        if sector in self.sector_mapping:
            for keyword in self.sector_mapping[sector]:
                for file_sector, file_path in self.ehs_files.items():
                    if keyword in file_sector:
                        relevant_files.append(file_path)
        
        # Si un sous-secteur est spécifié, filtrer davantage
        if subsector:
            # Logique de filtrage par sous-secteur à implémenter
            pass
            
        return relevant_files
    
    def extract_key_recommendations(self, pdf_path: str) -> Dict[str, List[str]]:
        """Extrait les recommandations clés d'un document EHS."""
        text = self.extract_text_from_pdf(pdf_path)
        
        recommendations = {
            'environmental': [],
            'health': [],
            'safety': []
        }
        
        # Patterns pour identifier les sections clés
        patterns = {
            'environmental': r'(?i)environmental.*?recommendations?|environmental.*?guidelines?',
            'health': r'(?i)health.*?recommendations?|health.*?guidelines?',
            'safety': r'(?i)safety.*?recommendations?|safety.*?guidelines?'
        }
        
        # Extraire les recommandations pour chaque catégorie
        for category, pattern in patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                # Extraire le paragraphe contenant la recommandation
                start = match.start()
                end = text.find('\n\n', start)
                if end == -1:
                    end = len(text)
                recommendation = text[start:end].strip()
                if recommendation:
                    recommendations[category].append(recommendation)
        
        return recommendations
    
    def get_sector_recommendations(self, sector: str, subsector: Optional[str] = None) -> Dict[str, List[str]]:
        """Récupère les recommandations EHS pour un secteur donné."""
        relevant_files = self.get_relevant_ehs_guidelines(sector, subsector)
        
        all_recommendations = {
            'environmental': [],
            'health': [],
            'safety': []
        }
        
        if not relevant_files:
            logger.warning(f"Aucune directive EHS trouvée pour le secteur {sector}")
            return all_recommendations
        
        for file_path in relevant_files:
            file_recommendations = self.extract_key_recommendations(file_path)
            for category in all_recommendations:
                all_recommendations[category].extend(file_recommendations[category])
        
        return all_recommendations 