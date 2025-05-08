from standards.loader import StandardsLoader, ESGStandard
from loguru import logger
import yaml
from pathlib import Path

def test_yaml_loading():
    """Test basic YAML loading."""
    try:
        with open("test.yaml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        logger.info("Successfully loaded test.yaml")
        logger.info(f"Data: {data}")
    except Exception as e:
        logger.error(f"Error loading test.yaml: {str(e)}")

def test_standards_loader():
    """Test the standards loader."""
    loader = StandardsLoader()
    
    # Test loading each framework
    frameworks = ['ifc', '2x', 'internal']
    
    for framework in frameworks:
        logger.info(f"\nTesting framework: {framework}")
        standard = loader.load_standard(framework)
        
        if standard:
            logger.info(f"Successfully loaded {framework}")
            logger.info(f"Name: {standard.name}")
            logger.info(f"Version: {standard.version}")
            logger.info(f"Number of criteria: {len(standard.criteria)}")
            
            # Test getting criteria by pillar
            pillars = ['E', 'S', 'G']
            for pillar in pillars:
                criteria = loader.get_criteria_by_pillar(framework, pillar)
                logger.info(f"Criteria for {pillar}: {len(criteria)}")
        else:
            logger.error(f"Failed to load {framework}")

if __name__ == "__main__":
    logger.info("Testing YAML loading...")
    test_yaml_loading()
    
    logger.info("\nTesting standards loader...")
    test_standards_loader() 