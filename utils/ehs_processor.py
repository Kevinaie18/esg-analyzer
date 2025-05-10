"""
Process IFC EHS guidelines and extract relevant information.
"""

import os
import re
from typing import Dict, List, Optional
from loguru import logger
import PyPDF2
from concurrent.futures import ThreadPoolExecutor, as_completed

class EHSProcessor:
    def __init__(self, ehs_dir: str = "ifc-ehs"):
        self.ehs_dir = ehs_dir
        self._validate_ehs_directory()
        self._load_ehs_files()
        
    def _validate_ehs_directory(self) -> None:
        """Validate that the EHS directory exists and contains PDF files."""
        if not os.path.exists(self.ehs_dir):
            raise FileNotFoundError(f"EHS directory not found: {self.ehs_dir}")
        
        pdf_files = [f for f in os.listdir(self.ehs_dir) if f.endswith('.pdf')]
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in {self.ehs_dir}")
        
        logger.info(f"Found {len(pdf_files)} EHS guideline PDFs")
    
    def _load_ehs_files(self) -> None:
        """Load all EHS PDF files into memory."""
        self.ehs_files = {}
        pdf_files = [f for f in os.listdir(self.ehs_dir) if f.endswith('.pdf')]
        
        with ThreadPoolExecutor(max_workers=min(8, len(pdf_files))) as executor:
            future_to_file = {
                executor.submit(self._extract_text_from_pdf, os.path.join(self.ehs_dir, pdf)): pdf
                for pdf in pdf_files
            }
            
            for future in as_completed(future_to_file):
                pdf = future_to_file[future]
                try:
                    text = future.result()
                    self.ehs_files[pdf] = text
                except Exception as e:
                    logger.error(f"Error processing {pdf}: {str(e)}")
                    self.ehs_files[pdf] = ""
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file with improved error handling."""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in reader.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Error extracting text from page in {pdf_path}: {str(e)}")
                        continue
                
                return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {str(e)}")
            raise
    
    def get_relevant_guidelines(self, sector: str, subsector: Optional[str] = None) -> Dict[str, str]:
        """
        Get relevant EHS guidelines for a given sector and subsector.
        
        Args:
            sector: The main sector (e.g., "Agribusiness")
            subsector: Optional subsector (e.g., "Crop Production")
            
        Returns:
            Dictionary mapping guideline filenames to their content
        """
        relevant_files = {}
        
        # Normalize sector and subsector names
        sector = sector.lower()
        subsector = subsector.lower() if subsector else None
        
        for filename, content in self.ehs_files.items():
            # Check if the file is relevant to the sector or subsector
            if self._is_relevant_guideline(filename, content, sector, subsector):
                relevant_files[filename] = content
        
        if not relevant_files:
            logger.warning(f"No relevant guidelines found for sector: {sector}, subsector: {subsector}")
        
        return relevant_files
    
    def _is_relevant_guideline(self, filename: str, content: str, sector: str, subsector: Optional[str]) -> bool:
        """
        Check if a guideline is relevant to the given sector and subsector.
        
        Args:
            filename: The name of the guideline file
            content: The content of the guideline
            sector: The main sector
            subsector: Optional subsector
            
        Returns:
            True if the guideline is relevant, False otherwise
        """
        # Check filename for sector/subsector keywords
        filename_lower = filename.lower()
        if sector in filename_lower or (subsector and subsector in filename_lower):
            return True
        
        # Check content for sector/subsector keywords
        content_lower = content.lower()
        
        # Look for sector-specific sections
        sector_patterns = [
            rf"{sector}\s+guidelines",
            rf"{sector}\s+standards",
            rf"{sector}\s+requirements",
            rf"{sector}\s+considerations"
        ]
        
        if any(re.search(pattern, content_lower) for pattern in sector_patterns):
            return True
        
        # If subsector is provided, check for subsector-specific content
        if subsector:
            subsector_patterns = [
                rf"{subsector}\s+guidelines",
                rf"{subsector}\s+standards",
                rf"{subsector}\s+requirements",
                rf"{subsector}\s+considerations"
            ]
            
            if any(re.search(pattern, content_lower) for pattern in subsector_patterns):
                return True
        
        return False
    
    def get_guideline_summary(self, filename: str) -> str:
        """
        Get a summary of a specific guideline.
        
        Args:
            filename: The name of the guideline file
            
        Returns:
            A summary of the guideline's content
        """
        if filename not in self.ehs_files:
            raise ValueError(f"Guideline not found: {filename}")
        
        content = self.ehs_files[filename]
        
        # Extract the first few paragraphs as a summary
        paragraphs = content.split('\n\n')
        summary = '\n\n'.join(paragraphs[:3])
        
        return summary.strip() 