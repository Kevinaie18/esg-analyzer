"""
Standards loader module for ESG frameworks.
Handles loading and parsing of ESG standards from YAML and Markdown files.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from loguru import logger
from pydantic import BaseModel

class StandardCriterion(BaseModel):
    """Model for a single criterion in an ESG standard."""
    id: str
    title: str
    pillar: str  # E, S, or G
    section: str
    keywords: List[str]
    priority: str  # critical, high, medium
    description: str

class ESGStandard(BaseModel):
    """Model for an ESG standard framework."""
    name: str
    version: str
    criteria: List[StandardCriterion]

class StandardsLoader:
    """Handles loading and parsing of ESG standards."""
    
    def __init__(self, standards_dir: str = "standards"):
        self.standards_dir = Path(standards_dir)
        self._standards_cache: Dict[str, ESGStandard] = {}
        
    def load_standard(self, framework: str) -> Optional[ESGStandard]:
        """Load a specific ESG framework."""
        if framework in self._standards_cache:
            return self._standards_cache[framework]
            
        try:
            framework_dir = self.standards_dir / framework
            yaml_path = framework_dir / f"{framework.lower()}.yaml"
            md_path = framework_dir / f"{framework.upper()}-standards.md"
            
            logger.info(f"Loading framework {framework} from {yaml_path} and {md_path}")
            
            if not yaml_path.exists() or not md_path.exists():
                logger.error(f"Missing files for framework {framework}")
                logger.error(f"YAML path exists: {yaml_path.exists()}")
                logger.error(f"MD path exists: {md_path.exists()}")
                return None
                
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
                
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
                
            # Create standard object
            standard = ESGStandard(
                name=yaml_data['name'],
                version=yaml_data['version'],
                criteria=[
                    StandardCriterion(
                        id=c['id'],
                        title=c['title'],
                        pillar=c['pillar'],
                        section=c['section'],
                        keywords=c['keywords'],
                        priority=c['priority'],
                        description=c['description']
                    )
                    for c in yaml_data['criteria']
                ]
            )
            
            self._standards_cache[framework] = standard
            return standard
            
        except Exception as e:
            logger.error(f"Error loading framework {framework}: {str(e)}")
            return None
            
    def get_all_standards(self) -> Dict[str, ESGStandard]:
        """Load all available ESG frameworks."""
        frameworks = ['ifc', '2x', 'internal']
        return {
            fw: self.load_standard(fw)
            for fw in frameworks
            if self.load_standard(fw) is not None
        }
        
    def get_criteria_by_pillar(self, framework: str, pillar: str) -> List[StandardCriterion]:
        """Get all criteria for a specific pillar in a framework."""
        standard = self.load_standard(framework)
        if not standard:
            return []
        return [c for c in standard.criteria if c.pillar == pillar]

    def get_ifc_standards(self) -> str:
        """Get IFC standards in a formatted string."""
        ifc_standard = self.load_standard('ifc')
        if not ifc_standard:
            return "IFC standards not found."
            
        standards_text = f"# IFC Standards ({ifc_standard.version})\n\n"
        for criterion in ifc_standard.criteria:
            standards_text += f"## {criterion.id}: {criterion.title}\n"
            standards_text += f"- Pillar: {criterion.pillar}\n"
            standards_text += f"- Section: {criterion.section}\n"
            standards_text += f"- Priority: {criterion.priority}\n"
            standards_text += f"- Description: {criterion.description}\n\n"
            
        return standards_text 