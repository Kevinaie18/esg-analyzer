"""
Prompt manager for assembling and generating prompts for ESG analysis.
"""

from typing import Dict, List, Optional
from jinja2 import Template
from loguru import logger
from standards.loader import StandardsLoader, StandardCriterion

class PromptManager:
    """Manages the generation and assembly of prompts for ESG analysis."""
    
    def __init__(self, standards_loader: StandardsLoader):
        self.standards_loader = standards_loader
        
    def _get_criteria_text(self, criteria: List[StandardCriterion]) -> str:
        """Convert criteria to formatted text."""
        return "\n".join([
            f"- {c.id}: {c.title} ({c.priority} priority)\n  {c.description}"
            for c in criteria
        ])
        
    def generate_analysis_prompt(
        self,
        company_info: Dict,
        selected_frameworks: List[str],
        detail_level: str = "standard"
    ) -> str:
        """Generate the main analysis prompt."""
        
        # Load selected standards
        standards = {
            fw: self.standards_loader.load_standard(fw)
            for fw in selected_frameworks
        }
        
        # Extract criteria by pillar
        criteria_by_pillar = {
            pillar: []
            for pillar in ['E', 'S', 'G']
        }
        
        for standard in standards.values():
            if standard:
                for criterion in standard.criteria:
                    criteria_by_pillar[criterion.pillar].append(criterion)
        
        # Generate the prompt template
        template = Template("""
You are an expert ESG and Impact analyst specializing in pre-investment analysis. Your task is to analyze the following company information and provide a comprehensive ESG and Impact assessment based on the specified frameworks.

COMPANY INFORMATION:
Name: {{ company_info.name }}
Country: {{ company_info.country }}
Sector: {{ company_info.sector }}
Description: {{ company_info.description }}
{% if company_info.size %}
Size: {{ company_info.size }}
{% endif %}

ANALYSIS FRAMEWORKS:
{% for framework in selected_frameworks %}
- {{ framework.upper() }}
{% endfor %}

RELEVANT CRITERIA:

ENVIRONMENTAL (E):
{{ criteria_e }}

SOCIAL (S):
{{ criteria_s }}

GOVERNANCE (G):
{{ criteria_g }}

Please provide a structured analysis following this format:

1. EXECUTIVE SUMMARY (1 page max)
   - Key ESG risks and opportunities
   - Main impact potential
   - Critical areas for due diligence

2. ENVIRONMENTAL ANALYSIS
   - Key environmental risks and opportunities
   - Climate impact assessment
   - Environmental management practices

3. SOCIAL ANALYSIS
   - Key social risks and opportunities
   - Labor and community relations
   - Social impact potential

4. GOVERNANCE ANALYSIS
   - Key governance risks and opportunities
   - Corporate structure and controls
   - Compliance and ethics

5. IMPACT ASSESSMENT
   - Alignment with SDGs
   - Potential impact metrics
   - Impact risks and mitigation

6. RECOMMENDATIONS
   - Priority actions for due diligence
   - Suggested ESG clauses for shareholder agreement
   - Key performance indicators to track

Please ensure your analysis is:
- Evidence-based and focused on the information provided
- Aligned with the specified frameworks
- Actionable and specific to the company's context
- Clear about any assumptions or limitations
""")
        
        # Render the template
        prompt = template.render(
            company_info=company_info,
            selected_frameworks=selected_frameworks,
            criteria_e=self._get_criteria_text(criteria_by_pillar['E']),
            criteria_s=self._get_criteria_text(criteria_by_pillar['S']),
            criteria_g=self._get_criteria_text(criteria_by_pillar['G'])
        )
        
        return prompt 