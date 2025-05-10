"""
IFC EHS Guidelines Processing Module.
"""
import os
import PyPDF2
from typing import Dict, List, Optional
import re
from loguru import logger

class EHSProcessor:
    def __init__(self, ehs_dir: str = "ifc-ehs"):
        """Initialize the EHS processor.
        
        Args:
            ehs_dir (str): Path to the directory containing EHS files.
                          Defaults to 'ifc-ehs' in the project root.
        """
        self.ehs_dir = ehs_dir
        if not os.path.exists(self.ehs_dir):
            logger.warning(f"""
            ⚠️ The {self.ehs_dir} directory does not exist.
            
            To enable sector-specific EHS recommendations:
            1. Create an `ifc-ehs` directory in the project root
            2. Place the IFC EHS Guidelines PDF files in it
            3. Restart the application
            """)
        
        self.ehs_files = self._get_ehs_files()
        self.sector_mapping = self._create_sector_mapping()
        
    def _get_ehs_files(self) -> Dict[str, str]:
        """Get the list of available EHS files."""
        files = {}
        if not os.path.exists(self.ehs_dir):
            logger.error(f"The {self.ehs_dir} directory does not exist.")
            return files
            
        for file in os.listdir(self.ehs_dir):
            if file.endswith('.pdf'):
                # Extract sector from filename
                sector = file.replace('-ehs-guidelines-en.pdf', '').replace('2007-', '').replace('2015-', '').replace('2016-', '').replace('2017-', '')
                files[sector] = os.path.join(self.ehs_dir, file)
        
        if not files:
            logger.warning(f"""
            ⚠️ No PDF files found in the {self.ehs_dir} directory
            
            To enable sector-specific EHS recommendations:
            1. Download the IFC EHS Guidelines PDF files from https://www.ifc.org/en/ehs-guidelines
            2. Place them in the `ifc-ehs` directory
            3. Restart the application
            """)
            
        return files
    
    def _create_sector_mapping(self) -> Dict[str, List[str]]:
        """Create a mapping between main sectors and corresponding EHS files."""
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
        """Extract text from a PDF file."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
        return text
    
    def get_relevant_ehs_guidelines(self, sector: str, subsector: Optional[str] = None) -> List[str]:
        """Get relevant EHS guidelines for a given sector."""
        relevant_files = []
        
        if not self.ehs_files:
            logger.warning("No EHS files available")
            return relevant_files
        
        # Check main sector
        if sector in self.sector_mapping:
            for keyword in self.sector_mapping[sector]:
                for file_sector, file_path in self.ehs_files.items():
                    if keyword in file_sector:
                        relevant_files.append(file_path)
        
        # If a subsector is specified, filter further
        if subsector:
            # Subsector filtering logic to be implemented
            pass
            
        return relevant_files
    
    def extract_key_recommendations(self, pdf_path: str) -> Dict[str, List[str]]:
        """Extract key recommendations from an EHS document."""
        text = self.extract_text_from_pdf(pdf_path)
        
        recommendations = {
            'environmental': [],
            'health': [],
            'safety': []
        }
        
        # Patterns to identify key sections
        patterns = {
            'environmental': r'(?i)environmental.*?recommendations?|environmental.*?guidelines?',
            'health': r'(?i)health.*?recommendations?|health.*?guidelines?',
            'safety': r'(?i)safety.*?recommendations?|safety.*?guidelines?'
        }
        
        # Extract recommendations for each category
        for category, pattern in patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                # Extract the paragraph containing the recommendation
                start = match.start()
                end = text.find('\n\n', start)
                if end == -1:
                    end = len(text)
                recommendation = text[start:end].strip()
                if recommendation:
                    recommendations[category].append(recommendation)
        
        return recommendations
    
    def get_sector_recommendations(self, sector: str, subsector: Optional[str] = None) -> Dict[str, List[str]]:
        """Get EHS recommendations for a given sector."""
        relevant_files = self.get_relevant_ehs_guidelines(sector, subsector)
        
        all_recommendations = {
            'environmental': [],
            'health': [],
            'safety': []
        }
        
        if not relevant_files:
            logger.warning(f"No EHS guidelines found for sector {sector}")
            return all_recommendations
        
        for file_path in relevant_files:
            file_recommendations = self.extract_key_recommendations(file_path)
            for category in all_recommendations:
                all_recommendations[category].extend(file_recommendations[category])
        
        return all_recommendations 